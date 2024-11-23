import psycopg2

from src.database.setup_db import connect_db
from src.models.account_manager import AccountSchema
from src.models.errors import NonExist


class AccountRepository:
    def __init__(self):
        self.conn = None

    def get_connection_and_cursor(self):
        if self.conn:
            return self.conn, self.conn.cursor()

        self.conn = connect_db()
        return self.conn, self.conn.cursor()

    def get_accounts(self):
        """Retrieve all accounts"""
        select_all_accounts = "SELECT * FROM accounts"
        try:
            conn, cur = self.get_connection_and_cursor()
            cur.execute(select_all_accounts)
            return cur.fetchall()

        except Exception as e:
            print("e", e)

    def get_account(self, account_id: str) -> AccountSchema:
        """Retrieve account by id"""
        select_account_by_id = "SELECT * FROM accounts WHERE account_id=%s;"
        try:
            conn, cur = self.get_connection_and_cursor()
            cur.execute(select_account_by_id, (account_id,))
            account = cur.fetchall()[0]

            if account:
                account_data = {
                    field: account[idx]
                    for idx, field in enumerate(AccountSchema.model_fields.keys())
                }

                return account_data
            else:
                raise "Account does not exist"

        except Exception as e:
            print("e", e)

    def create_account(self, account_id: str, initial_balance: int) -> AccountSchema:
        """Creates (account_id, initial_balance): account_id is unique"""
        create_account_sql = (
            "INSERT INTO accounts (account_id, balance) VALUES (%s, %s) RETURNING *;"
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
            updated_account = cur.fetchone()
            account_data = {
                field: updated_account[idx]
                for idx, field in enumerate(AccountSchema.model_fields.keys())
            }
            conn.commit()

            return account_data

        except Exception as e:
            print("e", e)

    def update_balance(self, account_id: str, amount: int) -> AccountSchema:
        select_account = "SELECT * FROM accounts WHERE account_id=%s FOR UPDATE;"
        update_balance_query = (
            "UPDATE accounts SET balance=%s WHERE account_id=%s RETURNING *;"
        )
        try:
            conn, cur = self.get_connection_and_cursor()
            # Lock the user's account row in the database
            cur.execute(select_account, (account_id,))
            account = cur.fetchone()

            if account:
                current_balance = account[1]
                # If withdraw

                if amount < 0:
                    assert current_balance >= -amount, "ERROR: Insufficient balance"
                new_balance = current_balance + amount

                # Update account balance and release lock
                cur.execute(
                    update_balance_query,
                    (
                        new_balance,
                        account_id,
                    ),
                )
                updated_account = cur.fetchone()
                account_data = {
                    field: updated_account[idx]
                    for idx, field in enumerate(AccountSchema.model_fields.keys())
                }
                conn.commit()

                return account_data
            else:
                if amount > 0:
                    account = self.create_account(account_id, amount)
                    return account

                else:
                    raise NonExist("ERROR: Tried to withdraw from non existing account")

        # except NonExist as e:
        #     print("e", e)  # TODO
        #     conn.rollback()
        #     raise e

        except Exception as e:
            print("e", e)  # TODO
            conn.rollback()
            raise e

        finally:
            if cur:
                cur.close()
            # if conn:
            #     conn.close()


account_repository = AccountRepository()
