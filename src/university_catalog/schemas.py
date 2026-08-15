from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from typing import Annotated


class SearchCoursesInput(BaseModel):
    query: Annotated[str, Field(min_length=1, max_length=200, description="Search query for course code, title, or description")]
    department_code: Annotated[Optional[str], Field(default=None, max_length=50, description="Optional department code to filter results")] = None

    class Config:
        json_schema_extra = {
            "example": {"query": "programming", "department_code": "CS"}
        }


class SearchCourseResult(BaseModel):
    course_code: Annotated[str, Field(description="Unique course code")]
    title: Annotated[str, Field(description="Course title")]
    credits: Annotated[int, Field(description="Number of credits")]

    class Config:
        json_schema_extra = {
            "example": {"course_code": "CS101", "title": "Introduction to Programming", "credits": 3}
        }


class GetPrerequisitesInput(BaseModel):
    course_code: Annotated[str, Field(min_length=1, max_length=50, description="Course code to get prerequisites for")]

    class Config:
        json_schema_extra = {
            "example": {"course_code": "CS301"}
        }


class PrerequisiteCourse(BaseModel):
    course_code: Annotated[str, Field(description="Course code of the prerequisite")]
    title: Annotated[str, Field(description="Title of the prerequisite course")]

    class Config:
        json_schema_extra = {
            "example": {"course_code": "CS102", "title": "Data Structures"}
        }


class GetPrerequisitesResult(BaseModel):
    course_code: Annotated[str, Field(description="Course code that was queried")]
    prerequisites: Annotated[List[PrerequisiteCourse], Field(description="List of direct prerequisite courses")]

    class Config:
        json_schema_extra = {
            "example": {"course_code": "CS301", "prerequisites": [{"course_code": "CS102", "title": "Data Structures"}]}
        }


class LookupInstructorInput(BaseModel):
    instructor_name: Annotated[str, Field(min_length=1, max_length=255, description="Instructor name to search for")]

    class Config:
        json_schema_extra = {
            "example": {"instructor_name": "Dr. Alice Smith"}
        }


class LookupInstructorResult(BaseModel):
    name: Annotated[str, Field(description="Instructor name")]
    email: Annotated[str, Field(description="Instructor email")]
    department_name: Annotated[str, Field(description="Department name")]

    class Config:
        json_schema_extra = {
            "example": {"name": "Dr. Alice Smith", "email": "alice.smith@university.edu", "department_name": "Computer Science"}
        }


class ErrorResponse(BaseModel):
    error: Annotated[str, Field(description="Error message")]

    class Config:
        json_schema_extra = {
            "example": {"error": "Instructor not found"}
        }


class PrerequisiteGraphInput(BaseModel):
    course_code: Annotated[str, Field(min_length=1, max_length=50, description="Course code to get prerequisite graph for")]

    class Config:
        json_schema_extra = {
            "example": {"course_code": "CS301"}
        }


class GraphNode(BaseModel):
    id: Annotated[str, Field(description="Course code")]

    class Config:
        json_schema_extra = {
            "example": {"id": "CS101"}
        }


class GraphEdge(BaseModel):
    source: Annotated[str, Field(description="Prerequisite course code")]
    target: Annotated[str, Field(description="Dependent course code")]

    class Config:
        json_schema_extra = {
            "example": {"source": "CS101", "target": "CS102"}
        }


class PrerequisiteGraphResult(BaseModel):
    nodes: Annotated[List[GraphNode], Field(description="All courses in the prerequisite graph")]
    edges: Annotated[List[GraphEdge], Field(description="Prerequisite relationships (source -> target)")]

    class Config:
        json_schema_extra = {
            "example": {
                "nodes": [{"id": "CS101"}, {"id": "CS102"}, {"id": "CS301"}],
                "edges": [{"source": "CS101", "target": "CS102"}, {"source": "CS102", "target": "CS301"}]
            }
        }


class HealthResponse(BaseModel):
    status: Annotated[str, Field(description="Health status")]
    database: Annotated[Optional[str], Field(default=None, description="Database connection status")] = None

    class Config:
        json_schema_extra = {
            "example": {"status": "healthy", "database": "connected"}
        }