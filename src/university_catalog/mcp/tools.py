from mcp.server.fastmcp import FastMCP
from university_catalog.services import CourseService, InstructorService
from university_catalog.schemas import (
    SearchCoursesInput,
    GetPrerequisitesInput,
    LookupInstructorInput,
    PrerequisiteGraphInput,
    GetPrerequisitesResult,
    LookupInstructorResult,
    PrerequisiteGraphResult,
    ErrorResponse,
)
from typing import List, Union
import json


course_service = CourseService()
instructor_service = InstructorService()


def register_tools(mcp: FastMCP):
    @mcp.tool(
        name="search_courses",
        description=(
            "Searches the university course catalog using a case-insensitive keyword "
            "against course codes, titles, and descriptions. Optionally restricts "
            "results to a department code. Use this tool when you need to discover "
            "courses matching a topic, keyword, course code, or department. Returns "
            "a deterministic list containing course code, title, and credit count."
        ),
    )
    def search_courses(query: str, department_code: str | None = None) -> Union[str, ErrorResponse]:
        """
        Search for courses by keyword with optional department filtering.
        
        Args:
            query: Search term for course code, title, or description
            department_code: Optional department code to filter results (e.g., 'CS', 'AIML')
        """
        if not query or not query.strip():
            return ErrorResponse(error="Query parameter is required")
        results = course_service.search_courses(query, department_code)
        return json.dumps([r.model_dump() for r in results])

    @mcp.tool(
        name="get_prerequisites",
        description=(
            "Retrieves the direct prerequisites for a specific course. "
            "Returns only immediate prerequisites, not transitive ones. "
            "Use when you need to know what courses must be completed "
            "before taking a specific course. Returns course code and title "
            "for each prerequisite."
        ),
    )
    def get_prerequisites(course_code: str) -> Union[GetPrerequisitesResult, ErrorResponse]:
        """
        Get direct prerequisites for a course.
        
        Args:
            course_code: The course code to get prerequisites for (e.g., 'CS301')
        """
        from university_catalog.database import get_db_session
        from university_catalog.models import Course
        from sqlalchemy import func
        
        with get_db_session() as session:
            course = session.query(Course).filter(
                func.lower(Course.course_code) == course_code.strip().lower()
            ).first()
            if not course:
                return ErrorResponse(error="Course not found")
        
        result = course_service.get_prerequisites(course_code)
        return result

    @mcp.tool(
        name="lookup_instructor",
        description=(
            "Looks up an instructor by name using case-insensitive matching. "
            "Returns the instructor's name, email, and department name. "
            "Use when you need to find who teaches a course or get instructor contact information."
        ),
    )
    def lookup_instructor(instructor_name: str) -> Union[LookupInstructorResult, ErrorResponse]:
        """
        Look up an instructor by name.
        
        Args:
            instructor_name: The instructor's name to search for (e.g., 'Dr. Alice Smith')
        """
        result = instructor_service.lookup_instructor(instructor_name)
        if not result.name:
            return ErrorResponse(error="Instructor not found")
        return result

    @mcp.tool(
        name="get_prerequisite_graph",
        description=(
            "Returns the complete prerequisite dependency graph for a course, "
            "including all transitive prerequisites. The graph shows all courses "
            "that must be completed before taking the target course. Nodes represent "
            "courses and edges represent prerequisite relationships (source -> target "
            "means source is a prerequisite for target). Use when you need to understand "
            "the full prerequisite chain for a course."
        ),
    )
    def get_prerequisite_graph(course_code: str) -> Union[PrerequisiteGraphResult, ErrorResponse]:
        """
        Get the complete prerequisite graph for a course.
        
        Args:
            course_code: The course code to get the prerequisite graph for (e.g., 'CS301')
        """
        result = course_service.get_prerequisite_graph(course_code)
        if not result.nodes:
            return ErrorResponse(error="Course not found")
        return result