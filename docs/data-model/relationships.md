# Data Relationships

## Overview

The catalog uses a relational model with explicit foreign keys and many-to-many relationships for prerequisites.

## Relationship Map

```
Department (1) ←→ (N) Instructor
Department (1) ←→ (N) Course
Instructor (1) ←→ (N) Course
Course (N) ←→ (M) Course (via Prerequisite)
```

## Detailed Relationships

### Department ↔ Instructor

**One-to-Many**: One department has many instructors.

```python
# Department → Instructors
department.instructors  # List[Instructor]

# Instructor → Department
instructor.department   # Department
```

**Foreign Key**: `instructors.department_id` → `departments.id`

**Cascade**: Department deletion cascades to instructors (SET NULL not used, would require handling)

### Department ↔ Course

**One-to-Many**: One department offers many courses.

```python
# Department → Courses
department.courses  # List[Course]

# Course → Department
course.department   # Department
```

**Foreign Key**: `courses.department_id` → `departments.id`

### Instructor ↔ Course

**One-to-Many**: One instructor teaches many courses.

```python
# Instructor → Courses
instructor.courses  # List[Course]

# Course → Instructor
course.instructor   # Instructor
```

**Foreign Key**: `courses.instructor_id` → `instructors.id`

### Course ↔ Course (Prerequisites)

**Many-to-Many**: Courses can have multiple prerequisites and be prerequisites for multiple courses.

```python
# Direct prerequisites (courses required before this one)
course.prerequisites  # List[Course]

# Dependents (courses that require this one)
course.dependents     # List[Course]
```

**Join Table**: `prerequisites`
- `course_id` → dependent course
- `prerequisite_id` → required course

**Direction**: `prerequisite_id` → `course_id` (prerequisite → dependent)

## Navigation Examples

### Get All Courses in a Department

```python
# Via relationship
cs_dept = session.query(Department).filter(Department.code == "CS").first()
cs_courses = cs_dept.courses  # All CS courses

# Via query
cs_courses = session.query(Course).join(Department).filter(Department.code == "CS").all()
```

### Get Instructor's Department

```python
instructor = session.query(Instructor).filter(Instructor.name == "Dr. Alice Smith").first()
dept_name = instructor.department.name  # "Computer Science"
```

### Get Course Prerequisites (Direct)

```python
course = session.query(Course).filter(Course.course_code == "CS301").first()
direct_prereqs = course.prerequisites  # [CS102]
```

### Get Course Dependents (Direct)

```python
course = session.query(Course).filter(Course.course_code == "CS101").first()
direct_dependents = course.dependents  # [CS102, CS201, CS202]
```

### Get Full Prerequisite Chain (Transitive)

```python
def get_all_prerequisites(course: Course) -> List[Course]:
    """Recursively get all transitive prerequisites."""
    visited = set()
    result = []
    
    def traverse(c: Course):
        if c.id in visited:
            return
        visited.add(c.id)
        for prereq in c.prerequisites:
            traverse(prereq)
            result.append(prereq)
    
    traverse(course)
    return result

# Usage
cs301 = session.query(Course).filter(Course.course_code == "CS301").first()
all_prereqs = get_all_prerequisites(cs301)
# Returns: [CS101, CS102] (in dependency order)
```

### Get Full Dependent Chain (Transitive)

```python
def get_all_dependents(course: Course) -> List[Course]:
    """Recursively get all transitive dependents."""
    visited = set()
    result = []
    
    def traverse(c: Course):
        if c.id in visited:
            return
        visited.add(c.id)
        for dependent in c.dependents:
            traverse(dependent)
            result.append(dependent)
    
    traverse(course)
    return result

# Usage
cs101 = session.query(Course).filter(Course.course_code == "CS101").first()
all_dependents = get_all_dependents(cs101)
# Returns: [CS102, CS201, CS202, CS301, CS302, DS301, AIML301]
```

## Prerequisite Graph Representation

### NetworkX Graph

