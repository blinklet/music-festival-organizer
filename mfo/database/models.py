# /mfo/database/models/profiles.py

from mfo.database.base import db
from sqlalchemy import Column, Table, ForeignKey, UniqueConstraint, ForeignKey, String, Boolean, Integer, DateTime, Date, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from decimal import Decimal
import datetime


profiles_users = Table(
    "profiles_users",
    db.metadata,
    Column("profile_id", ForeignKey("profile.id"), primary_key=True),
    Column("user_id", ForeignKey("user.id"), primary_key=True)
)

profiles_roles = Table(
    "profiles_roles",
    db.metadata,
    Column("profile_id", ForeignKey("profile.id"), primary_key=True),
    Column("role_id", ForeignKey("role.id"), primary_key=True)
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
    Column('class_id', ForeignKey('classes.id'), primary_key=True),
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

participants_entries = Table(
    'participants_entries', db.metadata,
    Column('participant_id', ForeignKey('profile.id'), primary_key=True),
    Column('entry_id', ForeignKey('entries.id'), primary_key=True)
)

accompanists_entries = Table(
    'accompanists_entries', db.metadata,
    Column('accompanist_id', ForeignKey('profile.id'), primary_key=True),
    Column('entry_id', ForeignKey('entries.id'), primary_key=True)
)

entry_repertoire = Table(
    'entry_repertoire', db.metadata,
    Column('entry_id', ForeignKey('entries.id'), primary_key=True),
    Column('repertoire_id', ForeignKey('repertoire.id'), primary_key=True)
)

participants_seasons = Table(
    'participants_seasons', db.metadata,
    Column('participant_id', Integer, ForeignKey('profile.id'), primary_key=True),
    Column('season_id', Integer, ForeignKey('seasons.id'), primary_key=True)
)

schools_seasons = Table(
    'schools_seasons', db.metadata,
    Column('school_id', Integer, ForeignKey('schools.id'), primary_key=True),
    Column('season_id', Integer, ForeignKey('seasons.id'), primary_key=True)
)

class UserFestivalsRoles(db.Model):
    __tablename__ = 'users_festivals_roles'
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), primary_key=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('role.id'), primary_key=True)
    festival_id: Mapped[int] = mapped_column(Integer, ForeignKey('festivals.id'), primary_key=True)
    
    user: Mapped['User'] = relationship('User', back_populates='roles_festivals')
    role: Mapped['Role'] = relationship('Role', back_populates='users_festivals')
    festival: Mapped['Festival'] = relationship('Festival', back_populates='roles_users')

seasons_classes = Table(
    'seasons_classes', db.metadata,
    Column('season_id', Integer, ForeignKey('seasons.id'), primary_key=True),
    Column('class_id', Integer, ForeignKey('classes.id'), primary_key=True)
)

class Profile(db.Model):
    __tablename__ = 'profile'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    #user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=True)
    primary: Mapped[bool] = mapped_column(Boolean, default=False)

    client_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    session: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    group_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    identifier: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    
    birthdate: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    
    address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    province: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)

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

    accompanies_entries: Mapped[List["Entry"]] = relationship(
        "Entry", secondary=accompanists_entries, back_populates="accompanists"
    )

    participates_in_entries: Mapped[List["Entry"]] = relationship(
        "Entry", secondary=participants_entries, back_populates="participants"
    )

    total_fee: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(precision=8, scale=2), nullable=True, default=0.00)
    fees_paid: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(precision=8, scale=2), nullable=True, default=0.00)

    comments: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    national_festival: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=False)

    users: Mapped[List["User"]] = relationship(
        "User",
        secondary=profiles_users,
        back_populates="profiles"
    )

    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary=profiles_roles,
        back_populates="profiles"
    )

    # Each profile may be conected to one or more festival seasons
    seasons: Mapped[List["Season"]] = relationship(
        "Season",
        secondary=participants_seasons,
        back_populates="participants"
    )

    __table_args__ = (
        UniqueConstraint('name', 'email', name='profile_patricipant_uc'),
        UniqueConstraint('group_name', 'email', name='profile_group_uc')
    )


