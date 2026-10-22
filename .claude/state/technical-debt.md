# Technical Debt Log: Cryptography Pedagogy Platform

## Initial Assessment
* Currently, no technical debt has accumulated as project implementation has not begun.
* Architectural principle: Maintain strict separation between core mathematical algorithms (`core/`), web API schemas (`api/`), and frontend components (`frontend/`).
* Avoid relying on heavy external C-extensions where pure Python arithmetic allows full inspection of step-by-step state.
