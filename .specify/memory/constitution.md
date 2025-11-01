<!--
Sync Impact Report
==================
Version Change: 1.2.0
Constitution Type: Default template for SpecKit users
Ratification: 2025-11-01
Last Amendment: 2025-11-01

Amendment Summary (v1.2.0 - Coding Agent Instructions):
- Added new "Coding Agent Instructions" section with coding standards
- Added logging requirements (use logging module, not print)
- Added mandatory exception logging with exc_info=True for stack traces
- Added output formatting prohibition (no emojis/icons in code, commits, docs)
- Moved commit message standards from Principle II to Coding Agent Instructions
- Enhanced commit message examples and prohibitions

Current Principle Structure:
- I. Simplicity & Code Quality (NON-NEGOTIABLE) - YAGNI/KISS unified + SOLID/CLEAN CODE/DRY
- II. Language & Communication Policy - Polish responses (concise), English docs/code, Python requirements
- Coding Agent Instructions - Logging standards, no emojis, commit message standards
- III. Incremental Delivery - MVP-first approach
- IV. Specification-First - Complete spec before implementation
- V. Independent Testability - Isolated testing requirements
- VI. Documentation Completeness - Cross-artifact consistency

Key Changes:
- Logging: Mandatory use of logging module instead of print statements
- Exception Logging: Mandatory exc_info=True for all exception logs to include stack traces
- Output Formatting: Absolute prohibition of emojis/icons in code, commits, and official docs
- Commit Standards: Consolidated and enhanced with examples, moved to dedicated section
- Print statements only allowed in CLI entry points for user output

Templates Requiring Updates:
✅ All templates - coding standards are procedural, no template changes needed

Follow-up TODOs:
- None
-->

# SpecKit Project Constitution

## Core Principles

### I. Simplicity & Code Quality (NON-NEGOTIABLE)

**Rule**: Always use the simplest solution that works. YAGNI (You Aren't Gonna Need It) and KISS (Keep It Simple, Stupid) are the same principle—do not build features, abstractions, or infrastructure until there is a concrete, immediate need. All code MUST strictly adhere to SOLID principles, Clean Code practices, and DRY (Don't Repeat Yourself).

**Simplicity Requirements** (YAGNI/KISS combined):
- Simplest solution that works is preferred
- No speculative features or "future-proofing" without documented justification
- Prefer standard library solutions over external dependencies
- Every abstraction must be justified in the Complexity Tracking section
- Reject patterns like Repository, Factory, Abstract Factory unless complexity justification is approved
- Default to direct implementations; introduce indirection only when duplication becomes painful
- Avoid clever code: Clarity over cleverness
- No premature optimization
- Straightforward logic paths over complex nested conditions

**SOLID Principles** (mandatory):
- **Single Responsibility**: Each class/module has ONE reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes must be substitutable for their base types
- **Interface Segregation**: Many specific interfaces better than one general interface
- **Dependency Inversion**: Depend on abstractions, not concretions

**Clean Code Practices** (mandatory):
- Meaningful names: Names reveal intent without need for comments
- Functions are small (ideally <20 lines) and do ONE thing
- No side effects: Functions do what their names promise, nothing more
- No magic numbers: Use named constants
- Error handling separated from business logic
- Consistent formatting enforced by automated tools

