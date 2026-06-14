---
name: cs-create-project
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
     - Contracts in `Common/[DomainSubdomain]/[BoundedContext]/Application/Contracts`
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

### 1. DDD & Encapsulation Rules (from `cs-domain-driven-design.md` & `cs-architecture.md`)
- **Entities/Aggregates**: Use standard C# `class`. Keep constructors `private`. Use `public static Either<Error, T> Create(...)` factory methods. Never expose public setters.
- **Value Objects**: Use immutable `class` or `record`. All internal fields must be `readonly`. Instantiation must go through private constructors and `public static Either<Error, T> Create(...)` factory methods. Protect all invariants.
- **Events & DTOs**: Use C# `record` types to represent immutable data payloads.
- **Repositories**: Define repo interfaces (ports) in the `Domain/Ports` layer. Implement them in the `Infrastructure` layer.
- **Folder Structure**: Organize files using `[BoundedContext]/[Action]/[Layer]` format (e.g., `Users/Register/Domain` or `Users/Register/Application`). This keeps files small and maintainable.

### 2. Modern C# Features & Coding Style (from `cs-coding-style.md`)
- Use **file-scoped namespaces** to reduce nesting.
- Use **primary constructors** for dependency injection in classes/controllers.
- Use **expression-bodied members (`=>`)** for single-expression methods.
- Emphasize class immutability by using `required` and `readonly` fields.
- **Inject via Extensions**: Always create `IServiceCollection` extension methods to encapsulate how settings and dependencies are injected. Keep `Program.cs` clean and free of individual service registrations. The static class containing the extension methods must be named after the bounded context (e.g. `RoomAccessServiceCollectionExtensions` or `RoomAccessServices`), never a generic name like `DependencyInjection` or `DependencyInjectionExtensions`.
- **Avoid Comments**: Keep code free of comments. In unit/integration tests, never write comments (like `// Arrange`, `// Act`, `// Assert`); separate logical phases using empty lines.
- **Application Contracts & Commands**: Ensure a `Contracts/` folder is created on the application layer (`Application/Contracts/`) to contain the use case contracts. Do not group all application interfaces in a single file; each contract must have its own dedicated file inside the `Contracts/` folder. The associated input Command/Request record must be declared in the same file, directly below the contract interface.

### 3. Monadic Control Flow (from `cs-architecture.md` & `cs-coding-style.md`)
- **No Exceptions**: Do not throw or catch exceptions for domain validation or error handling. All failure paths must use `Either` and return `Error`. The **only** exception is inside test projects (specifically within Test Data Builders), which may throw exceptions when unable to construct a valid object.
- **Ports return Either**: All port interfaces must return `Either<Error, T>` or `EitherAsync<Error, T>` to manage error handling.
- **LINQ Queries & Private Helpers**: Use LINQ query syntax (`from ... in ... select ...`) for pipeline execution. Use private helper methods to encapsulate transitions, maps, or branches that do not fit cleanly within LINQ.

### 4. Naming Conventions (from `cs-naming.md` & `cs-architecture.md`)
- Interfaces prefixed with `I` (e.g., `IInvoicePaymentClient`).
- Infrastructure classes prefixed with specific technology/protocol, never generic suffixes like `Impl` (e.g., `PostgresUserRepository` instead of `UserRepositoryImpl`).
- Unit test classes named `[ClassName]Should` (e.g., `UserRegisterShould`).
- **No Acronyms**: Avoid using acronyms in names (e.g., use `UserIdentifier` instead of `UID`, or `Request` instead of `Req`). Spell out concepts fully.
- **Web Controllers**: Must contain only **one** action method. Name the controller file and class following the pattern `<original-name><action>Should.cs` (e.g., `UserRegisterShould.cs` under the directory `Users/V1/`).

### 5. Centralized Error Handling (from `cs-coding-style.md`)
- Use static error holder classes with nested custom exception classes extending `Exception` (e.g., `BillingErrors.ClientValidationException`) to wrap LanguageExt errors.

### 6. Web Controllers & Workers (from `cs-coding-style.md`)
- Web controllers must specify routing, OpenAPI endpoints metadata via attributes (`Produces`, `EndpointSummary`, `EndpointDescription`, `ProducesResponseType`).
- Map pipelines to `IResult` via `.Match(...)` or `.MatchAsync(...)` using `Results.Ok` and `Results.Problem`.

### 7. Unit & Integration Testing (from `cs-testing.md`)
- Create unit tests using **xUnit**, **Shouldly** (fluent assertions), and **NSubstitute** (mocking).
- Assert both success and failure (invalid boundary) states for value objects.
- Create **Test Data Builders** (e.g., `UserBuilder`) to arrange test data cleanly. They are allowed to throw exceptions if build parameters are invalid. Do not include comments in tests.
- **Controllers**: Test API Controllers via **unit tests** using **NSubstitute** to mock use case/application contracts.
- **Infrastructure**: Test infrastructure components via **integration tests** using in-memory databases (for EF Core) or **Testcontainers** for specific external services (e.g. Postgres, RabbitMQ, Redis).
- **Domain**: Test Domain Models (Entities, Aggregates) and Value Objects via **unit tests** to validate business invariants, state transition rules, and factory methods without external mocks.

---

## Phase 3: Post-Execution & Cleanup

1. Run the test suite using `dotnet test` or build using `dotnet build` to verify the new components compile and work correctly.
2. Update the status in the temporary plan file.
3. Upon successful execution and verification, delete the temporary plan file `[project_root]/.agents/temp_create_plan.json` (or `.md`).
4. Report the completed tasks and files created to the user.
