# Agent Rules

This file defines the rules and standards that the Agent must follow when working on this project.

## 1. Type Checking Compliance
All code must satisfy **BasedPyright** Standard Type Check requirements.

- **Strict Compliance**: Ensure 0 errors in `basedpyright` output for all Python files.
- **Exception**: **Matplotlib** related calls are exempt from strict type checking. Use `# type: ignore` to suppress errors specifically related to `matplotlib` or `plt` calls if they cannot be resolved otherwise.
- **Argparse**: Strictly type `argparse` arguments using `NamedTuple` or similar structures to ensure `parser.parse_args()` returns typed objects, avoiding `Any`.

## 2. Single Responsibility Principle (SRP)
The project structure and file contents must adhere to the Single Responsibility Principle.

- **File Level**: Each file should have a single, well-defined purpose (e.g., data loading, plotting, optimization, script entry point). Avoid "god files" that do everything.
- **Function/Class Level**: Functions and classes should do one thing and do it well. Decouple logic (e.g., physical models) from side effects (e.g., I/O, plotting).
- **Project Structure**: Maintain a clear separation of concerns (e.g., `src/models`, `src/visualization`, `src/scripts`, `src/optimizer`).
