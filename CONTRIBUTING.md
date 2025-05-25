# Contributing to Kubernetes Deployment Manager

We welcome contributions to the Kubernetes Deployment Manager! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/ota-deploy-tracker.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate it: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
5. Install dependencies: `pip install -r requirements.txt`

## Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Add tests for your changes
4. Run the test suite: `pytest`
5. Run linting: `ruff check --fix .`
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Code Standards

- Follow PEP 8 for Python code style
- Use type hints where appropriate
- Write comprehensive tests for new features
- Update documentation for any API changes
- Use conventional commit messages

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov=cli --cov=dashboard

# Run specific test files
pytest tests/test_api.py
```

## Code Quality

We use Ruff for linting and formatting:

```bash
# Check for issues
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Format code
ruff format .
```

## Submitting Changes

1. Ensure all tests pass
2. Update documentation if needed
3. Add your changes to the changelog (if applicable)
4. Submit a pull request with a clear description of your changes

## Reporting Issues

When reporting issues, please include:

- Python version
- Kubernetes version
- Steps to reproduce
- Expected behavior
- Actual behavior
- Any relevant logs or error messages

## License

By contributing, you agree that your contributions will be licensed under the MIT License.