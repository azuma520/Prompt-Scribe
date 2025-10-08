---
description: Create or update a specification document following the spec template and ensuring constitution compliance.
---

# Command: speckit.spec

## Purpose

This command creates or updates a specification document in `.specify/specs/` directory. All specifications must follow the template at `.specify/templates/spec-template.md` and comply with the project constitution.

## User Input

```text
{USER_INPUT}
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Flow

### 1. Parse User Request

- Identify the feature or module name
- Determine if this is a new spec or update to existing spec
- Extract key requirements from user input

### 2. Load Constitution and Template

- Read `.specify/memory/constitution.md` to understand core principles
- Read `.specify/templates/spec-template.md` for structure
- Identify which principles are most relevant to this spec

### 3. Check for Existing Spec

- Search `.specify/specs/` for existing related specifications
- If updating, load the existing spec to preserve version history
- Identify dependencies on other specs

### 4. Draft Specification Content

Fill in all template sections:

- **Spec ID**: Generate in format SPEC-YYYY-NUMBER (e.g., SPEC-2025-001)
- **Version**: Start at 1.0.0 for new specs, increment appropriately for updates
- **Status**: Set appropriate status (Draft, In Review, Approved, Implemented, Deprecated)
- **Constitution Compliance Check**: Explicitly check all relevant principles
- **Architecture Stage**: Clearly identify if Stage 1, Stage 2, or cross-stage
- **Requirements**: Define both functional and non-functional requirements
- **Data Model**: Define data structures with validation rules
- **Interface Definition**: Define APIs, functions, or module interfaces
- **LLM Usage Declaration**: Explicitly declare IDE LLM vs Data Layer LLM usage
- **Testing Strategy**: Define unit, integration, and data quality tests
- **Implementation Plan**: Break down into phases with time estimates
- **Acceptance Criteria**: Define clear, testable completion criteria

### 5. Validate Constitution Compliance

Ensure the spec complies with:

- **Two-Stage Hybrid Architecture**: Correctly identified stage, no cross-stage coupling
- **LLM Role Separation**: If using LLM, correct separation and logging mechanism defined
- **Spec-Driven Development**: This spec must be approved before implementation
- **Data-First**: Data model and validation defined before implementation details
- **Modularity and Readability**: Clear structure, single responsibility

### 6. Generate Spec File

- Create file at `.specify/specs/SPEC-YYYY-NUMBER-feature-name.md`
- Use kebab-case for feature name in filename
- Ensure all placeholders are filled

### 7. Output Summary

Provide user with:

- Spec ID and file path
- Constitution compliance status
- Related specs or dependencies
- Next steps (e.g., review, approval, implementation)
- Suggested commit message

## Validation Checklist

Before finalizing, ensure:

- [ ] All template sections completed
- [ ] No unexplained placeholder tokens remain
- [ ] Constitution compliance explicitly checked
- [ ] Data model clearly defined
- [ ] Testing strategy included
- [ ] Acceptance criteria are testable
- [ ] LLM usage (if any) properly declared

## Special Cases

- **Cross-Stage Specs**: If a feature spans both stages, clearly document the decoupling strategy
- **LLM Integration**: Must define input format, output format, logging mechanism, failure handling
- **Data Processing**: Must include input validation, output validation, and consistency checks

## Important Notes

- Specifications are living documents - update them as requirements evolve
- Always increment version number when making changes
- Maintain a change log section in each spec
- Link related specs to maintain traceability

---

**End of Command Definition**

