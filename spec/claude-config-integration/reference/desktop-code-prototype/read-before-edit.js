#!/usr/bin/env node
/**
 * hooks/pre-tool-use/read-before-edit.js
 * GSD read-before-edit 安全检查
 * 在 Edit/Write 工具调用前，确保文件已在本会话中读取过
 *
 * Claude Code settings.json 配置：
 * {
 *   "hooks": {
 *     "PreToolUse": [{ "matcher": "Edit|Write", "hooks": [{ "type": "command", "command": "node ~/.claude/hooks/pre-tool-use/read-before-edit.js" }] }]
 *   }
 * }
 */

const input = JSON.parse(process.env.CLAUDE_TOOL_INPUT || '{}');
const toolName = process.env.CLAUDE_TOOL_NAME || '';
const sessionFiles = JSON.parse(process.env.CLAUDE_SESSION_READ_FILES || '[]');

if (['Edit', 'Write', 'str_replace_editor'].includes(toolName)) {
  const targetFile = input.file_path || input.path || '';

  if (targetFile && !sessionFiles.includes(targetFile)) {
    // 输出警告，Claude Code 会展示给用户
    process.stderr.write(
      `[read-before-edit] 警告：尝试编辑 ${targetFile}，但本会话未读取此文件。\n` +
      `请先使用 Read 工具读取该文件后再编辑。\n`
    );
    // exit 1 会阻止工具调用（Claude Code behavior）
    process.exit(1);
  }
}

process.exit(0);
