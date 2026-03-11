---
name: todo-discovery
description: Finds unaddressed TODO items in the codebase, evaluates relevant code around the TODO, and generates a file of questions for the user to respond to in order to help plan its implementation.
---

# SKILL: TODO Discovery & Planning

## Description
This skill locates unaddressed `TODO`, `FIXME`, or similar markers in the codebase, analyzes the surrounding code context to understand what needs to be done, and generates a structured file containing clarifying questions for the user. These questions will assist in formulating a precise plan to implement the required changes.

## Core Instructions

When triggered to find and plan unaddressed TODO items, execute this exact workflow:

### Step 1: Discover TODOs
- Use the `grep_search` tool to search for `TODO` or `FIXME` comments in the codebase.
- Select one or more relevant TODO items to focus on (or follow the user's specific guidance if provided).

### Step 2: Contextual Analysis
- Use the `view_file` tool to examine the selected TODO item(s) and the surrounding code context (e.g., the function, class, or module it belongs to).
- Analyze the existing code to understand the technical requirements, missing logic, or architectural constraints related to the TODO item.
- Consider what external dependencies, configurations, or related files might be impacted.

### Step 3: Generate Questions File
- Frame specific, actionable, and context-aware questions to resolve ambiguity, establish design choices, and clarify requirements needed to implement the TODO.
- Use the `write_to_file` tool to generate a markdown file (e.g., `todo_plan_questions.md`) containing these clarifying questions.
- Example structure of the questions file:
  - **Context:** Brief summary of what the TODO is and where it lives.
  - **Code Analysis:** What the current code does and why this TODO is needed.
  - **Questions for the User:** 
    1. [Specific question about an implementation detail]
    2. [Question about edge cases or error handling]
    3. [Question about dependencies or architecture]

### Step 4: Request User Feedback
- Use the `notify_user` tool (if applicable) or directly respond to the user, asking them to review the generated questions file and provide their answers.

## Rules & Guardrails
- **DO NOT** attempt to implement the TODO item immediately or blindly edit the code. You must gather the user's input and finalize a plan first.
- Keep the generated questions focused, specifically referencing the code context, rather than asking overly broad or generic software engineering questions.
