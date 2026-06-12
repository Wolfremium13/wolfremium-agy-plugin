---
name: py-lint-project
description: Audit the codebase or specific Python files to ensure strict compliance with Clean Architecture, DDD, monadic Result control flow, naming conventions, pytest/assertpy testing patterns, and commenting guidelines.
---

# Skill: Lint Python Project & Audits

Use this skill when you need to run a static check, audit, or linting process on Python files or projects to ensure they fully satisfy the architecture and design rules.

## Phase 1: Planning & Information Architecture (IA) Review (Mandatory)

Before running any audit steps, the agent MUST review the information architecture and usage limits, and write a persistent execution plan.

1. **Information Architecture (IA) Analysis**:
   - Identify the scope of the audit (e.g. specific files, a single bounded context, or the entire codebase).
   - Find all relevant Python files (`*.py`) and locate their directory paths.
   
2. **Usage & AI Limits Review**:
   - Calculate the total token footprint of the target files to be analyzed.
   - For larger projects, partition the files into batches so they can be audited sequentially without exceeding context/token limits.
   - Check connection status and estimate safety margins.

3. **Save the Temporary Plan**:
   - Write the plan to a temporary file: `[project_root]/.agents/temp_lint_plan.json` or `[project_root]/.agents/temp_lint_plan.md`.
   - The plan must document:
     - Target directories or specific file paths.
     - Planned audit steps (e.g. import architecture check, DDD invariants check, naming conventions check, comments check, pytest assertion checks).
     - Token estimate and batched scopes.
     - A status checklist for each file/step.
   - If the connection fails or context resets, read this file to resume the audit from the last checked file/step.

---

## Phase 2: Linting Checklist (Based on Rules)

Inspect each target file against the following specific rules:

### 1. Architectural & Import Alignment (from `architecture.md`)
- **Absolute Imports**: Verify that imports use absolute paths starting with `src`.
- **Dependency Flow**: Check that imports only flow inward:
  - `domain` must NOT import from `application` or `infrastructure`.
  - `application` must NOT import from `infrastructure`.
- **Feature Slicing**: Ensure files are organized in the `[feature_concept]/[feature_action]/[layer]` folder hierarchy.

### 2. Domain-Driven Design Invariants (from `domain-driven-design.md`)
- **Domain Models**: Are entities/aggregates defined as regular classes? Are their constructors protected? Do they use static factory methods (`create`) returning a generic `Result`?
- **Value Objects**: Are they immutable dataclasses (`@dataclass(frozen=True)`) or frozen Pydantic models? Are their fields read-only? Do they use `create` factory methods returning a `Result`?
- **State Encapsulation**: Are there any public class attributes being set directly? Ensure state is mutated or queried exclusively through domain-language methods ("Tell, Don't Ask").
- **Events & DTOs**: Are they defined as frozen dataclasses or frozen Pydantic models?

### 3. Error Handling & Pipelines (from `architecture.md` & `coding-style.md`)
- **Exceptions**: Ensure the code does not raise standard exceptions for domain validation or normal flow control. Validation must return `Result[T, Exception]`.
- **Pipelines**: Ensure query/pipeline operations handle results via pythonic pattern matching (`match case`), avoiding unhandled Exception raising or null/None returns in domain/application layers.

### 4. Naming Conventions (from `naming.md`)
- **Interfaces (Ports)**: Ensure interfaces are defined using `abc.ABC` and are NOT prefixed with `I` (e.g. `InvoicePaymentClient`, not `IInvoicePaymentClient`).
- **Infrastructure Adapters**: Check concrete implementations in the `infrastructure` folder. They must be prefixed with their specific technology/protocol (e.g. `PostgresDocumentRepository`) and MUST NOT use generic suffixes like `Impl` or `Base`.
- **Catch-All Words**: Ensure classes do not contain words like `Manager`, `Helper`, `Processor`, `Engine`, `Tool`, or `Utils`.
- **Consistency**: Verify that the same name is used for a specific concept throughout.

### 5. Commenting Guidelines (from `comments.md`)
- **Redundancy**: Verify that comments do not explain "how" the code works, repeat the code, or could be replaced by better naming or types.
- **Docstrings**: Ensure methods have Google-style docstrings explaining preconditions, side effects, and returns, without repeating parameter type information.
- **Code Clarity**: Check for comments documenting surprises, quirks, boundary conditions, or why alternatives were discarded.

### 6. Testing Patterns (from `testing.md`)
- **Naming**: Ensure test files start with `test_`, test classes start with `Test`, and test methods use snake_case starting with `test_`.
- **Assertions**: Verify that tests use `assertpy` fluent assertions (e.g. `assert_that(val).is_equal_to(expected)`).
- **Mocks**: Verify that mock setups utilize `unittest.mock` or `mocker` from `pytest-mock`.
- **Builders**: Verify that complex test data setup utilizes the Test Data Builder pattern.

---

## Phase 3: Reporting & Cleanup

1. Generate a detailed markdown audit report in the workspace or output. Ensure all findings include clickable file links with line numbers (e.g. `[invoice_id.py:L45](file:///path/to/invoice_id.py#L45)`).
2. Group the findings into:
   - **Errors (Blockers)**: Rule violations that break compile/runtime invariants (e.g. public setters on aggregate fields, direct value object instantiation, standard exceptions instead of Result, importing infrastructure from domain).
   - **Warnings (Warnings)**: Minor style/naming guidelines (e.g. redundant comments, docstring type duplication, missing prefix).
3. Update and delete the temporary plan file `[project_root]/.agents/temp_lint_plan.json` (or `.md`) upon completion.
