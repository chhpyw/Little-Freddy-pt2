# Repository Guidelines

Welcome to the **codex-ollama** repository. This guide provides the necessary standards and workflows to ensure consistency and quality across the project.

## Project Structure & Module Organization
Since this project is currently in its initial phase, we follow a modular approach. All core logic should be organized as follows:
- `/src`: Primary source code.
- `/tests`: Unit and integration tests.
- `/docs`: Documentation and architectural diagrams.
- `/scripts`: Automation and build utility scripts.

## Build, Test, and Development Commands
Standard development commands are provided to streamline the workflow:
- `npm install`: Install project dependencies.
- `npm run dev`: Start the development server with hot-reloading.
- `npm run build`: Compile the project for production.
- `npm test`: Execute the full test suite.

## Coding Style & Naming Conventions
We prioritize readability and maintainability:
- **Indentation**: Use 2 spaces for indentation.
- **Naming**: 
  - Variables and functions: `camelCase`.
  - Classes and Components: `PascalCase`.
  - Constants: `UPPER_SNAKE_CASE`.
- **Linting**: All code must pass the project's ESLint and Prettier configuration before being committed.

## Testing Guidelines
Quality assurance is mandatory for all new features:
- **Framework**: We use Jest for unit testing.
- **Naming**: Test files must follow the `.test.ts` or `.spec.ts` suffix (e.g., `auth.test.ts`).
- **Coverage**: Aim for a minimum of 80% code coverage for core modules.

## Commit & Pull Request Guidelines
To maintain a clean project history, please follow these rules:
- **Commits**: Use conventional commits (e.g., `feat: add ollama api integration` or `fix: resolve memory leak in stream handler`).
- **Pull Requests**:
  - Provide a clear description of the changes.
  - Link any related issues.
  - Include screenshots or logs if the change affects the UI or CLI output.
  - Ensure all tests pass in the CI pipeline.

## Agent-Specific Instructions
When contributing via AI agents, please ensure that you analyze the existing codebase for patterns before introducing new dependencies or architectural changes.
