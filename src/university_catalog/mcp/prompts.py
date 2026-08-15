from mcp.server.fastmcp import FastMCP


def course_comparison_template(course_code_1: str, course_code_2: str) -> str:
    """
    Compare two courses and provide a detailed analysis.

    Args:
        course_code_1: First course code to compare (e.g., 'CS101')
        course_code_2: Second course code to compare (e.g., 'CS102')
    """
    return """Compare the following two courses in detail:

Course 1: {{course_code_1}}
Course 2: {{course_code_2}}

Please provide a comparison covering:
1. **Title & Credits** - Compare course titles and credit hours
2. **Descriptions** - Analyze the content and focus of each course
3. **Prerequisites** - Compare prerequisite requirements and chains
4. **Department** - Which departments offer these courses
5. **Instructors** - Who typically teaches each course
6. **Key Differences** - What makes these courses distinct
7. **Similarities** - What concepts or skills overlap
8. **Recommended Audience** - Which students should take which course
9. **Course Sequence** - Whether they should be taken in order or can be taken independently

Be specific and use information from the course catalog."""


def course_advisor(student_goals: str, completed_courses: str) -> str:
    """
    Academic advising prompt for course planning.

    Args:
        student_goals: The student's academic and career goals
        completed_courses: Comma-separated list of courses already completed
    """
    return f"""You are an academic advisor for a university. A student has come to you for course planning advice.

Student Goals: {student_goals}
Completed Courses: {completed_courses}

Using the university course catalog, provide:
1. Recommended next courses based on prerequisites and goals
2. Potential course sequences for their intended major/track
3. Any prerequisite gaps they need to fill
4. Elective suggestions that align with their goals
5. Workload considerations for the upcoming semester

Reference specific courses from the catalog by their course codes and explain your reasoning."""


def register_prompts(mcp: FastMCP):
    mcp.prompt(
        name="course_comparison_template",
        description="Template for comparing two courses side by side, analyzing their differences and similarities.",
    )(course_comparison_template)

    mcp.prompt(
        name="course_advisor",
        description="Act as an academic advisor to help students plan their course schedule.",
    )(course_advisor)
