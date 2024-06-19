from collections import defaultdict

from fastapi import HTTPException


class MockDatabase:
    def __init__(self) -> None:
        self.balances = defaultdict(float)

    def reset(self) -> None:
        self.balances.clear()


class DatabaseWrapper:
    def __init__(self) -> None:
        self.db = MockDatabase()

    def contains_account(self, account_id: str) -> bool:
        return account_id in self.db.balances

    def get_current_balance(self, account_id: str) -> float:
        return self.db.balances.get(account_id, 0.0)

    def has_enough_balance(self, account_id: str, amount: float) -> bool:
        return self.get_current_balance(account_id) >= amount

    def deposit(self, account_id: str, amount: float) -> float:
        # How to propagate this error and return it as error?
        if amount <= 0:
            raise HTTPException(
                status_code=400, detail="Can't deposit amount 0 or less"
            )

        if self.contains_account(account_id):
            self.db.balances[account_id] += amount
        else:
            self.db.balances[account_id] = amount
        return self.db.balances[account_id]

    def withdraw(self, account_id: str, amount: float) -> float:
        if amount <= 0:
            raise HTTPException(
                status_code=400, detail="Can't withdraw amount 0 or less"
            )
        if self.has_enough_balance(account_id, amount):
            self.db.balances[account_id] -= amount
            return self.db.balances[account_id]
        else:
            raise HTTPException(
                status_code=400,
                detail="Can't withdraw. Amount is greater than current balance",
            )

    # Enhancement: currently, if the destination account does not exist, it's then created
    def transfer(self, origin_id: str, destination_id: str, amount: float) -> bool:
        if amount <= 0:
            raise HTTPException(
                status_code=400, detail="Can't transfer amount 0 or less"
            )
        if self.has_enough_balance(origin_id, amount):
            self.deposit(destination_id, amount)
            self.withdraw(origin_id, amount)
            return True
        return False


db_wrapper = DatabaseWrapper()
