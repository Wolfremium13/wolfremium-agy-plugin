# Testing Patterns & Guidelines

This document outlines the testing strategy, tools, and patterns implemented to ensure correctness and stability of the domain models and workflows.

---

## 1. Testing Stack & Libraries

The testing strategy focuses on isolated, fast-running unit tests and integration tests using:
- **xUnit**: Test runner and structural framework.
- **Shouldly**: Human-readable, fluent assertions (e.g., `value.ShouldBe(expected)`).
- **NSubstitute**: Clean, type-safe mocking framework for ports and dependencies.

### Crucial Constraints
- **No Comments in Tests**: Do not write comments in unit tests or integration tests to label sections (such as `// Arrange`, `// Act`, or `// Assert`). Instead, separate these logical phases strictly with empty lines (vertical whitespace).

---

## 2. Value Object Unit Tests

Value object tests must assert both the successful construction boundary and failures for invalid boundaries.

### Example Value Object Test
```csharp
using Xunit;
using Shouldly;
using Common.Billing.InvoiceGeneration.Domain.Models;
using Common.Test.Billing.InvoiceGeneration.Domain.Builders;
using static Common.Billing.Shared.Infrastructure.Errors.BillingErrors;

namespace Common.Test.Billing.InvoiceGeneration.Domain.Models;

public class InvoiceIdShould
{
    [Fact]
    public void BeCreatedCorrectly()
    {
        var rawId = new InvoiceIdBuilder().Build().ToString();

        _ = InvoiceId.Create(rawId).Match(
            success => success.ToString().ShouldBe(rawId),
            error => error.ShouldBeNull()
        );
    }

    [Theory]
    [InlineData("")]
    [InlineData(" ")]
    [InlineData("123")]
    public void FailCreationWhenValueIsInvalid(string invalidId)
    {
        _ = InvoiceId.Create(invalidId).Match(
            success => success.ShouldBeNull(),
            error => error.Exception.Case.ShouldBeOfType<ClientValidationException>()
        );
    }
}
```

---

## 3. Test Data Builders

Complex domain structures use the Builder pattern to provide fluid, maintainable arrangements in tests, avoiding duplicate instantiation code.

### Example Builder Pattern
```csharp
using Common.Billing.InvoiceGeneration.Domain.Models;

namespace Common.Test.Billing.InvoiceGeneration.Domain.Builders;

public class InvoiceIdBuilder
{
    private string _value = "INV-2026-9999";

    public InvoiceId Build()
    {
        return InvoiceId.Create(_value).Match(
            id => id,
            error => throw new InvalidOperationException($"Failed to build InvoiceId: {error.Message}")
        );
    }

    public InvoiceIdBuilder WithValue(string value)
    {
        _value = value;
        return this;
    }
}
```

---

## 4. Use Case Mocking Unit Tests

Unit tests for application Use Cases set up mock behaviors on ports using `NSubstitute` and verify invocation counts.

