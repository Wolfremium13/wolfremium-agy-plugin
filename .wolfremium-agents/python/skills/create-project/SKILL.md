---
name: create-project
description: Create new Python projects, bounded contexts, features, value objects, domain models, ports, use cases, or web routers complying with Clean Architecture, DDD, naming, coding-style, and monadic Result error handling.
---

# Skill: Create Python Project & Components

Use this skill when you need to create a new Python project, package, bounded context, or individual components (like models, value objects, aggregates, ports/interfaces, use cases, FastAPI routers, background workers, unit tests, and builders) conforming to the workspace's Python architecture rules.

## Phase 1: Planning & Information Architecture (IA) Review (Mandatory)

Before writing any code, the agent MUST review the information architecture and usage limits, and write a persistent execution plan.

1. **Information Architecture (IA) Analysis**:
   - Map out the package structure. Find files like `pyproject.toml`, `setup.py`, or `requirements.txt`.
   - Verify where the new components fit within the standard directory layout:
     - Domain models in `src/[domain_subdomain]/[bounded_context]/domain/models`
     - Domain ports in `src/[domain_subdomain]/[bounded_context]/domain/ports`
     - Use cases in `src/[domain_subdomain]/[bounded_context]/application/use_cases`
     - Infrastructure adapters in `src/[domain_subdomain]/[bounded_context]/infrastructure/`
     - Web routers in `src/[web_project]/routers/v[number]/[feature]`
     - Test files in `tests/` matching the main path.
   - Formulate correct absolute imports based on these directories starting with `src`.
   
2. **Usage & AI Limits Review**:
   - Estimate the size and token counts of files to create or modify.
   - Confirm that the proposed work fits comfortably within the current AI context window/token budget.
   - Check connectivity and define fallback/recovery points.

3. **Save the Temporary Plan**:
   - Write the plan to a temporary file: `[project_root]/.agents/temp_create_plan.json` or `[project_root]/.agents/temp_create_plan.md`.
   - The plan must document:
     - Bounded Context and Subdomain details.
     - Files to be created/modified with their exact target paths.
     - Expected import hierarchies and package dependencies.
     - A step-by-step task checklist.
     - Estimated token usage.
     - Status of each task (Pending/In Progress/Completed).
   - If the connection fails or the agent restarts, read this file to resume progress without starting over.

---

## Phase 2: Implementation Guidelines (Based on Rules)

Follow these strict design rules during creation:

### 1. DDD & Encapsulation Rules (from `domain-driven-design.md`)
- **Entities/Aggregates**: Use standard Python classes. Keep internal fields protected by single underscore `_`. Use `@classmethod` `create(...)` factory methods. Never expose public setters or attributes directly.
- **Value Objects**: Use immutable `@dataclass(frozen=True)` or Pydantic models with `frozen=True`. Instantiation must go through classmethod `create(...)` factory methods. Protect all invariants and validate fields.
- **Events & DTOs**: Use `@dataclass(frozen=True)` or Pydantic models to represent immutable data payloads.
- **Repositories**: Define repository interfaces (ports) in the `domain/ports` layer using Python's `abc.ABC`. Implement them in the `infrastructure` layer.

### 2. Python Features & Coding Style (from `coding-style.md`)
- Use standard PEP 8 coding style.
- Use explicit type annotations for all variables, parameters, and return types.
- Use native async/await for all I/O-bound tasks.
- Emphasize class immutability using frozen dataclasses where possible.

### 3. Monadic Control Flow (from `architecture.md` & `coding-style.md`)
- Do not throw exceptions for domain validation or normal workflow flows. Use a monadic `Result[T, Exception]` union with `Success[T]` and `Failure[Exception]`.
- Map operations using pythonic `match case` block check styles.

### 4. Naming Conventions (from `naming.md`)
- Package/module/function/variable names must use `snake_case`.
- Classes must use `PascalCase`.
- Unit test files must start with `test_` and test functions must start with `test_`.
- Do NOT prefix interfaces with `I`. Python relies on abstract base classes.
- Infrastructure classes must be prefixed with specific technology/protocol names, never generic suffixes like `Impl` (e.g. `PostgresDocumentRepository`).
- No generic, catch-all words (no `Manager`, `Helper`, `Processor`, `Engine`, `Utils`). Use precise domain concepts.

### 5. Centralized Error Handling (from `coding-style.md`)
- Define base domain exceptions and subclass specific errors (e.g. `BillingError` -> `ClientValidationError`).

### 6. Web Routers & Workers (from `coding-style.md`)
- API endpoints (FastAPI) must declare path/query parameters with validation, and provide proper OpenAPI attributes (status_code, summary, response_model).
- Map pipeline `Result` values to HTTP outputs using `match case`, throwing `HTTPException` on `Failure`.

### 7. Unit Testing (from `testing.md`)
- Create unit tests using **pytest** and **assertpy** (fluent assertions).
- Assert both success and failure (invalid boundary) states for value objects.
- Create **Test Data Builders** (e.g. `InvoiceIdBuilder`) to arrange test data cleanly.
- Use `unittest.mock` or `mocker` to mock interface dependencies.

---

## Phase 3: Post-Execution & Cleanup

1. Run the test suite using `pytest` or `poetry run pytest` to verify the new components work correctly.
2. Update the status in the temporary plan file.
3. Upon successful execution and verification, delete the temporary plan file `[project_root]/.agents/temp_create_plan.json` (or `.md`).
4. Report the completed tasks and files created to the user.
