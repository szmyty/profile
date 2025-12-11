# Contributing to Profile

Thank you for your interest in contributing to this project! 🎉

This repository primarily serves as a personal GitHub profile with dynamic content, but contributions of any kind are welcome and appreciated.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Recognition](#recognition)
- [Pull Request Process](#pull-request-process)
- [Development Setup](#development-setup)

## 📜 Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this standard. Please be respectful, constructive, and collaborative.

## 🤝 How Can I Contribute?

### Reporting Bugs

If you find a bug:
1. Check if the issue already exists in the [Issues](https://github.com/szmyty/profile/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs. actual behavior
   - Environment details (OS, browser, etc.)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:
1. Check existing issues/PRs for similar suggestions
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Potential implementation approach (if applicable)

### Code Contributions

Contributions to improve documentation, fix bugs, or add features are welcome:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Test your changes
5. Commit your changes with clear commit messages
6. Push to your fork
7. Open a Pull Request

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Poetry (for Python dependency management)
- npm (for Node.js dependencies)

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/szmyty/profile.git
   cd profile
   ```

2. **Install Python dependencies:**
   ```bash
   poetry install
   ```

3. **Install Node.js dependencies:**
   ```bash
   npm install
   cd dashboard-app && npm install
   ```

4. **Run tests:**
   ```bash
   poetry run pytest
   ```

5. **Build the dashboard:**
   ```bash
   cd dashboard-app
   npm run build
   ```

## ✨ Recognition

This project uses the [All Contributors](https://allcontributors.org/) specification to recognize all contributors.

### Contributor Types

We recognize various types of contributions, including:

- 💻 **Code** - Writing code
- 🎨 **Design** - Design work
- 🤔 **Ideas** - Ideas and planning
- 📖 **Documentation** - Documentation improvements
- 🚧 **Maintenance** - Repository maintenance
- 🚇 **Infrastructure** - Infrastructure improvements
- 🔧 **Tools** - Tool development
- 🤖 **Automation** - Automation improvements

### How to Get Recognition

#### Automatic Recognition

When you contribute via Pull Request, you can request recognition by commenting:

```
@all-contributors please add @your-username for code, doc
```

Replace `your-username` with your GitHub username and specify the contribution types.

#### Manual Addition

Maintainers can also add contributors manually using:

```bash
npm run contributors:add -- your-username code,doc
npm run contributors:generate
```

### AI and Bot Contributions

This project transparently recognizes automated and AI-assisted contributions:
- GitHub Actions bots that automate workflows
- GitHub Copilot for AI-assisted code generation
- Other automation tools that contribute to the project

## 🔄 Pull Request Process

1. **Update Documentation**: Update README.md or other docs if needed
2. **Test Your Changes**: Ensure all tests pass
3. **Follow Code Style**: Use the existing code style
4. **Clear Commit Messages**: Write descriptive commit messages
5. **Link Issues**: Reference related issues in your PR description
6. **Request Review**: Maintainers will review your PR
7. **Address Feedback**: Respond to review comments
8. **Merge**: Once approved, your PR will be merged

### Commit Message Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Maintenance tasks

Example:
```
feat: add weather widget to dashboard
```

## 🛠️ Development Setup

### Running Linters

```bash
# Python
poetry run black .
poetry run isort .
poetry run flake8 .
poetry run mypy .

# MegaLinter (runs all linters)
# See .megalinter.yml for configuration
```

### Pre-commit Hooks

This project uses pre-commit hooks. Install them with:

```bash
poetry run pre-commit install
```

## 📫 Questions?

If you have questions:
- Open an issue with the `question` label
- Check existing documentation
- Review closed issues for similar questions

## 🙏 Thank You!

Your contributions help make this project better for everyone. Thank you for taking the time to contribute!

---

*This project maintains high standards for code quality, security, and documentation. All contributions are valued and appreciated.*
