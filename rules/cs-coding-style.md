# C# Coding Style & Guidelines

This document outlines the coding standards, language features, and component design patterns used across the C# projects.

---

## 1. C# Feature Usage (C# 12+)

The project adopts modern C# features to write concise, immutable, and clean code.

1. **File-Scoped Namespaces**: Saves horizontal spacing.
2. **Primary Constructors**: Inject dependencies directly in the class signature to avoid boilerplate field assignment.
3. **Expression-Bodied Members**: Use `=>` for short single-expression methods or pipeline returns.
4. **Required / Readonly Fields**: Emphasize class immutability wherever possible.

---

### 2. Application Use Cases & Pipelines

Application Services coordinate domain interactions using functional query pipelines.

### 2.1 LINQ Queries and Private Helpers
- Keep LINQ query syntax clean and readable. 
- If a complex transformation, type mapping, or error mapping (`Bind`/`Match`) does not fit cleanly inside a LINQ pipeline, extract it to a **private method**. Do not clutter the pipeline with inline complex closures.

### 2.2 Application Contracts & Commands
- **Contracts Folder**: Ensure a `Contracts/` folder is created on the application layer (`Application/Contracts/`) to contain the use case contracts.
- **Single File per Contract**: Always declare exactly one use case/service interface (contract) per file. Each contract must have its own dedicated file inside the `Contracts/` folder. Do not bundle multiple unrelated use case interfaces together.
- **Commands in Contract Files**: Define the associated input Command or Request record directly in the same file as the interface contract, positioned immediately below the interface definition (e.g., place the interface first, and the command below it).

#### Example Contract File (`IRegisterUser.cs`)
```csharp
using LanguageExt;
using LanguageExt.Common;

namespace Common.Billing.Users.Register.Application.Contracts;

public interface IRegisterUser
{
    Task<Either<Error, RegisteredUserInfo>> Register(RegisterUserCommand command);
}

public record RegisterUserCommand(string Username, string Email);

public record RegisteredUserInfo(string UserId, string Username);
```

### Example Use Case Implementation
```csharp
using LanguageExt;
using LanguageExt.Common;
using Common.Billing.Users.Register.Domain.Models;
using Common.Billing.Users.Register.Domain.Ports;
using Common.Billing.Users.Register.Application.Contracts;
using static Common.Billing.Shared.Infrastructure.Errors.BillingErrors;

namespace Common.Billing.Users.Register.Application.UseCases;

public class RegisterUser(
    IUserRepository userRepository,
    IUserEventPublisher eventPublisher
) : IRegisterUser
{
    public async Task<Either<Error, RegisteredUserInfo>> Register(RegisterUserCommand command)
    {
        return await (
            from username in Username.Create(command.Username).ToAsync()
            from email in EmailAddress.Create(command.Email).ToAsync()
            from user in CreateUserEntity(username, email).ToAsync()
            from _ in userRepository.Save(user).ToAsync()
            from __ in eventPublisher.PublishUserRegistered(user).ToAsync()
            select new RegisteredUserInfo(user.Id, user.Username)
        );
    }

    // Private helper methods isolate logic that does not fit cleanly in the main LINQ query
    private Either<Error, User> CreateUserEntity(Username username, EmailAddress email) =>
        User.Create(username, email);
}
```

---

## 3. Centralized Error Handling

Custom errors are modeled using LanguageExt's `Either<Error, T>`.

### Exception and Error Handling Guidelines
- **No Exception Throwing/Catching**: Do not throw or catch exceptions to handle control flow, business validation, or external client failures in production code. Use `Either` and return `Error.New(new Exception(...))` if wrapping an exception.
- **Builder Exception Exception**: Inside the test project, Test Data Builders (e.g., `UserBuilder`) are permitted to throw exceptions (such as `InvalidOperationException`) when a test setup is invalid.
- **Ports return Either**: All interfaces defined as ports must return `Either` or `EitherAsync` to represent operations that can fail, enforcing error management at compile time.

### Example Error Definitions
```csharp
namespace Common.Billing.Shared.Infrastructure.Errors;

public static class BillingErrors
{
    public class ClientValidationException(string message) : Exception(message);
    
    public class GatewayTimeoutException(string message) : Exception(message);
    
    public class RemoteServiceUnavailableException(string message) : Exception(message);
    
    public class ResourceNotFoundException(string message) : Exception(message);
}
```

---

## 4. Web API Controllers

Controllers must follow the Single Responsibility Principle and the REPR (Request-Endpoint-Response) pattern.

- **Single Action Method**: Each controller class must expose exactly **one** public action method.
- **Naming Convention**: The controller class and file must be named `<original-name><action>Controller.cs` (e.g., `UserRegisterController.cs`).
- **Attributes**: State versioning, routing, OpenAPI summary, description, and expected response types (`ProducesResponseType`).
- **Functional Mapping**: Map Either outcomes to `IResult` outputs using `.Match` or `.MatchAsync`.

