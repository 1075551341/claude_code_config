# -*- coding: utf-8 -*-
"""
pre-tool-matcher.py v2.0
智能工具匹配推荐器 - 根据自然语言自动推荐合适的 MCP 工具

检测逻辑：
1. 分析用户输入的自然语言
2. 基于关键词和语义匹配最合适的工具
3. 输出推荐结果供模型参考
"""
import json
import re
import sys
from typing import Dict, List, Tuple, Optional

# 工具匹配规则库
# 格式: (匹配模式列表, 推荐工具, 推荐理由)
TOOL_MATCHING_RULES: List[Tuple[List[str], str, str]] = [
    # GitHub 仓库文档类
    (["github.com", "仓库文档", "GitHub 文档", "repo 文档", "项目文档", "anthropics/", "affaan-m/"], 
     "mcp0_ask_question", "GitHub 仓库文档查询，获取结构化 Wiki 内容"),
    
    # 语义搜索类
    (["搜索", "查找", "semantic", "类似", "相关", "AI 搜索", "语义", "智能检索", "找资料"], 
     "mcp1_web_search_exa", "AI 语义搜索，适合找相似内容和智能检索"),
    
    # URL 内容获取类
    (["https://", "http://", "网页内容", "获取页面", "URL", "网址", "访问链接"], 
     "mcp2_fetch", "直接获取 URL 内容，用于访问特定网页"),
    
    # Figma 设计稿类
    (["figma.com", "figma", "设计稿", "UI 设计", "设计稿转代码", "设计规范"], 
     "mcp3_get_design_context", "Figma 设计稿获取，适合设计转代码场景"),
    
    # 文件系统操作类
    (["读取文件", "文件操作", "目录结构", "批量重命名", "复制文件", "移动文件", "文件列表"], 
     "mcp4_", "文件系统操作，项目内/外文件读写"),
    
    # Git 操作类
    (["git 状态", "提交历史", "git log", "git diff", "分支", "git blame", "代码变更"], 
     "mcp5_git_", "Git 版本控制操作，本地仓库管理"),
    
    # Playwright 浏览器类
    (["截图", "网页测试", "E2E", "浏览器自动化", "点击页面", "填写表单", "页面测试"], 
     "mcp6_browser_", "Playwright 浏览器自动化，E2E 测试首选"),
    
    # 记忆存储类
    (["记住", "保存上下文", "记忆", "跨会话", "存储信息", "记住偏好"], 
     "mcp7_create_memory", "跨会话记忆持久化，保存重要上下文"),
    
    # Puppeteer 类（备选浏览器）
    (["PDF 生成", "打印页面", "Chrome 自动化", "puppeteer"], 
     "mcp8_puppeteer_", "Puppeteer Chrome 自动化，PDF 生成场景"),
    
    # 时区和时间类
    (["现在几点", "时区", "时间转换", "timestamp", "时间差"], 
     "mcp-time", "时间与时区工具"),
    
    # 结构化推理类
    (["分析", "设计", "规划", "对比方案", "决策", "架构设计", "复杂推理"], 
     "skill -> sequentialthinking", "复杂推理任务，调用 sequential thinking 技能"),
]

# 技能触发器映射
SKILL_TRIGGERS: Dict[str, List[str]] = {
    "design-brainstorming": ["新功能", "设计组件", "架构设计", "方案讨论", "brainstorm"],
    "systematic-debugging": ["报错", "调试", "bug", "异常", "崩溃", "troubleshooting"],
    "code-refactor": ["重构", "代码优化", "整理代码", "clean up"],
    "test-driven-development": ["TDD", "测试驱动", "先写测试", "red-green-refactor"],
    "implementation-planning": ["写计划", "实施计划", "开发计划", "任务分解"],
    "plan-execution": ["执行计划", "按计划实施", "跟踪进度"],
    "writing-plans": ["计划编写", "方案规划", "milestone"],
    "subagent-driven-development": ["子代理", "并行开发", "agent 协作"],
}

