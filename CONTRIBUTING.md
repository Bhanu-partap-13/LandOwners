# Contributing to Land Owners OCR System

Thank you for your interest in contributing to the Land Owners OCR System! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/LandOwners.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `npm test` (frontend) and `pytest` (backend)
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r tests/requirements.txt
python app.py
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## Code Style

### Python
- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Maximum line length: 100 characters

### JavaScript/React
- Use ES6+ syntax
- Follow Airbnb React style guide
- Use functional components with hooks
- Write JSDoc comments for complex functions

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

## Pull Request Guidelines

1. **Title**: Use a clear and descriptive title
2. **Description**: Explain what changes you made and why
3. **Tests**: Add tests for new features
4. **Documentation**: Update README.md if needed
5. **Code Quality**: Ensure all tests pass and code follows style guidelines

## Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat(ocr): Add support for Punjabi language

- Add Punjabi language detection
- Update Tesseract configuration for Punjabi
- Add Punjabi test cases

Closes #123
```

## Feature Requests

To request a new feature:
1. Check existing issues to avoid duplicates
2. Create a new issue with the "feature request" label
3. Describe the feature and its use case
4. Explain why it would be valuable

## Bug Reports

When reporting bugs, include:
1. Description of the bug
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. Screenshots (if applicable)
6. Environment details (OS, Python/Node version, etc.)

## Code Review Process

1. All submissions require review
2. Maintainers will review your PR within 7 days
3. Address any requested changes
4. Once approved, a maintainer will merge your PR

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Questions?

Feel free to open an issue for any questions or concerns.

Thank you for contributing! 🎉
