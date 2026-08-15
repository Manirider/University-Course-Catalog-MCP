from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional

from university_catalog.models import Course, Department, Prerequisite


class CourseRepository:
    def __init__(self, session: Session):
        self.session = session

    def search_courses(self, query: str, department_code: Optional[str] = None) -> List[Course]:
        normalized_query = f"%{query.strip().lower()}%"
        
        stmt = self.session.query(Course).join(Department).filter(
            or_(
                func.lower(Course.course_code).like(normalized_query),
                func.lower(Course.title).like(normalized_query),
                func.lower(Course.description).like(normalized_query),
            )
        )
        
        if department_code:
            stmt = stmt.filter(func.lower(Department.code) == department_code.strip().lower())
        
        return stmt.order_by(Course.course_code.asc()).all()

    def get_by_code(self, course_code: str) -> Optional[Course]:
        return self.session.query(Course).filter(
            func.lower(Course.course_code) == course_code.strip().lower()
        ).first()

    def get_all(self) -> List[Course]:
        return self.session.query(Course).order_by(Course.course_code.asc()).all()

    def get_direct_prerequisites(self, course_id: int) -> List[Course]:
        return self.session.query(Course).join(
            Prerequisite, Course.id == Prerequisite.prerequisite_id
        ).filter(Prerequisite.course_id == course_id).order_by(Course.course_code.asc()).all()

    def get_prerequisite_graph_data(self, course_code: str) -> List[Course]:
        start_course = self.get_by_code(course_code)
        if not start_course:
            return []
        
        visited = set()
        result = []
        
        def traverse(course: Course):
            if course.id in visited:
                return
            visited.add(course.id)
            result.append(course)
            for prereq in course.prerequisites:
                traverse(prereq)
        
        traverse(start_course)
        return result

    def get_prerequisite_edges(self, course_code: str) -> List[tuple]:
        courses = self.get_prerequisite_graph_data(course_code)
        course_ids = {c.id for c in courses}
        
        edges = self.session.query(Prerequisite).filter(
            Prerequisite.course_id.in_(course_ids),
            Prerequisite.prerequisite_id.in_(course_ids)
        ).all()
        
        return [(e.prerequisite_id, e.course_id) for e in edges]


class DepartmentRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Department]:
        return self.session.query(Department).order_by(Department.code.asc()).all()

    def get_by_code(self, code: str) -> Optional[Department]:
        return self.session.query(Department).filter(
            func.lower(Department.code) == code.strip().lower()
        ).first()


class InstructorRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_name(self, name: str) -> Optional["Instructor"]:
        from university_catalog.models import Instructor
        return self.session.query(Instructor).filter(
            func.lower(Instructor.name) == name.strip().lower()
        ).first()