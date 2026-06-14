# Domain-Driven Design (DDD) & Domain Models Guide

This document defines the rules and guidelines for domain logic encapsulation, entity modeling, value objects, events, and transactional boundaries in Python.

---

## 1. Class and Dataclass Organization

To establish clear semantic purpose across types:
- **Domain Models (Entities & Aggregates)**: Always use standard classes (`class`). They represent identity and carry mutable state that is protected by encapsulation.
- **Value Objects**: Always use `@dataclass(frozen=True)` (or Pydantic models with `frozen=True`). They measure, quantify, or describe domain concepts, and have no identity.
- **Domain & Integration Events**: Always use `@dataclass(frozen=True)` to represent immutable historical facts.
- **Data Transfer Objects (DTOs)**: Use `@dataclass(frozen=True)` or Pydantic models.

---

## 2. Domain Encapsulation & Validation

Domain models must protect their invariants and remain isolated from external concerns.

### 2.1 State Encapsulation ("Tell, Don't Ask")
- Never expose class attributes via public properties with public setters. Prefix internal fields with a single underscore `_` (e.g. `self._status`).
- State must be mutated or queried exclusively through domain-language methods representing business actions (e.g. `approve_payment()` instead of `status = "APPROVED"`).
- The Domain layer must be entirely isolated from Application and Infrastructure layers. Use Abstract Base Classes (`abc.ABC`) in the Domain layer to define ports (interfaces) that are implemented in the Infrastructure layer.

### 2.2 Factory Methods & Creation Boundaries
- **No Direct Instantiation**: Prevent direct instantiation of Value Objects or Domain Models.
- **Factory Methods**: Class creation must go through `@classmethod` factory methods (e.g. `create()`).
- **Validation**: Factory methods must validate all business invariants and return a `Result[T, Exception]` union. Never throw exceptions for normal domain validation failures.
- **Immutability**: Internal fields of Value Objects must be immutable. Replace the entire instance when values change.

### 2.3 Value Object Example (`InvoiceId`)
```python
from dataclasses import dataclass
from src.billing.shared.errors import ClientValidationError
from src.utils.result import Result, Success, Failure

@dataclass(frozen=True)
class InvoiceId:
    value: str

    # Private constructor rule: by team convention, do not instantiate directly.
    # Users must always call the create() classmethod.

    @classmethod
    def create(cls, given_invoice_id: str) -> Result['InvoiceId', Exception]:
        if not given_invoice_id or given_invoice_id.isspace():
            return Failure(ClientValidationError("Invoice Identifier cannot be empty or null."))
            
        if len(given_invoice_id) < 5:
            return Failure(ClientValidationError("Invoice Identifier is too short."))
            
        return Success(cls(given_invoice_id))

    def __str__(self) -> str:
        return self.value
```

---

## 3. Aggregates & Eventual Consistency

- **Small Aggregates**: Design small aggregates to protect business invariants. Reference other aggregates by unique identity only (e.g. string or typed identifier like `InvoiceId`), never by direct object references.
- **Eventual Consistency**: Use Domain Events for eventual consistency. When an aggregate undergoes state transition, it should append a Domain Event to an internal list of events. This list is read and published after the transaction commits.
- **Outbox Pattern**: Store integration events in an Outbox table within the same database transaction as the domain state change to ensure reliable event delivery.
- **Transactional Safety**: If any step of an application workflow returns a validation or domain error (a `Failure` in the `Result` monad), the database transaction must be rolled back, ensuring no partial state is persisted.
- **Repositories**: Create repositories only for Aggregate Roots. Provide a collection-like interface that hides underlying database operations.
