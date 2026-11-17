# Skill Name: [Insert Skill Name Here]

[TOC]

## Overview

*Provide a 1-2 sentence description of what this skill does. e.g., "This skill allows the agent to analyze a provided code snippet or file, identify anti-patterns, and generate a refactored version adhering to SOLID and DRY principles."*

## Features

* *[Feature 1: e.g., Automatically detects common code smells like long methods or duplicate logic.]*
* *[Feature 2: e.g., Generates a side-by-side diff of the original vs. refactored code.]*
* *[Feature 3: e.g., Supports Python, JavaScript/TypeScript, and Java.]*
* *[Feature 4: e.g., Suggests updated unit tests to match the refactored logic.]*

## Prerequisites & Setup

Before this skill can be tested or deployed, ensure the following requirements are met:

* **Environment Variables:** *[e.g., Copy `.env.example` to `.env` and configure `SONARQUBE_API_KEY` if using external static analysis.]*
* **Local Tools:** *[e.g., Ensure `black` or `prettier` formatters are installed in the local environment.]*
* **Dependencies:** *[e.g., Run `pip install -r requirements.txt` or `npm install`]*
* **Model Context Protocol (MCP):** *[e.g., Ensure the host agent environment supports MCP to handle tool execution and context sharing.]*

## Local Testing & Usage

*Explain how a human developer can run and test the skill locally without needing to spin up the full agent framework.*

```bash
# Example test command
python test_skill.py --target_file ./src/legacy_module.py --language python
```

## Trigger Prompts & User Scenarios

*Examples of human prompts that should trigger the agent to invoke this skill. This helps maintainers understand the intended UX.*

- **Scenario 1: General Cleanup**
  - *User Prompt:* "Can you clean up this Python function? It's getting too hard to read."
  - *Expected Agent Behavior:* Agent extracts the code snippet from the chat, identifies the language, and triggers this skill to return a more readable version.
- **Scenario 2: Targeted Refactoring**
  - *User Prompt:* "Refactor this React class component to use functional components and Hooks."
  - *Expected Agent Behavior:* Agent triggers this skill using the `focus_area="modernization"` and `language="javascript"` parameters.

## Input & Output Specification

**Inputs (Arguments provided by the Agent)** 

*The arguments are requested by skill and passed by Agent.*

**Outputs (Payload returned to the Agent)**

*The skill returns a structured JSON object to the agent's context containing:*

- `status` (string): "success" or "error".
- `refactored_code` (string): The fully formatted, executable refactored code.
- `explanation` (string): A brief summary of what was changed and why (e.g., "Extracted nested loop into a helper function to reduce cyclomatic complexity").
- `diff` (string): A standard unified diff string showing exact line changes.
- `error_message` (string | null): Populated only if the parser fails.

## Limitations & Known Issues

*Crucial context for developers to understand why an agent might fail or hallucinate when using this tool.*

- **Limitation 1:** [e.g., Token limits: This skill cannot process entire repositories or files larger than 500 lines at once. The agent must chunk the code.]
- **Limitation 2:** [e.g., Framework Context: The skill evaluates code in isolation. It might suggest removing a variable that looks unused but is actually required by an undocumented framework macro.]
- **Edge Case:** [e.g., Incompletely pasted code snippets (missing closing brackets) will cause the internal AST parser to throw a 500 error.]

## Non-Functional Metrics

*Add non-functional requirements here for performance, reliability etc.*

- **Average Latency:** [e.g., ~5-8 seconds per execution, highly dependent on code size]
- **Token Consumption:** [e.g., High. Expect ~1500 prompt tokens and ~1000 completion tokens per standard execution.]
- **Reliability:** [e.g., 95% successful AST parsing rate.]

## Packaging Instructions

*To bundle this skill for the agent (which automatically ignores this documentation and focuses only on the code and schema), run:*

```bash
[Insert your build script command here, e.g., make build-agent-package]
```

## Contributing

*Provide guidelines for pull requests, linting, testing standards, and adding new languages or refactoring patterns to the internal logic.*

## Acknowledgments & References

*This skill was built by adapting and wrapping the following open-source projects:*

- [Skills-4-SE: code-refactoring-assistant](https://github.com/ArabelaTso/Skills-4-SE/tree/main/skills/code-refactoring-assistant): Systematically improve code structure and quality through targeted refactoring.
- [Skills-4-SE: code-smell-detector](https://github.com/ArabelaTso/Skills-4-SE/tree/main/skills/code-smell-detector): Identify code quality and design smells in Python codebases.

## License

This project is licensed, please see the [LICENSE](LICENSE.txt) file for details.