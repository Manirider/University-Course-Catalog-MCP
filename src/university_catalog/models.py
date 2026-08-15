from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False, unique=True, index=True)

    instructors = relationship("Instructor", back_populates="department")
    courses = relationship("Course", back_populates="department")

    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}', code='{self.code}')>"


class Instructor(Base):
    __tablename__ = "instructors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    office = Column(String(255), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)

    department = relationship("Department", back_populates="instructors")
    courses = relationship("Course", back_populates="instructor")

    __table_args__ = (Index("ix_instructors_name", "name"),)

    def __repr__(self):
        return f"<Instructor(id={self.id}, name='{self.name}', email='{self.email}')>"


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_code = Column(String(50), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    credits = Column(Integer, nullable=False)
    instructor_id = Column(Integer, ForeignKey("instructors.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)

    instructor = relationship("Instructor", back_populates="courses")
    department = relationship("Department", back_populates="courses")
    prerequisites = relationship(
        "Course",
        secondary="prerequisites",
        primaryjoin="Course.id==Prerequisite.course_id",
        secondaryjoin="Course.id==Prerequisite.prerequisite_id",
        back_populates="dependents",
    )
    dependents = relationship(
        "Course",
        secondary="prerequisites",
        primaryjoin="Course.id==Prerequisite.prerequisite_id",
        secondaryjoin="Course.id==Prerequisite.course_id",
        back_populates="prerequisites",
    )

    __table_args__ = (
        Index("ix_courses_course_code", "course_code"),
        Index("ix_courses_title", "title"),
        Index("ix_courses_department_id", "department_id"),
        Index("ix_courses_instructor_id", "instructor_id"),
    )

    def __repr__(self):
        return f"<Course(id={self.id}, course_code='{self.course_code}', title='{self.title}')>"


class Prerequisite(Base):
    __tablename__ = "prerequisites"

    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)
    prerequisite_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)

    __table_args__ = (
        Index("ix_prerequisites_course_id", "course_id"),
        Index("ix_prerequisites_prerequisite_id", "prerequisite_id"),
    )

    def __repr__(self):
        return f"<Prerequisite(course_id={self.course_id}, prerequisite_id={self.prerequisite_id})>"
