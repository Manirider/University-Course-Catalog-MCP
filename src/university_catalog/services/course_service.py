from typing import List, Optional
from university_catalog.schemas import (
    SearchCourseResult,
    GetPrerequisitesResult,
    PrerequisiteCourse,
    PrerequisiteGraphResult,
    GraphNode,
    GraphEdge,
)
from university_catalog.repositories import CourseRepository
from university_catalog.database import get_db_session


class CourseService:
    def search_courses(self, query: str, department_code: Optional[str] = None) -> List[SearchCourseResult]:
        with get_db_session() as session:
            repo = CourseRepository(session)
            courses = repo.search_courses(query, department_code)
            return [
                SearchCourseResult(
                    course_code=c.course_code,
                    title=c.title,
                    credits=c.credits,
                )
                for c in courses
            ]

    def get_prerequisites(self, course_code: str) -> GetPrerequisitesResult:
        with get_db_session() as session:
            repo = CourseRepository(session)
            course = repo.get_by_code(course_code)
            
            if not course:
                return GetPrerequisitesResult(
                    course_code=course_code.upper(),
                    prerequisites=[],
                )
            
            prereqs = repo.get_direct_prerequisites(course.id)
            
            return GetPrerequisitesResult(
                course_code=course.course_code,
                prerequisites=[
                    PrerequisiteCourse(course_code=p.course_code, title=p.title)
                    for p in prereqs
                ],
            )

    def get_prerequisite_graph(self, course_code: str) -> PrerequisiteGraphResult:
        with get_db_session() as session:
            repo = CourseRepository(session)
            course = repo.get_by_code(course_code)
            
            if not course:
                return PrerequisiteGraphResult(nodes=[], edges=[])
            
            courses = repo.get_prerequisite_graph_data(course_code)
            edges_data = repo.get_prerequisite_edges(course_code)
            
            course_map = {c.id: c for c in courses}
            
            nodes = [
                GraphNode(id=c.course_code)
                for c in sorted(courses, key=lambda x: x.course_code)
            ]
            
            edges = []
            for prereq_id, course_id in edges_data:
                if prereq_id in course_map and course_id in course_map:
                    edges.append(
                        GraphEdge(
                            source=course_map[prereq_id].course_code,
                            target=course_map[course_id].course_code,
                        )
                    )
            
            edges.sort(key=lambda e: (e.source, e.target))
            
            return PrerequisiteGraphResult(nodes=nodes, edges=edges)