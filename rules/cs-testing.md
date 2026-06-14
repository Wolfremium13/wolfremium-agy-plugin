# Testing Patterns & Guidelines

This document outlines the testing strategy, tools, and patterns implemented to ensure correctness and stability of the domain models and workflows.

---

## 1. Testing Stack & Libraries

The testing strategy focuses on isolated, fast-running unit tests and integration tests using:
- **xUnit**: Test runner and structural framework.
- **Shouldly**: Human-readable, fluent assertions (e.g., `value.ShouldBe(expected)`).
- **NSubstitute**: Clean, type-safe mocking framework for ports and dependencies.

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
    [InlineData("123")] // Too short
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
    // Dependencies
    private readonly IBillingTokenCache _tokenCache = Substitute.For<IBillingTokenCache>();
    private readonly IInvoicePaymentClient _paymentClient = Substitute.For<IInvoicePaymentClient>();
    private readonly IPaymentGatewayClient _gatewayClient = Substitute.For<IPaymentGatewayClient>();
    
    // System Under Test (SUT)
    private readonly ProcessInvoicePayment _useCase;
    private readonly string _invoiceId = new InvoiceIdBuilder().Build().ToString();

    public ProcessInvoicePaymentShould()
    {
        _useCase = new ProcessInvoicePayment(_tokenCache, _paymentClient, _gatewayClient, "test-env");
    }

    [Fact]
    public async Task RetrieveTokenFromCacheWhenItExists()
    {
        // Arrange
        var cachedToken = "TOKEN-123456";
        _tokenCache.FindBy(Arg.Any<InvoiceId>(), Arg.Any<string>()).Returns(cachedToken);

        // Act
        var result = await _useCase.Process(_invoiceId, 150.00m);

        // Assert
        result.Match(
            token =>
            {
                token.ToString().ShouldBe(cachedToken);
                // Ensure no external API clients were invoked
                _paymentClient.DidNotReceive().RequestToken(Arg.Any<InvoiceId>());
                _gatewayClient.DidNotReceive().ExecuteTransaction(Arg.Any<string>(), Arg.Any<decimal>());
            },
            error => error.ShouldBeNull()
        );
    }

    [Fact]
    public async Task FetchTokenFromApiAndSaveWhenNotInCache()
    {
        // Arrange
        var newApiToken = "NEW-TOKEN-789";
        _tokenCache.FindBy(Arg.Any<InvoiceId>(), Arg.Any<string>())
            .Returns(Error.New(new ResourceNotFoundException("Cache miss")));
        
        _paymentClient.RequestToken(Arg.Any<InvoiceId>()).Returns(newApiToken);
        _gatewayClient.ExecuteTransaction(Arg.Any<string>(), Arg.Any<decimal>()).Returns(new PaymentReceipt("TX-777", "Success", DateTime.UtcNow));
        _tokenCache.Save(Arg.Any<InvoiceId>(), Arg.Any<string>(), Arg.Any<string>()).Returns(Unit.Default);

        // Act
        var result = await _useCase.Process(_invoiceId, 250.00m);

        // Assert
        result.Match(
            token =>
            {
                token.ToString().ShouldBe(newApiToken);
                // Verify interactions
                _paymentClient.Received(1).RequestToken(Arg.Any<InvoiceId>());
                _tokenCache.Received(1).Save(Arg.Any<InvoiceId>(), newApiToken, "test-env");
            },
            error => error.ShouldBeNull()
        );
    }
}
```
