---
description: Create or update a task list following the tasks template and ensuring constitution compliance.
---

# Command: speckit.tasks

## Purpose

This command creates or updates a task list in `.specify/tasks/` directory. All task lists must follow the template at `.specify/templates/tasks-template.md` and comply with the project constitution.

## User Input

```text
{USER_INPUT}
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Flow

### 1. Parse User Request

- Identify the project or feature for task breakdown
- Determine if this relates to existing plan or spec
- Extract any specific task requirements

### 2. Load Constitution, Plan, and Specs

- Read `.specify/memory/constitution.md` for principles
- Read `.specify/templates/tasks-template.md` for structure
- Identify related plan in `.specify/plans/`
- Identify related specs in `.specify/specs/`

### 3. Check for Existing Task List

- Search `.specify/tasks/` for existing task list
- If updating, load existing to preserve completion status
- Identify dependencies between tasks

### 4. Generate Task List Content

Fill in all template sections:

- **Tasks ID**: Generate in format TASKS-YYYY-NUMBER
- **Related Plan**: Link to corresponding plan
- **Related Specs**: Link to all relevant specifications
- **Constitution Compliance Reminder**: Include checklist
- **Stage 1 Tasks**: Break down local data pipeline work
- **Stage 2 Tasks**: Break down cloud backend work
- **Cross-Stage Tasks**: Identify infrastructure and compliance tasks

For each task, include:

- **Task ID**: Format as TASK-XXX (sequential numbering)
- **Title**: Clear, action-oriented title
- **Description**: Detailed task description
- **Spec Reference**: Link to governing specification
- **Priority**: High/Medium/Low based on criticality
- **Estimated Time**: Realistic time estimate
- **Owner**: Assign to team member
- **Dependencies**: List prerequisite tasks
- **Acceptance Criteria**: Define "done" conditions
- **Technical Details**: Specify languages, files, frameworks
- **Notes**: Any additional context

### 5. Categorize Tasks

Organize tasks by categories:

**Stage 1 Categories:**
- Data Processing Core
- Data Validation and Quality
- LLM Integration (Data Layer)
- Testing and Documentation

**Stage 2 Categories:**
- Data Migration
- Vectorization and Search
- API Development
- Testing and Deployment

**Cross-Stage Categories:**
- Project Infrastructure
- Constitution Compliance

### 6. Validate Constitution Compliance

Ensure tasks respect:

- **Two-Stage Architecture**: Clear stage separation, no coupling
- **LLM Role Separation**: Correct LLM usage with logging
- **Spec-Driven**: All tasks based on approved specs
- **Data-First**: Data quality tasks prioritized
- **Modularity**: Each task has single, clear responsibility

### 7. Generate Task Statistics

Calculate and include:

- Total number of tasks
- Tasks per stage
- Tasks per priority level
- Completion percentage
- Blocked tasks tracking

### 8. Generate Task File

- Create file at `.specify/tasks/TASKS-YYYY-NUMBER-project-name.md`
- Use kebab-case for project name in filename
- Ensure all task details complete

### 9. Output Summary

Provide user with:

- Tasks ID and file path
- Total task count and breakdown by stage
- High-priority tasks requiring immediate attention
- Blocked tasks requiring resolution
- Estimated total effort
- Next steps (e.g., task assignment, sprint planning)
- Suggested commit message

## Task Status Management

Use these status markers:

- `[ ]` Not Started
- `[>]` In Progress
- `[✓]` Completed
- `[!]` Blocked
- `[?]` Pending Clarification
- `[-]` Cancelled

## Validation Checklist

Before finalizing, ensure:

- [ ] All tasks linked to approved specs
- [ ] Constitution compliance verified
- [ ] Stage separation clear
- [ ] Dependencies identified
- [ ] Acceptance criteria defined
- [ ] Technical details specified
- [ ] Priorities assigned
- [ ] Owners assigned (or assignable)
- [ ] Estimates realistic
- [ ] Task statistics calculated

## Special Cases

- **Blocked Tasks**: Create separate tracking section
- **High-Priority Tasks**: Clearly flag and assign first
- **LLM Integration Tasks**: Ensure logging requirements explicit
- **Data Quality Tasks**: Prioritize in Stage 1
- **Testing Tasks**: Ensure adequate test coverage planned

## Important Notes

- Keep task list updated as work progresses
- Mark tasks complete only when acceptance criteria met
- Record blocked tasks immediately with resolution plan
- Conduct regular task list reviews
- Update estimates based on actual completion times
- Maintain constitution compliance throughout execution

---

**End of Command Definition**

