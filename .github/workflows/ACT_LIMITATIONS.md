# Known Limitations of act with This Repository

This document describes known limitations when running GitHub Actions locally with `act` in this repository.

## Composite Actions Not Fully Supported

**Issue**: The repository uses custom composite actions (`.github/actions/setup-environment` and `.github/actions/pip-install`). These may not work correctly with act.

**Error Message**:
```
failed to read 'action.yml' from action 'Setup environment' with path '' of step: file does not exist
```

**Why**: act has limitations with local composite actions using relative paths (e.g., `uses: ./.github/actions/setup-environment`).

**Workarounds**:

### Option 1: Test Individual Workflow Steps

Instead of running the full workflow, test individual script executions:

```bash
# Instead of: act -j test-python
# Run the tests directly:
python -m pytest tests/ -v

# Instead of: act -j test-shell
# Run the shell tests directly:
bash tests/test_retry_logic.sh
bash tests/test_health_checks.sh
```

### Option 2: Create Simplified Test Workflows

Create temporary workflow files without composite actions:

```bash
# Create a simplified version
cat > /tmp/simple-test.yml << 'EOF'
name: Simple Test
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/ -v
EOF

# Run with act
act -W /tmp/simple-test.yml
```

### Option 3: Use act with GitHub Public Actions Only

Modify workflows temporarily to use GitHub's public actions instead of local composite actions.

## Workflows That Work

These workflows and jobs can be tested with act (with limitations):

✅ **Individual Script Testing**: All Python scripts can be tested directly  
✅ **Build Profile** (partial): Can test individual phases  
✅ **Release Validation**: Validation logic works  
⚠️ **Tests**: Requires workarounds due to composite actions  
⚠️ **Monitoring**: Some jobs work, others depend on GitHub API

## Workflows with Known Issues

### tests.yml

**Issue**: Uses `.github/actions/setup-environment` composite action

**Workaround**: Run tests directly instead:
```bash
# Python tests
python -m pytest tests/ -v

# Shell tests
bash tests/test_retry_logic.sh
```

### build-profile.yml

**Issue**: Complex workflow with many dependencies and secrets

**What Works**:
- Individual script steps can be tested
- Data fetching scripts work if secrets are provided
- Card generation scripts work with existing data

**What Doesn't Work**:
- Full workflow execution
- GitHub Pages deployment
- Some API integrations

**Workaround**: Test specific scripts:
```bash
# Test developer stats script
python scripts/fetch-developer-stats.py szmyty test-output.json

# Test card generation
python scripts/generate-developer-dashboard.py developer/stats.json output.svg
```

### monitoring.yml

**Issue**: Depends on workflow_run events and GitHub API for metrics

**What Works**:
- Status page generation (if data files exist)

**What Doesn't Work**:
- Workflow metrics collection
- GitHub issue creation
- Workflow_run triggered jobs

### release.yml

**Issue**: Requires specific tag or workflow_dispatch event

**What Works**:
- Validation steps
- CHANGELOG parsing
- Version checking

**What Doesn't Work**:
- GitHub Release creation (requires actual GitHub API)
- Deployment triggering

## General Limitations

### 1. GitHub API Actions

Actions that create/update GitHub resources won't work:
- Creating releases
- Opening issues
- Updating pull requests
- GitHub Pages deployment

### 2. Secrets and Environment

- GitHub-provided secrets won't be available
- Must provide your own in `.secrets` file
- Some environment variables may differ from actual GitHub Actions

### 3. Runner Images

- act uses Docker images that approximate GitHub runners
- Some tools or versions may differ
- Resource constraints may differ

### 4. Caching

- GitHub Actions cache is not available
- Must download dependencies each time
- No cross-run state preservation

### 5. Matrix Builds

- Matrix strategies work but can be slow
- No parallelization like in GitHub Actions
- Resource intensive locally

## Recommended Testing Strategy

Given these limitations, here's the recommended approach:

### 1. Unit Testing (Local)

Test individual scripts and functions:
```bash
# Python unit tests
python -m pytest tests/ -v

# Shell script tests
bash tests/test_retry_logic.sh

# Type checking
python -m mypy scripts/
```

### 2. Integration Testing (Local with act)

Test simplified workflows:
```bash
# Create minimal workflow files
# Test specific logic paths
# Use mock data where possible
```

### 3. Full Workflow Testing (GitHub)

For full end-to-end testing:
- Push to a feature branch
- Let GitHub Actions run
- Review the actual CI results

### 4. Script-Level Testing (Direct Execution)

Most valuable for this repository:
```bash
# Test fetching
GITHUB_TOKEN=xxx python scripts/fetch-developer-stats.py szmyty output.json

# Test generation
python scripts/generate-developer-dashboard.py developer/stats.json output.svg

# Test with dev mode
./scripts/dev-mode.sh all
```

## Future Improvements

Potential ways to improve act compatibility:

1. **Refactor Composite Actions**: Convert to reusable workflows or inline steps
2. **Add act-specific Workflows**: Create simplified versions specifically for local testing
3. **Mock Services**: Add local mocks for GitHub API interactions
4. **Documentation**: Keep this document updated as act evolves

## When to Use act

**Good Use Cases**:
- ✅ Testing workflow syntax changes
- ✅ Debugging environment issues
- ✅ Validating workflow structure
- ✅ Testing simple, linear workflows
- ✅ Quick iteration on workflow logic

**Not Recommended**:
- ❌ Testing workflows with composite actions
- ❌ Testing GitHub API integrations
- ❌ Testing deployment workflows
- ❌ Testing complex multi-job workflows

## Conclusion

While act has limitations with this repository's workflows (primarily due to composite actions), it's still valuable for:

1. Validating workflow YAML syntax
2. Testing individual script execution
3. Understanding workflow structure
4. Learning GitHub Actions concepts

For full integration testing, use feature branches and actual GitHub Actions runs.

---

**Last Updated**: December 2025  
**act Version**: 0.2.83+
