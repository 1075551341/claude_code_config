---
name: skill-creator
description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Agent's capabilities with specialized knowledge, workflows, or tool integrations.
metadata:
  version: 1.0.3
loading_tier: L3
disable-model-invocation: true
---

# Skill Creator

This skill provides guidance for creating effective skills with Huawei practices.

## Anatomy of a Skill

Every skill consists of a required `SKILL.md` file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
├── README.md (required)
├── CHANGELOG.md (required)
├── LICENSE.txt (required)
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

### `SKILL.md` (required)

Every `SKILL.md` consists of:

- **Frontmatter** (YAML): Contains `name` and `description` fields (required), plus optional fields like `license`, `metadata`, and `compatibility`. Only `name` and `description` are read by Agent to determine when the skill triggers, so be clear and comprehensive about what the skill is and when it should be used. The `compatibility` field is for noting environment requirements (target product, system packages, etc.) but most skills don't need it.
- **Body** (Markdown): Instructions and guidance for using the skill. Only loaded AFTER the skill triggers (if at all).

## Progressive Disclosure Design Principle

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **`SKILL.md` body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Agent (Unlimited because scripts can be executed without reading into context window)

### Progressive Disclosure Patterns

Keep `SKILL.md` body to the essentials and under 500 lines to minimize context bloat. Split content into separate files when approaching this limit. When splitting out content into other files, it is very important to reference them from `SKILL.md` and describe clearly when to read them, to ensure the reader of the skill knows they exist and when to use them.

**Key principle:** When a skill supports multiple variations, frameworks, or options, keep only the core workflow and selection guidance in `SKILL.md`. Move variant-specific details (patterns, examples, configuration) into separate reference files.

**Pattern 1: High-level guide with references**

```markdown
# PDF Processing

## Quick start

Extract text with pdfplumber:
[code example]

## Advanced features

- **Form filling**: See [FORMS.md](FORMS.md) for complete guide
- **API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
- **Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
```

Agent loads `FORMS.md`, `REFERENCE.md`, or `EXAMPLES.md` only when needed.

**Pattern 2: Domain-specific organization**

For Skills with multiple domains, organize content by domain to avoid loading irrelevant context:

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

When a user asks about sales metrics, Agent only reads sales.md.

Similarly, for skills supporting multiple frameworks or variants, organize by variant:

```
cloud-deploy/
├── SKILL.md (workflow + provider selection)
└── references/
    ├── aws.md (AWS deployment patterns)
    ├── gcp.md (GCP deployment patterns)
    └── azure.md (Azure deployment patterns)
```

When the user chooses AWS, Agent only reads aws.md.

**Pattern 3: Conditional details**

Show basic content, link to advanced content:

```markdown
# DOCX Processing

## Creating documents

Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents

For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

Agent reads `REDLINING.md` or `OOXML.md` only when the user needs those features.

**Important guidelines:**

- **Avoid deeply nested references** - Keep references one level deep from `SKILL.md`. All reference files should link directly from `SKILL.md`.
- **Structure longer reference files** - For files longer than 100 lines, include a table of contents at the top so Agent can see the full scope when previewing.

## Skill Creation Process

Skill creation involves these steps:

1. Determine the target skill name
2. Ask for confirmation
3. Understand the skill with concrete examples
4. Plan reusable skill contents (scripts, references, assets)
5. Initialize the skill (run `init_skill.py`)
6. Edit the skill (implement resources and write `SKILL.md`)
7. Validate the skill (run `quick_validate.py`)
8. Iterate based on real usage

Follow these steps in order, skipping only if there is a clear reason why they are not applicable.

**Note:** The working directory is the skill root (the same level as `SKILL.md`). Ensure all scripts are executed from this location.

### Step 1: Validate Target Skill Name

Evaluate the user's request:
* **If a skill name is provided:** You MUST validate it against the strictly enforced rules below before asking any other questions or executing any commands.
* **If a skill name is NOT provided yet:** You MUST resolve by yourself to create a valid skill name and validate it with below rules.

**Naming Rules & Constraints:**

1. **`SKILL.md` filename:** Case-sensitive and must be exactly `SKILL.md` (all caps)—`skill.md` or `Skill.md` are invalid.
2. **The required `name` field in `SKILL.md`**
   - Must be 1-64 characters
   - May only contain unicode lowercase alphanumeric characters (`a-z`) and hyphens (`-`)
   - Must not start or end with a hyphen (`-`)
   - Must not contain consecutive hyphens (`--`)
   - Must match the parent directory name of `SKILL.md`
3. **The required `description` field:**
   - Must be 1-1024 characters
   - Should describe both what the skill does and when to use it
   - Should include specific keywords that help agents identify relevant tasks

**Examples for Reference:**
| Rule Context        | Valid Examples             | Invalid Examples                       |
| :------------------ | :------------------------- | :------------------------------------- |
| Casing & Characters | `pdf-editor`, `calc-min-2` | `calculateMin`, `MySkill`, `calc!min`  |
| Separators & Spaces | `my-skill`, `data-fetch`   | `my skill`, `my_skill`, `data.fetch`   |
| Hyphen Placement    | `fast-search`              | `-search`, `search-`, `fast--search`   |
| Length              | `short-name`               | *(Any string exceeding 64 characters)* |

**Action Protocol for Validation:**

* **If INVALID:** Immediately halt. Politely inform the user exactly which rule(s) their proposed name violated, and ask them to provide a corrected name.
* **If VALID:** Confirm the name is accepted, store it as `<skill-name>`, and proceed to the next step.

### Step 2: Ask for User Confirmation

**Routing Check:**

If you had already asked for the user confirmation, and user typed their proposed skill name, no need to extra confirmation and proceed to the next step.

**Parameter Resolution:**

Prepare the following variables for the following steps:

* `<skill-name>`: The exact, valid skill name confirmed in Step 1
* `<output-directory>`: The default path is project level directory of Agent (E.g. If you're OpenCode, the default path should be `.opencode/skills`) Use the user's provided path if they give one.

You must trigger an interactive terminal menu that allows the user to select an option using their arrow keys and the Enter key. **DO NOT just print plain text or Markdown checkboxes.**

Display this context before the prompt:

> "I'm ready to create the skill. Please review the skill name and paths below:
>
> * Skill Name: <skill_name>
> * Output Path: <output-directory>

Then, present an interactive choice prompt with these exactly options:

1. `Proceed with creation`
2. `Abort creation`
3. `Type your own answer` (**DO NOT duplicate this option**)

Branching Logic:

* If the user selects **Proceed with creation**, proceed to the next step.
* If the user selects **Abort creation**, output *"Creation aborted. Let me know if you need to create another skill!"* and terminate the execution cleanly.
* If the user selects **Type your own answer**, Update the skill name based on their input, and ensure the new name passes the validation rules from Step 1.

### Step 3: Understanding the Skill with Concrete Examples

Skip this step only when the skill's usage patterns are already clearly understood. It remains valuable even when working with an existing skill.

To create an effective skill, clearly understand concrete examples of how the skill will be used. This understanding can come from either direct user examples or generated examples that are validated with user feedback.

For example, when building an image-editor skill, relevant questions include:

- "What functionality should the image-editor skill support? Editing, rotating, anything else?"
- "Can you give some examples of how this skill would be used?"
- "I can imagine users asking for things like 'Remove the red-eye from this image' or 'Rotate this image'. Are there other ways you imagine this skill being used?"
- "What would a user say that should trigger this skill?"

To avoid overwhelming users, avoid asking too many questions in a single message. Start with the most important questions and follow up as needed for better effectiveness.

Conclude this step when there is a clear sense of the functionality the skill should support.

### Step 4: Planning the Reusable Skill Contents

To turn concrete examples into an effective skill, analyze each example by:

1. Considering how to execute on the example from scratch
2. Identifying what scripts, references, and assets would be helpful when executing these workflows repeatedly

Example: When building a `pdf-editor` skill to handle queries like "Help me rotate this PDF," the analysis shows:

1. Rotating a PDF requires re-writing the same code each time
2. A `scripts/rotate_pdf.py` script would be helpful to store in the skill

Example: When designing a `frontend-webapp-builder` skill for queries like "Build me a todo app" or "Build me a dashboard to track my steps," the analysis shows:

1. Writing a frontend webapp requires the same boilerplate HTML/React each time
2. An `assets/hello-world/` template containing the boilerplate HTML/React project files would be helpful to store in the skill

Example: When building a `big-query` skill to handle queries like "How many users have logged in today?" the analysis shows:

1. Querying BigQuery requires re-discovering the table schemas and relationships each time
2. A `references/schema.md` file documenting the table schemas would be helpful to store in the skill

To establish the skill's contents, analyze each concrete example to create a list of the reusable resources to include: `scripts`, `references`, and `assets`.

### Step 5: Initializing the Skill

At this point, it is time to actually create the skill.

**Routing Check:**

* **If EXISTING skill:** Skip this step entirely and proceed to the next step.
* **If NEW skill:** Continue below to initialize the template.

**Action:**

Run the `init_skill.py` script to generate a new template directory. This automatically includes everything a skill requires, making the creation process much more efficient.

Usage:

```bash
python scripts/init_skill.py <skill-name> --path <output-directory>
```

The script:

- Creates the skill directory at the specified path
- Generates a `SKILL.md` template with proper frontmatter and TODO placeholders
- Generates `README.md`, `CHANGELOG.md` and `LICENSE.*` templates
- Creates example tests directories: `evals/` and `tests/`
- Creates example resource directories: `scripts/`, `references/`, and `assets/`
- Adds example files in each directory that can be customized or deleted

After initialization, customize or remove the generated example and tests files as needed.

### Step 6: Edit the Skill

When editing the (newly-generated or existing) skill, remember that the skill is being created for another instance of Agent to use. Include information that would be beneficial and non-obvious to Agent. Consider what procedural knowledge, domain-specific details, or reusable assets would help another Agent instance execute these tasks more effectively.

#### Learn Proven Design Patterns

Consult these helpful guides based on your skill's needs:

- **Multi-step processes**: See `references/workflows.md` for sequential workflows and conditional logic
- **Specific output formats or quality standards**: See `references/output-patterns.md` for template and example patterns

These files contain established best practices for effective skill design.

#### Start with Reusable Skill Contents

To begin implementation, start with the reusable resources identified above: `scripts/`, `references/`, and `assets/` files. Note that this step may require user input. For example, when implementing a `brand-guidelines` skill, the user may need to provide brand assets or templates to store in `assets/`, or documentation to store in `references/`.

Added scripts must be tested by actually running them to ensure there are no bugs and that the output matches what is expected. If there are many similar scripts, only a representative sample needs to be tested to ensure confidence that they all work while balancing time to completion.

Any example files and directories not needed for the skill should be deleted. The initialization script creates example files in `scripts/`, `references/`, and `assets/` to demonstrate structure, but most skills won't need all of them.

#### Update `SKILL.md`

**Writing Guidelines:** Always use imperative/infinitive form.

**Frontmatter**

Write the YAML frontmatter with `name`, `description` and `metadata`:

- `name`: The skill name
- `description`: This is the primary triggering mechanism for your skill, and helps Agent understand when to use the skill.
  - Include both what the Skill does and specific triggers/contexts for when to use it.
  - Include all "when to use" information here - Not in the body. The body is only loaded after triggering, so "When to Use This Skill" sections in the body are not helpful to Agent.
  - Example description for a `docx` skill: "Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. Use when Agent needs to work with professional documents (.docx files) for: (1) Creating new documents, (2) Modifying or editing content, (3) Working with tracked changes, (4) Adding comments, or any other document tasks"
- `metadata`: Arbitrary key-value mapping for additional metadata. Now only add `version: 1.0.0`  as the sub-additional one.

Do not include any other fields in YAML frontmatter.

**Body**

Write instructions for using the skill and its bundled resources.

#### Documentation & License Synchronization

You must now update the following three files in the target skill's directory. Complete these updates sequentially:

1. Synchronize `README.md`

Update `README.md` so that its content fully aligns with and accurately reflects the configurations, descriptions, and capabilities defined in `SKILL.md`.

2. Update `CHANGELOG.md` Date

Update the version release date to the *current* system date. You must use the `YYYY-MM-DD` format (e.g., `2026-03-28`).

3. Resolve Licensing (`LICENSE.txt`)

Evaluate the user's previously stated requirements to determine the correct open-source license for the project.

* **Default Behavior (No explicit request):** If the user did not specify a license, you just keep file and don't need any change.
* **Custom Behavior (Explicit request):** If the user specifically requested a different license (e.g., MIT, GPL-3.0), generate the full, standard text for that specific license and write it into `LICENSE.txt`.

**Action Protocol:**

Do not ask the user for confirmation on these specific file updates unless they explicitly asked you to pause. Execute the file writes/deletions and then notify the user that the documentation and licensing have been successfully synchronized.

#### Tests & Evaluations Synchronization

You must now synchronize the evaluations and testing suite for the target skill. Complete these two tasks sequentially:

1. Synchronize `evals/evals.json`

Review the capabilities and requirements defined in `SKILL.md` and `README.md`. Update `evals/evals.json` so that its test cases and evaluation metrics fully align with the current state of `SKILL.md` and `README.md`.

2. Generate developer tests

First, check the `scripts/` folder for the target skill. 

* **If NO scripts exist in the `scripts/` folder:** Do not generate any tests, and proceed to the next step.
* **If scripts DO exist in the `scripts/` folder:** Generate comprehensive Unit and End-to-End (E2E) tests in the `tests/` folder adhering strictly to the following requirements:
  * **Import Pattern (Zero Collisions):** Reuse the previously generated `tests/conftest.py` to handle imports. Import your script modules cleanly (e.g., `from scripts.module_name import function_name`).
  * **Naming Conventions:** Unit test files MUST be prefixed with `test_` (e.g., `test_data_fetcher.py`).The E2E test file MUST be exactly named `test_e2e.py`.
  * **Pytest Markers:** You MUST add the appropriate decorators to your test classes or methods: Use `@pytest.mark.unit` for all unit tests. Use `@pytest.mark.e2e` for all E2E tests.

### Step 7: Validating a Skill

Once development of the skill is complete, it must be validated with below script:

```bash
python scripts/quick_validate.py <path/to/skill-folder>
```

The validating script will automatically check:

- YAML frontmatter format and required fields
- Skill naming conventions and directory structure
- Description completeness and quality
- File organization and resource references

If validation fails, the script will report the errors and exit, you need to stop skill creation, analyze the errors and inform the user a summary report.

### Step 8: Iterate

After testing the skill, users may request improvements. Often this happens right after using the skill, with fresh context of how the skill performed.

**Iteration workflow:**

1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Identify how `SKILL.md` or bundled resources should be updated
4. Implement changes and test again
