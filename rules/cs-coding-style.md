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
- **Single File per Contract**: Always declare exactly one use case/service interface (contract) per file. Do not bundle multiple unrelated use case interfaces together.
- **Commands in Contract Files**: Define the associated input Command or Request record directly in the same file as the interface contract, positioned immediately below the interface definition.

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
- **Naming Convention**: The controller class and file must be named `<original-name><action>Should.cs` (e.g., `UserRegisterShould.cs`).
- **Attributes**: State versioning, routing, OpenAPI summary, description, and expected response types (`ProducesResponseType`).
- **Functional Mapping**: Map Either outcomes to `IResult` outputs using `.Match` or `.MatchAsync`.

### Example Controller (`UserRegisterShould.cs`)
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
public class UserRegisterShould(
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
```
