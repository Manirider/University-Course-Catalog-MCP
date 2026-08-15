from typing import Optional
from university_catalog.schemas import LookupInstructorResult
from university_catalog.repositories import InstructorRepository
from university_catalog.database import get_db_session


class InstructorService:
    def lookup_instructor(self, instructor_name: str) -> LookupInstructorResult:
        with get_db_session() as session:
            repo = InstructorRepository(session)
            instructor = repo.get_by_name(instructor_name)
            
            if not instructor:
                return LookupInstructorResult(
                    name="",
                    email="",
                    department_name="",
                )
            
            return LookupInstructorResult(
                name=instructor.name,
                email=instructor.email,
                department_name=instructor.department.name,
            )