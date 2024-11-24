from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer

from src.database.setup_db import DATABASE_URL
from src.models.account_manager import AccountSchema
from src.models.errors import NonExist
from src.utils.logger import get_logger

Base = declarative_base()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logger = get_logger(__name__)


class Account(Base):
    __tablename__ = "accounts"
    account_id = Column(String, primary_key=True, index=True)
    balance = Column(Integer, default=0)


class AccountRepository:
    def __init__(self):
        self.session = SessionLocal()

    def parse_account_to_return(self, account) -> AccountSchema:
        account = account.__dict__
        return {"id": account["account_id"], "balance": account["balance"]}

    def get_accounts(self):
        """Retrieve all accounts"""
        try:
            accounts = self.session.query(Account).all()
            return [self.parse_account_to_return(account) for account in accounts]
        except exc.SQLAlchemyError as sql_err:
            logger.error("SQLAlchemy error while retrieving accounts: ", sql_err)
        except Exception as err:
            logger.error("General error while retrieving accounts: ", err)

    def get_account(self, account_id: str) -> AccountSchema:
        """Retrieve account by ID"""
        try:
            account = (
                self.session.query(Account).filter_by(account_id=account_id).first()
            )

            if account:
                return self.parse_account_to_return(account)
            else:
                raise NonExist("Account does not exist")
        except exc.SQLAlchemyError as sql_err:
            logger.error("SQLAlchemy error while retrieving account: ", sql_err)
        except Exception as err:
            logger.error("General error while retrieving account: ", err)

    def create_account(self, account_id: str, initial_balance: int) -> AccountSchema:
        """Creates (account_id, initial_balance): account_id is unique"""
        try:
            new_account = Account(account_id=account_id, balance=initial_balance)
            self.session.add(new_account)
            self.session.commit()
            self.session.refresh(new_account)
            return self.parse_account_to_return(new_account)
        except exc.SQLAlchemyError as sql_err:
            logger.error("SQLAlchemy error while creating account: ", sql_err)
            self.session.rollback()
            raise sql_err
        except Exception as err:
            logger.error("General error while creating account: ", err)
            self.session.rollback()
            raise err

    def update_balance(self, account_id: str, amount: int) -> AccountSchema:
        """Update the balance of an account, create if it doesn't exist"""
        try:
            account = (
                self.session.query(Account)
                .with_for_update()
                .filter_by(account_id=account_id)
                .first()
            )
            if account:
                if amount < 0 and account.balance < -amount:
                    raise ValueError("ERROR: Insufficient balance")
                account.balance += amount
                self.session.commit()
                self.session.refresh(account)
                return self.parse_account_to_return(account)
            else:
                if amount > 0:
                    return self.create_account(account_id, amount)
                else:
                    raise NonExist("ERROR: Tried to withdraw from non-existing account")
        except exc.SQLAlchemyError as sql_err:
            logger.error("SQLAlchemy error while updating balance: ", sql_err)
            self.session.rollback()
            raise sql_err
        except Exception as err:
            logger.error("General error while updating balance: ", err)
            self.session.rollback()
            raise err

    def close(self):
        self.session.close()


Base.metadata.create_all(bind=engine)

account_repository = AccountRepository()
