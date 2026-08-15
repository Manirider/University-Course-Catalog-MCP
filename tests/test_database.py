import pytest
from sqlalchemy import inspect
from university_catalog.database import init_db, get_engine
from university_catalog.models import Department, Instructor, Course, Prerequisite, Base
from data.seed import seed_database


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    init_db()
    seed_database()
    yield


def test_tables_exist(setup_database):
    engine = get_engine()
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    assert "departments" in tables
    assert "instructors" in tables
    assert "courses" in tables
    assert "prerequisites" in tables


def test_departments_table(setup_database):
    engine = get_engine()
    inspector = inspect(engine)
    columns = {col["name"] for col in inspector.get_columns("departments")}
    
    assert "id" in columns
    assert "name" in columns
    assert "code" in columns
    
    indexes = inspector.get_indexes("departments")
    index_columns = set()
    for idx in indexes:
        index_columns.update(idx["column_names"])
    assert "code" in index_columns


def test_instructors_table(setup_database):
    engine = get_engine()
    inspector = inspect(engine)
    columns = {col["name"] for col in inspector.get_columns("instructors")}
    
    assert "id" in columns
    assert "name" in columns
    assert "email" in columns
    assert "office" in columns
    assert "department_id" in columns
    
    fks = inspector.get_foreign_keys("instructors")
    assert any(fk["referred_table"] == "departments" for fk in fks)
    
    indexes = inspector.get_indexes("instructors")
    index_columns = set()
    for idx in indexes:
        index_columns.update(idx["column_names"])
    assert "name" in index_columns


def test_courses_table(setup_database):
    engine = get_engine()
    inspector = inspect(engine)
    columns = {col["name"] for col in inspector.get_columns("courses")}
    
    assert "id" in columns
    assert "course_code" in columns
    assert "title" in columns
    assert "description" in columns
    assert "credits" in columns
    assert "instructor_id" in columns
    assert "department_id" in columns
    
    fks = inspector.get_foreign_keys("courses")
    referred_tables = {fk["referred_table"] for fk in fks}
    assert "instructors" in referred_tables
    assert "departments" in referred_tables
    
    indexes = inspector.get_indexes("courses")
    index_columns = set()
    for idx in indexes:
        index_columns.update(idx["column_names"])
    assert "course_code" in index_columns
    assert "title" in index_columns
    assert "department_id" in index_columns
    assert "instructor_id" in index_columns


def test_prerequisites_table(setup_database):
    engine = get_engine()
    inspector = inspect(engine)
    columns = {col["name"] for col in inspector.get_columns("prerequisites")}
    
    assert "course_id" in columns
    assert "prerequisite_id" in columns
    
    pks = inspector.get_pk_constraint("prerequisites")
    assert set(pks["constrained_columns"]) == {"course_id", "prerequisite_id"}
    
    fks = inspector.get_foreign_keys("prerequisites")
    referred_tables = {fk["referred_table"] for fk in fks}
    assert "courses" in referred_tables
    
    indexes = inspector.get_indexes("prerequisites")
    index_columns = set()
    for idx in indexes:
        index_columns.update(idx["column_names"])
    assert "course_id" in index_columns
    assert "prerequisite_id" in index_columns


def test_row_counts(setup_database):
    from university_catalog.database import get_session_factory
    
    SessionLocal = get_session_factory()
    session = SessionLocal()
    
    dept_count = session.query(Department).count()
    inst_count = session.query(Instructor).count()
    course_count = session.query(Course).count()
    prereq_count = session.query(Prerequisite).count()
    
    session.close()
    
    assert dept_count >= 5
    assert inst_count >= 5
    assert course_count >= 15
    assert prereq_count >= 10


def test_unique_course_codes(setup_database):
    from university_catalog.database import get_session_factory
    
    SessionLocal = get_session_factory()
    session = SessionLocal()
    
    codes = session.query(Course.course_code).all()
    course_codes = [c[0] for c in codes]
    
    session.close()
    
    assert len(course_codes) == len(set(course_codes))


def test_foreign_key_integrity(setup_database):
    from university_catalog.database import get_session_factory
    
    SessionLocal = get_session_factory()
    session = SessionLocal()
    
    courses = session.query(Course).all()
    for course in courses:
        assert session.query(Instructor).filter(Instructor.id == course.instructor_id).first() is not None
        assert session.query(Department).filter(Department.id == course.department_id).first() is not None
    
    prereqs = session.query(Prerequisite).all()
    for prereq in prereqs:
        assert session.query(Course).filter(Course.id == prereq.course_id).first() is not None
        assert session.query(Course).filter(Course.id == prereq.prerequisite_id).first() is not None
    
    instructors = session.query(Instructor).all()
    for inst in instructors:
        assert session.query(Department).filter(Department.id == inst.department_id).first() is not None
    
    session.close()


def test_no_self_prerequisites(setup_database):
    from university_catalog.database import get_session_factory
    
    SessionLocal = get_session_factory()
    session = SessionLocal()
    
    prereqs = session.query(Prerequisite).filter(Prerequisite.course_id == Prerequisite.prerequisite_id).all()
    session.close()
    
    assert len(prereqs) == 0


def test_no_prerequisite_cycles(setup_database):
    from university_catalog.database import get_session_factory
    import networkx as nx
    
    SessionLocal = get_session_factory()
    session = SessionLocal()
    
    prereqs = session.query(Prerequisite).all()
    session.close()
    
    G = nx.DiGraph()
    for p in prereqs:
        G.add_edge(p.prerequisite_id, p.course_id)
    
    assert nx.is_directed_acyclic_graph(G)