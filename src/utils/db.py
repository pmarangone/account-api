from collections import defaultdict


class MockDatabase:
    def __init__(self) -> None:
        self.balances = defaultdict(int)

    def reset(self) -> None:
        self.balances = defaultdict(int)


class DatabaseWrapper:
    def __init__(self) -> None:
        self.db = MockDatabase()

    def contains_account(self, account_id: str) -> bool:
        return account_id in self.db.balances

    def get_current_balance(self, account_id: str) -> bool:
        if self.contains_account(account_id):
            return self.db.balances[account_id]
        return 0

    def has_enough_balance(self, account_id: str, amount: int) -> bool:
        return self.get_current_balance(account_id) >= amount

    def deposit(self, account_id: str, amount: int) -> bool:
        assert amount > 0, "can't deposit a value lower 0"
        if self.contains_account(account_id):
            self.db.balances[account_id] += amount
        else:
            self.db.balances[account_id] = amount
        return True

    def withdraw(self, account_id: str, amount: int) -> bool:
        assert amount > 0, "can't withdraw a value lower 0"
        if self.has_enough_balance(account_id, amount):
            self.db.balances[account_id] -= amount
            return True
        return False

    # Enhancement: currently, if the destination account does not exist, it's then created
    def transfer(self, origin_id: str, destination_id: str, amount: int) -> bool:
        assert amount > 0, "can't transfer a value lower 0"
        if self.has_enough_balance(origin_id, amount):
            self.deposit(destination_id, amount)
            self.withdraw(origin_id, amount)
            return True
        return False


db_wrapper = DatabaseWrapper()
