# Domain-Driven Design (DDD) & Domain Models Guide

This document defines the rules and guidelines for domain logic encapsulation, entity modeling, value objects, events, and transactional boundaries.

---

## 1. Class and Record Organization

To establish clear semantic purpose across types:
- **Domain Models**: Always use `class` for Entities and Aggregates.
- **Value Objects**: Use immutable `class` or `record` types to measure, quantify, or describe domain concepts.
- **Domain & Integration Events**: Always use `record` types. Since events represent immutable historical facts, `record` types are ideal for their representation.
- **Data Transfer Objects (DTOs)**: Always use `record` types.

---

## 2. Domain Encapsulation & Validation

Domain models must protect their invariants and remain isolated from external concerns.

### 2.1 State Encapsulation ("Tell, Don't Ask")
- Never expose class attributes via public properties with public setters. State must be mutated or queried exclusively through domain-language methods representing business actions.
- The Domain layer must be entirely isolated from Application and Infrastructure layers. Use the **Separated Interface** pattern to define ports (interfaces) in the Domain that are implemented in the Infrastructure.

### 2.2 Private Constructors & Factory Methods
- **Private Constructors**: Prevent raw, unvalidated instantiation of Domain Models and Value Objects. All class constructors must be `private`.
- **Factory Methods**: Instantiation must go through `public static` factory methods (e.g., `Create()`).
- **Validation**: Factory methods must validate all business invariants and return an `Either<Error, T>` monad using `LanguageExt`. Never throw exceptions for normal domain validation failures.
- **Immutability**: Internal fields of Value Objects must be readonly. Replace them entirely when their value changes.

### 2.3 Value Object Example (`InvoiceId`)
```csharp
using LanguageExt;
using LanguageExt.Common;
using static Common.Billing.Shared.Infrastructure.Errors.BillingErrors;

namespace Common.Billing.InvoiceGeneration.Domain.Models;

public class InvoiceId
{
    private readonly string _value;

    // Private constructor guarantees creation only via static validation factory
    private InvoiceId(string value) => _value = value;

    public static Either<Error, InvoiceId> Create(string givenInvoiceId)
    {
        if (string.IsNullOrWhiteSpace(givenInvoiceId))
        {
            return Error.New(new ClientValidationException("Invoice Identifier cannot be empty or null."));
        }

        if (givenInvoiceId.Length < 5)
        {
            return Error.New(new ClientValidationException("Invoice Identifier is too short."));
        }

        return new InvoiceId(givenInvoiceId);
    }

    public override string ToString() => _value;
}
```

---

## 3. Aggregates & Eventual Consistency

- **Small Aggregates**: Design small aggregates to protect business invariants. Reference other aggregates by unique identity only (e.g., `Guid` or typed identifier), never by direct object references.
- **Eventual Consistency**: Use Domain Events for eventual consistency. When an aggregate undergoes state transition, it should raise a Domain Event. This event is handled after the primary transaction commits to update other aggregates or external systems.
- **Outbox Pattern**: When publishing integration events to external systems, store the events in an Outbox table within the same database transaction as the domain changes. A background worker should then read and dispatch the events, ensuring reliable at-least-once delivery.
- **Transactional Safety**: If any step of an application workflow returns a validation or domain error (a Left value in the `Either` monad), the transaction must be aborted/rolled back, ensuring no partial state is committed to the persistence layer.
- **Repositories**: Create repositories only for Aggregate Roots. Provide a collection-like interface that completely hides the underlying database operations.
