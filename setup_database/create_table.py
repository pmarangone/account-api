import psycopg2

from account import AccountSchema

DB_HOST = "localhost"
DB_NAME = "database"
DB_USER = "user"
DB_PASSWORD = "password"


def create_conn():
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()

    return conn, cur


def create_table():
    try:
        conn, cur = create_conn()

        with open("data.sql", "r") as sql_file:
            sql_commands = sql_file.read()

        cur = conn.cursor()
        cur.execute(sql_commands)
        conn.commit()

        return conn
    except Exception as e:
        print("e", e)


def create_account(account_id, balance):
    create_account_sql = "INSERT INTO accounts (account_id, balance) VALUES (%s, %s);"
    try:
        conn, cur = create_conn()
        cur.execute(
            create_account_sql,
            (
                account_id,
                balance,
            ),
        )
        conn.commit()
    except Exception as e:
        print("e", e)


def read_accounts():
    select_all = "SELECT * FROM accounts"
    try:
        conn, cur = create_conn()
        cur.execute(select_all)
        data = cur.fetchall()

        print("data", data)
    except Exception as e:
        print("e", e)


def get_account(account_id):
    """Retrieve account by id"""
    select_account_by_id = "SELECT * FROM accounts WHERE account_id=%s;"
    try:
        conn, cur = create_conn()
        cur.execute(select_account_by_id, (account_id,))
        data = cur.fetchall()
        print(data)

    except Exception as e:
        print("e", e)


def update_balance(id, value=10):
    select_account = "SELECT * FROM accounts WHERE account_id=%s FOR UPDATE;"
    update_balance_query = (
        "UPDATE accounts SET balance=%s WHERE account_id=%s RETURNING *;"
    )
    try:
        conn, cur = create_conn()
        # Lock the user's account row in the database
        cur.execute(select_account, (id,))
        account = cur.fetchone()

        current_balance = account[1]
        # If withdraw
        if value < 0:
            assert current_balance >= -value, "Error"

        if account:
            new_balance = current_balance + value

            cur.execute(
                update_balance_query,
                (
                    new_balance,
                    id,
                ),
            )
            updated_account = cur.fetchone()
            account_data = {
                field: updated_account[idx]
                for idx, field in enumerate(AccountSchema.model_fields.keys())
            }
            conn.commit()
        else:
            pass

    except Exception as e:
        print("e", e)


if __name__ == "__main__":
    id = "1000"
    create_table()
    # create_account(id, 1001)
    # read_accounts()
    # update_balance(id, value=-200)
    # read_accounts()
    # get_account("1000")
