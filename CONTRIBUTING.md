# Contributing to DocProcessor

## Before You Start

Read the [LICENSE](LICENSE). Contributions are accepted only under the same license terms. By submitting a pull request you agree that your contribution will be distributed under those terms.

## How to Contribute

### Reporting Bugs

Open an issue with:
- OS and Python version
- Full error output
- Minimal reproduction (file type, command run)

Do **not** attach real documents — they may contain sensitive data.

### Proposing Changes

Open an issue before writing code for anything non-trivial. Changes that add scope, new dependencies, or alter the JSON schema require discussion first.

Keep the pipeline linear. The three-stage architecture (extract → categorize → output) is intentional — resist adding stages or cross-stage dependencies.

### Submitting a Pull Request

1. Fork and create a feature branch from `main`.
2. Set up the dev environment:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"
   ```
3. Make focused changes. One concern per PR.
4. Run lint before pushing:
   ```bash
   ruff check doc_processor/
   ruff format --check doc_processor/
   ```
5. Write or update tests if behavior changes.
6. Update `README.md` if the interface or output schema changes.
7. Open the PR against `main` with a clear description of *why*, not just *what*.

### Code Style

- Formatter: `ruff format` (line length 100)
- Linter: `ruff check`
- Type hints on all public functions
- No comments explaining *what* the code does — only *why* when non-obvious
- No print statements in library code; raise exceptions instead

### Commit Messages

Conventional Commits format:

```
type(scope): short description

Optional longer explanation of why, not what.
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

### What Will Not Be Merged

- New system dependencies beyond PyMuPDF, Tesseract, Pillow, Anthropic SDK
- Changes that break the JSON output schema without a version bump
- Code that sends documents or extracted text to any service other than the Anthropic API
- Hardcoded API keys or credentials of any kind
- AI-generated contributions that have not been reviewed and understood by the submitter

## Questions

Open a GitHub Discussion, not an issue.
