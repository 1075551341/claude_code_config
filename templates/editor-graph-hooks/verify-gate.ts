/**
 * OpenCode 验证门（本地判定，不 spawn 外部脚本）。
 *
 * 平台限制：无 Stop exit-2。用 system 注入 + idle 未验标记 + 下轮加急提醒。
 * 状态：~/.config/opencode/.state/verify-gate.json
 *
 * 钩子：
 *  - chat.message / message.updated[user] → 记录需求文本
 *  - tool.execute.after                  → 追踪 bash / edit|write|patch|multiedit
 *  - session.idle                        → 有未验编辑则待提醒
 *  - experimental.text.complete          → R20 合格则清除待提醒
 *  - experimental.chat.system.transform  → 有未验编辑时注入一次 R20；idle 加急每周期一次
 */
import type { Plugin } from "@opencode-ai/plugin";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const STATE_DIR = join(homedir(), ".config", "opencode", ".state");
const STATE_FILE = join(STATE_DIR, "verify-gate.json");

const R20_RULE =
  "[完成验证] 仅当本回合有过文件编辑时输出短 R20（各一行：满足/遗漏/错改/漏改/原功能/影响范围）。" +
  "计划未落地、零编辑不要终审。满足须承认/反驳/弃权；漏改写无文档影响或路径；原功能附证据；影响范围含 CRG/IMPACT/blast。" +
  "非简单：每轮修改→验证→审查（对照预期审全部修改），最多 3 轮；禁止只连审不改。机械门与 scripts/r20_check.py 对齐。无观察输出不得声称完成。";

const EDIT_TOOLS = new Set(["edit", "write", "patch", "multiedit"]);

type SessionState = {
  edited: boolean;
  verified: boolean;
  req?: string;
};

type Store = Record<string, SessionState>;