```python
import networkx as nx

# Build directed graph
G = nx.DiGraph()

# Add all courses as nodes
for course in session.query(Course).all():
    G.add_node(course.course_code, title=course.title)

# Add prerequisite edges (prerequisite → dependent)
for prereq in session.query(Prerequisite).all():
    prereq_course = session.query(Course).get(prereq.prerequisite_id)
    dep_course = session.query(Course).get(prereq.course_id)
    G.add_edge(prereq_course.course_code, dep_course.course_code)

# Verify DAG (no cycles)
assert nx.is_directed_acyclic_graph(G)

# Get prerequisite chain for a course
def get_prerequisite_chain(graph: nx.DiGraph, target: str) -> List[str]:
    """Get all nodes that can reach target (all prerequisites)."""
    return list(nx.ancestors(graph, target))

# Get dependent chain for a course
def get_dependent_chain(graph: nx.DiGraph, source: str) -> List[str]:
    """Get all nodes reachable from source (all dependents)."""
    return list(nx.descendants(graph, source))

# Usage
chain = get_prerequisite_chain(G, "CS301")
# Returns: {"CS101", "CS102"}

dependents = get_dependent_chain(G, "CS101")
# Returns: {"CS102", "CS201", "CS202", "CS301", "CS302", "DS301", "AIML301"}
```

## Data Integrity Rules

### Enforced by Database

1. **Foreign Keys** — All relationships validated
2. **Unique Constraints** — No duplicate course codes or department codes
3. **Not Null** — Required fields always populated
4. **No Self-Prerequisites** — `course_id != prerequisite_id`

### Enforced by Application

1. **No Cycles** — Validated on seed and can be checked anytime
2. **Referential Integrity** — Orphaned records prevented
3. **Deterministic Ordering** — Queries use explicit ORDER BY

## Query Patterns

### Eager Loading (Avoid N+1)

```python
from sqlalchemy.orm import joinedload, selectinload

# Load courses with department and instructor
courses = session.query(Course).options(
    joinedload(Course.department),
    joinedload(Course.instructor)
).all()

# Load course with prerequisites
course = session.query(Course).options(
    selectinload(Course.prerequisites).joinedload(Course.department)
).filter(Course.course_code == "CS301").first()
```

### Common Queries

```python
# Search courses by keyword
courses = session.query(Course).join(Department).filter(
    or_(
        Course.course_code.ilike(f"%{query}%"),
        Course.title.ilike(f"%{query}%"),
        Course.description.ilike(f"%{query}%")
    )
).all()

# Courses by department
courses = session.query(Course).join(Department).filter(
    Department.code == "CS"
).all()

# Instructor by name (case-insensitive)
instructor = session.query(Instructor).filter(
    func.lower(Instructor.name) == name.lower()
).first()
```

## Performance Considerations

| Operation | Complexity | Optimization |
|-----------|------------|--------------|
| Course lookup by code | O(log n) | Unique index |
| Department courses | O(log n + m) | FK index + limit |
| Direct prerequisites | O(log n + p) | FK index on join table |
| Transitive closure | O(V + E) | NetworkX / recursive CTE |
| Instructor lookup | O(log n) | Name index |

## Validation Queries

```python
# Check for orphaned courses
orphans = session.query(Course).filter(
    ~Course.department_id.in_(session.query(Department.id))
).all()

# Check for orphaned instructors
orphans = session.query(Instructor).filter(
    ~Instructor.department_id.in_(session.query(Department.id))
).all()

# Check for invalid prerequisites
invalid = session.query(Prerequisite).filter(
    or_(
        ~Prerequisite.course_id.in_(session.query(Course.id)),
        ~Prerequisite.prerequisite_id.in_(session.query(Course.id))
    )
).all()

# Check for cycles
import networkx as nx
G = nx.DiGraph()
for p in session.query(Prerequisite).all():
    G.add_edge(p.prerequisite_id, p.course_id)
assert nx.is_directed_acyclic_graph(G)
```