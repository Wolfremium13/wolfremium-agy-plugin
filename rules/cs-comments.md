**The overarching heuristic rule for your agent is: Comments should describe
things that aren't obvious from the code itself.**

Before writing a comment, the agent should follow this decision-making framework
to determine whether a comment is necessary and how to structure it:

### Phase 1: Ask "Can this comment be eliminated by better code?"

Before leaving a comment, the agent must evaluate if the code can be refactored
to speak for itself.

- **Can the type system explain it?** Guide the reader by giving APIs distinct
  types first, as types are enforced by the compiler. Do not say anything in a
  method name or comment that you can say with a type.
- **Can a name explain it?** If the comment simply explains what a block of code
  does, **extract that block into a function and give it a well-thought-out
  name**. You should favor well-named methods over comments.
- **Does it explain _HOW_ the code works?** If a comment details the mechanics
  of the implementation, it should be deleted. The code already shows how it
  operates; **commenting on the "how" is redundant and violates the DRY (Don't
  Repeat Yourself) principle**.
- **Does it repeat the code?** If someone could write the exact same comment
  just by looking at the code next to it (e.g., using the same words that make
  up the method name), the comment provides no value and must be removed.

### Phase 2: When to write comments

If the information cannot be cleanly expressed through types or names, the agent
should use comments to capture the informal, abstract, or hidden context.

- **Document the "Why":** Use comments to explain the purpose, goals,
  engineering trade-offs, and why certain alternatives were discarded.
- **Document the Abstraction (Interface Comments):** Write comments immediately
  preceding a class or method to provide a high-level, simplified view of its
  behavior. **These should hide implementation details so a developer can use
  the module without reading its internal code**. Include preconditions, side
  effects, exceptions, and return values.
- **Add Precision to Variables:** Use lower-level comments to clarify exact
  meanings that code cannot express, such as units of measurement (e.g., pixels,
  milliseconds), inclusive/exclusive boundary conditions, or what a `null` value
  implies.
- **Enhance Intuition:** Inside long methods, add higher-level comments before
  major blocks of code to summarize _what_ the block is trying to achieve
  abstractly, helping readers navigate without parsing the details.
- **Document Surprises and Quirks:** Use comments to explain complex regular
  expressions, surprising behaviors from third-party libraries, or workarounds
  for bugs.

### Phase 3: The "Comments as a Design Tool" Check

The agent should use the act of commenting to evaluate its own design choices.

- **Write the comments _first_:** The agent should draft the interface comments
  before filling in the method bodies.
- **Watch for the "Hard to Describe" red flag:** **If the agent finds it
  difficult to write a simple yet complete comment for a method or variable,
  this is a major red flag indicating a flawed design or a bad abstraction**.
  The agent should take this as a cue to rethink the code structure.

### Phase 4: Maintenance Guidelines

- **Keep comments close to the code:** To prevent comments from becoming stale,
  always place them immediately next to the code they describe.
- **Do not use the commit log for code documentation:** Crucial design decisions
  and the subtle reasons behind a bug fix must be documented in the code, not
  just in the Git commit message, because future developers will rarely look in
  the logs when reading the source file.
