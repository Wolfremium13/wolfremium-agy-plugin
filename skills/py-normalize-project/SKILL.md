---
name: py-normalize-project
description: Automatically refactor, format, and normalize Python files or projects to conform with Clean Architecture, DDD, monadic Result pipelines, naming rules, test structures, and comment guidelines.
---

# Skill: Normalize Python Project & Refactor

Use this skill when you need to automatically clean up, refactor, and format a Python project or specific Python files to align them with the standard architecture, DDD, naming, comments, and testing rules.

## Phase 1: Planning & Information Architecture (IA) Review (Mandatory)

Before performing any code modifications, the agent MUST review the information architecture and usage limits, and write a persistent execution plan.

1. **Information Architecture (IA) Analysis**:
   - Identify the target files and directories to normalize.
   - Inspect their imports and dependent module structures.
   - Identify specific deviations from the standard architecture rules (e.g. standard exception throws to convert, relative imports to fix, properties to encapsulate, etc.).

2. **Usage & AI Limits Review**:
   - Estimate the token footprint of each file that needs modification.
   - Ensure the required edits can be applied without exceeding context window or API limits.
   - Since code modification requires high precision, plan to process files individually or in small batches.

3. **Save the Temporary Plan**:
   - Write the plan to a temporary file: `[project_root]/.agents/temp_normalize_plan.json` or `[project_root]/.agents/temp_normalize_plan.md`.
   - The plan must document:
     - Target files to refactor.
     - Planned modifications per file (e.g. "convert relative imports", "replace exceptions with Result", "make attributes protected").
     - A step-by-step checklist.
     - Current token estimate.
     - Status of each refactoring task.
   - If the connection fails or the context resets, read this file to resume the refactoring process exactly where it stopped.

---

## Phase 2: Normalization Guidelines (Based on Rules)

Execute the refactoring steps precisely based on the workspace rules:

### 1. Import & Feature Slicing Normalization (from `py-architecture.md`)
- Convert relative imports (e.g. `from ..models import X`) to absolute imports starting with `src`.
- Ensure imports flow strictly inward (no infrastructure imports in domain/application layers).
- Move misplaced files to conform with the vertical slice hierarchy `[feature_concept]/[feature_action]/[layer]`.

### 2. DDD Model Normalization (from `py-domain-driven-design.md`)
- Convert domain models to regular classes, and value objects/DTOs to `@dataclass(frozen=True)` or frozen Pydantic models.
- Set class constructor calls to be protected by team conventions, routing instantiation exclusively through a `@classmethod` factory method `create(...)`.
- Implement validation inside the factory method, returning `Failure` wrapping a domain exception if invariants are violated.
- Convert mutable public attributes to protected fields (prefixed with `_`) and remove public setters. Implement modification methods in the domain language ("Tell, Don't Ask").
- Convert DTOs and events to frozen dataclasses.

### 3. Error Handling & Functional Pipeline Normalization (from `py-architecture.md` & `py-coding-style.md`)
- Replace standard exceptions (like `raise ValueError(...)`) in Use Cases, Domain Models, or API Routers with monadic `Result` returns.
- Rewrite procedural methods to use Python pattern matching (`match case`) to branch on success or failure results.
- Convert FastAPI endpoint methods to return DTO schemas mapping results, raising `HTTPException` on monadic `Failure`.

### 4. Naming Normalization (from `py-naming.md`)
- Remove the `I` prefix from all interface/port classes, using abstract base classes (`abc.ABC`).
- Remove generic prefixes/suffixes like `Impl` or `Base` from infrastructure classes. Prefix them with specific tech names (e.g. rename `DocumentRepositoryImpl` to `PostgresDocumentRepository`).
- Rename any classes using catch-all words (like `Manager`, `Helper`, `Processor`, `Engine`, `Utils`) to names representing concrete business intents.

### 5. Comment Cleanup (from `py-comments.md`)
- Delete comments that explain "how" the code works or repeat what the code says.
- If a comment explains what a block of code does, extract that block into a well-named helper function and delete the comment.
- Format all docstrings to Google Python Style Guide standards, ensuring no duplicate type information is documented.

### 6. Test & Test Data Builder Normalization (from `py-testing.md`)
- Rename test files to `test_[module].py`, test classes to `Test[ClassName]`, and test methods to snake_case.
- Convert test assertions to `assertpy` fluent syntax (`assert_that(val).is_equal_to(...)`).
- Implement `unittest.mock` or `mocker` for mocks and stub behaviors.
- Refactor complex test setups into Test Data Builders.

---

## Phase 3: Verification & Cleanup

1. Run the test suite (`pytest` or `poetry run pytest`) to verify there are no errors after refactoring.
2. Update the temporary plan file status after each file is refactored and verified.
3. Once the entire normalization scope is finished and verified, delete the temporary plan file `[project_root]/.agents/temp_normalize_plan.json` (or `.md`).
4. Summarize all refactored files and changes to the user.
