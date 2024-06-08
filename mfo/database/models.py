# /mfo/database/models/profiles.py

from mfo.database.base import db
from sqlalchemy import Column, Table, ForeignKey, UniqueConstraint, ForeignKey, Integer
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

class_repertoire = Table(
    'class_repertoire', db.metadata,
    Column('class_id', ForeignKey('class.id'), primary_key=True),
    Column('repertoire_id', ForeignKey('repertoire.id'), primary_key=True)
)

schools_contacts = Table(
    'schools_contacts', db.metadata,
    Column('school_id', ForeignKey('schools.id'), primary_key=True),
    Column('contact_id', ForeignKey('profile.id'), primary_key=True)
)

schools_participants = Table(
    'schools_participants', db.metadata,
    Column('school_id', ForeignKey('schools.id'), primary_key=True),
    Column('participant_id', ForeignKey('profile.id'), primary_key=True)
)

schools_teachers = Table(
    'schools_teachers', db.metadata,
    Column('school_id', ForeignKey('schools.id'), primary_key=True),
    Column('teacher_id', ForeignKey('profile.id'), primary_key=True)
)

class Profile(db.Model):
    __tablename__ = 'profile'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    client_id: Mapped[Optional[str]] = mapped_column(nullable=True)
    session: Mapped[Optional[str]] = mapped_column(nullable=True)

    name: Mapped[Optional[str]] = mapped_column(nullable=True)
    group_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    identifier: Mapped[Optional[int]] = mapped_column(nullable=True, default=0)
    
    birthdate: Mapped[Optional[datetime.date]] = mapped_column(nullable=True)
    
    address: Mapped[Optional[str]] = mapped_column(nullable=True)
    city: Mapped[Optional[str]] = mapped_column(nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(nullable=True)
    province: Mapped[Optional[str]] = mapped_column(nullable=True)

    email: Mapped[Optional[str]] = mapped_column(nullable=True)

    phone: Mapped[Optional[str]] = mapped_column(nullable=True)

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

    contact_for_schools: Mapped[list["School"]] = relationship(
        "School", secondary=schools_contacts, back_populates="contacts"
    )

    attends_schools: Mapped[list["School"]] = relationship(
        "School", secondary=schools_participants, back_populates="students_or_groups"
    )

    teaches_at_schools: Mapped[list["School"]] = relationship(
        "School", secondary=schools_teachers, back_populates="teachers"
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
        UniqueConstraint('name', 'email', name='profile_patricipant_uc'),
        UniqueConstraint('group_name', 'email', name='profile_group_uc')
    )


class FestivalClass(db.Model):
    __tablename__ = 'class'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    number: Mapped[Optional[str]] = mapped_column(nullable=True)
    suffix: Mapped[Optional[str]] = mapped_column(nullable=True)

    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    class_type: Mapped[Optional[str]] = mapped_column(nullable=True)
    fee: Mapped[Optional[str]] = mapped_column(nullable=True)
    discipline: Mapped[Optional[str]] = mapped_column(nullable=True)
    adjudication_time: Mapped[Optional[int]] = mapped_column(nullable=True)
    move_time: Mapped[Optional[int]] = mapped_column(nullable=True)

    test_pieces: Mapped[list["Repertoire"]] = relationship(
        "Repertoire", secondary=class_repertoire, back_populates="festival_classes"
    )


class Repertoire(db.Model):
    _tablename__ = 'repertoire'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    title: Mapped[Optional[str]] = mapped_column(nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(nullable=True)
    composer: Mapped[Optional[str]] = mapped_column(nullable=True)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)

    festival_classes: Mapped[list[FestivalClass]] = relationship(
        "FestivalClass", secondary=class_repertoire, back_populates="test_pieces"
    )


class School(db.Model):
    __tablename__ = 'schools'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[Optional[str]] = mapped_column(nullable=True)
    notes: Mapped[Optional[int]] = mapped_column(nullable=True)
     
    contacts: Mapped[list[Profile]] = relationship(
        "Profile", secondary=schools_contacts, back_populates="contact_for_schools"
    )

    students_or_groups: Mapped[list[Profile]] = relationship(
        "Profile", secondary=schools_participants, back_populates="attends_schools"
    )

    teachers: Mapped[list[Profile]] = relationship(
        "Profile", secondary=schools_teachers, back_populates="teaches_at_schools"
    )