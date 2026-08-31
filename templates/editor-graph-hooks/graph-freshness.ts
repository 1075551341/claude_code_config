/**
 * OpenCode 图谱保鲜：每会话 ensure 一次、规则注入一次；idle refresh 有冷却。
 * CLI = 本目录 scripts/graph_freshness_cli.py（自管副本，不读 ~/.claude）。
 */
import type { Plugin } from "@opencode-ai/plugin";
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const HOME = join(homedir(), ".config", "opencode");
const CLI = join(HOME, "scripts", "graph_freshness_cli.py");
const CFG = join(HOME, "graph-freshness.json");
const REFRESH_COOLDOWN_MS = 60_000;
const GRAPH_RULE =
  "[图谱保鲜] eligible git 仓须先有 codegraph 与 code-review-graph。" +
  "插件已在会话开始执行 ensure（每会话一次）。无图禁止 Grep/Glob 当探索主路径。" +
  "禁止反复重跑 ensure/refresh，禁止把压缩提示伪造成新的用户消息。";

type Result = {
  ok?: boolean;
  skipped?: boolean;
  blocked?: boolean;
  error?: string;
  mode?: string;
  ui?: string;
  codegraph?: boolean;
  crg?: boolean;
  root?: string;
};

function fallbackBanner(result: Result, action: "ensure" | "refresh"): string {
  const verb = action === "ensure" ? "会话同步双图" : "收尾刷新双图";
  if (result.skipped) return `【${verb}】跳过：非 git 仓或已关闭`;
  if (result.ok) return `【${verb}】成功`;
  return `【${verb}】失败：${result.error || "ensure 失败"}`;
}

function runCli(
  mode: "ensure" | "refresh",
  cwd: string,
  log: (m: string, extra?: Record<string, unknown>) => void,
): Result {
  if (!existsSync(CLI)) {
    log("cli missing", { cli: CLI });
    return {
      ok: false,
      blocked: true,
      error: "graph_freshness_cli.py missing",
    };
  }
  const args = [CLI, mode, "--cwd", cwd];
  if (existsSync(CFG)) args.push("--config", CFG);
  const proc = spawnSync("python", args, {
    encoding: "utf8",
    timeout: mode === "ensure" ? 130000 : 40000,
    windowsHide: true,
  });
  const line =
    (proc.stdout || "").trim().split(/\r?\n/).filter(Boolean).pop() || "";
  try {
    return JSON.parse(line) as Result;
  } catch {
    log("cli parse fail", {
      status: proc.status,
      err: (proc.stderr || "").slice(0, 240),
    });
    return { ok: false, blocked: true, error: "cli json parse fail" };
  }
}

export const GraphFreshness: Plugin = async ({
  client,
  directory,
  worktree,
}) => {
  const cwd = worktree || directory || process.cwd();
  const ensured = new Set<string>();
  const ruleInjected = new Set<string>();
  const blockedInjected = new Set<string>();
  const lastRefreshAt = new Map<string, number>();
  const toasted = new Set<string>();
  let last: Result = { ok: true, skipped: true };

  async function log(message: string, extra?: Record<string, unknown>) {
    try {
      await client.app.log({
        body: { service: "graph-freshness", level: "info", message, extra },
      });
    } catch {
      // 日志失败不得阻断
    }
  }

  async function showUi(sid: string, action: "ensure" | "refresh", result: Result) {
    const key = `${sid}:${action}`;
    if (toasted.has(key)) return;
    const banner = (result.ui || fallbackBanner(result, action)).slice(0, 400);
    const variant = result.skipped ? "info" : result.ok ? "success" : "error";
    try {
      await client.tui.showToast({
        body: {
          title: "双图谱",
          message: banner,
          variant,
          duration: result.ok ? 6000 : 12000,
        },
      });
      toasted.add(key);
    } catch {
      // TUI 未就绪则下次 chat.message 再试，不改成伪造用户消息
    }
  }

  function ensureOnce(sid: string) {
    if (!sid) return;
    if (!ensured.has(sid)) {
      ensured.add(sid);
      last = runCli("ensure", cwd, (m, extra) => {
        void log(m, extra);
      });
      void log("ensure", {
        sid: sid.slice(0, 12),
        ok: last.ok,
        skipped: last.skipped,
        blocked: last.blocked,
      });
    }
    void showUi(sid, "ensure", last);
  }

  function refreshIdle(sid: string) {
    const key = sid || cwd;
    const now = Date.now();
    const prev = lastRefreshAt.get(key) ?? 0;
    if (now - prev < REFRESH_COOLDOWN_MS) {
      void log("refresh skipped (cooldown)", { key: key.slice(0, 12) });
      return;
    }
    lastRefreshAt.set(key, now);
    last = runCli("refresh", cwd, (m, extra) => {
      void log(m, extra);
    });
    void log("refresh", { ok: last.ok, skipped: last.skipped });
    if (sid) void showUi(sid, "refresh", last);
  }

  await log("plugin loaded", { cwd, cli: CLI });

  return {
    "chat.message": async (msg: { sessionID?: string }) => {
      if (msg?.sessionID) ensureOnce(msg.sessionID);
    },

    event: async ({
      event,
    }: {
      event: { type?: string; properties?: { sessionID?: string } };
    }) => {
      const ev = event as {
        type?: string;
        properties?: { sessionID?: string };
      };
      if (ev?.type === "session.created") {
        const sid = String(ev.properties?.sessionID ?? "");
        if (sid) ensureOnce(sid);
        return;
      }
      if (ev?.type === "session.idle") {
        refreshIdle(String(ev.properties?.sessionID ?? ""));
      }
    },

    "experimental.chat.system.transform": async (inp, output) => {
      const sid = String((inp as { sessionID?: string })?.sessionID ?? cwd);
      if (!ruleInjected.has(sid)) {
        output.system.push(GRAPH_RULE);
        ruleInjected.add(sid);
      }
      if (last.blocked && !blockedInjected.has(sid)) {
        output.system.push(
          `[图谱未就绪] ${last.error || "ensure 失败"}。禁止 Grep/编辑/查询 MCP，先安装 CLI 并重开会话。`,
        );
        blockedInjected.add(sid);
      }
    },
  };
};
