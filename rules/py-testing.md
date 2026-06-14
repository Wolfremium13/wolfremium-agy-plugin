# Testing Patterns & Guidelines

This document outlines the testing strategy, tools, and patterns implemented to ensure correctness and stability of the domain models and workflows in Python.

---

## 1. Testing Stack & Libraries

The testing strategy focuses on isolated, fast-running unit tests and integration tests using:
- **pytest**: Test runner and structural framework. Uses fixture functions for dependency injection and setup/teardown.
- **assertpy**: Fluent, human-readable assertions (e.g. `assert_that(val).is_equal_to(expected)`).
- **unittest.mock** (or `pytest-mock` via the `mocker` fixture): For mocking ports, databases, and external HTTP clients.

---

## 2. Value Object Unit Tests

Value object tests must assert both the successful construction boundary and failures for invalid boundaries.

### Example Value Object Test
```python
import pytest
from assertpy import assert_that
from src.billing.invoice_generation.domain.models.invoice_id import InvoiceId
from src.billing.shared.errors import ClientValidationError
from tests.billing.invoice_generation.domain.builders.invoice_id_builder import InvoiceIdBuilder

class TestInvoiceId:
    def test_should_be_created_correctly(self) -> None:
        raw_id = InvoiceIdBuilder().build().value

        # Act
        result = InvoiceId.create(raw_id)

        # Assert
        assert_that(result.is_success()).is_true()
        assert_that(result.value.value).is_equal_to(raw_id)

    @pytest.mark.parametrize("invalid_id", ["", " ", "123"])  # Empty, whitespace, or too short
    def test_should_fail_creation_when_value_is_invalid(self, invalid_id: str) -> None:
        # Act
        result = InvoiceId.create(invalid_id)

        # Assert
        assert_that(result.is_failure()).is_true()
        assert_that(result.error).is_instance_of(ClientValidationError)
```

---

## 3. Test Data Builders

Complex domain structures use the Builder pattern to provide fluid, maintainable arrangements in tests, avoiding duplicate instantiation code.

### Example Builder Pattern
```python
from src.billing.invoice_generation.domain.models.invoice_id import InvoiceId

class InvoiceIdBuilder:
    def __init__(self) -> None:
        self._value: str = "INV-2026-9999"

    def with_value(self, value: str) -> 'InvoiceIdBuilder':
        self._value = value
        return self

    def build(self) -> InvoiceId:
        match InvoiceId.create(self._value):
            case Success(invoice_id):
                return invoice_id
            case Failure(err):
                raise ValueError(f"Failed to build InvoiceId: {str(err)}")
```

---

## 4. Use Case Mocking Unit Tests

Unit tests for application Use Cases set up mock behaviors on ports using `unittest.mock` (or `mocker` fixture) and verify invocation parameters and counts.

