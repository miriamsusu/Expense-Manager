from sqlalchemy.orm import Session

from app.auth.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


def getUserByEmail(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def createUser(db: Session, payload: UserCreate) -> User:
    db_user = User(
        email=payload.email,
        phone_number=payload.phone_number,
        hashed_password=hash_password(payload.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user