from university_catalog.database import get_db_session
from university_catalog.repositories import InstructorRepository
from university_catalog.schemas import LookupInstructorResult


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
                name=instructor.name,  # type: ignore[arg-type]
                email=instructor.email,  # type: ignore[arg-type]
                department_name=instructor.department.name,  # type: ignore[arg-type]
            )
