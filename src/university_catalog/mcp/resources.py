from mcp.server.fastmcp import FastMCP
from university_catalog.database import get_db_session
from university_catalog.models import Course, Department
from university_catalog.repositories import DepartmentRepository


def course_descriptions() -> str:
    """Get all course descriptions."""
    with get_db_session() as session:
        courses = session.query(Course).order_by(Course.course_code.asc()).all()
        
        lines = []
        for course in courses:
            lines.append(
                f"[{course.course_code}] {course.title}: {course.description}"
            )
        
        return "\n\n".join(lines)


def department_directory() -> str:
    """Get all departments."""
    with get_db_session() as session:
        repo = DepartmentRepository(session)
        departments = repo.get_all()
        
        lines = []
        for dept in departments:
            lines.append(f"{dept.name} ({dept.code})")
        
        return "\n".join(lines)


def register_resources(mcp: FastMCP):
    mcp.resource(
        uri="resource://course_descriptions",
        name="course_descriptions",
        description="Complete list of all course descriptions in the catalog including course code, title, and full description.",
        mime_type="text/plain",
    )(course_descriptions)

    mcp.resource(
        uri="resource://department_directory",
        name="department_directory",
        description="Complete list of all departments in the university with their names and codes.",
        mime_type="text/plain",
    )(department_directory)