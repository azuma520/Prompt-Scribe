---
description: Create or update a development plan following the plan template and ensuring constitution compliance.
---

# Command: speckit.plan

## Purpose

This command creates or updates a development plan in `.specify/plans/` directory. All plans must follow the template at `.specify/templates/plan-template.md` and comply with the project constitution.

## User Input

```text
{USER_INPUT}
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Flow

### 1. Parse User Request

- Identify the project or feature being planned
- Determine scope (single feature, milestone, or full project)
- Extract timeline constraints and resource availability

### 2. Load Constitution and Related Specs

- Read `.specify/memory/constitution.md` for core principles
- Read `.specify/templates/plan-template.md` for structure
- Identify all related specifications in `.specify/specs/`
- Ensure all work items are based on approved specs

### 3. Check for Existing Plan

- Search `.specify/plans/` for existing related plans
- If updating, load existing plan to preserve history
- Identify dependencies on other plans

### 4. Draft Plan Content

Fill in all template sections:

- **Plan ID**: Generate in format PLAN-YYYY-NUMBER (e.g., PLAN-2025-001)
- **Version**: Start at 1.0.0 for new plans
- **Status**: Set to Planning initially
- **Constitution Compliance Check**: Verify alignment with all principles
- **Architecture Stage Planning**: Clearly separate Stage 1 and Stage 2 work
- **Spec-to-Implementation Mapping**: Map each spec to specific tasks
- **Task Breakdown**: Organize tasks by stage and category
- **Timeline**: Define milestones and Gantt chart
- **Resource Planning**: Identify personnel, technical resources, budget
- **Risk Management**: Identify risks and mitigation strategies
- **Quality Assurance**: Define testing and review processes
- **Completion Criteria**: Define what "done" means

### 5. Validate Constitution Compliance

Ensure the plan respects:

- **Two-Stage Hybrid Architecture**: Stage 1 tasks complete before Stage 2 begins
- **LLM Role Separation**: IDE LLM for coding, Data Layer LLM properly integrated
- **Spec-Driven Development**: All tasks based on approved specs
- **Data-First**: Data processing tasks prioritized
- **Modularity**: Tasks are clearly defined with single responsibilities

### 6. Generate Task List Reference

- Create or reference corresponding tasks document in `.specify/tasks/`
- Ensure task breakdown in plan aligns with detailed task list

### 7. Generate Plan File

- Create file at `.specify/plans/PLAN-YYYY-NUMBER-project-name.md`
- Use kebab-case for project name in filename
- Ensure all placeholders are filled

### 8. Output Summary

Provide user with:

- Plan ID and file path
- Constitution compliance status
- Timeline overview (start date, milestones, target completion)
- Critical path and high-risk items
- Resource requirements
- Next steps (e.g., team review, task assignment)
- Suggested commit message

## Validation Checklist

Before finalizing, ensure:

- [ ] All template sections completed
- [ ] Constitution compliance verified
- [ ] All work items map to approved specs
- [ ] Stage 1 and Stage 2 clearly separated
- [ ] Milestones and timeline realistic
- [ ] Resources identified and allocated
- [ ] Risks identified with mitigation plans
- [ ] Quality assurance processes defined
- [ ] Completion criteria clear and testable

## Special Cases

- **Cross-Stage Planning**: Ensure Stage 1 completion before Stage 2 begins
- **Resource Constraints**: Adjust timeline or scope accordingly
- **High-Risk Items**: Allocate extra time and resources
- **LLM Integration**: Plan for API rate limits and cost management

## Important Notes

- Plans should be reviewed and approved before work begins
- Update plan status regularly as work progresses
- Adjust timeline and resources as needed (with version increment)
- Conduct retrospectives at milestone completion
- Maintain alignment with constitution throughout execution

---

**End of Command Definition**