**DRY (Don't Repeat Yourself)** (mandatory):
- No code duplication: Extract repeated logic into reusable functions/classes
- Single source of truth for each piece of knowledge
- Duplication must be eliminated before PR approval

**Rationale**: Simplicity (YAGNI/KISS) prevents premature abstraction and speculative features that create maintenance burden, cognitive overhead, and technical debt. Simple solutions are easier to understand, modify, and maintain. SOLID and Clean Code practices ensure maintainability, readability, and longevity. DRY eliminates inconsistencies and maintenance burden.

### II. Language & Communication Policy

**Rule**: AI assistant communication with users MUST be in Polish and kept short and concise. All documentation, code, and technical artifacts MUST be exclusively in English.

**Requirements**:
- AI assistant MUST respond to users in Polish language
- AI assistant responses MUST be short and concise: no unnecessary introductions, conclusions, or verbose explanations
- All documentation MUST be in English: `spec.md`, `plan.md`, `tasks.md`, contracts, data models
- All source code MUST use English for: identifiers, classes, functions, variables, constants
- All file names, directory names, and module names MUST be in English
- All API contracts, data models, and technical schemas MUST be in English
- Configuration files and technical documentation MUST be in English
- No mixing of Polish and English within code (e.g., no Polish variable names)

**Programming Language Requirements**:
- All implementation code MUST be written in Python 3.11 or higher
- Python is the mandatory programming language for this project
- Follow PEP 8 style guide for Python code
- Use type hints (PEP 484) for all function signatures
- Use snake_case for variables, functions, and module names (Python convention)
- Use PascalCase for class names (Python convention)

**Rationale**: Polish communication enables natural interaction with users and is the most precise language for work with coding agents, while English documentation and code maintain international standards, enable global collaboration, and leverage universal programming conventions. Concise communication respects user time and reduces noise.

## Coding Agent Instructions

### General Coding Standards

**Logging Requirements**:
- MUST use proper logging module instead of print statements
- Configure logging with appropriate levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Use structured logging with meaningful context
- Print statements are ONLY allowed in CLI entry points that output to users
- **Exception logging**: MUST log exceptions with `exc_info=True` to include stack traces
  - Example: `logger.error("Operation failed", exc_info=True)`
  - Alternative: `logger.exception("Operation failed")` (automatically includes exc_info)
  - Never log exceptions without stack trace context

**Output Formatting** (NON-NEGOTIABLE):
- **Absolute prohibition**: No emojis or icons in production code
- **Absolute prohibition**: No emojis or icons in commit messages
- **Absolute prohibition**: No emojis or icons in official documentation (spec.md, plan.md, tasks.md, README, API docs)
- **Only permitted exceptions**: User-facing UI/UX where emojis are part of the product specification (requires explicit justification)
- **Rationale**: Emojis introduce encoding issues, reduce professionalism, create accessibility problems, and clutter version control history. Code and documentation must be universally readable and maintainable.

### Commit Message Standards

**Format Requirements**:
- All commit messages MUST be in English
- First line: Brief summary in imperative mood (50 chars max)
- Two blank lines after the summary
- Body: Brief justification explaining WHY, not WHAT
- Focus exclusively on code changes and their rationale
- Keep short and concise

**Prohibited Content**:
- **Absolute prohibition**: No meta-references to AI tools
- No "Co-authored-by: Claude" or similar AI attribution
- No "Generated with Claude Code" or similar tool references
- No emojis or decorative icons
- No unnecessary verbosity or filler text

**Example**:
```
Add environment variable support for API keys


Enables users to override API keys via OPENAI_API_KEY and ELEVENLABS_API_KEY environment variables, improving security by avoiding hardcoded credentials in config files.
```

### III. Incremental Delivery

**Rule**: Every feature must be decomposable into independently deliverable user stories, each providing standalone value and forming a viable Minimum Viable Product (MVP) increment.

**Requirements**:
- User stories MUST be prioritized (P1, P2, P3, etc.) by business value
- Each user story MUST be independently testable and deployable
- P1 story alone should constitute a working MVP
- Implementation MUST follow priority order; deliver P1 before starting P2
- Stop and validate after each story—do not batch deliveries

**Rationale**: Incremental delivery reduces risk, enables early feedback, and ensures that work can be paused at any checkpoint while still delivering value. It prevents all-or-nothing delivery and supports iterative refinement.

### IV. Specification-First

**Rule**: No implementation begins until the feature specification is complete, reviewed, and approved. Specifications define the "what" and "why," not the "how."

**Requirements**:
- All features MUST have a completed `spec.md` before planning begins
- Specifications MUST include user scenarios, acceptance criteria, and success metrics
- Specifications are technology-agnostic—no implementation details
- Use `/speckit.clarify` to resolve underspecified areas before implementation
- Stakeholder approval is required before proceeding to `/speckit.plan`

**Rationale**: Specifications force clarity of purpose and alignment on requirements before investing in design and code. They prevent rework caused by misunderstood requirements and enable stakeholders to validate intent early.

### V. Independent Testability

**Rule**: Every user story and component must be independently testable. Dependencies should be minimized, and tests should not require running the entire system.

**Requirements**:
- User stories MUST define independent acceptance scenarios
- Tests are organized by user story to enable isolated validation
- Contract tests verify API boundaries without full system integration
- Integration tests focus on critical interaction paths, not exhaustive coverage
- Mock external dependencies to enable local testing

**Rationale**: Independent testability enables faster feedback cycles, parallel development, and confident refactoring. It reduces test brittleness and makes debugging failures more straightforward.

### VI. Documentation Completeness

**Rule**: Every artifact generated by SpecKit workflows (`spec.md`, `plan.md`, `tasks.md`, contracts, data models) must be complete, consistent, and cross-referenced.

**Requirements**:
- No placeholder sections like `[NEEDS CLARIFICATION]` in approved artifacts
- All design decisions MUST be documented with rationale
- Use `/speckit.analyze` to validate cross-artifact consistency
- Quickstart guides MUST be validated against implementation
- Updates to one artifact trigger consistency checks across related files

**Rationale**: Documentation completeness ensures that team members can onboard quickly, understand design decisions, and make informed changes. Inconsistent or incomplete documentation leads to confusion, misalignment, and implementation drift.

## Quality Standards

**Testing Requirements**:
- Tests are OPTIONAL unless explicitly requested in the feature specification
- When tests are requested, they MUST be written before implementation (TDD)
- Tests MUST follow the Red-Green-Refactor cycle: write test → verify failure → implement → verify success
- Contract tests for API boundaries; integration tests for critical user journeys; unit tests for complex logic

**Code Quality Principles**:
- All code MUST adhere to SOLID, CLEAN CODE, DRY, and KISS principles (see Principle VII)
- Linting and formatting tools MUST be configured and enforced
- Code reviews MUST verify compliance with all constitution principles
- No TODOs or placeholders in approved pull requests
- Performance requirements MUST be defined in `plan.md` and validated before merging

**Code Comment Policy (NON-NEGOTIABLE)**:
- **Absolute prohibition**: No comments or docstrings in production code
- Code MUST be self-documenting through:
  - Clear, meaningful function and variable names that reveal intent
  - Small, focused functions that do ONE thing
  - Well-structured code following Clean Code principles
  - Proper abstractions and design patterns where appropriate
- **Only permitted exceptions** (requires explicit justification in PR):
  - Complex algorithms where the "why" cannot be expressed in code structure (e.g., mathematical formulas, domain-specific business rules)
  - Public API documentation for external library interfaces (when creating reusable libraries)
  - Copyright notices and licensing headers (legal requirement)
- **Rationale**: Comments are a sign of unclear code. They become outdated, lie, and create maintenance burden. Clean Code eliminates the need for comments by making code intention obvious through structure and naming. If you feel you need a comment, refactor the code instead.

**Complexity Justification**:
- Any violation of Principle I (Simplicity & YAGNI) MUST be documented in the Complexity Tracking section of `plan.md`
- Justifications must explain: (a) why the complexity is needed, (b) what simpler alternative was rejected and why
- Examples requiring justification: adding a 4th project when 3 exist, introducing Repository pattern, creating abstraction layers

## Development Workflow

**Specification Phase** (`/speckit.specify`):
- Capture user requirements in natural language
- Define prioritized user stories with acceptance criteria
- Identify edge cases and success metrics
- Use `/speckit.clarify` to resolve ambiguities

**Planning Phase** (`/speckit.plan`):
- Execute Phase 0 (research), Phase 1 (design artifacts: data models, contracts, quickstart), Phase 2 (task generation handoff)
- Perform Constitution Check before Phase 0; re-check after Phase 1
- Document technical context, project structure, and complexity justifications
- Validate all design decisions against core principles

**Implementation Phase** (`/speckit.implement`):
- Generate `tasks.md` via `/speckit.tasks`
- Execute tasks in dependency order, grouped by user story priority
- Deliver and validate P1 (MVP) before proceeding to P2
- Use `/speckit.analyze` to verify consistency across artifacts

**Validation**:
- Run tests (if requested) and verify all acceptance criteria
- Execute quickstart guide to validate end-to-end functionality
- Perform code review with constitution compliance check
- Update documentation to reflect any implementation learnings

## Governance

**Amendment Procedure**:
- Constitution changes require documented rationale and stakeholder approval
- Version updates follow semantic versioning:
  - **MAJOR**: Backward-incompatible principle removals or redefinitions
  - **MINOR**: New principles added or material guidance expansions
  - **PATCH**: Clarifications, wording fixes, non-semantic refinements
- Amendments trigger updates to all dependent templates and commands
- A Sync Impact Report MUST accompany every amendment

**Compliance Review**:
- All pull requests MUST verify compliance with constitution principles
- Constitution Check in `plan.md` is a mandatory gate before Phase 0 research
- `/speckit.analyze` MUST be run before marking any feature as complete
- Non-compliance requires either: (a) fixing the violation, or (b) documenting justified complexity

**Template Evolution**:
- Templates in `.specify/templates/` reflect constitution principles
- Template updates MUST maintain backward compatibility unless major version bump
- Command files in `.claude/commands/speckit.*.md` are implementation-specific and should avoid agent-specific references (e.g., use "AI assistant" not "Claude")

**Versioning Policy**:
- Constitution version is independent of SpecKit framework version
- Each project using SpecKit may customize this constitution to fit their needs
- Customizations should increment version and document changes in Sync Impact Report

**Version**: 1.2.0 | **Ratified**: 2025-11-01 | **Last Amended**: 2025-11-01
