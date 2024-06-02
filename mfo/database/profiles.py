# /mfo/database/models/profiles.py

from mfo.database.base import db
from sqlalchemy import Column, Table, ForeignKey, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
import datetime


profiles_users = Table(
    "profiles_users",
    db.metadata,
    Column("profile_id", ForeignKey("profile.id"), primary_key=True),
    Column("user_id", ForeignKey("user.id"), primary_key=True)
)

teachers_students = Table(
    'teacher_student', db.metadata,
    Column('teacher_id', ForeignKey('profile.id'), primary_key=True),
    Column('student_id', ForeignKey('profile.id'), primary_key=True)
)

groups_contacts = Table(
    'groups_contacts', db.metadata,
    Column('group_id', ForeignKey('profile.id'), primary_key=True),
    Column('contact_id', ForeignKey('profile.id'), primary_key=True)
)

class Profile(db.Model):
    __tablename__ = 'profile'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    client_id: Mapped[Optional[str]] = mapped_column(nullable=True)
    session: Mapped[Optional[str]] = mapped_column(nullable=True)

    first_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    group_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    identifier: Mapped[Optional[int]] = mapped_column(nullable=True, default=0)
    
    birthdate: Mapped[Optional[datetime.date]] = mapped_column(nullable=True)
    
    address: Mapped[Optional[str]] = mapped_column(nullable=True)
    city: Mapped[Optional[str]] = mapped_column(nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(nullable=True)
    province: Mapped[Optional[str]] = mapped_column(nullable=True)

    email: Mapped[Optional[str]] = mapped_column(nullable=True)

    phone: Mapped[Optional[str]] = mapped_column(nullable=True)
    school: Mapped[Optional[str]] = mapped_column(nullable=True)

    teachers: Mapped[List["Profile"]] = relationship(
        "Profile",
        secondary=teachers_students,
        primaryjoin=id == teachers_students.c.student_id,
        secondaryjoin=id == teachers_students.c.teacher_id,
        back_populates="students",
        foreign_keys=[teachers_students.c.student_id, teachers_students.c.teacher_id]
    )

    students: Mapped[List["Profile"]] = relationship(
        "Profile",
        secondary=teachers_students,
        primaryjoin=id == teachers_students.c.teacher_id,
        secondaryjoin=id == teachers_students.c.student_id,
        back_populates="teachers",
        foreign_keys=[teachers_students.c.teacher_id, teachers_students.c.student_id]
    )

    group_contacts: Mapped[List["Profile"]] = relationship(
        "Profile",
        secondary=groups_contacts,
        primaryjoin=id == groups_contacts.c.group_id,
        secondaryjoin=id == groups_contacts.c.contact_id,
        back_populates="group",
        foreign_keys=[groups_contacts.c.group_id, groups_contacts.c.contact_id]
    )

    group: Mapped[List["Profile"]] = relationship(
        "Profile",
        secondary=groups_contacts,
        primaryjoin=id == groups_contacts.c.contact_id,
        secondaryjoin=id == groups_contacts.c.group_id,
        back_populates="group_contacts",
        foreign_keys=[groups_contacts.c.contact_id, groups_contacts.c.group_id]
    )

    total_fee: Mapped[Optional[float]] = mapped_column(nullable=True, default=0.0)
    fees_paid: Mapped[Optional[float]] = mapped_column(nullable=True, default=0.0)
    comments: Mapped[Optional[str]] = mapped_column(nullable=True)
    national_festival: Mapped[Optional[bool]] = mapped_column(nullable=True, default=False)

    users: Mapped[List["User"]] = relationship(
        "User",
        secondary=profiles_users,
        back_populates="profiles"
    )

    __table_args__ = (
        UniqueConstraint('first_name', 'last_name', 'identifier', name='profile_name_uc'),
    )

# class Profile(db.Model):
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

#     # Change to a foreign key relationship to the Clients table
#     client_id: Mapped[str] = mapped_column(nullable=True)

#     # Change to a foreign key relationship to the Sessions table
#     session: Mapped[str] = mapped_column(nullable=True)

#     first_name: Mapped[str] = mapped_column(nullable=True)
#     last_name: Mapped[str] = mapped_column(nullable=True)
#     group_name: Mapped[str] = mapped_column(nullable=True)
#     # extra field in case two people have same first and last names
#     identifier: Mapped[int]  = mapped_column(nullable=True, default=0)
    
#     birthdate: Mapped[datetime.date] = mapped_column(nullable=True)
    
#     address: Mapped[str] = mapped_column(nullable=True)
#     city: Mapped[str] = mapped_column(nullable=True)
#     postal_code: Mapped[str] = mapped_column(nullable=True)
#     province: Mapped[str] = mapped_column(nullable=True)

#     email: Mapped[str] = mapped_column(nullable=True)

#     phone: Mapped[str] = mapped_column(nullable=True)
#     school: Mapped[str] = mapped_column(nullable=True)

#     teachers: Mapped[list["Profile"]] = relationship(
#         secondary=teachers_students, back_populates="students")

#     group_contacts: Mapped[list["Profile"]] = relationship(
#         secondary=groups_contacts, back_populates="group")

#     total_fee: Mapped[float] = mapped_column(nullable=True, default=0.0)
#     fees_paid: Mapped[float] = mapped_column(nullable=True, default=0.0)
#     comments: Mapped[str] = mapped_column(nullable=True)
#     national_festival: Mapped[bool] = mapped_column(nullable=True, default=False)

#     users: Mapped[list["User"]] = relationship(
#         secondary=profiles_users, back_populates="profiles"
#     )
#     __table_args__ = (
#         UniqueConstraint('first_name', 'last_name', 'identifier', name='profile_name_uc'),
#     )