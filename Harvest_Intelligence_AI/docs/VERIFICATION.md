# Phase 1 verification

- Automated verification: `python -m pytest -q` — 30 passed.
- Covered: every supplied numeric result; partial allocations and surplus caps; repeated matching; duplicate rejection; missing/negative/non-finite input; custom mapping; zero and negative returns; SQLite snapshot round-trip and invalid-write preservation; Streamlit startup, navigation, Tamil labels and shared state.
- Live local server: health endpoint returned HTTP 200 (`ok`); entry page returned HTTP 200.
- Runtime: Python 3.12; direct package versions recorded in requirements-tested.txt.
- Full seven-screen judging workflow is pending later phases. Assistant prioritisation is not implemented or claimed in Phase 1.
- Manual browser/mobile layout and actual Windows execution were not performed in this environment.
