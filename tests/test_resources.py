from university_catalog.database import get_session_factory
from university_catalog.mcp.resources import course_descriptions, department_directory
from university_catalog.models import Course, Department


class TestCourseDescriptionsResource:
    def test_resource_exists(self):
        result = course_descriptions()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_all_course_codes_present(self):
        result = course_descriptions()

        SessionLocal = get_session_factory()
        session = SessionLocal()
        courses = session.query(Course).all()
        session.close()

        for course in courses:
            assert f"[{course.course_code}]" in result

    def test_all_titles_present(self):
        result = course_descriptions()

        SessionLocal = get_session_factory()
        session = SessionLocal()
        courses = session.query(Course).all()
        session.close()

        for course in courses:
            assert course.title in result

    def test_all_descriptions_present(self):
        result = course_descriptions()

        SessionLocal = get_session_factory()
        session = SessionLocal()
        courses = session.query(Course).all()
        session.close()

        for course in courses:
            assert course.description in result

    def test_deterministic_order(self):
        result1 = course_descriptions()
        result2 = course_descriptions()

        assert result1 == result2


class TestDepartmentDirectoryResource:
    def test_resource_exists(self):
        result = department_directory()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_all_departments_present(self):
        result = department_directory()

        SessionLocal = get_session_factory()
        session = SessionLocal()
        departments = session.query(Department).all()
        session.close()

        for dept in departments:
            assert dept.name in result
            assert f"({dept.code})" in result

    def test_deterministic_order(self):
        result1 = department_directory()
        result2 = department_directory()

        assert result1 == result2
