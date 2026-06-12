---
name: generate-bdd-report
description: Scan the workspace to discover existing or new Gherkin scenarios, map their implementation and test outcomes, and compile/archive the Product Report (Living Documentation) in a structured history directory.
---

# Skill: Discover BDD Scenarios & Compile Product Report (Living Documentation)

Use this skill to scan and assess the workspace's Behavior-Driven Development (BDD) scenarios, map them to current code implementations and test runs, and compile/archive the Product Report (Living Documentation). This skill supports both **existing** features (assessing current status) and **new** features (planning, example mapping, and injecting scenarios), storing a structured history of all execution runs in the project's ignored folder.

---

## Phase 1: Workspace BDD Discovery

Instead of assuming you are starting from scratch, always begin by discovering the current codebase state:

1.  **Scan for Scenarios**:
    *   Find all Gherkin `.feature` files in the project workspace (excluding standard build/ignored folders like `bin/`, `obj/`, `.git/`, `.agents/`, etc.).
2.  **Inspect Implementation (Step Bindings)**:
    *   Search codebase source files (e.g. `*.cs` for C# projects) for matching step definition attributes (e.g., `[Given]`, `[When]`, `[Then]`, `[StepDefinition]`).
    *   A scenario step is marked as `Pending` if no matching implementation or step binding is found in the code.
3.  **Inspect Test Outcomes**:
    *   Scan for recent test execution run reports (e.g. `.trx` files, JUnit XML results).
    *   Map executed tests back to the Gherkin scenarios to classify outcomes as `Success`, `Failure`, `Error`, or `Skipped`.
4.  **Automated Scan Utility**:
    *   You can automate this discovery and mapping process by executing the helper script:
        ```bash
        python3 .agents/skills/generate-bdd-report/scripts/generate_report.py
        ```
    *   This script automatically scans, maps code/test outcomes, updates the historical index, and outputs the markdown report.

---

## Phase 2: Feature Injection & Example Mapping

When adding *new* capabilities or extending existing ones, collaborate with stakeholders (or analyze requirements) using Feature Injection and Example Mapping:

1.  **Hunt the Value (Business Goals)**:
    *   Determine the primary business value of the new feature/slice (e.g., "reduce checkout drop-off by 15%").
    *   Document the "Why" behind the feature.
2.  **Inject the Features**:
    *   Identify the minimum set of capabilities or vertical slices required to deliver that business value.
3.  **Spot the Examples (Example Mapping)**:
    *   Map the requirements using the following categories:
        *   **User Story (Yellow)**: The short description of the user requirement.
        *   **Business Rules (Blue)**: The business constraints or acceptance criteria governing the story.
        *   **Concrete Examples (Green)**: Real-world examples with realistic numbers/states illustrating each rule.
        *   **Questions/Assumptions (Red)**: Any unresolved questions or critical assumptions that need clarification.

---

## Phase 3: Formulate BDD Scenarios

Translate the concrete examples into formal Gherkin syntax (`Given/When/Then`) scenarios inside `.feature` files. Adhere strictly to the BDD rule conventions:

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

## Phase 4: Compile & Store BDD History (Living Documentation)

Every time discovery is performed or tests are run, compile the outcomes into the **Product Report** representing the **Living Documentation** of the system, and archive it in a structured history directory.

### 1. Storage Location
All historical reports and execution data must be stored in the project's ignored configuration folder:
`[project-root]/.agents/bdd/history/`

### 2. History File Structure
*   **`index.json`**: A catalog of all past runs. Sorted from newest to oldest:
    ```json
    [
      {
        "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
        "run_id": "run-YYYYMMDD-HHMMSS",
        "summary": {
          "total_features": 3,
          "ready_features": 2,
          "feature_readiness_pct": 66.67,
          "total_scenarios": 12,
          "passed_scenarios": 10,
          "step_success_rate_pct": 91.25
        },
        "report_file": ".agents/bdd/history/report-YYYYMMDD-HHMMSS.md",
        "data_file": ".agents/bdd/history/run-YYYYMMDD-HHMMSS.json"
      }
    ]
    ```
*   **`run-<timestamp>.json`**: Detailed JSON outcome of the run, containing feature structures, scenario execution outcomes, and individual step statuses.
*   **`report-<timestamp>.md`**: The full markdown Living Documentation report compiled at that point in time.
*   **`BDD_REPORT.md`** (at the project root): A copy of the latest compiled report, serving as the immediate, easily accessible living documentation page for developers.

### 3. Metric Definitions
*   **Feature Readiness**: A feature is `Ready` (100% pass of all scenarios) or `In Progress` (any pending/failed/error states).
*   **Feature Coverage**: Map user stories/epics to the BDD scenarios that test them. Highlight gaps where user stories lack corresponding scenarios.
*   **Step Outcomes**: Classify steps as:
    *   `Success`: Expected business outcome matched or step is implemented.
    *   `Failure`: Expected business outcome did not match (assertion failed).
    *   `Error`: Technical exception occurred (system crashed/timeout).
    *   `Pending`: Scenario step is defined but code binding/implementation is missing.
    *   `Skipped`: Step was bypassed because a preceding step failed.

---

## Phase 5: Output Report Template

The markdown reports generated at `.agents/bdd/history/report-<timestamp>.md` and at the root `BDD_REPORT.md` must adhere to this template:

```markdown
# Product Specification & Readiness Report (Living Documentation)

**Compiled on**: YYYY-MM-DD HH:MM:SS
**Target Scope**: [Product / Feature Name or Workspace Scan]

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
