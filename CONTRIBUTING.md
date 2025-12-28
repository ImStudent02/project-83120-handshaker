# Contributing to Project 83120 - Handshaker

Thank you for your interest in contributing! This document provides guidelines for contributing to the Handshaker signaling server.

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- MongoDB
- Git

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/your-username/project-83120-handshaker.git
cd project-83120-handshaker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio  # For testing

# Copy environment file
cp .env.example .env
# Edit .env with your local config

# Run server
uvicorn app.main:app --reload
```

## 📝 Code Guidelines

### Python Style

- Follow PEP 8
- Use type hints for all functions
- Maximum line length: 100 characters
- Use meaningful variable names

### Example Function

```python
async def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Retrieve a user by their unique ID.

    Args:
        user_id: The user's unique identifier

    Returns:
        User object if found, None otherwise
    """
    return await db.users.find_one({"_id": user_id})
```

### Commit Messages

Use conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Adding tests

Example: `feat: add password reset with OTP`

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=app
```

## 📬 Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Add/update tests
4. Update documentation if needed
5. Submit PR with clear description

### PR Template

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

- [ ] Tests added/updated
- [ ] All tests passing

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Documentation updated
```

## 🔍 Areas for Contribution

### Good First Issues

- Add input validation
- Improve error messages
- Add logging
- Write tests

### Intermediate

- WebSocket signaling (replace polling)
- Rate limiting
- Connection request expiry

### Advanced

- TURN server integration
- Push notifications
- Admin dashboard

## ❓ Questions?

Open an issue with the `question` label.

Thank you for contributing! 🎉
