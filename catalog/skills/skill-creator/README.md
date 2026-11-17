# Skill Name: Skill Creator

[TOC]

## Overview

The Skill Creator is a meta-skill designed to create effective skills with Huawei practices.

## Features

* **Lifecycle Management:** Seamlessly create new skills or iterate updating on existing ones.
* **Standardized Validation:** Ensure strict compliance with the [open specification standard](https://agentskills.io/specification).
* **Smart Frontmatter:** Easily define core descriptions, usage contexts, and version metadata.
* **Automated Scaffolding:** Instantly generate essential project files, including `README.md`, `CHANGELOG.md`, and appropriate licenses.
* **Built-in Testing:** Auto-generate robust test cases and evaluation sets to guarantee skill quality.

## Prerequisites & Setup

Before this skill can be tested or deployed, ensure the following requirements are met:

* **Python Environment:** Requires a standard Python 3.10+ to execute `scripts/init_skill.py`
* **Dependencies:** Requires PyYAML package, install with command: `pip install pyyaml`
* **Target Skill:** Requires the target skill to only be updated. Default is installed at the project level directory of agent, or specified by the user

## Local Testing & Usage

To run and test the skill locally without needing to spin up the full agent framework:

**Skill Initializer**

```bash
python scripts/init_skill.py <skill-name> --path <path>
```

* `skill-name`: The skill name to be created or updated.
* `<path>`: The output folder path contained the target skill

```bash
Skill Initializer - Creates a new skill from template

Usage:
    init_skill.py <skill-name> --path <path>

Examples:
    init_skill.py my-new-skill --path skills/public
    init_skill.py my-api-helper --path skills/private
    init_skill.py custom-skill --path /custom/location
```

**Skill Validator**

```bash
python scripts/quick_validate.py <skill-directory>
```

`skill-directory`: The skill directory

## Trigger Prompts & User Scenarios

Examples of human prompts that should trigger the agent to invoke this skill. (**Note: all below scenarios are executing on OpenCode*)

- **Scenario 1: Create a simple new skill**
  - *User Prompt:* `Create a skill to greeting message as simple as possible`
  - *Expected Agent Behavior:* Agent triggers `skill-creator` to create a simple greeting skill

Script Output by  `init_skill.py` (As intermediate process output for LLM reasoning):

```bash
Initializing skill: simple-greeting
   Location: .opencode/skills
Created skill directory: .opencode\skills\simple-greeting
Created SKILL.md
Created scripts/example.py
Created references/api_reference.md
Created assets/example_asset.txt
Created evals/evals.json
Created tests/conftest.py
Copied template/README.md
Copied template/CHANGELOG.md
Copied template/LICENSE.md
Copied template/LICENSE.txt
Skill 'simple-greeting' initialized successfully at .opencode\skills\simple-greeting
Next steps:
1. Edit SKILL.md to complete the TODO items and update the description
2. Customize or delete the example files in scripts/, references/, and assets/
3. Customize the test files in evals/ and tests/
4. Customize template files (README.md, CHANGELOG.md, LICENSE.*)
5. Run the validator when ready to check the skill structure
```

Script Output by  `quick_validate.py` (As intermediate process output for LLM reasoning):

```bash
Skill is valid!
```

Skill Output (As final output for end user):

```markdown
Created simple-greeting skill successfully at .opencode/skills/simple-greeting.
```

The folder structure of created skill as below:

```bash
.opencode/skills/simple-greeting
|   CHANGELOG.md
|   LICENSE.md
|   README.md
|   SKILL.md
|
+---assets
+---evals
|       evals.json
|
+---references
+---scripts
\---tests
```

- **Scenario 2: Create a simple new skill with script file**

  - *User Prompt:* `create a skill to greeting message as simple as possible, and all messages need to be outputted from a Python script`
  - *Expected Agent Behavior:* Agent triggers `skill-creator` to create another simple greeting skill

  Script Output by  `init_skill.py` (As intermediate process output for LLM reasoning):

  ```bash
  Initializing skill: python-greeting
     Location: .opencode/skills
  Created skill directory: .opencode\skills\python-greeting
  Created SKILL.md
  Created scripts/example.py
  Created references/api_reference.md
  Created assets/example_asset.txt
  Created evals/evals.json
  Created tests/conftest.py
  Copied template/README.md
  Copied template/CHANGELOG.md
  Copied template/LICENSE.md
  Copied template/LICENSE.txt
  Skill 'python-greeting' initialized successfully at .opencode\skills\python-greeting
  Next steps:
  1. Edit SKILL.md to complete the TODO items and update the description
  2. Customize or delete the example files in scripts/, references/, and assets/
  3. Customize the test files in evals/ and tests/
  4. Customize template files (README.md, CHANGELOG.md, LICENSE.*)
  5. Run the validator when ready to check the skill structure
  ```

  Script Output by  `quick_validate.py` (As intermediate process output for LLM reasoning):

  ```bash
  Skill is valid!
  ```

  Skill Output (As final output for end user):

  ```markdown
  Created python-greeting skill successfully at .opencode/skills/python-greeting.
  ```

  The folder structure of created skill as below:

  ```bash
  .opencode/skills/python-greeting
  |   CHANGELOG.md
  |   LICENSE.md
  |   README.md
  |   SKILL.md
  |
  +---evals
  |       evals.json
  |
  +---scripts
  |       greeting.py
  |
  +---references
  +---scripts
  \---tests
          conftest.py
          test_e2e.py
          test_greeting.py
  ```

* **Scenario 3: Create a new skill with wrong name**
  * *User Prompt:* `create a skill with name CodeReviewer`
  * *Expected Agent Behavior:* Agent triggers `skill-creator` to create with name `CodeReviewer`, detect its violation to open standard, and open a confirmation to give an appropriate name as `code-reviewer`

Skill Output:

```bash
Rule violation: Skill names may only contain lowercase alphanumeric characters (a-z) and hyphens (-). Uppercase letters are not allowed.
Valid alternatives:
- code-reviewer
- code-reviewer-skill
Please provide a corrected skill name that follows the naming rules.
```

After using the the right name, the skill will be created successfully.

## Input & Output Specification

**Inputs (Arguments provided by the Agent)** 

* `skill_name` (Optional): The name of the skill being created or updated (e.g., "code-refactoring").
* `output_path` (Optional): The specific path containing the skill folder. If not provided, it defaults to project level skill's directory of agent.

**Outputs (Payload returned to the Agent)**

The skill was created or updated successfully.

## Limitations & Known Issues

N/A

## Non-Functional Metrics

- **Average Latency:** Highly dependent on the complexity of user's scenarios
- **Token Consumption:** Expect ~20K tokens

## Packaging Instructions

N/A

## Contributing

* Compliance with the [open specification standard](https://agentskills.io/specification)
* Make sure to pass all tests

## Acknowledgments & References

This skill was built by adapting and wrapping the following open-source projects:

- [Claude-Skills: skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator): A skill for creating new skills and iteratively improving them.

## License

This project is licensed, please see the [LICENSE](LICENSE.txt) file for details.