# Testing Ecosystem Documentation

This guide describes the complete testing infrastructure for ResumeAI, covering backend unit testing, frontend unit testing, security vulnerability scanning, load testing, and CI/CD pipelines.

---

## 🧪 Testing Types

1.  **Backend Pytest Suite**: Automates functional tests, mock integrations, and calculates code coverage.
2.  **Frontend Vitest Suite**: Renders components under `jsdom` (mock browser environment) and tests events/views.
3.  **Vulnerability Scanner (`security_audit.py`)**: Tests access bypasses, SQL injections, directory traversals, and XSS risks.
4.  **Load Test (`locustfile.py`)**: Models candidate request volume and measures latency.



## 🐍 Backend Testing (Pytest)

We transitioned from the standard Django test runner to `pytest` for faster test discovery, fixtures, and coverage diagnostics.

### Setup and Configuration
- **`pytest.ini`**: Registers django environments and discovery patterns.
- **`conftest.py`**: Defines database factories (`UserFactory`) and API clients (`api_client`).
- **`.coveragerc`**: Discovers real business logic while filtering migrations and setup scripts.

### Execution
Run tests locally with coverage verification:
```bash
cd backend
venv\Scripts\pytest --cov-config=.coveragerc --cov=.
```

---

## ⚛️ Frontend Testing (Vitest & RTL)

We use `Vitest` as the testing runner and `React Testing Library` (RTL) for rendering DOM interfaces.

### Setup and Configuration
- **`vitest.config.js`**: Integrates `@vitejs/plugin-react` and enables JSDOM.
- **`src/test/setup.js`**: Supplies matchers (`@testing-library/jest-dom`) and mocks window API properties (like `matchMedia`).

### Test Coverage Files
- **`src/test/Navbar.test.jsx`**: Validates landing links for guests and dashboard menus for logged-in candidates/admins.
- **`src/test/NotificationBell.test.jsx`**: Mocks notifications API to test badge counts and menu drawer interactions.

### Execution
Run tests:
```bash
cd frontend
npx vitest run
```

---

## 🚨 Security & Vulnerability Checks

The security scanner checks common web injection vulnerabilities against a running dev server:
- SQL injection payload handling.
- Cross-Site Scripting (XSS) input filtering.
- Directory traversal blocks.
- Authorization bypass barriers.

### Execution
Start your local server:
```bash
cd backend
venv\Scripts\python manage.py runserver
```
Run the scanner:
```bash
python scripts/security_audit.py
```

---

## ⚡ Load & Stress Testing

We use Locust to simulate concurrent user sessions.

### Execution
Install Locust and run:
```bash
pip install locust
locust -f scripts/locustfile.py
```
Open `http://localhost:8089` to target your host URL.

---

## 🎯 Target Coverage Metrics

| Component | Target Coverage | Tool |
| :--- | :--- | :--- |
| **Backend Core** | `90%` (Minimum `80%` CI block) | `pytest-cov` |
| **Frontend Components** | `80%` | `vitest --coverage` |
| **Critical Auth APIs** | `100%` | `pytest-cov` |
