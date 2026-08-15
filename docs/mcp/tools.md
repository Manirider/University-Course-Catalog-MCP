# MCP Tools Reference

## Overview

This server exposes 4 tools via the MCP protocol. All tools return structured JSON responses with automatic validation.

---

## `search_courses`

Search the course catalog by keyword across course codes, titles, and descriptions.

### Input

```typescript
interface SearchCoursesInput {
  query: string;                    // Required, 1-200 chars
  department_code?: string;         // Optional, max 50 chars
}
```

### Output

```typescript
interface SearchCourseResult {
  course_code: string;
  title: string;
  credits: number;
}
```

Returns: `SearchCourseResult[]`

### Examples

=== "Basic Search"
    ```typescript
    await mcp.callTool("search_courses", { query: "programming" });
    ```
    **Response:**
    ```json
    [
      {"course_code": "CS101", "title": "Introduction to Programming", "credits": 3},
      {"course_code": "CS202", "title": "Object-Oriented Programming", "credits": 3},
      {"course_code": "CS301", "title": "Algorithms", "credits": 4}
    ]
    ```

=== "With Department Filter"
    ```typescript
    await mcp.callTool("search_courses", { 
      query: "data", 
      department_code: "CS" 
    });
    ```
    **Response:**
    ```json
    [
      {"course_code": "CS102", "title": "Data Structures", "credits": 3},
      {"course_code": "CS201", "title": "Database Systems", "credits": 3}
    ]
    ```

=== "Course Code Search"
    ```typescript
    await mcp.callTool("search_courses", { query: "CS301" });
    ```
    **Response:**
    ```json
    [{"course_code": "CS301", "title": "Algorithms", "credits": 4}]
    ```

### Behavior

- **Case-insensitive** matching
- **Partial matches** on course_code, title, description
- **Department filter** matches department code (case-insensitive)
- **Deterministic ordering** by course_code
- **Empty results** returns `[]`
- **Empty query** returns error: `"Query parameter is required"`

---

## `get_prerequisites`

Retrieve **direct** (non-transitive) prerequisites for a specific course.

### Input

```typescript
interface GetPrerequisitesInput {
  course_code: string;  // Required, 1-50 chars
}
```

### Output

```typescript
interface GetPrerequisitesResult {
  course_code: string;
  prerequisites: PrerequisiteCourse[];
}

interface PrerequisiteCourse {
  course_code: string;
  title: string;
}
```

### Examples

=== "Course with Prerequisites"
    ```typescript
    await mcp.callTool("get_prerequisites", { course_code: "CS301" });
    ```
    **Response:**
    ```json
    {
      "course_code": "CS301",
      "prerequisites": [
        {"course_code": "CS102", "title": "Data Structures"}
      ]
    }
    ```

=== "Course without Prerequisites"
    ```typescript
    await mcp.callTool("get_prerequisites", { course_code: "CS101" });
    ```
    **Response:**
    ```json
    {
      "course_code": "CS101",
      "prerequisites": []
    }
    ```

=== "Nonexistent Course"
    ```typescript
    await mcp.callTool("get_prerequisites", { course_code: "INVALID" });
    ```
    **Response:**
    ```json
    {"error": "Course not found"}
    ```

### Behavior

- **Case-insensitive** course code lookup
- **Whitespace normalization** (trim)
- Returns **direct prerequisites only** (not transitive)
- **Deterministic ordering** by course_code
- Returns error for nonexistent courses

---

## `lookup_instructor`

Find an instructor by name with contact information.

### Input

```typescript
interface LookupInstructorInput {
  instructor_name: string;  // Required, 1-255 chars
}
```

### Output

```typescript
interface LookupInstructorResult {
  name: string;
  email: string;
  department_name: string;
}
```

### Examples

=== "Valid Instructor"
    ```typescript
    await mcp.callTool("lookup_instructor", { 
      instructor_name: "Dr. Alice Smith" 
    });
    ```
    **Response:**
    ```json
    {
      "name": "Dr. Alice Smith",
      "email": "alice.smith@university.edu",
      "department_name": "Computer Science"
    }
    ```

=== "Case Insensitive"
    ```typescript
    await mcp.callTool("lookup_instructor", { 
      instructor_name: "dr. alice smith" 
    });
    ```
    **Response:** Same as above

=== "Whitespace Tolerance"
    ```typescript
    await mcp.callTool("lookup_instructor", { 
      instructor_name: "  Dr. Alice Smith  " 
    });
    ```
    **Response:** Same as above

=== "Nonexistent Instructor"
    ```typescript
    await mcp.callTool("lookup_instructor", { 
      instructor_name: "Dr. Nobody" 
    });
    ```
    **Response:**
    ```json
    {"error": "Instructor not found"}
    ```

### Behavior

- **Case-insensitive** name matching
- **Whitespace normalization** (trim)
- Returns **department name** (not code)
- Returns error for nonexistent instructors

---

## `get_prerequisite_graph`

Get the complete transitive prerequisite dependency graph for a course.

### Input

```typescript
interface PrerequisiteGraphInput {
  course_code: string;  // Required, 1-50 chars
}
```

### Output

```typescript
interface PrerequisiteGraphResult {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

interface GraphNode {
  id: string;  // course_code
}

interface GraphEdge {
  source: string;  // prerequisite course_code
  target: string;  // dependent course_code
}
```

### Examples

=== "Simple Chain (CS102)"
    ```typescript
    await mcp.callTool("get_prerequisite_graph", { course_code: "CS102" });
    ```
    **Response:**
    ```json
    {
      "nodes": [
        {"id": "CS101"},
        {"id": "CS102"}
      ],
      "edges": [
        {"source": "CS101", "target": "CS102"}
      ]
    }
    ```

=== "Multi-Level Chain (CS301)"
    ```typescript
    await mcp.callTool("get_prerequisite_graph", { course_code: "CS301" });
    ```
    **Response:**
    ```json
    {
      "nodes": [
        {"id": "CS101"},
        {"id": "CS102"},
        {"id": "CS301"}
      ],
      "edges": [
        {"source": "CS101", "target": "CS102"},
        {"source": "CS102", "target": "CS301"}
      ]
    }
    ```

=== "Complex Graph (AIML301)"
    ```typescript
    await mcp.callTool("get_prerequisite_graph", { course_code: "AIML301" });
    ```
    **Response:**
    ```json
    {
      "nodes": [
        {"id": "AIML201"},
        {"id": "AIML301"},
        {"id": "CS201"}
      ],
      "edges": [
        {"source": "AIML201", "target": "AIML301"},
        {"source": "CS201", "target": "AIML301"}
      ]
    }
    ```

=== "Nonexistent Course"
    ```typescript
    await mcp.callTool("get_prerequisite_graph", { course_code: "INVALID" });
    ```
    **Response:**
    ```json
    {"error": "Course not found"}
    ```

### Behavior

- **Case-insensitive** course code lookup
- **Whitespace normalization** (trim)
- Includes **requested course** in nodes
- Includes **all transitive prerequisites**
- **No duplicate nodes or edges**
- **Deterministic ordering** (nodes by course_code, edges by source then target)
- **Edge direction**: `source` = prerequisite, `target` = dependent
- Returns error for nonexistent courses

---

## Error Response Format

All tools return consistent error structure:

```json
{
  "error": "Human-readable error message"
}
```

Common errors:
- `"Query parameter is required"` — Empty search query
- `"Course not found"` — Invalid course code
- `"Instructor not found"` — Invalid instructor name

---

## Rate Limits

No built-in rate limiting. Consider adding at reverse proxy level for production.