import json

import pytest

from university_catalog.mcp.server import mcp_server


@pytest.mark.asyncio
async def test_mcp_tools_registered():
    tools = await mcp_server.list_tools()
    tool_names = {tool.name for tool in tools}
    expected_tools = {
        "search_courses",
        "get_prerequisites",
        "lookup_instructor",
        "get_prerequisite_graph",
    }
    assert expected_tools.issubset(tool_names)


@pytest.mark.asyncio
async def test_mcp_resources_registered():
    resources = await mcp_server.list_resources()
    resource_uris = {str(r.uri) for r in resources}
    expected_resources = {
        "resource://course_descriptions",
        "resource://department_directory",
    }
    assert expected_resources.issubset(resource_uris)


@pytest.mark.asyncio
async def test_mcp_prompts_registered():
    prompts = await mcp_server.list_prompts()
    prompt_names = {p.name for p in prompts}
    expected_prompts = {"course_comparison_template", "course_advisor"}
    assert expected_prompts.issubset(prompt_names)


@pytest.mark.asyncio
async def test_mcp_tool_search_courses():
    result = await mcp_server.call_tool("search_courses", {"query": "programming"})
    assert isinstance(result, list)
    assert len(result) > 0

    content_text = result[0].text
    courses = json.loads(content_text)

    assert isinstance(courses, list)
    assert len(courses) > 0
    assert all("course_code" in c for c in courses)
    assert all("title" in c for c in courses)
    assert all("credits" in c for c in courses)


@pytest.mark.asyncio
async def test_mcp_tool_get_prerequisites():
    result = await mcp_server.call_tool("get_prerequisites", {"course_code": "CS301"})
    assert isinstance(result, list)
    assert len(result) > 0

    content_text = result[0].text
    data = json.loads(content_text)

    assert "course_code" in data
    assert "prerequisites" in data
    assert data["course_code"] == "CS301"
    assert isinstance(data["prerequisites"], list)


@pytest.mark.asyncio
async def test_mcp_tool_lookup_instructor():
    result = await mcp_server.call_tool(
        "lookup_instructor", {"instructor_name": "Dr. Alice Smith"}
    )
    assert isinstance(result, list)
    assert len(result) > 0

    content_text = result[0].text
    data = json.loads(content_text)

    assert "name" in data
    assert "email" in data
    assert "department_name" in data
    assert data["name"] == "Dr. Alice Smith"


@pytest.mark.asyncio
async def test_mcp_tool_get_prerequisite_graph():
    result = await mcp_server.call_tool(
        "get_prerequisite_graph", {"course_code": "CS301"}
    )
    assert isinstance(result, list)
    assert len(result) > 0

    content_text = result[0].text
    data = json.loads(content_text)

    assert "nodes" in data
    assert "edges" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["edges"], list)

    node_ids = {n["id"] for n in data["nodes"]}
    assert "CS101" in node_ids
    assert "CS102" in node_ids
    assert "CS301" in node_ids


@pytest.mark.asyncio
async def test_mcp_resource_course_descriptions():
    result = await mcp_server.read_resource("resource://course_descriptions")
    assert isinstance(result, list)
    assert len(result) > 0

    content = result[0].content
    assert isinstance(content, str)
    assert len(content) > 0
    assert "CS101" in content
    assert "Introduction to Programming" in content


@pytest.mark.asyncio
async def test_mcp_resource_department_directory():
    result = await mcp_server.read_resource("resource://department_directory")
    assert isinstance(result, list)
    assert len(result) > 0

    content = result[0].content
    assert isinstance(content, str)
    assert len(content) > 0
    assert "Computer Science" in content
    assert "(CS)" in content


@pytest.mark.asyncio
async def test_mcp_prompt_course_comparison():
    result = await mcp_server.get_prompt(
        "course_comparison_template",
        {"course_code_1": "CS101", "course_code_2": "CS102"},
    )
    assert result.messages is not None
    assert len(result.messages) > 0

    content = result.messages[0].content.text
    assert "{{course_code_1}}" in content
    assert "{{course_code_2}}" in content
