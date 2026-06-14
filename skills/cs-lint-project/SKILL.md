---
name: cs-lint-project
description: Audit the codebase or specific C# files to ensure strict compliance with Clean Architecture, DDD, LanguageExt monadic control flow, naming conventions, unit testing patterns, and commenting guidelines.
---

# Skill: Lint C# Project & Audits

Use this skill when you need to run a static check, audit, or linting process on C# files or projects to ensure they fully satisfy the architecture and design rules.

## Phase 1: Planning & Information Architecture (IA) Review (Mandatory)

Before running any audit steps, the agent MUST review the information architecture and usage limits, and write a persistent execution plan.

1. **Information Architecture (IA) Analysis**:
   - Identify the scope of the audit (e.g., specific files, a single bounded context, or the entire codebase).
   - Find all relevant C# files (`*.cs`) and locate their directory paths.
   
2. **Usage & AI Limits Review**:
   - Calculate the total token footprint of the target files to be analyzed.
   - For larger projects, partition the files into batches so they can be audited sequentially without exceeding context/token limits.
   - Check connection status and estimate safety margins.

3. **Save the Temporary Plan**:
   - Write the plan to a temporary file: `[project_root]/.agents/temp_lint_plan.json` or `[project_root]/.agents/temp_lint_plan.md`.
   - The plan must document:
     - Target directories or specific file paths.
     - Planned audit steps (e.g., namespace check, DDD invariants check, naming conventions check, commenting check).
     - Token estimate and batched scopes.
     - A status checklist for each file/step.
   - If the connection fails or context resets, read this file to resume the audit from the last checked file/step.

---

## Phase 2: Linting Checklist (Based on Rules)

Inspect each target file against the following specific rules:

### 1. Architectural & Namespace Alignment (from `cs-architecture.md`)
- **Namespaces**: Verify that namespaces exactly match the folder structure:
  - Expect: `namespace Common.[DomainSubdomain].[BoundedContext].[Action].[Layer].[SubFolder];`
- **File-Scoped Namespaces**: Ensure namespaces use file-scoped syntax (e.g., `namespace X;` with no curly braces) as per `cs-coding-style.md`.
- **Folder Structure**: Ensure files are organized in the `[BoundedContext]/[Action]/[Layer]` folder hierarchy (e.g., `Users/Register/Domain` or `Users/Register/Application`), with `Application/Contracts` containing contracts and `Application/UseCases` containing the implementations.
- **Dependency Injection**: Ensure dependency and settings registration is encapsulated inside extension methods, keeping `Program.cs` clean and high-level. The name of the static registration class must be related to the bounded context (e.g., `RoomAccessServiceCollectionExtensions` or `RoomAccessServices`), never a generic name like `DependencyInjection`.
- **Application Contracts & Commands**: Verify that a `Contracts/` folder is created on the application layer (`Application/Contracts/`). Verify that application interfaces are not grouped into a single file and that any associated Command/Request record is defined inside the same file in the `Contracts/` folder, directly below the contract interface definition.

### 2. Domain-Driven Design Invariants (from `cs-domain-driven-design.md`)
- **Domain Models**: Are entities/aggregates defined as `class`? Are their constructors `private`? Do they use static factory methods (`Create`) returning `Either<Error, T>`?
- **Value Objects**: Are they immutable `class` or `record` types with `readonly` fields? Are their constructors `private` with static `Create` factory methods returning `Either<Error, T>`?
- **State Encapsulation**: Are there any public properties with public setters? Ensure state is mutated or queried exclusively through domain-language methods ("Tell, Don't Ask").
- **Events & DTOs**: Are they defined as `record` types?

### 3. Error Handling & Pipelines (from `cs-architecture.md` & `cs-coding-style.md`)
- **Exceptions**: Ensure the code does not throw or catch exceptions for domain validation or error handling. Validation must return `Either<Error, T>` or `EitherAsync<Error, T>`. The only exception allowed is inside Test Data Builders (e.g., throwing when test configuration is invalid).
- **Monadic Bindings**: Ensure query/pipeline operations use LINQ query syntax or monadic methods (`Match`/`MatchAsync`), avoiding raw try-catch blocks or null-returns in application/domain layers.
- **Ports & Interfaces**: Ensure all port interface methods that can fail return `Either` or `EitherAsync` to manage errors functionally.
- **Private Helper Methods**: Ensure complex transformations, mappings, or branches that do not fit cleanly in the main LINQ pipeline are extracted to private helper methods.

### 4. Naming Conventions (from `cs-naming.md` & `cs-architecture.md`)
- **Interfaces**: Check if interfaces are prefixed with `I` (e.g., `IInvoicePaymentClient`) and represent a business abstraction.
- **Infrastructure Adapters**: Check concrete implementations in the `Infrastructure` folder. They must be prefixed with their specific technology/protocol (e.g., `PostgresUserRepository`) and MUST NOT use generic suffixes like `Impl` or `Base`.
- **Catch-All Words**: Ensure classes do not contain words like `Manager`, `Helper`, `Processor`, `Engine`, `Tool`, or `Utils`.
- **No Acronyms**: Ensure that names do not contain acronyms or abbreviations (e.g., use `UserIdentifier` instead of `UID`, or `Request` instead of `Req`). Spell out concepts fully.
- **Web Controllers**: Ensure each controller class exposes exactly **one** public action method. Check if the controller class/file is named `<original-name><action>Should.cs` (e.g., `UserRegisterShould.cs`).

### 5. Commenting Guidelines (from `cs-comments.md`)
- **Redundancy (Phase 1)**: Verify that comments do not explain "how" the code works, repeat the code, or could be replaced by better naming or types. Comments must be avoided as much as possible.
- **Interface Comments (Phase 2)**: Ensure interface methods have high-level comments explaining preconditions, side effects, exceptions, and return values without detailing implementation.
- **Code Clarity**: Check for comments documenting surprises, quirks, units of measurements, boundary conditions, or why alternatives were discarded.

### 6. Testing Patterns (from `cs-testing.md` & `cs-comments.md`)
- **Naming**: Ensure test classes are named `[ClassName]Should` and test methods use PascalCase describing the expected behavior.
- **Mocks & Assertions**: Verify that tests use `xUnit`, `Shouldly` assertions (e.g., `ShouldBe`), and `NSubstitute` mocks.
- **Builders**: Verify that complex test data setup utilizes the Test Data Builder pattern.
- **No Comments in Tests**: Ensure unit and integration tests do not contain block comments (such as `// Arrange`, `// Act`, `// Assert`). Test phases must be separated strictly by vertical whitespace (empty lines).
- **Testing Strategy**: Verify API controllers are unit-tested using mocks for application contracts, infrastructure components use integration tests (EF Core in-memory or Testcontainers), and Domain Models/Value Objects are unit-tested for invariants and factory methods.

---

## Phase 3: Reporting & Cleanup

1. Generate a detailed markdown audit report in the workspace or output. Ensure all findings include clickable file links with line numbers (e.g. `[InvoiceId.cs:L45](file:///path/to/InvoiceId.cs#L45)`).
2. Group the findings into:
   - **Errors (Blockers)**: Rule violations that break compile/runtime invariants (e.g., public setters in domain models, standard exceptions instead of Either, namespace mismatches).
   - **Warnings (Warnings)**: Minor style/naming guidelines (e.g., redundant comments, missing file-scoped namespace).
3. Update and delete the temporary plan file `[project_root]/.agents/temp_lint_plan.json` (or `.md`) upon completion.