class Festival(db.Model):
    __tablename__ = 'festivals'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    name: Mapped[str] = mapped_column(nullable=True)
    nickname: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    location: Mapped[Optional[str]] = mapped_column(nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(nullable=True)
    
    seasons: Mapped[List["Season"]] = relationship(
        "Season", 
        back_populates="festival"
    )

    roles_users: Mapped[List["UserFestivalsRoles"]] = relationship(
        'UserFestivalsRoles',
        back_populates='festival'
    )


class Season(db.Model):
    __tablename__ = 'seasons'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    festival_id: Mapped[int] = mapped_column(Integer, ForeignKey('festivals.id'))

    name: Mapped[str] = mapped_column(String, nullable=True)
    primary: Mapped[bool] = mapped_column(Boolean, default=False)
    start_date: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    registration_start_date: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    registration_end_date: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    end_date: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    
    festival: Mapped["Festival"] = relationship("Festival", back_populates="seasons")
    classes: Mapped[List["FestivalClass"]] = relationship(
        "FestivalClass", secondary=seasons_classes, back_populates="seasons"
    )
    entries: Mapped[List["Entry"]] = relationship("Entry", back_populates="season")
    repertoire: Mapped[List["Repertoire"]] = relationship("Repertoire", back_populates="season")

    schools: Mapped[List["School"]] = relationship(
        "School",
        secondary=schools_seasons,
        back_populates="seasons"
    )

    participants: Mapped[List["Profile"]] = relationship(
        "Profile",
        secondary=participants_seasons,
        back_populates="seasons"
    )

    __table_args__ = (
        # Each season is unique to a festival
        UniqueConstraint('id', 'festival_id', name='unique_festival_season'),
        # Each festival has only one primary season
        UniqueConstraint('festival_id', 'primary', name='unique_festival_primary'),
    )


class FestivalClass(db.Model):
    __tablename__ = 'classes'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    number: Mapped[str] = mapped_column(nullable=True)
    suffix: Mapped[Optional[str]] = mapped_column(nullable=True)

    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    class_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    fee: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(precision=8, scale=2), nullable=True)
    discipline: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    adjudication_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    move_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    test_pieces: Mapped[List["Repertoire"]] = relationship(
        "Repertoire", secondary=class_repertoire, back_populates="festival_classes"
    )

    # Each class may be connected to multiple seasons
    seasons: Mapped[List["Season"]] = relationship(
        "Season", secondary=seasons_classes, back_populates="classes"
    )

    entries: Mapped[List["Entry"]] = relationship("Entry", back_populates="festival_class")


class Entry(db.Model):
    __tablename__ = 'entries'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    participants: Mapped[List["Profile"]] = relationship(
        "Profile", secondary=participants_entries, back_populates="participates_in_entries"
    )
    accompanists: Mapped[List["Profile"]] = relationship(
        "Profile", secondary=accompanists_entries, back_populates="accompanies_entries"
    )
    repertoire: Mapped[List["Repertoire"]] = relationship(
        "Repertoire", secondary=entry_repertoire, back_populates="used_in_entries"
    )
    timestamp: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    comments: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    class_id: Mapped[int] = mapped_column(Integer, ForeignKey('classes.id'))
    festival_class: Mapped["FestivalClass"] = relationship("FestivalClass", back_populates="entries")

    # Each entry is connected to one season
    season_id: Mapped[int] = mapped_column(Integer, ForeignKey('seasons.id'))
    season: Mapped["Season"] = relationship("Season", back_populates="entries")


class Repertoire(db.Model):
    _tablename__ = 'repertoire'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    composer: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    level: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    discipline: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    festival_classes: Mapped[List["FestivalClass"]] = relationship(
        "FestivalClass", secondary=class_repertoire, back_populates="test_pieces"
    )

    used_in_entries: Mapped[List["Entry"]] = relationship(
        "Entry", secondary=entry_repertoire, back_populates="repertoire"
    )

    # Each repertoire is connected to one festival and is available for all that festival's seasons
    season_id: Mapped[int] = mapped_column(Integer, ForeignKey('seasons.id'))
    season: Mapped["Season"] = relationship("Season", back_populates="repertoire")


class School(db.Model):
    __tablename__ = 'schools'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    notes: Mapped[Optional[int]] = mapped_column(String, nullable=True)
     
    contacts: Mapped[list[Profile]] = relationship(
        "Profile", secondary=schools_contacts, back_populates="contact_for_schools"
    )

    students_or_groups: Mapped[list[Profile]] = relationship(
        "Profile", secondary=schools_participants, back_populates="attends_schools"
    )

    teachers: Mapped[list[Profile]] = relationship(
        "Profile", secondary=schools_teachers, back_populates="teaches_at_schools"
    )

    seasons: Mapped[List["Season"]] = relationship(
        "Season", secondary=schools_seasons, back_populates="schools")
