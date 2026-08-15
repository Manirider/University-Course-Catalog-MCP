from university_catalog.mcp.prompts import course_comparison_template


class TestCourseComparisonTemplate:
    def test_prompt_exists(self):
        result = course_comparison_template("CS101", "CS102")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_required_placeholders(self):
        result = course_comparison_template("CS101", "CS102")

        assert "{{course_code_1}}" in result
        assert "{{course_code_2}}" in result

    def test_template_non_empty(self):
        result = course_comparison_template("CS101", "CS102")

        assert len(result.strip()) > 0

    def test_contains_comparison_sections(self):
        result = course_comparison_template("CS101", "CS102")

        sections = [
            "Title & Credits",
            "Descriptions",
            "Prerequisites",
            "Department",
            "Instructors",
            "Key Differences",
            "Similarities",
            "Recommended Audience",
            "Course Sequence",
        ]

        for section in sections:
            assert section in result
