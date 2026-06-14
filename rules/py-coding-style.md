# Python Coding Style & Guidelines

This document outlines the coding standards, language features, and component design patterns used across the Python projects.

---

## 1. Python Feature Usage (Python 3.10+)

The project adopts modern Python features to write concise, immutable, and type-safe code:

1. **Type Hinting**: All functions, methods, and class signatures must use complete PEP 484 type annotations.
2. **Dataclasses**: Use `@dataclass(frozen=True)` to define immutable Value Objects, DTOs, and Event payloads.
3. **Structural Pattern Matching**: Use `match case` statements to handle different states of monads or unions (e.g. Success vs Failure).
4. **Union Type Operator (`|`)**: Use `T | None` instead of `Optional[T]` and `A | B` instead of `Union[A, B]`.
5. **Async / Await**: Use native async and await for all I/O-bound operations (network requests, DB queries).

---

## 2. Monadic Result Pattern

Since Python lacks a built-in Result type, we define and use a lightweight generic `Result` container:

```python
from typing import Generic, TypeVar, Union

T = TypeVar('T')  # Represents the success value type
E = TypeVar('E')  # Represents the error value type (usually a subclass of Exception)

class Success(Generic[T]):
    __slots__ = ('value',)
    
    def __init__(self, value: T):
        self.value = value
        
    def is_success(self) -> bool:
        return True
        
    def is_failure(self) -> bool:
        return False

class Failure(Generic[E]):
    __slots__ = ('error',)
    
    def __init__(self, error: E):
        self.error = error
        
    def is_success(self) -> bool:
        return False
        
    def is_failure(self) -> bool:
        return True

Result = Success[T] | Failure[E]
```

---

## 3. Application Use Cases & Pipelines

Application Services coordinate domain interactions using functional query pipelines. Since Python does not have LINQ query syntax, use structural pattern matching or sequential helper bindings (`match case`) to route monadic returns.

### Example Use Case Implementation
```python
from dataclasses import dataclass
from src.billing.invoice_generation.domain.models.invoice_id import InvoiceId
from src.billing.invoice_generation.domain.ports.token_cache import BillingTokenCache
from src.billing.invoice_generation.domain.ports.payment_client import InvoicePaymentClient
from src.billing.invoice_generation.domain.ports.gateway_client import PaymentGatewayClient
from src.billing.shared.errors import ResourceNotFoundError
from src.billing.shared.models import PaymentReceipt
from src.utils.result import Result, Success, Failure

class ProcessInvoicePayment:
    def __init__(
        self,
        token_cache: BillingTokenCache,
        payment_client: InvoicePaymentClient,
        gateway_client: PaymentGatewayClient,
        environment_flow: str
    ):
        self._token_cache = token_cache
        self._payment_client = payment_client
        self._gateway_client = gateway_client
        self._environment_flow = environment_flow

    async def process(self, raw_invoice_id: str, raw_amount: float) -> Result[PaymentReceipt, Exception]:
        # 1. Create and validate the InvoiceId Value Object
        match InvoiceId.create(raw_invoice_id):
            case Failure(err):
                return Failure(err)
            case Success(invoice_id):
                # 2. Check the token cache
                match await self._token_cache.find_by(invoice_id, self._environment_flow):
                    case Success(token):
                        return Success(PaymentReceipt(
                            transaction_id="CACHED",
                            status=f"Using cached token: {token}",
                            processed_at=None
                        ))
                    case Failure(err) if isinstance(err, ResourceNotFoundError):
                        # Cache miss: request token from external service, execute tx, then cache
                        match await self._payment_client.request_token(invoice_id):
                            case Failure(token_err):
                                return Failure(token_err)
                            case Success(new_token):
                                match await self._gateway_client.execute_transaction(new_token, raw_amount):
                                    case Failure(tx_err):
                                        return Failure(tx_err)
                                    case Success(receipt):
                                        await self._token_cache.save(invoice_id, new_token, self._environment_flow)
                                        return Success(receipt)
                    case Failure(err):
                        return Failure(err)
```

---

## 4. Centralized Error Handling

Custom domain and system exceptions are defined centrally using class structures inheriting from a base domain exception.

### Example Error Definitions
```python
class BillingError(Exception):
    """Base class for all billing domain errors."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class ClientValidationError(BillingError):
    """Raised when client inputs or Value Objects violate business rules."""
    pass

class GatewayTimeoutError(BillingError):
    """Raised when the payment gateway times out."""
    pass

class ResourceNotFoundError(BillingError):
    """Raised when a requested resource is missing."""
    pass
```

---

## 5. Web API Routers (e.g. FastAPI)

API Routers map incoming HTTP requests to application use cases, serialize inputs, map functional pipeline outputs, and document responses with OpenAPI metadata.

- **FastAPI Endpoints**: Use standard route decorators with correct descriptions, response schemas, and status codes.
- **Monadic Mapping**: Match the `Result` output, converting success to DTO responses, and failure to `HTTPException` values with appropriate status codes.

### Example Endpoint
```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from datetime import datetime
from src.billing.invoice_generation.application.use_cases.process_payment import ProcessInvoicePayment
from src.billing.shared.errors import ClientValidationError, ResourceNotFoundError

router = APIRouter(prefix="/v1/billing", tags=["Invoice Operations"])

class PaymentResponse(BaseModel):
    transaction_id: str = Field(..., serialization_alias="transactionId")
    status: str = Field(...)
    processed_at: datetime | None = Field(None, serialization_alias="processedAt")

@router.post(
    "/process-payment",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
    summary="Process payment for a specific customer invoice",
    description="Submits an invoice identifier and payment amount to process via the integrated billing engine."
)
async def process_payment(
    invoice_id: str = Query(..., alias="invoiceId", description="Target invoice identifier"),
    amount: float = Query(..., description="Transaction amount"),
    payment_service: ProcessInvoicePayment = Depends(get_payment_service)
):
    match await payment_service.process(invoice_id, amount):
        case Success(receipt):
            return PaymentResponse(
                transaction_id=receipt.transaction_id,
                status=receipt.status,
                processed_at=receipt.processed_at
            )
        case Failure(err):
            # Map exception type to HTTP Status Code
            if isinstance(err, ClientValidationError):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
            elif isinstance(err, ResourceNotFoundError):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
            else:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Gateway integration error: {str(err)}"
                )
```
