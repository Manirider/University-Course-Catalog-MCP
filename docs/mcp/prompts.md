# MCP Prompts Reference

## Overview

This server exposes 2 prompt templates via the MCP protocol. Prompts provide reusable, parameterized templates for common AI-assisted tasks.

---

## `course_comparison_template`

Structured template for comparing two courses side-by-side.

### Arguments

```typescript
interface CourseComparisonArgs {
  course_code_1: string;  // Required
  course_code_2: string;  // Required
}
```

### Template Content

The prompt generates a comprehensive comparison covering:

1. **Title & Credits** — Compare course titles and credit hours
2. **Descriptions** — Analyze content and focus
3. **Prerequisites** — Compare prerequisite requirements and chains
4. **Department** — Which departments offer these courses
5. **Instructors** — Who typically teaches each course
6. **Key Differences** — What makes these courses distinct
7. **Similarities** — Overlapping concepts or skills
8. **Recommended Audience** — Which students should take which course
9. **Course Sequence** — Order dependencies or independence

### Example Usage

```typescript
const result = await mcp.getPrompt("course_comparison_template", {
  course_code_1: "CS101",
  course_code_2: "CS102"
});

console.log(result.messages[0].content.text);
// Output: Full comparison template with {{course_code_1}} and {{course_code_2}} placeholders
```

### Placeholder Format

The template uses **Mustache-style** placeholders:

```
{{course_code_1}}  // Replaced with first course code
{{course_code_2}}  // Replaced with second course code
```

### Example Output Structure

```
Compare the following two courses in detail:

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

Be specific and use information from the course catalog.
```

### Use Cases

- Student course selection guidance
- Curriculum planning
- Academic advising sessions
- Course equivalence evaluation
- Transfer credit assessment

---

## `course_advisor`

Academic advising prompt for personalized course planning.

### Arguments

```typescript
interface CourseAdvisorArgs {
  student_goals: string;        // Required - Academic/career goals
  completed_courses: string;    // Required - Comma-separated course codes
}
```

### Template Content

The prompt acts as an academic advisor and provides:

1. **Recommended next courses** based on prerequisites and goals
2. **Potential course sequences** for intended major/track
3. **Prerequisite gaps** that need to be filled
4. **Elective suggestions** aligning with goals
5. **Workload considerations** for upcoming semester

### Example Usage

```typescript
const result = await mcp.getPrompt("course_advisor", {
  student_goals: "I want to specialize in machine learning and AI research",
  completed_courses: "CS101, CS102, MATH101, MATH201"
});

console.log(result.messages[0].content.text);
// Output: Personalized advising prompt
```

### Example Output Structure

```
You are an academic advisor for a university. A student has come to you for course planning advice.

Student Goals: {{student_goals}}
Completed Courses: {{completed_courses}}

Using the university course catalog, provide:
1. Recommended next courses based on prerequisites and goals
2. Potential course sequences for their intended major/track
3. Any prerequisite gaps they need to fill
4. Elective suggestions that align with their goals
5. Workload considerations for the upcoming semester

Reference specific courses from the catalog by their course codes and explain your reasoning.
```

### Use Cases

- Academic advising automation
- Degree planning assistance
- Course registration guidance
- Career pathway exploration
- Prerequisite checking

---

## Prompt Discovery

```typescript
// List all available prompts
const prompts = await mcp.listPrompts();
// Returns:
// [
//   { name: "course_comparison_template", description: "..." },
//   { name: "course_advisor", description: "..." }
// ]
```

## Fetching Prompts

```typescript
// Get course comparison template
const comparison = await mcp.getPrompt("course_comparison_template", {
  course_code_1: "CS101",
  course_code_2: "CS102"
});

// Get course advisor template
const advisor = await mcp.getPrompt("course_advisor", {
  student_goals: "Data science career",
  completed_courses: "CS101, MATH101"
});

// Access rendered content
const comparisonText = comparison.messages[0].content.text;
const advisorText = advisor.messages[0].content.text;
```

## Prompt Rendering

Prompts are **templates**, not rendered output. The client (LLM) should:

1. Fetch the prompt template
2. Substitute placeholders with actual values
3. Send to LLM for completion

### Client-Side Rendering Example

```typescript
async function renderCourseComparison(course1: string, course2: string) {
  const prompt = await mcp.getPrompt("course_comparison_template", {
    course_code_1: course1,
    course_code_2: course2
  });
  
  // Template has placeholders - substitute them
  let template = prompt.messages[0].content.text;
  template = template.replace(/\{\{course_code_1\}\}/g, course1);
  template = template.replace(/\{\{course_code_2\}\}/g, course2);
  
  return template;
}

// Usage
const rendered = await renderCourseComparison("CS101", "CS102");
// Send `rendered` to LLM
```

## Best Practices

1. **Always fetch fresh** — Templates may be updated
2. **Validate arguments** — Ensure required fields provided
3. **Handle missing prompts** — Check `listPrompts()` first
4. **Cache templates** — Templates don't change at runtime
5. **Substitute placeholders** — Don't send raw template to LLM

## Custom Prompts

To add custom prompts:

1. Add function in `src/university_catalog/mcp/prompts.py`
2. Register in `register_prompts()`
3. Add tests in `tests/test_prompts.py`
4. Update this documentation

---

## Comparison: Tools vs Prompts

| Aspect | Tools | Prompts |
|--------|-------|---------|
| **Purpose** | Execute actions | Provide templates |
| **Returns** | Data/results | Template text |
| **Arguments** | Typed input | Typed arguments |
| **Execution** | Server-side | Client-side (LLM) |
| **Use Case** | Queries, computations | Guidance, analysis |