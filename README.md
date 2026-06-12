To integrate your custom `.wolfremium-agents` vault into your project, you will
use a **Symbolic Linking (Symlink)** approach combined with **Progressive
Disclosure** and **Multi-Agent Orchestration**. Based on standardized patterns
for agent repositories, here is exactly how this integration functions within
your project:

**1. The Symlink Integration (The Setup Script)** You will run your Bash setup
script from the root of your project to act as a bridge between your vault and
the IDE. Rather than copying files, the script creates symbolic links (`ln -s`)
from your project's local `.agents/skills/` and `.agents/rules/` directories
directly to the specific vertical slices (e.g., your Python and folders) inside
your isolated `.wolfremium-agents` vault.

- This establishes a **Project-Level Integration** (Workspace Scope).
- Because the target is the `.agents/` folder, adding it to your project's
  `.gitignore` guarantees that the agent configurations remain local and never
  pollute your main codebase. _(Note: If you want to skip writing the bash
  script entirely, there are open-source CLI utilities like `open-agent-hub`
  that automate this exact capability using commands like
  `oah link -p -t antigravity` to inject skills into your workspace)_.

**2. Progressive Disclosure (Context Optimization)** Once the symlinks are
created, the Antigravity engine natively integrates these skills into your
workflow without overloading the AI's context window. It does this through a
highly efficient three-phase lifecycle:

- **Discovery Phase:** When you open your project, the engine only indexes the
  YAML frontmatter of your symlinked `SKILL.md` files. This keeps the system
  incredibly fast, consuming only about 100 tokens per skill to build its
  catalog.
- **Activation Phase:** When you submit a prompt (e.g., "Normalize my database
  models"), the agent evaluates your intent against the `description` fields in
  the YAML. If there is a match, it dynamically injects the full Markdown
  instructions into the active context.
- **Execution Phase:** The agent follows the instructions, which includes
  cleanly invoking your determinist local Bash or Python scripts located in the
  skill's `scripts/` directory.

**3. Integrating the Multi-Agent Orchestrator** To satisfy your requirement of
having different models handle different tasks (e.g., a heavy model for
architecture planning and a fast/local model for running scripts), you integrate
**Control Primitives** from the Agent Development Kit (ADK) into your execution
flow:

- **`SequentialAgent`:** You can use this primitive to run specialized
  sub-agents linearly. It guarantees that the consolidated output of your
  high-effort planning agent is cleanly passed into the context window of your
  low-effort script-running agent.
- **`LoopAgent`:** If your scripts involve validation (like linting or testing),
  you can use this primitive to create an autonomous self-correction cycle. It
  utilizes an execution agent and a Judge agent, looping the task until the
  Judge issues a "pass" state or hits a maximum iteration limit.
- **State-Based Handoffs:** For highly complex workflows, you can completely
  decouple the agents by using repository labels (like GitHub PR tags). An
  Architect agent can plan the app and apply a `ready-for-dev` label, which
  immediately signals the local Engineer agent to pick up the task and execute
  the bash scripts, entirely asynchronously.

By using this architecture, your project remains lightweight and untouched by AI
configuration files, while the overarching workspace dynamically pulls exactly
the right rules, scripts, and multi-agent models needed for the task at hand.
