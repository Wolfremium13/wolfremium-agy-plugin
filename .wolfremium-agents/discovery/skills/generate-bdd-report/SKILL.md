---
name: generate-bdd-report
description: Generate Behavior-Driven Development (BDD) scenarios, map examples, and compile a Product Report (Living Documentation) to specify a new feature or product.
---

# Skill: Generate BDD Scenarios & Product Report

Use this skill when you need to specify a new feature or product using Behavior-Driven Development (BDD). This skill guides you through eliciting requirements, structuring them into scenarios using Given/When/Then syntax, and compiling a comprehensive Product Report (Living Documentation).

---

## Phase 1: Feature Injection & Example Mapping

Before writing Gherkin scenarios, collaborate with stakeholders (or analyze requirements) using Feature Injection and Example Mapping.

1.  **Hunt the Value (Business Goals)**:
    *   Determine the primary business value of the product or feature (e.g., "reduce checkout drop-off by 15%").
    *   Document the "Why" behind the feature.
2.  **Inject the Features**:
    *   Identify the minimum set of capabilities or vertical slices required to deliver that business value.
3.  **Spot the Examples (Example Mapping)**:
    *   Hold a virtual or documented Example Mapping session. Represent information using the following categories:
        *   **User Story (Yellow)**: The short description of the user requirement.
        *   **Business Rules (Blue)**: The business constraints or acceptance criteria governing the story.
        *   **Concrete Examples (Green)**: Real-world examples with realistic numbers/states illustrating each rule.
        *   **Questions/Assumptions (Red)**: Any unresolved questions or critical assumptions that need clarification.

---

## Phase 2: Formulate BDD Scenarios

Translate the mapped examples into formal BDD scenarios using Gherkin syntax (`Given/When/Then`). Adhere strictly to the BDD rule conventions:

1.  **Focus on the "What", not the "How"**:
    *   Write scenarios declaratively. Describe user intents and outcomes rather than technical interactions (e.g., use `When the shopper checks out` instead of `When the user clicks the "Proceed to Checkout" button`).
2.  **Ensure Scenario Independence**:
    *   Each scenario must run in isolation. Preconditions (`Given` steps) must set up all required state without depending on previous scenarios.
3.  **Use the "Background" Keyword**:
    *   Move repetitive, identical `Given` steps shared across scenarios in the same feature file into a single `Background` block.
4.  **Parameterize via Scenario Outlines**:
    *   When testing the same workflow with multiple inputs, use `Scenario Outline` with `Examples` tables to avoid duplicate text blocks.
5.  **Use "Should" Assertions**:
    *   Phrase `Then` steps using "should" (e.g., `Then the discount should be applied`) to define expectation boundaries clearly.

---

## Phase 3: Compile the Product Report (Living Documentation)

Once scenarios are specified (and/or executed), compile them into a **Product Report** representing the **Living Documentation** of the system. The report must track and display the following sections:

### 1. Header & Metadata
*   **Target Product/Feature Name**
*   **Compilation Timestamp**
*   **Aggregated Execution Metrics** (Pass Rate, Coverage Rate).

### 2. Feature Readiness Dashboard
*   Track the readiness of each feature based on scenario validation.
*   **Formula**: A feature is `Ready` (100% pass) or `In Progress` (any pending/failed/error states).

### 3. Feature Coverage Matrix
*   Map user stories/epics to the BDD scenarios that test them. Highlight any gaps where user stories lack corresponding scenarios.

### 4. Step-Level Outcomes
*   Classify each step's execution state:
    *   `Success`: Expected business outcome matched.
    *   `Failure`: Expected business outcome did not match (assertion failed).
    *   `Error`: Technical exception occurred (system crashed/timeout).
    *   `Pending`: Scenario is defined but automation/implementation is not complete.
    *   `Skipped`: Step was bypassed because a preceding step failed.

### 5. Tag-Based Traceability Index
*   Organize scenarios using tags (e.g., `@security`, `@performance`, `@billing`, `@issue-456`) to allow stakeholders to filter documentation by concern.

---

## Phase 4: Output Templates & Deliverables

Generate the final output as a Markdown report. Use the template below:

```markdown
# Product Specification & Readiness Report (Living Documentation)

**Compiled on**: YYYY-MM-DD HH:MM:SS
**Target Scope**: [Product / Feature Name]

## 📊 Summary Dashboard
*   **Total Features**: [Count]
*   **Feature Readiness**: [Pass %]
*   **Total Scenarios**: [Count]
*   **Step Success Rate**: [Success %]

---

## 📋 Feature Readiness Details
| Feature Link | Scenarios (Passed/Total) | Status | Tags |
| :--- | :--- | :--- | :--- |
| [Feature Name](path/to/feature) | X / Y | [Ready / In Progress] | `@tag1`, `@tag2` |

---

## 🔍 Feature Coverage & Requirements Traceability
| User Story ID | Description | Associated Scenarios | Coverage Status |
| :--- | :--- | :--- | :--- |
| US-001 | As a [role] I want to [action] so that [value] | `Scenario 1`, `Scenario 2` | [Covered / Gap] |

---

## ⚙️ Step-Level Execution Details
```gherkin
Feature: [Feature Name]
  [Feature Description...]

  Background:
    Given [Precondition...]

  Scenario: [Scenario Name]
    Given [Context...]
    When [Action...]
    Then [Expected Outcome...] --> [SUCCESS / FAILURE / ERROR / PENDING / SKIPPED]
```
```
