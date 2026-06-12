---
name: create-project
description: Create new C# projects, bounded contexts, features, value objects, domain models, ports, use cases, or controllers complying with Clean Architecture, DDD, naming, coding-style, and LanguageExt monadic error handling.
---

# Skill: Create C# Project & Components

Use this skill when you need to create a new C# project, solution, bounded context, or individual components (like models, value objects, aggregates, ports, use cases, API controllers, background workers, unit tests, and builders) conforming to the workspace's C# architecture rules.

## Phase 1: Planning & Information Architecture (IA) Review (Mandatory)

Before writing any code, the agent MUST review the information architecture and usage limits, and write a persistent execution plan.

1. **Information Architecture (IA) Analysis**:
   - Map out the solution/project structure. Find the `.sln` and `.csproj` files.
   - Verify where the new components fit within the standard directory layout:
     - Domain models in `Common/[DomainSubdomain]/[BoundedContext]/Domain/Models`
     - Domain ports in `Common/[DomainSubdomain]/[BoundedContext]/Domain/Ports`
     - Use cases in `Common/[DomainSubdomain]/[BoundedContext]/Application/UseCases`
     - Infrastructure adapters in `Common/[DomainSubdomain]/[BoundedContext]/Infrastructure/`
     - Web controllers in `DomainProject.Internal.Web/Controllers/V[Number]/[Feature]`
     - Worker consumers in `DomainProject.Internal.Worker/Consumers/V[Number]`
     - Test files in `Common.Test/` matching the main path.
   - Formulate correct namespaces based on these directories:
     - Main classes: `Common.[DomainSubdomain].[BoundedContext].[Layer].[SubFolder]`
     - Test classes: `Common.Test.[DomainSubdomain].[BoundedContext].[Layer].[SubFolder]`
   
2. **Usage & AI Limits Review**:
   - Estimate the size and token counts of files to create or modify.
   - Confirm that the proposed work fits comfortably within the current AI context window/token budget.
   - Check connectivity and define fallback/recovery points.

3. **Save the Temporary Plan**:
   - Write the plan to a temporary file: `[project_root]/.agents/temp_create_plan.json` or `[project_root]/.agents/temp_create_plan.md`.
   - The plan must document:
     - Bounded Context and Subdomain details.
     - Files to be created/modified with their exact target paths.
     - Expected namespaces and dependencies.
     - A step-by-step task checklist.
     - Estimated token usage.
     - Status of each task (Pending/In Progress/Completed).
   - If the connection fails or the agent restarts, read this file to resume progress without starting over.

---

## Phase 2: Implementation Guidelines (Based on Rules)

Follow these strict design rules during creation:

### 1. DDD & Encapsulation Rules (from `domain-driven-design.md`)
- **Entities/Aggregates**: Use standard C# `class`. Keep constructors `private`. Use `public static Either<Error, T> Create(...)` factory methods. Never expose public setters.
- **Value Objects**: Use immutable `class` or `record`. All internal fields must be `readonly`. Instantiation must go through private constructors and `public static Either<Error, T> Create(...)` factory methods. Protect all invariants.
- **Events & DTOs**: Use C# `record` types to represent immutable data payloads.
- **Repositories**: Define repo interfaces (ports) in the `Domain/Ports` layer. Implement them in the `Infrastructure` layer.

### 2. Modern C# Features & Coding Style (from `coding-style.md`)
- Use **file-scoped namespaces** to reduce nesting.
- Use **primary constructors** for dependency injection in classes/controllers.
- Use **expression-bodied members (`=>`)** for single-expression methods.
- Emphasize class immutability by using `required` and `readonly` fields.

### 3. Monadic Control Flow (from `architecture.md` & `coding-style.md`)
- Do not throw exceptions for domain validation. Use `LanguageExt` monadic control flow.
- Return `Either<Error, T>` or `EitherAsync<Error, T>`.
- Use LINQ query syntax (`from ... in ... select ...`) for pipeline execution.

### 4. Naming Conventions (from `naming.md`)
- Interfaces prefixed with `I` (e.g., `IInvoicePaymentClient`).
- Infrastructure classes prefixed with specific technology/protocol, never generic suffixes like `Impl` (e.g., `PostgresDocumentRepository` instead of `DocumentRepositoryImpl`).
- Unit test classes named `[ClassName]Should` (e.g., `PaymentProcessorShould`).
- No generic, catch-all words (no `Manager`, `Helper`, `Processor`, `Engine`, `Utils`). Use precise domain concepts.

### 5. Centralized Error Handling (from `coding-style.md`)
- Use static error holder classes with nested custom exception classes extending `Exception` (e.g., `BillingErrors.ClientValidationException`).

### 6. Web Controllers & Workers (from `coding-style.md`)
- Web controllers must specify routing, OpenAPI endpoints metadata via attributes (`Produces`, `EndpointSummary`, `EndpointDescription`, `ProducesResponseType`).
- Map pipelines to `IResult` via `.Match(...)` or `.MatchAsync(...)` using `Results.Ok` and `Results.Problem`.

### 7. Unit Testing (from `testing.md`)
- Create unit tests using **xUnit**, **Shouldly** (fluent assertions), and **NSubstitute** (mocking).
- Assert both success and failure (invalid boundary) states for value objects.
- Create **Test Data Builders** (e.g., `InvoiceIdBuilder`) to arrange test data cleanly.

---

## Phase 3: Post-Execution & Cleanup

1. Run the test suite using `dotnet test` or build using `dotnet build` to verify the new components compile and work correctly.
2. Update the status in the temporary plan file.
3. Upon successful execution and verification, delete the temporary plan file `[project_root]/.agents/temp_create_plan.json` (or `.md`).
4. Report the completed tasks and files created to the user.