### Example Controller (`UserRegisterController.cs`)
```csharp
using System.ComponentModel;
using System.Text.Json.Serialization;
using Microsoft.AspNetCore.Mvc;
using Common.Billing.Users.Register.Domain.Models;
using Common.Billing.Users.Register.Application.Contracts;
using static Common.Billing.Shared.Infrastructure.Errors.BillingErrorsWeb;

namespace DomainProject.Internal.Web.Controllers.V1.Users;

[ApiController]
[Route("v1/users")]
[Tags("User Management")]
public class UserRegisterController(
    IRegisterUser registerService
) : ControllerBase
{
    [HttpPost("register")]
    [Produces("application/json")]
    [EndpointSummary("Register a new user")]
    [EndpointDescription("Validates and registers a new user with the specified credentials.")]
    [ProducesResponseType(typeof(RegisterResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<IResult> Register(
        [FromQuery(Name = "username")] string username,
        [FromQuery(Name = "email")] string email
    ) =>
        await (
            from info in registerService.Register(new RegisterUserCommand(username, email)).ToAsync()
            select new RegisterResponse(info.UserId, info.Username)
        ).Match<IResult>(
            success => Results.Ok(success),
            error => Results.Problem(MapToProblemDetails(error, HttpContext))
        );
}

public record RegisterResponse(
    [property: JsonPropertyName("userId")] string UserId,
    [property: JsonPropertyName("username")] string Username
);
```

---

## 5. Event Consumers & Background Workers

Background services process incoming domain event payloads using LanguageExt pipelines.

### Example Background Consumer
```csharp
using Azure.Messaging.ServiceBus;
using LanguageExt;
using LanguageExt.Common;

namespace DomainProject.Internal.Worker.Consumers.V1;

public class ProcessBillingNotificationConsumer(
    ServiceBusClient serviceBusClient,
    ITelemetryClient telemetryClient,
    ServiceBusQueueSettings queueSettings,
    INotificationProcessor notificationProcessor
) : ServiceBusEventConsumer(serviceBusClient, telemetryClient)
{
    protected override string Queue => queueSettings.BillingNotificationsQueue;

    protected override async Task<Either<Error, Unit>> ProcessMessageAsync(
        string jsonDomainEvent,
        CancellationToken cancellationToken,
        string? correlationId = null
    ) =>
        await (
            from eventAttributes in BillingNotificationEventAttributes.FromJson(jsonDomainEvent).ToAsync()
            from result in notificationProcessor.SendEmailNotification(new EmailNotificationInfo(
                eventAttributes.TargetAddress,
                eventAttributes.Subject,
                eventAttributes.Body
            )).ToAsync()
            select Unit.Default
        );
}
```

---

## 6. Dependency Injection & Configuration Setup

To keep `Program.cs` clean, always encapsulate DI registrations inside extension methods.

### Example Extension Method
```csharp
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Configuration;
using Common.Billing.Users.Register.Domain.Ports;
using Common.Billing.Users.Register.Infrastructure;

namespace Common.Billing.Users.Register.Infrastructure.Settings;

public static class RegisterServiceCollectionExtensions
{
    public static IServiceCollection AddUserRegisterServices(
        this IServiceCollection services, 
        IConfiguration configuration
    )
    {
        var settings = configuration.GetSection("UserRegisterSettings").Get<UserRegisterSettings>();
        services.AddSingleton(settings);

        services.AddScoped<IUserRepository, PostgresUserRepository>();

        return services;
    }
}

### Bounded Context DI Registration Example

When registering dependencies (repositories, use cases, etc.) for a bounded context in program files/extension classes, do NOT use generic names like `DependencyInjection` for the static class. The name of the static class must be related to the bounded context (e.g., `RoomAccessServiceCollectionExtensions` or `RoomAccessServices`).

Example:

```csharp
using Microsoft.Extensions.DependencyInjection;

namespace Common.RoomAccess.Infrastructure.Settings;

public static class RoomAccessServiceCollectionExtensions
{
    public static void AddRoomAccessServices(this IServiceCollection services)
    {
        services.AddSingleton<IEstimationRoomRepository, InMemoryEstimationRoomRepository>();
        
        services.AddTransient<ICreateRoomUseCase, CreateRoomUseCase>();
        services.AddTransient<IRequestToJoinUseCase, RequestToJoinUseCase>();
        services.AddTransient<IApproveJoinRequestUseCase, ApproveJoinRequestUseCase>();
        services.AddTransient<IRejectJoinRequestUseCase, RejectJoinRequestUseCase>();
        services.AddTransient<IDisconnectModeratorUseCase, DisconnectModeratorUseCase>();
    }
}
```

---

## 7. Deterministic Non-Deterministic Operations (Time & Random Generations)

Direct dependency on non-deterministic system calls like `DateTime.UtcNow`, `DateTime.Now`, `Guid.NewGuid()`, or `Random` inside domain models, services, or use cases violates testability and predictability. All such generations must be abstractable and mockable.

### 7.1 Abstracting DateTime and Guids
- **Never call directly**: Never use `DateTime.UtcNow`, `DateTime.Now`, `Guid.NewGuid()` directly in production business logic.
- **Use Interfaces**: Wrap these behind dedicated port interfaces in the domain or application layers.
  - For system clock and time: Use `IDateTimeProvider` or `ISystemClock`.
  - For unique identifiers: Use `IGuidProvider` or `IIdGenerator`.
- **Dependency Injection**: Inject these providers into use cases, domain services, or factory methods that require them, allowing unit tests to stub or mock them to return stable, predictable values.

#### Example Interface & Usage
```csharp
namespace Common.Billing.Shared.Domain.Ports;

public interface IDateTimeProvider
{
    DateTime UtcNow { get; }
}

public interface IGuidProvider
{
    Guid NewGuid();
}
```

```csharp
namespace Common.Billing.Users.Register.Application.UseCases;

public class RegisterUser(
    IUserRepository userRepository,
    IGuidProvider guidProvider,
    IDateTimeProvider dateTimeProvider
) : IRegisterUser
{
    public async Task<Either<Error, User>> Execute(string username, string email)
    {
        var userId = guidProvider.NewGuid();
        var createdAt = dateTimeProvider.UtcNow;
        // ...
    }
}
```
```
