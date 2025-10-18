# Contributing to the Context Compression System & DRCC

👏 Thanks for your interest in improving Dynamic Runtime Context Compression! This guide summarises how to set up a development environment, propose changes, and keep the project healthy.

## 1. Getting Started

1. Fork the repository and clone your fork.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```
3. Run the quick-start pipeline to verify your environment:
   ```bash
   python -m src.cli compress claude \
     --source examples/sample_context.md \
     --output outputs/dev-check
   pytest
   ```

## 2. Branch & Commit Convention

- Use feature branches named `feature/...`, `fix/...`, or `docs/...`.
- Keep commits focused; reference GitHub issues when applicable.
- Update `CHANGELOG.md` with a short summary under the “Unreleased” section.

## 3. Coding Standards

- Type hints are encouraged throughout Python modules.
- Follow the existing bilingual comment style (English primary + Thai support where helpful).
- Ensure any new CLI options or config flags include docstrings and README notes.

## 4. Tests & Validation

- Add or update tests in the `tests/` directory for new behaviour.
- Every compression change must meet the round-trip rule: compressed output must expand back to the original text.
- `pytest` must pass locally before you open a pull request.

## 5. Documentation

- Update `README.md`, `docs/PROJECT.PROMPT.md`, and examples when behaviour changes.
- Provide sample Appendix E entries when you introduce new mapping fields.

## 6. Pull Request Checklist

- [ ] Tests pass (`pytest`)
- [ ] CHANGELOG updated
- [ ] README / docs updated
- [ ] Appendix E format adjusted if necessary
- [ ] Self-review for sensitive content (no secrets, no credentials)

We look forward to your ideas. DRCC is still young—every contribution helps shape the next generation of AI context reasoning! 🚀
