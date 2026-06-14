---
name: cs-normalize-project
description: Automatically refactor, format, and normalize C# files or projects to conform with Clean Architecture, DDD, LanguageExt monadic pipelines, naming rules, test structures, and comment guidelines.
---

# Skill: Normalize C# Project & Refactor

Use this skill when you need to automatically clean up, refactor, and format a C# project or specific C# files to align them with the standard architecture, DDD, naming, comments, and testing rules.

## Phase 1: Planning & Information Architecture (IA) Review (Mandatory)

Before performing any code modifications, the agent MUST review the information architecture and usage limits, and write a persistent execution plan.

1. **Information Architecture (IA) Analysis**:
   - Identify the target files and directories to normalize.
   - Inspect their references and dependent project structures.
   - Identify specific deviations from the standard architecture rules (e.g., standard try-catch blocks to convert, namespaces to align, properties to encapsulate, etc.).

2. **Usage & AI Limits Review**:
   - Estimate the token footprint of each file that needs modification.
   - Ensure the required edits can be applied without exceeding context window or API limits.
   - Since code modification requires high precision, plan to process files individually or in small batches.

3. **Save the Temporary Plan**:
   - Write the plan to a temporary file: `[project_root]/.agents/temp_normalize_plan.json` or `[project_root]/.agents/temp_normalize_plan.md`.
   - The plan must document:
     - Target files to refactor.
     - Planned modifications per file (e.g., "convert namespaces", "replace try-catch with Either", "make constructors private").
     - A step-by-step checklist.
     - Current token estimate.
     - Status of each refactoring task.
   - If the connection fails or the context resets, read this file to resume the refactoring process exactly where it stopped.

---

## Phase 2: Normalization Guidelines (Based on Rules)

Execute the refactoring steps precisely based on the workspace rules:

### 1. Namespace & File-Scoped Namespace Conversion (from `cs-architecture.md` & `cs-coding-style.md`)
- Replace block-scoped namespaces (with curly braces) with file-scoped namespaces (e.g., `namespace Common.Domain;`).
- Adjust the namespace value to match the exact directory path using action-based vertical feature slicing:
  `namespace Common.[DomainSubdomain].[BoundedContext].[Action].[Layer].[SubFolder];`
- Move files to conform to the `[BoundedContext]/[Action]/[Layer]` folder hierarchy (e.g., `Users/Register/Domain` or `Users/Register/Application`), ensuring `Application/Contracts` holds use case contracts.
- Encapsulate all settings and dependency injections into `IServiceCollection` extension methods, cleaning up `Program.cs`. Ensure that the static class containing extension methods is named after the bounded context (e.g., `RoomAccessServiceCollectionExtensions` or `RoomAccessServices`), never a generic name like `DependencyInjection`.
- **Application Contracts & Commands**: Split grouped application interface declarations into separate dedicated files under the `Contracts/` folder, and ensure the corresponding Command/Request record is defined in the same file directly below the interface.

### 2. DDD Model Normalization (from `cs-domain-driven-design.md`)
- Change Domain Entities and Aggregates from `struct` or `record` to `class` where appropriate.
- Mark all constructors of domain models and value objects as `private`.
- Introduce a static factory method `public static Either<Error, T> Create(...)` for instantiation.
- Implement invariant validation inside the factory method, returning `Error` as the Left side if validation fails.
- Convert mutable public properties to `readonly` and remove public setters. Implement modification methods in the domain language ("Tell, Don't Ask").
- Convert DTOs and events to `record` types.

### 3. Error Handling & Functional Pipeline Normalization (from `cs-architecture.md` & `cs-coding-style.md`)
- Replace standard exceptions (like `throw new ArgumentException(...)`) in Use Cases, Domain Models, or API Controllers with LanguageExt monadic returns. Standard exception handling is only allowed in test builders.
- Ensure all Port interfaces manage and return `Either` or `EitherAsync` for error handling.
- Extract complex transitions, mappings, or logic from LINQ queries into private helper methods.
- Rewrite procedural methods to use functional pipelines:
  - Use LINQ query syntax (`from ... in ... select ...`) to chain operations returning `Either` or `EitherAsync`.
  - Use `.Match(...)` or `.MatchAsync(...)` to handle outcomes at boundaries (e.g., in controllers).
- Convert API endpoint methods to return `IResult` mapping monadic results to `Results.Ok(success)` or `Results.Problem(MapToProblemDetails(error))`.
- **Time & UUID/Guid Generation**: Refactor direct references to `DateTime.UtcNow`, `DateTime.Now`, or `Guid.NewGuid()` in production code by introducing and injecting mockable provider interfaces (e.g., `IDateTimeProvider`, `IGuidProvider`).

### 4. Naming Normalization (from `cs-naming.md` & `cs-architecture.md`)
- Add `I` prefix to all interface names.
- Remove generic prefixes/suffixes like `Impl` or `Base` from infrastructure classes. Prefix them with specific tech names (e.g., rename `UserRepositoryImpl` to `PostgresUserRepository`).
- Rename any classes using catch-all words (like `Manager`, `Helper`, `Processor`, `Engine`, `Utils`) to names representing concrete business intents.
- **No Acronyms**: Replace acronyms and abbreviations with fully spelled-out names (e.g., rename `UID` to `UserIdentifier`, `Req` to `Request`).
- **Web Controllers**: Ensure each controller class exposes exactly **one** action method. Rename the controller file and class to `<original-name><action>Controller.cs` (e.g., `UserRegisterController.cs`).

### 5. Comment Cleanup (from `cs-comments.md`)
- Avoid comments as much as possible. Delete comments that explain "how" the code works or repeat what the code says.
- If a comment explains what a block of code does, extract that block into a well-named helper function and delete the comment.
- Retain or write clear interface comments describing preconditions, exceptions, side-effects, and returns.

### 6. Test & Test Data Builder Normalization (from `cs-testing.md` & `cs-comments.md`)
- Rename test classes to `[ClassName]Should` and target test methods to PascalCase.
- Convert test assertions to Shouldly fluent syntax (`value.ShouldBe(...)`).
- Implement NSubstitute for mocks (`Substitute.For<T>()`, `Received()`, `DidNotReceive()`).
- Refactor complex test setups into Test Data Builders (which may throw exceptions if configured invalidly).
- **Remove Comments in Tests**: Delete all comments (such as `// Arrange`, `// Act`, `// Assert`, and descriptions) from unit/integration tests, using empty lines instead.
- **Testing Strategy**: Align test scopes (unit test controllers with NSubstitute mocks; integration test infrastructure using EF in-memory or Testcontainers; unit test domain models/value objects for business invariants).
- **Scenario Tests**: Move scenario/E2E tests into separate files under a `Scenarios/` folder, and ensure their classes are decorated with the `[Collection("ScenarioTests")]` attribute to handle potential database/port concurrency issues.

---

## Phase 3: Verification & Cleanup

1. Run `dotnet build` to verify there are no compilation errors after refactoring.
2. Run `dotnet test` to ensure all tests pass.
3. Update the temporary plan file status after each file is refactored and verified.
4. Once the entire normalization scope is finished and verified, delete the temporary plan file `[project_root]/.agents/temp_normalize_plan.json` (or `.md`).
5. Summarize all refactored files and changes to the user.
