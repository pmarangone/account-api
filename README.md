Account API

## How to use it
Tested using Python 3.10.14

```bash
pip install -r requirements.txt
fastapi run src/main.py
```

## Routes breakdown
**You can run all routes in sequence through postman `run collection` feature. The postman file is in the project root.**

> POST: /reset, resets the application state.

> GET: /balance?account_id=, returns the current balance of account if present.

> POST: /event, which have 3 types:
- **deposit**: deposits _amount_ to _account_ if account does not exists, otherwise increments the current balance.
- **withdraw**: withdraws _amount_ from _account_ if account exists and amount is less than or equal than current balance.
- **transfer**: transfer _amount_ from _origin_ to _destination_. If _origin_ does not exists or _origin_ balance is less than amount, returns error. If _destination_ does not exists, creates the _destination_ account, deposits amount to _destination_ and withdraws from _origin_.

## Patterns applied

- [x] Repository pattern (AccountRepository): The Facade Pattern provides a simplified interface to a set of subsystems.
- [x] Service pattern (EventService): Encapsulates business logic into service classes to keep your endpoints simple and reusable.
- [x] Singleton Pattern (Database): The pattern ensures that only one instance of the class is created. If an instance already exists, the pattern provides access to that same instance.
- [x] Validation Pattern (AccountRepository, field_validator): FastAPI provides built-in validation using Pydantic models. To test this, try making a deposit where the destination is an integer instead of a string or amount is less than or equal zero.
- [x] Error handling pattern (search for `raise`): Good error handling ensures robust APIs.
- [x] Observer pattern (consume_messages.py): Allows components to subscribe to events and get notified when something changes. Everytime an account receives a deposit or transfer, the account's owner is notified.

## Test it
Run the tests using `python3 -m unittest tests/test_db_wrapper.py`



