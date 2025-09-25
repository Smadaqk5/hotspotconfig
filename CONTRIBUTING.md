# Contributing to MikroTik Hotspot Config Generator

Thank you for your interest in contributing to the MikroTik Hotspot Config Generator! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 16+ (for frontend assets)
- Git
- PostgreSQL (for local development)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/mikrotik-hotspot-config-generator.git
   cd mikrotik-hotspot-config-generator
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   npm install
   ```

4. **Set up Environment Variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run Database Migrations**
   ```bash
   python manage.py migrate
   python manage.py loaddata sample_data.sql
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

## 📝 Development Guidelines

### Code Style

#### Python
- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused
- Use type hints where appropriate

#### JavaScript/CSS
- Use consistent indentation (2 spaces)
- Follow TailwindCSS conventions
- Use meaningful class names
- Keep components small and reusable

### Git Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clean, readable code
   - Add tests for new functionality
   - Update documentation if needed

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```

4. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create pull request on GitHub
   ```

### Commit Message Format

Use the following format for commit messages:

```
type: brief description

Longer description if needed

- Bullet point for changes
- Another bullet point
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

## 🧪 Testing

### Running Tests
```bash
python manage.py test
```

### Writing Tests
- Write tests for new features
- Test edge cases and error conditions
- Aim for good test coverage
- Use descriptive test names

### Test Structure
```python
def test_feature_name():
    """Test description of what the test does."""
    # Arrange
    # Act
    # Assert
```

## 📚 Documentation

### Code Documentation
- Add docstrings to functions and classes
- Use clear, concise language
- Include parameter and return type information
- Add examples for complex functions

### API Documentation
- Update API_DOCUMENTATION.md for API changes
- Include request/response examples
- Document error codes and messages

### User Documentation
- Update README.md for major changes
- Add screenshots for UI changes
- Keep installation instructions up to date

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: OS, Python version, browser, etc.
6. **Screenshots**: If applicable
7. **Error Logs**: Any error messages or logs

## 💡 Feature Requests

When suggesting features:

1. **Problem**: Describe the problem you're trying to solve
2. **Solution**: Describe your proposed solution
3. **Alternatives**: Any alternative solutions you've considered
4. **Use Cases**: Who would benefit from this feature
5. **Implementation**: Any ideas about how to implement it

## 🔒 Security

### Reporting Security Issues
- **DO NOT** create public issues for security vulnerabilities
- Email security issues to: security@yourdomain.com
- Include detailed information about the vulnerability
- Allow time for the issue to be addressed before disclosure

### Security Best Practices
- Never commit secrets or API keys
- Use environment variables for sensitive data
- Validate all user inputs
- Follow OWASP guidelines
- Keep dependencies updated

## 📋 Pull Request Process

### Before Submitting
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] No merge conflicts
- [ ] Commit messages are clear

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
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## 🏷️ Labels and Milestones

### Labels
- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `priority: high`: High priority
- `priority: low`: Low priority

### Milestones
- `v1.0.0`: Initial release
- `v1.1.0`: Feature updates
- `v1.0.1`: Bug fixes

## 🤝 Community Guidelines

### Be Respectful
- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the community

### Communication
- Use clear, concise language
- Provide context for questions
- Be patient with newcomers
- Help others learn and grow

## 📞 Getting Help

### Resources
- **Documentation**: Check README.md and API_DOCUMENTATION.md
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Code Review**: Request reviews from maintainers

### Contact
- **Issues**: Use GitHub Issues for bug reports
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact maintainers directly for sensitive issues

## 🎯 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation
- GitHub contributors page

Thank you for contributing to the MikroTik Hotspot Config Generator! 🚀
