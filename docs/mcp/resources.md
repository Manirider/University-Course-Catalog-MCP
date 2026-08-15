# MCP Resources Reference

## Overview

This server exposes 2 read-only resources via the MCP protocol. Resources provide structured access to catalog data without requiring tool invocation.

---

## `resource://course_descriptions`

Complete list of all course descriptions in the catalog.

### URI

```
resource://course_descriptions
```

### MIME Type

```
text/plain
```

### Content Format

Plain text with one course per entry:

```
[CS101] Introduction to Programming: A foundational course covering programming fundamentals, variables, control structures, functions, and basic data types using Python.

[CS102] Data Structures: Study of fundamental data structures including arrays, linked lists, stacks, queues, trees, and graphs with emphasis on algorithmic efficiency.

[CS201] Database Systems: Introduction to database design, relational models, SQL, normalization, transactions, and database management systems.

...
```

### Example Usage

```typescript
const result = await mcp.readResource("resource://course_descriptions");
console.log(result[0].content);
// Output: Full text with all 15 courses
```

### Properties

| Property | Value |
|----------|-------|
| Courses included | All 15 seeded courses |
| Ordering | By course_code (ascending) |
| Fields per course | course_code, title, description |
| Deterministic | Yes |

### Use Cases

- Bulk course catalog export
- Offline browsing
- LLM context injection for course recommendations
- Documentation generation

---

## `resource://department_directory`

Complete list of all departments in the university.

### URI

```
resource://department_directory
```

### MIME Type

```
text/plain
```

### Content Format

Plain text with one department per line:

```
Computer Science (CS)
Artificial Intelligence & Machine Learning (AIML)
Data Science (DS)
Information Technology (IT)
Mathematics (MATH)
```

### Example Usage

```typescript
const result = await mcp.readResource("resource://department_directory");
console.log(result[0].content);
// Output: All 5 departments
```

### Properties

| Property | Value |
|----------|-------|
| Departments included | All 5 seeded departments |
| Ordering | By department code (ascending) |
| Fields per department | name, code |
| Deterministic | Yes |

### Use Cases

- Department selection UI
- Filter options for course search
- Organizational reporting
- Navigation menus

---

## Resource Discovery

```typescript
// List all available resources
const resources = await mcp.listResources();
// Returns:
// [
//   { uri: "resource://course_descriptions", name: "course_descriptions", ... },
//   { uri: "resource://department_directory", name: "department_directory", ... }
// ]
```

## Reading Resources

```typescript
// Read single resource
const courseDesc = await mcp.readResource("resource://course_descriptions");
const deptDir = await mcp.readResource("resource://department_directory");

// Read multiple (sequential)
const [courses, depts] = await Promise.all([
  mcp.readResource("resource://course_descriptions"),
  mcp.readResource("resource://department_directory")
]);
```

## Caching

Resources are **read-only** and **deterministic**. Safe to cache:

```typescript
// Client-side caching example
let courseCache: string | null = null;

async function getCourseDescriptions() {
  if (!courseCache) {
    const result = await mcp.readResource("resource://course_descriptions");
    courseCache = result[0].content;
  }
  return courseCache;
}
```

## Refresh Behavior

Resources reflect current database state. To refresh:

1. Re-read the resource (always returns current data)
2. Or restart server (re-seeds database if empty)

---

## Comparison: Tools vs Resources

| Aspect | Tools | Resources |
|--------|-------|-----------|
| **Purpose** | Actions/queries | Data access |
| **Parameters** | Yes | No |
| **Mutating** | No (read-only) | No |
| **Caching** | Per-request | Long-term safe |
| **Discovery** | `listTools()` | `listResources()` |
| **Invocation** | `callTool()` | `readResource()` |

---

## Raw Content Access

For direct HTTP access (non-MCP):

```bash
# Not directly accessible via HTTP
# Must use MCP protocol at /mcp endpoint
```

Use MCP Inspector or compatible client to access resources.