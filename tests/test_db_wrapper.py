import unittest
from src.utils.db import DatabaseWrapper


class WrapperTestCase(unittest.TestCase):
    def setUp(self):
        self.wrapper = DatabaseWrapper()

    def test_deposit(self):
        destination = "100"
        amount = 10
        self.assertEqual(
            self.wrapper.deposit(destination, amount), True, "deposit failed"
        )
        self.assertEqual(
            self.wrapper.get_current_balance(destination), amount, "incorrect balance"
        )

    def test_deposit_negative_amount(self):
        destination = "100"
        amount = -10
        self.assertRaises(AssertionError, self.wrapper.deposit, destination, amount)

    def test_withdraw_success(self):
        origin = "100"
        amount = 10
        amount_to_withdraw = 5

        self.assertEqual(
            self.wrapper.withdraw(origin, amount),
            False,
            "withdraw from non-existing account",
        )

        self.wrapper.deposit(origin, amount)

        self.assertEqual(
            self.wrapper.withdraw(origin, amount_to_withdraw),
            True,
            "withdraw failed",
        )
        self.assertEqual(
            self.wrapper.get_current_balance(origin),
            amount - amount_to_withdraw,
            "incorrect balance",
        )

    def test_withdraw_amount_greater_than_holding(self):
        origin = "100"
        amount = 10
        amount_to_withdraw = 11

        self.assertEqual(
            self.wrapper.withdraw(origin, amount),
            False,
            "withdraw from non-existing account",
        )

        self.wrapper.deposit(origin, amount)

        self.assertEqual(
            self.wrapper.withdraw(origin, amount_to_withdraw),
            False,
            "withdraw more than balance",
        )

    def test_withdraw_negative_amount(self):
        origin = "100"
        amount = 10
        amount_to_withdraw = -1

        self.wrapper.deposit(origin, amount)

        self.assertRaises(
            AssertionError, self.wrapper.deposit, origin, amount_to_withdraw
        )

    def test_transfer_to_non_existing_account(self):
        origin = "100"
        destination = "200"
        amount_to_deposit = 10
        amount_to_transfer = amount_to_deposit // 2

        self.wrapper.deposit(origin, amount_to_deposit)

        self.assertEqual(
            self.wrapper.transfer(origin, destination, amount_to_transfer),
            True,
            "transfer to non-existing account failed",
        )

        expected_origin_balance = amount_to_deposit - amount_to_transfer
        self.assertEqual(
            self.wrapper.get_current_balance(origin),
            expected_origin_balance,
            "wrong amount transferred",
        )

        self.assertEqual(
            self.wrapper.get_current_balance(destination),
            amount_to_transfer,
            "wrong amount transferred",
        )

    def test_transfer_to_existing_account(self):
        origin = "100"
        destination = "200"
        amount_to_deposit = 10
        amount_to_transfer = amount_to_deposit // 2

        self.wrapper.deposit(origin, amount_to_deposit)
        self.wrapper.deposit(destination, amount_to_deposit)

        self.assertEqual(
            self.wrapper.transfer(origin, destination, amount_to_transfer),
            True,
            "transfer to non-existing account failed",
        )

        expected_origin_balance = amount_to_deposit - amount_to_transfer
        self.assertEqual(
            self.wrapper.get_current_balance(origin),
            expected_origin_balance,
            "wrong amount transferred",
        )

        expected_destination_balance = amount_to_deposit + amount_to_transfer
        self.assertEqual(
            self.wrapper.get_current_balance(destination),
            expected_destination_balance,
            "wrong amount transferred",
        )

    def test_transfer_amount_greater_than_holding(self):
        origin = "100"
        destination = "200"
        amount_to_deposit = 10
        amount_to_transfer = amount_to_deposit * 2

        self.wrapper.deposit(origin, amount_to_deposit)

        self.assertEqual(
            self.wrapper.transfer(origin, destination, amount_to_transfer),
            False,
            "transferred amount greater than holding",
        )


if __name__ == "__main__":
    unittest.main()
