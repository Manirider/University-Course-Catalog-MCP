from university_catalog.database import get_db_session
from university_catalog.repositories import CourseRepository
from university_catalog.schemas import (
    GetPrerequisitesResult,
    GraphEdge,
    GraphNode,
    PrerequisiteCourse,
    PrerequisiteGraphResult,
    SearchCourseResult,
)


class CourseService:
    def search_courses(
        self, query: str, department_code: str | None = None
    ) -> list[SearchCourseResult]:
        with get_db_session() as session:
            repo = CourseRepository(session)
            courses = repo.search_courses(query, department_code)
            return [
                SearchCourseResult(
                    course_code=c.course_code,  # type: ignore[arg-type]
                    title=c.title,  # type: ignore[arg-type]
                    credits=c.credits,  # type: ignore[arg-type]
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

            prereqs = repo.get_direct_prerequisites(course.id)  # type: ignore[arg-type]

            return GetPrerequisitesResult(
                course_code=course.course_code,  # type: ignore[arg-type]
                prerequisites=[
                    PrerequisiteCourse(
                        course_code=p.course_code,  # type: ignore[arg-type]
                        title=p.title,  # type: ignore[arg-type]
                    )
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
                GraphNode(id=c.course_code)  # type: ignore[arg-type]
                for c in sorted(courses, key=lambda x: x.course_code)
            ]

            edges = []
            for prereq_id, course_id in edges_data:
                if prereq_id in course_map and course_id in course_map:
                    edges.append(
                        GraphEdge(
                            source=course_map[prereq_id].course_code,  # type: ignore[arg-type]
                            target=course_map[course_id].course_code,  # type: ignore[arg-type]
                        )
                    )

            edges.sort(key=lambda e: (e.source, e.target))

            return PrerequisiteGraphResult(nodes=nodes, edges=edges)