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
        return self.session.query(Account).all()

    def get_account(self, account_id: str) -> Account:
        return self.session.query(Account).filter_by(account_id=account_id).first()

    def get_account_with_lock(self, account_id: str) -> Account:
        return (
            self.session.query(Account)
            .with_for_update()
            .filter_by(account_id=account_id)
            .first()
        )

    def create_account(self, account_id: str, balance: int) -> Account:
        logger.info(f"here { account_id }, { balance }")
        new_account = Account(account_id=account_id, balance=balance)
        self.session.add(new_account)
        return new_account

    def update_account_balance(self, account: Account, amount: int):
        account.balance += amount
        return account

    def close(self):
        self.session.close()

    def rollback(self):
        self.session.rollback()

    def commit(self):
        self.session.commit()


Base.metadata.create_all(bind=engine)
