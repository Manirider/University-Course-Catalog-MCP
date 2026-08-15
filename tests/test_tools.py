import pytest
from university_catalog.services import CourseService, InstructorService
from university_catalog.schemas import (
    SearchCoursesInput,
    GetPrerequisitesInput,
    LookupInstructorInput,
    PrerequisiteGraphInput,
)


class TestSearchCourses:
    def test_search_by_keyword(self):
        service = CourseService()
        results = service.search_courses("programming")
        
        assert len(results) > 0
        assert all(isinstance(r.course_code, str) for r in results)
        assert all(isinstance(r.title, str) for r in results)
        assert all(isinstance(r.credits, int) for r in results)
    
    def test_search_case_insensitive(self):
        service = CourseService()
        results_lower = service.search_courses("programming")
        results_upper = service.search_courses("PROGRAMMING")
        results_mixed = service.search_courses("Programming")
        
        assert len(results_lower) == len(results_upper) == len(results_mixed)
    
    def test_search_by_course_code(self):
        service = CourseService()
        results = service.search_courses("CS101")
        
        assert len(results) == 1
        assert results[0].course_code == "CS101"
    
    def test_search_by_title(self):
        service = CourseService()
        results = service.search_courses("Data Structures")
        
        assert len(results) == 1
        assert results[0].course_code == "CS102"
    
    def test_search_by_description(self):
        service = CourseService()
        results = service.search_courses("machine learning")
        
        assert len(results) > 0
        assert any("machine learning" in r.title.lower() or "machine learning" in r.course_code.lower() for r in results)
    
    def test_department_filter(self):
        service = CourseService()
        results = service.search_courses("programming", department_code="CS")
        
        assert all(r.course_code.startswith("CS") for r in results)
    
    def test_department_filter_case_insensitive(self):
        service = CourseService()
        results_cs = service.search_courses("", department_code="CS")
        results_cs_lower = service.search_courses("", department_code="cs")
        
        assert len(results_cs) == len(results_cs_lower)
        assert all(r.course_code.startswith("CS") for r in results_cs)
    
    def test_empty_results(self):
        service = CourseService()
        results = service.search_courses("nonexistentcourse12345")
        
        assert results == []
    
    def test_whitespace_normalization(self):
        service = CourseService()
        results = service.search_courses("  programming  ")
        results_trimmed = service.search_courses("programming")
        
        assert len(results) == len(results_trimmed)
    
    def test_deterministic_ordering(self):
        service = CourseService()
        results1 = service.search_courses("CS")
        results2 = service.search_courses("CS")
        
        codes1 = [r.course_code for r in results1]
        codes2 = [r.course_code for r in results2]
        
        assert codes1 == codes2
        assert codes1 == sorted(codes1)


class TestGetPrerequisites:
    def test_course_with_prerequisites(self):
        service = CourseService()
        result = service.get_prerequisites("CS301")
        
        assert result.course_code == "CS301"
        assert len(result.prerequisites) > 0
        assert all(hasattr(p, "course_code") for p in result.prerequisites)
        assert all(hasattr(p, "title") for p in result.prerequisites)
    
    def test_course_without_prerequisites(self):
        service = CourseService()
        result = service.get_prerequisites("CS101")
        
        assert result.course_code == "CS101"
        assert result.prerequisites == []
    
    def test_unknown_course(self):
        service = CourseService()
        result = service.get_prerequisites("NONEXISTENT")
        
        assert result.course_code == "NONEXISTENT"
        assert result.prerequisites == []
    
    def test_deterministic_ordering(self):
        service = CourseService()
        result1 = service.get_prerequisites("CS301")
        result2 = service.get_prerequisites("CS301")
        
        codes1 = [p.course_code for p in result1.prerequisites]
        codes2 = [p.course_code for p in result2.prerequisites]
        
        assert codes1 == codes2
        assert codes1 == sorted(codes1)


class TestLookupInstructor:
    def test_valid_instructor(self):
        service = InstructorService()
        result = service.lookup_instructor("Dr. Alice Smith")
        
        assert result.name == "Dr. Alice Smith"
        assert result.email == "alice.smith@university.edu"
        assert result.department_name == "Computer Science"
    
    def test_case_insensitive_lookup(self):
        service = InstructorService()
        result1 = service.lookup_instructor("Dr. Alice Smith")
        result2 = service.lookup_instructor("dr. alice smith")
        result3 = service.lookup_instructor("  Dr. Alice Smith  ")
        
        assert result1.name == result2.name == result3.name
    
    def test_unknown_instructor(self):
        service = InstructorService()
        result = service.lookup_instructor("Dr. Nonexistent")
        
        assert result.name == ""
        assert result.email == ""
        assert result.department_name == ""


class TestPrerequisiteGraph:
    def test_single_level_chain(self):
        service = CourseService()
        result = service.get_prerequisite_graph("CS102")
        
        assert len(result.nodes) == 2
        node_ids = {n.id for n in result.nodes}
        assert "CS101" in node_ids
        assert "CS102" in node_ids
        
        assert len(result.edges) == 1
        assert result.edges[0].source == "CS101"
        assert result.edges[0].target == "CS102"
    
    def test_multi_level_chain(self):
        service = CourseService()
        result = service.get_prerequisite_graph("CS301")
        
        node_ids = {n.id for n in result.nodes}
        assert "CS101" in node_ids
        assert "CS102" in node_ids
        assert "CS301" in node_ids
        
        edge_pairs = {(e.source, e.target) for e in result.edges}
        assert ("CS101", "CS102") in edge_pairs
        assert ("CS102", "CS301") in edge_pairs
    
    def test_edge_direction_correctness(self):
        service = CourseService()
        result = service.get_prerequisite_graph("CS301")
        
        for edge in result.edges:
            assert edge.source != edge.target
    
    def test_unknown_course(self):
        service = CourseService()
        result = service.get_prerequisite_graph("NONEXISTENT")
        
        assert result.nodes == []
        assert result.edges == []
    
    def test_no_unrelated_nodes(self):
        service = CourseService()
        result = service.get_prerequisite_graph("CS301")
        
        node_ids = {n.id for n in result.nodes}
        assert "AIML201" not in node_ids
        assert "DS201" not in node_ids
    
    def test_deterministic_ordering(self):
        service = CourseService()
        result1 = service.get_prerequisite_graph("CS301")
        result2 = service.get_prerequisite_graph("CS301")
        
        nodes1 = [n.id for n in result1.nodes]
        nodes2 = [n.id for n in result2.nodes]
        edges1 = [(e.source, e.target) for e in result1.edges]
        edges2 = [(e.source, e.target) for e in result2.edges]
        
        assert nodes1 == nodes2
        assert edges1 == edges2