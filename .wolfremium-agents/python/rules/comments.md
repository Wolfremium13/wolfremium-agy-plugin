# Commenting & Documentation Guidelines

This document outlines standard policies for comments and docstrings in Python code.

---

## 1. Docstring Rules (PEP 257)

- **Class & Function Docstrings**: Every public module, class, method, and function should have a docstring outlining its intent.
- **Google Docstring Style**: Use the Google Style Python Docstrings convention.
- **No Redundant Type Info**: Do NOT document type information inside docstrings if it is already declared in the function signatures (e.g. avoid `:type parameter: str` or `Args: parameter (str): ...`). Let type hints be the single source of truth for types.

### Example Docstring
```python
class PaymentGatewayClient(abc.ABC):
    """Abstract interface representing a port to communicate with the payment gateway client."""

    @abc.abstractmethod
    async def execute_transaction(self, payment_token: str, amount: float) -> Result[PaymentReceipt, Exception]:
        """Submits a tokenized payment request to the external processor.

        Preconditions:
            - payment_token must be a valid, unexpired session token.
            - amount must be greater than zero.

        Returns:
            Success wrapping the transaction receipt if successfully captured.
            Failure wrapping GatewayTimeoutError or ConnectionError if communication fails.
        """
        pass
```

---

## 2. In-Code Comments

- **Why, Not How**: Code comments should only explain *why* something is done a certain way (e.g. documenting surprises, quirks, boundary conditions, and decisions). Do not explain *how* the code works, as the code itself should be clean enough to be self-documenting.
- **Avoid Commented-Out Code**: Never commit commented-out code. Use source control history to retrieve old code.
- **No Redundant Comments**: Do not add comments that simply repeat the name of the function or the variable.
  - *Incorrect:*
    ```python
    # Calculate total price
    total = calculate_total(items)
    ```
  - *Correct:*
    ```python
    total = calculate_total(items)
    ```
