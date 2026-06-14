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

## 2. Application Use Cases & Pipelines

Application Services coordinate domain interactions using functional query pipelines.

### Example Use Case Implementation
```csharp
using LanguageExt;
using LanguageExt.Common;
using Common.Billing.InvoiceGeneration.Domain.Models;
using Common.Billing.InvoiceGeneration.Domain.Ports;
using Common.Billing.InvoiceGeneration.Application.Contracts;
using static Common.Billing.Shared.Infrastructure.Errors.BillingErrors;

namespace Common.Billing.InvoiceGeneration.Application.UseCases;

public class ProcessInvoicePayment(
    IBillingTokenCache tokenCache,
    IInvoicePaymentClient paymentClient,
    IPaymentGatewayClient gatewayClient,
    string environmentFlow
) : IProcessInvoicePayment
{
    public async Task<Either<Error, PaymentReceipt>> Process(string rawInvoiceId, decimal rawAmount)
    {
        // Execute a functional query pipeline
        return await (
            from invoiceId in InvoiceId.Create(rawInvoiceId)
            from token in tokenCache.FindBy(invoiceId, environmentFlow)
            select (invoiceId, token)
        ).MatchAsync(
            Right: context => context.token,
            LeftAsync: async _ => await (
                from invoiceId in InvoiceId.Create(rawInvoiceId).ToAsync()
                from paymentToken in paymentClient.RequestToken(invoiceId).ToAsync()
                from receipt in gatewayClient.ExecuteTransaction(paymentToken, rawAmount).ToAsync()
                from __ in tokenCache.Save(invoiceId, paymentToken, environmentFlow).ToAsync()
                select paymentToken
            )
        );
    }
}
```

---

## 3. Centralized Error Handling

Custom domain and system exceptions are defined centrally using static error holder classes and C# 12 primary constructor exception inheritances.

### Example Error Definitions
```csharp
namespace Common.Billing.Shared.Infrastructure.Errors;

public static class BillingErrors
{
    // Custom exceptions grouped under static classes
    public class ClientValidationException(string message) : Exception(message);
    
    public class GatewayTimeoutException(string message) : Exception(message);
    
    public class RemoteServiceUnavailableException(string message) : Exception(message);
    
    public class ResourceNotFoundException(string message) : Exception(message);
}
```

---

## 4. Web API Controllers

Controllers follow RESTful principles, provide comprehensive OpenAPI metadata, and map functional pipeline results to standard HTTP responses.

- **Attributes**: Every endpoint must state its routing, summary, description, and expected response types (`ProducesResponseType`).
- **Functional Mapping**: Action bodies use monadic bindings (`Match`/`MatchAsync`), returning standard ASP.NET Core `IResult` outputs (`Results.Ok`, `Results.Problem`).
- **Response DTOs**: Implemented cleanly as record types below the controller class.

### Example Controller
```csharp
using System.ComponentModel;
using System.Text.Json.Serialization;
using Microsoft.AspNetCore.Mvc;
using Common.Billing.InvoiceGeneration.Domain.Models;
using Common.Billing.InvoiceGeneration.Application.Contracts;
using static Common.Billing.Shared.Infrastructure.Errors.BillingErrorsWeb;

namespace DomainProject.Internal.Web.Controllers.V1.Billing;

[ApiController]
[Route("v1/billing")]
[Tags("Invoice Operations")]
public class InvoiceBillingController(
    IProcessInvoicePayment paymentService
) : ControllerBase
{
    [HttpPost("process-payment")]
    [Produces("application/json")]
    [EndpointSummary("Process payment for a specific customer invoice")]
    [EndpointDescription(
        """
        Submits an invoice identifier and payment amount to process via the integrated billing engine.

        **Status Codes:**
        - **200 OK**: Payment was processed successfully.
        - **400 Bad Request**: Invalid inputs.
        - **404 Not Found**: Invoice not found.
        - **502 Bad Gateway**: Payment gateway unavailable.
        """
    )]
    [ProducesResponseType(typeof(PaymentResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public async Task<IResult> ProcessPayment(
        [FromQuery(Name = "invoiceId"), Description("Target invoice identifier")] string invoiceId,
        [FromQuery(Name = "amount"), Description("Transaction amount")] decimal amount
    ) =>
        await (
            from receipt in paymentService.Process(invoiceId, amount).ToAsync()
            select new PaymentResponse(
                receipt.TransactionId,
                receipt.Status,
                receipt.ProcessedAt
            )
        ).Match<IResult>(
            success => Results.Ok(success),
            error => Results.Problem(MapToProblemDetails(error, HttpContext))
        );
}

public record PaymentResponse(
    [property: JsonPropertyName("transactionId")] string TransactionId,
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("processedAt")] DateTime ProcessedAt
);
```

---

## 5. Event Consumers & Background Workers

Background services (like Azure Service Bus consumers) extend base workers and process incoming domain event payloads using LanguageExt pipelines.

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
