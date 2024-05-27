# /mfo/database/models/profiles.py

from mfo.database.base import db
from sqlalchemy import Column, Table, ForeignKey, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime


profiles_users = Table(
    "profiles_users",
    db.metadata,
    Column("profile_id", ForeignKey("profile.id"), primary_key=True),
    Column("user_id", ForeignKey("user.id"), primary_key=True)
)

# class Profiles_Users(db.model):
#     __tablename__ = "profiles_users"
#     profile_id: Mapped[int] = mapped_column(ForeignKey("profile.id"), primary_key=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
#     primary_profile: Mapped[bool] = mapped_column(nullable=False)


class Profile(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    # extra field in case two people have same first and last names
    identifier: Mapped[int]  = mapped_column(nullable=True, default=0)
    
    birthdate: Mapped[datetime.date] = mapped_column(nullable=True)
    
    address: Mapped[str] = mapped_column(nullable=True)
    city: Mapped[str] = mapped_column(nullable=True)
    postal_code: Mapped[str] = mapped_column(nullable=True)
    province: Mapped[str] = mapped_column(nullable=True)

    # Profile is associated with 1 or more users
    # if profile.email = user.email, then this is the user's primary profile
    # if emails do not match, then this is a profile associated with the user
    # like a student associated with a teacher
    email: Mapped[str] = mapped_column(nullable=False)

    phone: Mapped[str] = mapped_column(nullable=True)
    school: Mapped[str] = mapped_column(nullable=True)
    teacher: Mapped[str] = mapped_column(nullable=True)

    total_fee: Mapped[float] = mapped_column(nullable=False, default=0.0)
    feed_paid: Mapped[float] = mapped_column(nullable=False, default=0.0)
    comments: Mapped[str] = mapped_column(nullable=True)
    national_festival: Mapped[bool] = mapped_column(nullable=False, default=False)

    users: Mapped[list["User"]] = relationship(
        secondary=profiles_users, back_populates="profiles"
    )
    __table_args__ = (
        UniqueConstraint('first_name', 'last_name', 'identifier', name='profile_name_uc'),
    )