# Contributing

Thank you for considering contributing to OWL Server! This document provides guidelines and instructions for contributing to the project.

## Development Environment

### Prerequisites

- Python 3.10 or later
- Git

### Setup

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/owl-mcp.git
   cd owl-mcp
   ```

3. Sync your `uv`:
   ```bash
   uv sync --all-extras
   ```


## Development Workflow

### Running Tests

Tests are written using pytest. To run the tests:

```bash
make test
```

To run a specific test:

```bash
uv run pytest tests/test_owl_api.py::test_add_axiom
```

### Code Formatting

We use Black for code formatting and isort for import sorting:

```bash
uv run black src tests
uv run isort src tests
```

### Type Checking

We use mypy for type checking:

```bash
uv run mypy src
```

### Documentation

We use mkdocs with the Material theme for documentation. To build and serve the documentation locally:

```bash
mkdocs serve
```

Then visit http://127.0.0.1:8000/ in your web browser.

## Pull Request Process

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and ensure all tests pass:
   ```bash
   make test
   ```

3. Update the documentation if necessary.

4. Add your changes to git and commit them:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

5. Push your branch to GitHub:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a pull request against the `main` branch of the original repository.

### Pull Request Guidelines

- Keep pull requests focused on a single issue or feature.
- Include tests for new functionality or bug fixes.
- Update documentation as needed.
- Ensure all tests pass and code is properly formatted.
- Provide a clear description of what your pull request changes or fixes.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## License

By contributing to OWL Server, you agree that your contributions will be licensed under the same license as the project.