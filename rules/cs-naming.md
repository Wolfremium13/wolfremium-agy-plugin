# Naming Conventions Guide

This document defines the naming conventions observed across all projects. Consistent naming ensures readability, reduces cognitive load, and aligns the code with business domains.

---

## 1. Naming Conventions Table

Consistency in naming ensures readability across diverse modules:

| Element | Style | Example | Notes |
| :--- | :--- | :--- | :--- |
| **Interfaces** | PascalCase, prefixed with `I` | `IInvoicePaymentClient` | Represents a port or abstraction. |
| **Classes / Records** | PascalCase | `InvoicePayment` | Implementations, entities, or value objects. |
| **Methods** | PascalCase | `ProcessPayment` | Should start with a verb indicating action. |
| **Method Parameters** | camelCase | `invoiceId`, `givenAmount` | Descriptive parameter names. |
| **Private Fields** | camelCase, prefixed with `_` | `_paymentClient` | For class-level dependencies or state. |
| **Unit Test Classes** | PascalCase, suffixed with `Should` | `PaymentProcessorShould` | Identifies the target class under test. |
| **Test Methods** | PascalCase | `ApproveValidPayment` | States the expected outcome or scenario. |
| **Test Data Builders** | PascalCase, suffixed with `Builder` | `InvoiceBuilder` | Follows the test builder pattern. |

---

## 2. Core Naming Guidelines

### 2.1 Adopt the Ubiquitous Language of the Domain
- Base class, method, and variable names strictly on the vocabulary spoken by domain experts.
- Avoid artificial, technical names like `OrderFactory`, `OrderManager`, or `OrderHelper` unless they have a genuine meaning to the business. The code should act as the single source of truth for the shared mental model of the domain.

### 2.2 Focus on Intent and Purpose
- Name classes and interfaces to explicitly describe their effect, purpose, and role, without referencing *how* they achieve it (their internal implementation).
- Pause and ask yourself, "What is my motivation to create this?" to find a name that perfectly reveals the class's intent.

### 2.3 Ports & Interfaces
- **Domain/Application Interfaces (Ports)**: Prefix interfaces with `I` and name them purely based on business intent and ubiquitous language (e.g., `IDocumentRepository`, `IGovernmentClient`, `IEventPublisher`). They must contain absolutely no technical, framework, or connection details in their names or method signatures.

### 2.4 Infrastructure Implementations (Adapters)
- **Concrete implementations**: Place concrete implementations strictly in the `Infrastructure` folder. 
- **No Generic Suffixes**: Never use generic suffixes like `Impl` (e.g., `DocumentRepositoryImpl` or `KafkaPublisherImpl`). 
- **Prefix with Technology**: Prefix the implementation with the specific technology or protocol being used (e.g., `PostgresDocumentRepository`, `HttpGovernmentClient`, `KafkaEventPublisher`, `RabbitMqEventSubscriber`).

### 2.5 Eliminate Technical Jargon and Type Information
- Do not embed technical patterns, data types, or implementation details in class names.
- Avoid suffixes like `Abstract` or `Base` as they do not add semantic business value. Eliminate extraneous nouns like `Object` (e.g., use `File` instead of `FileObject`). Do not say anything with a name that you can easily say with a type signature.

### 2.6 Be Concrete and Avoid "Catch-All" Words
- Ensure names are precise enough to instantly create a clear mental image of what the underlying entity is and is not.
- Avoid overly generic words that "can mean anything but say nothing," such as `Manager`, `Helper`, `Processor`, `Engine`, `Tool`, or `Utils`.

### 2.7 Distinguish Nouns for Classes and Verbs for Methods
- Typically, use **nouns** to name classes (answering "what is it?") and **verbs** to name methods (answering "what does it do?").
- An exception is when a class represents a single action or operation (such as implementing the Command pattern); in this case, the class name can legitimately be a verb phrase like `PayOrder` or `SendEmail`.

### 2.8 Enforce Strict Consistency and Reject Aliases
- Use the exact same name for a specific concept throughout the entire codebase. Do not use synonyms, aliases, or alternative translations for the same domain concept.

### 2.9 Do Not Use Acronyms
- Avoid using acronyms or abbreviations in naming. Spell out words fully to ensure clarity, reduce ambiguity, and maintain readability across the codebase (e.g., use `UserIdentifier` instead of `UID`, or `Request` instead of `Req`).

### 2.10 Do Not Use "Should" in Production Naming
- Production code names (including files, classes, interfaces, records, methods, parameters, and variables) must not contain the word 'should' (case-insensitive) in their names. The use of 'should' is strictly reserved for test projects and test-related elements (e.g., unit test classes named with `Should` suffix).
