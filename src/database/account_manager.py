import psycopg2

from src.database.setup_db import connect_db


class AccountManager:
    def __init__(self):
        pass

    def get_connection_and_cursor(self):
        conn = connect_db()
        cur = conn.cursor()

        return conn, cur

    def get_accounts(self):
        """Retrieve all accounts"""
        select_all_accounts = "SELECT * FROM accounts"
        try:
            conn, cur = self.get_connection_and_cursor()
            cur.execute(select_all_accounts)
            return cur.fetchall()

        except Exception as e:
            print("e", e)

    def get_account(self, account_id: str):
        """Retrieve account by id"""
        select_account_by_id = "SELECT * FROM accounts WHERE account_id=%s;"
        try:
            conn, cur = self.get_connection_and_cursor()
            cur.execute(select_account_by_id, (account_id,))
            return cur.fetchall()

        except Exception as e:
            print("e", e)

    def create_account(self, account_id: str, initial_balance: int):
        """Creates (account_id, initial_balance): account_id is unique"""
        create_account_sql = (
            "INSERT INTO accounts (account_id, balance) VALUES (%s, %s);"
        )
        try:
            conn, cur = self.get_connection_and_cursor()
            cur.execute(
                create_account_sql,
                (
                    account_id,
                    initial_balance,
                ),
            )
            conn.commit()

            return self.get_account(account_id)

        except Exception as e:
            print("e", e)

    def update_balance(self, account_id: str, amount: int):
        select_account = "SELECT * FROM accounts WHERE account_id=%s FOR UPDATE;"
        update_balance_query = "UPDATE accounts SET balance=%s WHERE account_id=%s;"
        try:
            conn, cur = self.get_connection_and_cursor()
            # Lock the user's account row in the database
            cur.execute(select_account, (account_id,))
            account = cur.fetchone()

            if account:
                current_balance = account[1]
                # If withdraw
                if amount < 0:
                    assert current_balance >= -amount, "Error"
                new_balance = current_balance + amount

                # Update account balance and release lock
                cur.execute(
                    update_balance_query,
                    (
                        new_balance,
                        1,
                    ),
                )
                conn.commit()
            else:
                if amount > 0:
                    self.create_account(account_id, amount)
                else:
                    raise "ERROR: Tried to withdraw from non existing account"

        except Exception as e:
            print("e", e)  # TODO


account_manager = AccountManager()
