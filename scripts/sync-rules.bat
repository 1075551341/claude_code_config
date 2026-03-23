@echo off
REM 同步 Claude 规则到各编辑器
REM 用法: sync-rules.bat

setlocal enabledelayedexpansion

set "CLAUDE_DIR=%USERPROFILE%\.claude"
set "RULES_SOURCE=%CLAUDE_DIR%\rules"

echo 🔄 开始同步 Claude 规则...

REM 同步核心规则到各编辑器根目录
for %%e in (cursor windsurf trae) do (
    set "target=%USERPROFILE%\.%%erules"
    if exist "%RULES_SOURCE%\RULES_CORE.md" (
        copy /Y "%RULES_SOURCE%\RULES_CORE.md" "!target!" >nul
        echo ✅ 已同步核心规则到 !target!
    )
)

REM 同步完整规则到各编辑器的 rules 目录
for %%e in (cursor windsurf trae) do (
    set "target_dir=%USERPROFILE%\.%%e\rules"
    if not exist "!target_dir!" mkdir "!target_dir!"

    if exist "%RULES_SOURCE%\RULES_BACKEND.md" (
        copy /Y "%RULES_SOURCE%\RULES_BACKEND.md" "!target_dir!\backend.md" >nul
    )

    if exist "%RULES_SOURCE%\RULES_FRONTEND.md" (
        copy /Y "%RULES_SOURCE%\RULES_FRONTEND.md" "!target_dir!\frontend.md" >nul
    )

    echo ✅ 已同步完整规则到 !target_dir!\
)

echo.
echo 📊 同步完成统计:
echo    - 核心规则: ~/.cursorrules, ~/.windsurfrules, ~/.traerules
echo    - 完整规则: ~/.cursor/rules/, ~/.windsurf/rules/, ~/.trae/rules/

endlocal