### Example Use Case Mocking Test
```python
import pytest
from assertpy import assert_that
from unittest.mock import AsyncMock, MagicMock
from src.billing.invoice_generation.application.use_cases.process_payment import ProcessInvoicePayment
from src.billing.invoice_generation.domain.ports.token_cache import BillingTokenCache
from src.billing.invoice_generation.domain.ports.payment_client import InvoicePaymentClient
from src.billing.invoice_generation.domain.ports.gateway_client import PaymentGatewayClient
from src.billing.shared.errors import ResourceNotFoundError
from src.billing.shared.models import PaymentReceipt
from src.utils.result import Success, Failure

class TestProcessInvoicePayment:
    @pytest.fixture
    def mock_token_cache(self) -> MagicMock:
        cache = MagicMock(spec=BillingTokenCache)
        cache.find_by = AsyncMock()
        cache.save = AsyncMock()
        return cache

    @pytest.fixture
    def mock_payment_client(self) -> MagicMock:
        client = MagicMock(spec=InvoicePaymentClient)
        client.request_token = AsyncMock()
        return client

    @pytest.fixture
    def mock_gateway_client(self) -> MagicMock:
        client = MagicMock(spec=PaymentGatewayClient)
        client.execute_transaction = AsyncMock()
        return client

    @pytest.fixture
    def use_case(
        self,
        mock_token_cache: MagicMock,
        mock_payment_client: MagicMock,
        mock_gateway_client: MagicMock
    ) -> ProcessInvoicePayment:
        return ProcessInvoicePayment(
            token_cache=mock_token_cache,
            payment_client=mock_payment_client,
            gateway_client=mock_gateway_client,
            environment_flow="test-env"
        )

    async def test_should_retrieve_token_from_cache_when_it_exists(
        self,
        use_case: ProcessInvoicePayment,
        mock_token_cache: MagicMock,
        mock_payment_client: MagicMock,
        mock_gateway_client: MagicMock
    ) -> None:
        # Arrange
        cached_token = "TOKEN-123456"
        mock_token_cache.find_by.return_value = Success(cached_token)
        raw_invoice_id = "INV-2026-9999"

        # Act
        result = await use_case.process(raw_invoice_id, 150.00)

        # Assert
        assert_that(result.is_success()).is_true()
        assert_that(result.value.status).contains(cached_token)
        
        # Verify no external API clients were invoked
        mock_payment_client.request_token.assert_not_called()
        mock_gateway_client.execute_transaction.assert_not_called()

    async def test_should_fetch_token_from_api_and_save_when_not_in_cache(
        self,
        use_case: ProcessInvoicePayment,
        mock_token_cache: MagicMock,
        mock_payment_client: MagicMock,
        mock_gateway_client: MagicMock
    ) -> None:
        # Arrange
        new_api_token = "NEW-TOKEN-789"
        mock_token_cache.find_by.return_value = Failure(ResourceNotFoundError("Cache miss"))
        mock_payment_client.request_token.return_value = Success(new_api_token)
        mock_gateway_client.execute_transaction.return_value = Success(
            PaymentReceipt(transaction_id="TX-777", status="Success", processed_at=None)
        )
        mock_token_cache.save.return_value = Success(None)
        raw_invoice_id = "INV-2026-9999"

        # Act
        result = await use_case.process(raw_invoice_id, 250.00)

        # Assert
        assert_that(result.is_success()).is_true()
        assert_that(result.value.transaction_id).is_equal_to("TX-777")
        
        # Verify interactions
        mock_payment_client.request_token.assert_called_once()
        mock_token_cache.save.assert_called_once_with(
            pytest.any(),  # Match any InvoiceId
            new_api_token,
            "test-env"
        )
```

---

## 5. Scenario Tests & Concurrency

Scenario tests (end-to-end flow tests or multi-component integration tests) verify complete business workflows, often interacting with actual databases, caches, or external containers. Because these tests share stateful external resources, running them concurrently can lead to race conditions, database constraints violations, or transient failures.

### 5.1 Separate Files
- Every scenario test must reside in its own dedicated module and file. Never mix scenario tests with unit tests or group multiple unrelated scenario tests within the same file.
- Scenario tests should be placed in a dedicated `scenarios/` folder inside the test directory (e.g., `tests/billing/scenarios/`).

### 5.2 Handling Concurrency (pytest)
To prevent concurrent execution problems (especially when running with parallel test runners like `pytest-xdist`), all scenario tests that share the same database or test container must run sequentially.
- **xdist Grouping**: Decorate scenario test classes or methods with `@pytest.mark.xdist_group(name="scenario_tests")`. This ensures all tests within the group run on a single worker process sequentially.
- **Marker Filter**: Register a custom marker (e.g. `@pytest.mark.scenario`) and if parallel runners cause issues, run them separately without parallelism using the command: `pytest -m scenario -n0`.
- **Database & State Isolation**: Ensure each test run resets state or uses unique identifiers (e.g., random client IDs, unique generated transaction codes) to prevent test-to-test pollution even when executed sequentially.

#### Example Scenario Test
```python
import pytest
from assertpy import assert_that

@pytest.mark.scenario
@pytest.mark.xdist_group(name="scenario_tests")
class TestUserRegistrationScenario:
    async def test_should_register_and_activate_user_successfully(self) -> None:
        # Act and assert the full registration and activation flow
        pass
```
