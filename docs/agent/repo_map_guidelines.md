## 1. Core Objective

Maintain root `REPO_MAP.md` as the architectural source of truth. This prevents context-window navigation errors, "file blindness," and broken import paths for future agent tasks.

## 2. Update Triggers

Update the map **exactly once at the end of the task** (right before handoff) **only if** you:

* Created, deleted, renamed, or moved files/directories.
* Altered structural boundaries or critical system-wide dependencies.

## 3. Universal Schema & Formatting

Use standard ASCII tree characters (`├──`, `│  `, `└──`). Follow this exact metadata structure:

### Node Syntax

* `name.ext (Language/Type)` — e.g., `main.py (Python)`, `schema.sql (SQL)`, `Dockerfile (None)`

### Required Nested Fields (For new or modified files)

* **`Description`**: One-line explanation of the file's primary purpose.
* **`Maintenance Flag`**: Exact match: `Stable` | `Volatile` | `Generated` | `Legacy`.
* **`Architectural Role`**: Exact match: `Entrypoint` | `Configuration` | `API Route / Controller` | `Service / Business Logic` | `Data Model / Schema` | `Persistence / Database` | `UI Component` | `Utility` | `Test` | `Other`.
* **`Critical Dependencies`**: Sub-list mapping key imports to their role:
```markdown
├── Critical Dependencies:
├──   - package.or.module.name: Brief explanation of why it is critical.

```


### Conditional Fields (Add only if highly relevant)

* **`Developer Consideration`**: Implementation edge cases, async warnings, or state traps.
* **`Security Assessment`**: Vulnerability vectors, credential rules, or sensitive data tracking.
* **`Refactoring Suggestions`**: Technical debt or separation of concerns notes.

## 4. Execution Flow (Direct Editing Only)

* **DO NOT** execute terminal discovery commands, directory scanners, or generation scripts.
* **DO** use file-writing tools to modify `REPO_MAP.md` directly, relying entirely on your self-contained knowledge of the files you changed.
* **DO** replicate the document's exact indentation, spacing, and tree structure.

```

```