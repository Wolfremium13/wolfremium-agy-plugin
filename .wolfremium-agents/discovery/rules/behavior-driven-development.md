# Rule Conventions for Generating BDD Use Cases (Scenarios)

To effectively generate Behavior-Driven Development (BDD) use cases (commonly referred to as scenarios), you must build a bridge between business requirements and technical specifications using concrete examples. Follow these conventions to generate them:

*   **Integrate Codebase Discovery:** Do not assume reports are only for new features. Scan the existing workspace to map out existing `.feature` files, code step-bindings, and automated test runs.
*   **Start with Feature Injection:** Identify the business goals first. Use a three-step process: **Hunt the value** (understand the business goals), **Inject the features** (identify the minimum features to deliver that value), and **Spot the examples** (use high-level examples to flesh out the feature scope).
*   **Structure Conversations via Example Mapping:** Before writing BDD scenarios, hold short, collaborative workshops using Example Mapping to ensure a shared understanding. Use visual markers:
    *   **Yellow cards** for User Stories.
    *   **Blue cards** for Business Rules or acceptance criteria.
    *   **Green cards** for Concrete Examples that illustrate those rules.
    *   **Red cards** for Questions or assumptions that need further clarification.
*   **Use the Given/When/Then Structure:** Translate your concrete examples into executable scenarios using this formal notation:
    *   **Given:** Sets the context or preconditions for the test. It should put the application in the correct starting state.
    *   **When:** Describes the principal action or event that you want to test.
    *   **Then:** Compares the observed outcome or state of the system with what you expect in business terms.

---

## Rules for BDD Cases

When writing your BDD scenarios, adhere to the following rules to ensure they remain maintainable, readable, and robust:

*   **Focus on the "What", not the "How":** Scenarios must be declarative, not imperative. Describe the business intent rather than technical implementation details (e.g., avoid detailing specific UI button clicks or field names in the scenario text).
*   **Keep Examples Concrete but Essential:** Use specific, precise data (like real usernames or amounts) to remove ambiguity. However, only include the concrete data that is strictly essential to illustrate the specific rule being tested. 
*   **Avoid Dependencies Between Scenarios:** Every scenario must be self-sufficient and run in isolation. A scenario should never rely on the outcome or data setup of a previous scenario.
*   **Minimize Duplication Using Tables:** If you have multiple examples illustrating the same rule, do not write separate, wordy scenarios. Instead, summarize them into a single scenario using a table of examples (Scenario Outlines). You can also use embedded tables within steps to cleanly pass complex data.
*   **Use the "Background" Keyword for Shared Context:** If multiple scenarios in the same feature share identical `Given` preconditions, move those steps into a `Background` section to avoid repetition and keep scenarios focused.
*   **Write Assertions using "Should":** Phrase your `Then` steps using the word "should" (e.g., "Then the user should receive a confirmation"). This encourages questioning and focuses on intended behavior rather than rigid, formal constraints.

---

## Product Report & History Definition

At the end of the BDD lifecycle, the executed scenarios automatically generate a product report. This report is defined as **Living Documentation**—a dynamic, always up-to-date artifact that describes what the application does and verifies that it works correctly. 

All BDD report compilations and metrics runs must be logged and archived to maintain a structured history of project progress:

*   **Ignored BDD History Storage:** All history runs, including JSON execution logs and archived markdown reports, must be saved under the project's ignored directory: `.agents/bdd/history/`.
*   **History Indexing:** The history folder must maintain an `index.json` catalog that records the summary metrics and file paths of all past runs to enable stakeholders to trace project readiness over time.
*   **Feature Readiness:** A metric that aggregates test results at the feature level. A feature is only defined as "ready" or "done" when 100% of its automated acceptance criteria pass. 
*   **Feature Coverage:** A metric that goes beyond simple code coverage by mapping executed tests to the original requirements. It identifies which user stories or epics have automated acceptance criteria and highlights requirements that still lack tests.
*   **Step Outcomes:** A granular breakdown of test execution. The report must define the status of every scenario step as **Success** (passed), **Failure** (business expectation not met), **Error** (unexpected technical exception), **Pending** (step not yet automated), or **Skipped** (ignored due to a prior step failing).
*   **Cross-Functional Traceability (Tags):** The report must group scenarios and features using tags (e.g., `@security`, `@performance`, or issue tracker IDs like `@issue-123`). This enables stakeholders to view documentation filtered by specific non-functional requirements or release iterations.