def analyze_intent(query: str) -> Dict:
    """
    分析用户查询意图，返回匹配结果
    """
    query_lower = query.lower()
    recommendations = []
    
    # 1. MCP 工具匹配
    for patterns, tool_prefix, reason in TOOL_MATCHING_RULES:
        for pattern in patterns:
            if pattern.lower() in query_lower:
                recommendations.append({
                    "type": "mcp_tool",
                    "tool": tool_prefix,
                    "confidence": "high" if any(p in query for p in patterns[:2]) else "medium",
                    "reason": reason,
                    "matched_keyword": pattern
                })
                break
    
    # 2. 技能触发器匹配
    for skill_name, triggers in SKILL_TRIGGERS.items():
        for trigger in triggers:
            if trigger in query:
                recommendations.append({
                    "type": "skill",
                    "skill": skill_name,
                    "confidence": "high",
                    "reason": f"触发词 '{trigger}' 匹配技能",
                    "matched_keyword": trigger
                })
                break
    
    # 3. 特殊场景检测
    special_detections = detect_special_scenarios(query)
    recommendations.extend(special_detections)
    
    return {
        "recommendations": recommendations,
        "suggested_action": generate_suggested_action(recommendations)
    }

def detect_special_scenarios(query: str) -> List[Dict]:
    """
    检测特殊场景，如组合工具调用
    """
    results = []
    query_lower = query.lower()
    
    # 组合场景：调试 + 搜索
    if any(k in query_lower for k in ["报错", "错误", "失败"]) and \
       any(k in query_lower for k in ["怎么解决", "怎么办", "原因"]):
        results.append({
            "type": "combination",
            "tools": ["mcp1_web_search_exa", "skill -> systematic-debugging"],
            "confidence": "high",
            "reason": "错误排查场景：先搜索解决方案，再系统化调试",
            "workflow": "1. mcp1_web_search_exa 搜索错误原因 → 2. systematic-debugging 定位根因"
        })
    
    # 组合场景：设计 + 文档
    if any(k in query_lower for k in ["设计", "架构", "规划"]) and \
       any(k in query_lower for k in ["文档", "说明", "wiki"]):
        results.append({
            "type": "combination",
            "tools": ["mcp0_ask_question", "skill -> design-brainstorming"],
            "confidence": "high",
            "reason": "设计规划场景：查询参考设计 + 头脑风暴",
            "workflow": "1. mcp0_ask_question 查参考设计 → 2. design-brainstorming 制定方案"
        })
    
    # 组合场景：开发 + 测试
    if any(k in query_lower for k in ["开发", "实现", "编写"]) and \
       any(k in query_lower for k in ["功能", "模块", "组件"]):
        results.append({
            "type": "combination",
            "tools": ["skill -> implementation-planning", "skill -> test-driven-development"],
            "confidence": "medium",
            "reason": "功能开发场景：先制定计划，考虑 TDD 模式",
            "workflow": "建议先调用 implementation-planning 制定实施计划"
        })
    
    return results

def generate_suggested_action(recommendations: List[Dict]) -> str:
    """
    根据推荐结果生成建议动作
    """
    if not recommendations:
        return "未检测到特定工具需求，按标准流程处理"
    
    high_conf = [r for r in recommendations if r.get("confidence") == "high"]
    
    if high_conf:
        top = high_conf[0]
        if top["type"] == "mcp_tool":
            return f"建议调用 {top['tool']} 工具：{top['reason']}"
        elif top["type"] == "skill":
            return f"建议调用 skill '{top['skill']}'：{top['reason']}"
        elif top["type"] == "combination":
            return f"建议组合调用：{top['workflow']}"
    
    return f"有 {len(recommendations)} 个潜在匹配，请根据上下文选择最合适的工具"

def main():
    """主入口函数"""
    try:
        # 读取 stdin
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
        
        # 提取查询内容
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
        
        # 如果工具已明确指定，跳过匹配
        if tool_name and tool_name != "Skill":
            sys.exit(0)
        
        # 构建查询字符串
        query_parts = []
        if isinstance(tool_input, dict):
            for key, value in tool_input.items():
                if isinstance(value, str):
                    query_parts.append(value)
        query = " ".join(query_parts) if query_parts else str(tool_input)
        
        # 分析意图
        result = analyze_intent(query)
        
        # 如果有高置信度推荐，输出建议
        if result["recommendations"]:
            print(f"[工具匹配推荐] {result['suggested_action']}", file=sys.stderr)
            
            # 输出结构化结果供后续处理
            output = {
                "tool_matching": {
                    "detected": True,
                    "recommendations": result["recommendations"],
                    "suggested_action": result["suggested_action"],
                    "original_query": query[:200]  # 限制长度
                }
            }
            print(json.dumps(output, ensure_ascii=False))
        
        sys.exit(0)
        
    except Exception as e:
        # 静默失败，不影响主流程
        sys.exit(0)

if __name__ == "__main__":
    main()