### Example Use Case Mocking Test
```csharp
using Xunit;
using Shouldly;
using NSubstitute;
using LanguageExt;
using LanguageExt.Common;
using Common.Billing.InvoiceGeneration.Application.UseCases;
using Common.Billing.InvoiceGeneration.Domain.Models;
using Common.Billing.InvoiceGeneration.Domain.Ports;
using Common.Test.Billing.InvoiceGeneration.Domain.Builders;
using static Common.Billing.Shared.Infrastructure.Errors.BillingErrors;

namespace Common.Test.Billing.InvoiceGeneration.Application.UseCases;

public class ProcessInvoicePaymentShould
{
    private readonly IBillingTokenCache _tokenCache = Substitute.For<IBillingTokenCache>();
    private readonly IInvoicePaymentClient _paymentClient = Substitute.For<IInvoicePaymentClient>();
    private readonly IPaymentGatewayClient _gatewayClient = Substitute.For<IPaymentGatewayClient>();
    
    private readonly ProcessInvoicePayment _useCase;
    private readonly string _invoiceId = new InvoiceIdBuilder().Build().ToString();

    public ProcessInvoicePaymentShould()
    {
        _useCase = new ProcessInvoicePayment(_tokenCache, _paymentClient, _gatewayClient, "test-env");
    }

    [Fact]
    public async Task RetrieveTokenFromCacheWhenItExists()
    {
        const string cachedToken = "TOKEN-123456";
        _tokenCache.FindBy(Arg.Any<InvoiceId>(), Arg.Any<string>()).Returns(cachedToken);

        var result = await _useCase.Process(_invoiceId, 150.00m);

        result.Match(
            token =>
            {
                token.ToString().ShouldBe(cachedToken);

                _paymentClient.DidNotReceive().RequestToken(Arg.Any<InvoiceId>());
                _gatewayClient.DidNotReceive().ExecuteTransaction(Arg.Any<string>(), Arg.Any<decimal>());
            },
            error => error.ShouldBeNull()
        );
    }

    [Fact]
    public async Task FetchTokenFromApiAndSaveWhenNotInCache()
    {
        var newApiToken = "NEW-TOKEN-789";
        _tokenCache.FindBy(Arg.Any<InvoiceId>(), Arg.Any<string>())
            .Returns(Error.New(new ResourceNotFoundException("Cache miss")));
        
        _paymentClient.RequestToken(Arg.Any<InvoiceId>()).Returns(newApiToken);
        _gatewayClient.ExecuteTransaction(Arg.Any<string>(), Arg.Any<decimal>()).Returns(new PaymentReceipt("TX-777", "Success", DateTime.UtcNow));
        _tokenCache.Save(Arg.Any<InvoiceId>(), Arg.Any<string>(), Arg.Any<string>()).Returns(Unit.Default);

        var result = await _useCase.Process(_invoiceId, 250.00m);

        result.Match(
            token =>
            {
                token.ToString().ShouldBe(newApiToken);

                _paymentClient.Received(1).RequestToken(Arg.Any<InvoiceId>());
                _tokenCache.Received(1).Save(Arg.Any<InvoiceId>(), newApiToken, "test-env");
            },
            error => error.ShouldBeNull()
        );
    }
}

---

## 5. Testing Strategy by Layer

Testing is structured to balance speed and confidence:

### 5.1 Web API Controllers
- **Unit Tests with Mocks**: API Controllers must be tested using unit tests with mock representations of the external contract / application use cases using **NSubstitute**.
- **Scope**: Focus on validating routing, input parsing, error mapping to HTTP responses, and ensuring the correct application contract is called.

### 5.2 Infrastructure Layer
- **Integration Tests**: Most infrastructure-level components (e.g. database repositories, API clients, cache wrappers) must be tested using integration tests rather than unit tests.
- **Entity Framework**: Use an in-memory database configuration (e.g., EF Core InMemory provider) to test repositories.
- **Specific Infrastructure & Services (Testcontainers)**: For complex external integration pieces (e.g., PostgreSQL specific features, Redis, RabbitMQ, Kafka), use **Testcontainers** to spin up actual containerized environments dynamically for tests.

### 5.3 Domain Layer
- **Unit Tests for Domain Models**: Domain Models (Entities, Aggregates) and Value Objects must be thoroughly tested using unit tests.
- **Scope**: Validate all business invariants, state transition rules, and factory methods (`Create`), ensuring both success paths and error states (represented as Left values in `Either` monads) are fully covered. Do not use mocks or external dependencies when testing the domain layer.

---

## 6. Scenario Tests & Concurrency

Scenario tests (end-to-end flow tests or multi-component integration tests) verify complete business workflows, often interacting with actual databases, caches, or external containers. Because these tests share stateful external resources, running them concurrently can lead to race conditions, database constraints violations, or transient failures.

### 6.1 Separate Files
- Every scenario test must reside in its own dedicated class and file. Never mix scenario tests with unit tests or group multiple unrelated scenario tests within the same file.
- Scenario tests should be placed in a dedicated `Scenarios/` folder inside the test project (e.g., `Common.Test.Billing.Scenarios/`).

### 6.2 Handling Concurrency (xUnit)
To prevent concurrent execution problems, all scenario tests that share the same database or test container must run sequentially.
- **xUnit Test Collections**: Decorate every scenario test class with the `[Collection("ScenarioTests")]` attribute. xUnit executes all test classes belonging to the same collection sequentially rather than in parallel.
- **Database & State Isolation**: Ensure each test run resets state or uses unique identifiers (e.g., random client IDs, unique generated transaction codes) to prevent test-to-test pollution even when executed sequentially.

#### Example Scenario Test
```csharp
using Xunit;
using Shouldly;
using Microsoft.Extensions.DependencyInjection;

namespace Common.Test.Billing.Scenarios;

[Collection("ScenarioTests")]
public class UserRegistrationScenario
{
    [Fact]
    public async Task RegisterAndActivateUserSuccessfully()
    {
        // Act and assert the full registration and activation flow
    }
}
```
