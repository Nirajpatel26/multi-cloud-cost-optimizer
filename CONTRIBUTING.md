# Contributing to Multi-Cloud Cost Optimizer

Thank you for your interest in contributing to this project!

## Development Workflow

### Branch Strategy
- `main` - Production-ready code
- `develop` - Integration branch for features
- `staging` - Pre-production testing
- `feature/*` - Feature development branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Critical production fixes

### Getting Started

1. **Fork and Clone**
   ```bash
   git clone https://github.com/Nirajpatel26/multi-cloud-cost-optimizer.git
   cd multi-cloud-cost-optimizer
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set Up Environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Update .env with your credentials
   # Start services
   docker-compose up -d
   ```

### Development Guidelines

#### Backend (Python/FastAPI)
- Follow PEP 8 style guide
- Use type hints
- Write docstrings for all functions/classes
- Maintain test coverage above 80%
- Run tests before committing:
  ```bash
  cd backend
  pytest
  black .
  flake8
  ```

#### Frontend (React)
- Follow Airbnb React/JSX Style Guide
- Use functional components with hooks
- Write PropTypes for all components
- Run linting:
  ```bash
  cd frontend
  npm run lint
  npm test
  ```

#### Terraform
- Format code: `terraform fmt`
- Validate: `terraform validate`
- Document all variables and outputs

### Commit Messages
Follow conventional commits format:
```
type(scope): subject

body (optional)

footer (optional)
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(backend): add AWS cost analysis endpoint

- Implement Cost Explorer API integration
- Add data aggregation logic
- Include unit tests

Closes #123
```

### Pull Request Process

1. **Update develop branch**
   ```bash
   git checkout develop
   git pull origin develop
   ```

2. **Rebase your feature branch**
   ```bash
   git checkout feature/your-feature
   git rebase develop
   ```

3. **Push and create PR**
   ```bash
   git push origin feature/your-feature
   ```

4. **PR Requirements**
   - Clear description of changes
   - Link to related issues
   - All tests passing
   - Code review approval required
   - No merge conflicts

### Testing

#### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

#### Frontend Tests
```bash
cd frontend
npm test -- --coverage
```

#### Integration Tests
```bash
pytest tests/integration/ -v
```

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed
- [ ] Error handling implemented
- [ ] Logging added where appropriate

### Release Process

1. Merge `develop` to `staging`
2. Test in staging environment
3. Create release PR from `staging` to `main`
4. Tag release: `git tag -a v1.0.0 -m "Release v1.0.0"`
5. Push tag: `git push origin v1.0.0`

## Questions?

Open an issue or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.