function loadStore(): Store {
  try {
    if (!existsSync(STATE_FILE)) return {};
    const raw = readFileSync(STATE_FILE, "utf8");
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

function saveStore(store: Store) {
  try {
    mkdirSync(STATE_DIR, { recursive: true });
    writeFileSync(STATE_FILE, JSON.stringify(store, null, 2), "utf8");
  } catch {
    // 状态写入失败不得阻断主链路
  }
}

function sessionOf(store: Store, sid: string): SessionState {
  if (!store[sid]) store[sid] = { edited: false, verified: false };
  return store[sid];
}

function extractText(parts: any[] | undefined): string {
  if (!Array.isArray(parts)) return "";
  return parts
    .filter((p) => p && p.type === "text" && typeof p.text === "string")
    .map((p) => p.text)
    .join("\n");
}

function extractPaths(args: any): string[] {
  if (!args || typeof args !== "object") return [];
  const raw = args.filePath ?? args.file_path ?? args.path ?? args.file;
  if (typeof raw === "string") return [raw];
  if (Array.isArray(raw))
    return raw.filter((x): x is string => typeof x === "string");
  return [];
}

const EMPTY_SAT = new Set(["", ".", "..", "...", "…", "无", "n/a", "na", "none"]);
const IMPACT_TOKENS = [
  "crg",
  "get_impact_radius",
  "impact",
  "blast-radius",
  "blast radius",
  "影响面",
  "影响范围",
];
const FIELD_RE =
  /(?:^|\n)\s*-?\s*(满足|遗漏|错改|漏改|原功能|影响范围|影响面)\s*[：:]\s*([\s\S]*?)(?=(?:\n\s*-?\s*(?:满足|遗漏|错改|漏改|原功能|影响范围|影响面)\s*[：:])|\n结论|$)/g;

function fieldValue(text: string, name: string): string {
  FIELD_RE.lastIndex = 0;
  let match: RegExpExecArray | null;
  while ((match = FIELD_RE.exec(text))) {
    if (match[1] === name) return (match[2] || "").trim();
  }
  return "";
}

function checkR20(text: string): boolean {
  if (!text || !text.trim()) return false;
  if (!/会话终验|\bR20\b/.test(text)) return false;
  for (const field of ["遗漏", "错改", "漏改", "原功能", "影响范围"]) {
    if (!text.includes(field)) return false;
  }
  const sat = fieldValue(text, "满足");
  if (EMPTY_SAT.has(sat.toLowerCase())) return false;
  const missed = fieldValue(text, "漏改");
  if (!missed) return false;
  if (!/(文档|无文档影响)/.test(missed) && !/[\\/]|\.\w{2,8}\b/.test(missed))
    return false;
  const orig = fieldValue(text, "原功能");
  if (!orig || !/(证据|测试|冒烟)/.test(orig)) return false;
  const impact = fieldValue(text, "影响范围") || fieldValue(text, "影响面");
  if (!impact || EMPTY_SAT.has(impact.toLowerCase())) return false;
  const low = impact.toLowerCase();
  if (!IMPACT_TOKENS.some((token) => low.includes(token))) return false;
  return true;
}

export const VerifyGate: Plugin = async ({ client }) => {
  const pendingReminder = new Set<string>();
  const captured = new Set<string>();
  const ruleInjected = new Set<string>();
  const urgentInjected = new Set<string>();

  async function log(
    level: "debug" | "info" | "warn" | "error",
    message: string,
    extra?: Record<string, any>,
  ) {
    try {
      await client.app.log({
        body: { service: "verify-gate", level, message, extra },
      });
    } catch {
      // 日志失败静默
    }
  }

  function captureReq(sid: string, text: string, source: string) {
    if (!sid || !text.trim() || captured.has(sid)) return;
    captured.add(sid);
    const store = loadStore();
    const s = sessionOf(store, sid);
    s.req = text.slice(0, 4000);
    saveStore(store);
    void log("info", `capture-req(${source})`, { sid: sid.slice(0, 12) });
  }

  await log("info", "plugin loaded", { state: STATE_FILE });

  return {
    "chat.message": async (msg) => {
      const sid = msg.sessionID;
      pendingReminder.delete(sid);
      urgentInjected.delete(sid);
      captureReq(sid, extractText(msg.parts), "chat.message");
    },

    "tool.execute.after": async (evt) => {
      const sid = evt.sessionID;
      if (!sid) return;
      const tool = String(evt.tool || "").toLowerCase();
      const store = loadStore();
      const s = sessionOf(store, sid);
      if (tool === "bash") {
        const cmd = String(evt.args?.command ?? evt.args?.cmd ?? "");
        if (
          cmd.trim() &&
          /(test|lint|build|typecheck|pytest|vitest|npm test|pnpm test)/i.test(
            cmd,
          )
        ) {
          s.verified = s.verified || false;
        }
        saveStore(store);
        return;
      }
      if (EDIT_TOOLS.has(tool)) {
        const paths = extractPaths(evt.args);
        if (paths.length) {
          s.edited = true;
          s.verified = false;
          saveStore(store);
        }
      }
    },

    event: async ({ event }) => {
      const ev = event as any;
      if (ev?.type === "message.updated") {
        const info = ev.properties?.info;
        if (info?.role === "user" && info?.sessionID) {
          const sid = String(info.sessionID);
          pendingReminder.delete(sid);
          urgentInjected.delete(sid);
          captureReq(sid, extractText(ev.properties?.parts), "message.updated");
        }
        return;
      }
      if (ev?.type === "session.idle") {
        const sid = String(ev.properties?.sessionID ?? "");
        if (!sid) return;
        const store = loadStore();
        const s = store[sid];
        if (s && s.edited && !s.verified) {
          pendingReminder.add(sid);
          await log("info", "idle unverified → pending reminder", {
            sid: sid.slice(0, 12),
          });
        }
      }
    },

    "experimental.text.complete": async (inp, output) => {
      const sid = inp.sessionID;
      if (!sid) return;
      const store = loadStore();
      const s = store[sid];
      if (!s || !s.edited) return;
      if (checkR20(output.text ?? "")) {
        s.verified = true;
        saveStore(store);
        pendingReminder.delete(sid);
        urgentInjected.delete(sid);
      }
    },

    "experimental.chat.system.transform": async (inp, output) => {
      const sid = (inp as { sessionID?: string })?.sessionID as
        | string
        | undefined;
      const store = sid ? loadStore() : {};
      const s = sid ? store[sid] : undefined;
      if (sid && s?.edited && !s.verified && !ruleInjected.has(sid)) {
        output.system.push(R20_RULE);
        ruleInjected.add(sid);
      }
      if (sid && pendingReminder.has(sid) && !urgentInjected.has(sid)) {
        output.system.push(
          "[加急] 上一回合结束时检测到存在未经验证的编辑：本回合必须先完成验证并输出合格 R20 会话终验，再回应其他内容。",
        );
        urgentInjected.add(sid);
      }
    },
  };
};
