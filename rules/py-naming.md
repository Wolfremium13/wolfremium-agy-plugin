# Naming Conventions Guide

This document defines the naming conventions observed across all Python projects. Consistent naming ensures readability, reduces cognitive load, and aligns the code with business domains.

---

## 1. Naming Conventions Table

Consistency in naming ensures readability across diverse modules:

| Element | Style | Example | Notes |
| :--- | :--- | :--- | :--- |
| **Packages / Modules** | snake_case | `invoice_generation` | All python files and folders must use snake_case. |
| **Classes / Dataclasses** | PascalCase | `InvoicePayment` | Implementations, entities, value objects, or DTOs. |
| **Functions / Methods** | snake_case | `process_payment` | Should start with a verb indicating action. |
| **Parameters / Variables** | snake_case | `invoice_id`, `amount` | Descriptive parameter names. |
| **Private Fields / Methods** | snake_case, prefixed with `_` | `_payment_client` | For class-level dependencies or state. |
| **Constants** | UPPER_CASE | `MAX_RETRIES` | Configuration constants or static thresholds. |
| **Unit Test Files** | snake_case, prefixed with `test_` | `test_invoice_id.py` | Required for pytest to discover tests. |
| **Unit Test Classes** | PascalCase, prefixed with `Test` | `TestInvoiceId` | Identifies the target class under test. |
| **Test Methods** | snake_case, prefixed with `test_` | `test_should_be_created_correctly` | States the expected outcome or scenario. |
| **Test Data Builders** | PascalCase, suffixed with `Builder` | `InvoiceBuilder` | Follows the test builder pattern. |

---

## 2. Core Naming Guidelines

### 2.1 Adopt the Ubiquitous Language of the Domain
- Base class, method, and variable names strictly on the vocabulary spoken by domain experts.
- Avoid artificial, technical names like `OrderFactory`, `OrderManager`, or `OrderHelper` unless they have a genuine meaning to the business. The code should act as the single source of truth for the shared mental model of the domain.

### 2.2 Focus on Intent and Purpose
- Name classes and functions to explicitly describe their effect, purpose, and role, without referencing *how* they achieve it (their internal implementation).
- Pause and ask yourself, "What is my motivation to create this?" to find a name that perfectly reveals the class's intent.

### 2.3 Ports & Interfaces
- **Domain/Application Interfaces (Ports)**: Name interfaces based on business intent and ubiquitous language (e.g. `DocumentRepository`, `GovernmentClient`, `EventPublisher`). They must contain absolutely no technical, framework, or connection details in their names or method signatures.
- *Note:* Unlike C#, do NOT prefix interfaces with `I`. Python relies on abstract base classes (ABCs) and structural subtyping (protocols); prefixing with `I` is un-pythonic.

### 2.4 Infrastructure Implementations (Adapters)
- **Concrete implementations**: Place concrete implementations strictly in the `infrastructure` package.
- **No Generic Suffixes**: Never use generic suffixes like `Impl` (e.g. `DocumentRepositoryImpl` or `KafkaPublisherImpl`).
- **Prefix with Technology**: Prefix the implementation with the specific technology or protocol being used (e.g. `PostgresDocumentRepository`, `HttpGovernmentClient`, `KafkaEventPublisher`, `RabbitMqEventSubscriber`).

### 2.5 Eliminate Technical Jargon and Type Information
- Do not embed technical patterns, data types, or implementation details in class names.
- Avoid suffixes like `Abstract` or `Base` as they do not add semantic business value. Eliminate extraneous nouns like `Object` (e.g. use `File` instead of `FileObject`). Do not say anything with a name that you can easily say with a type signature.

### 2.6 Be Concrete and Avoid "Catch-All" Words
- Ensure names are precise enough to instantly create a clear mental image of what the underlying entity is and is not.
- Avoid overly generic words that "can mean anything but say nothing," such as `Manager`, `Helper`, `Processor`, `Engine`, `Tool`, or `Utils`.

### 2.7 Distinguish Nouns for Classes and Verbs for Methods
- Typically, use **nouns** to name classes (answering "what is it?") and **verbs** to name methods (answering "what does it do?").
- An exception is when a class represents a single action or operation (such as implementing the Command pattern); in this case, the class name can legitimately be a verb phrase like `PayOrder` or `SendEmail`.

### 2.8 Enforce Strict Consistency and Reject Aliases
- Use the exact same name for a specific concept throughout the entire codebase. Do not use synonyms, aliases, or alternative translations for the same domain concept.
