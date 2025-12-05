# act Compatibility Matrix

Quick reference for which workflows work with `act` in this repository.

## Workflow Compatibility

| Workflow | File | act Status | Notes |
|----------|------|-----------|-------|
| **act Demo** | `act-demo.yml` | ✅ Works | Purpose-built for act testing |
| **Unit Tests** | `tests.yml` | ⚠️ Limited | Uses composite actions - see workarounds |
| **Build Profile** | `build-profile.yml` | ⚠️ Partial | Complex dependencies - test individual jobs |
| **Monitoring** | `monitoring.yml` | ⚠️ Partial | Some jobs work, others need GitHub API |
| **Release** | `release.yml` | ⚠️ Partial | Validation works, release creation doesn't |
| **Greetings** | `greetings.yml` | ❌ No | Requires GitHub API (issues/PRs) |

## Legend

- ✅ **Works**: Fully functional with act
- ⚠️ **Limited/Partial**: Some features work, others require workarounds
- ❌ **No**: Cannot run with act due to dependencies

## Recommended Testing Approach

### 1. Start with act-demo.yml ✨

```bash
# Best workflow to test act setup
act -j list-files -W .github/workflows/act-demo.yml
act -j check-environment -W .github/workflows/act-demo.yml
```

**Why**: No composite actions, minimal dependencies, demonstrates act features

### 2. Test Scripts Directly

```bash
# Python tests
python -m pytest tests/ -v

# Shell tests
bash tests/test_retry_logic.sh

# Card generation with mock data
./scripts/dev-mode.sh all
```

**Why**: Fastest feedback loop, no Docker overhead, works reliably

### 3. Use act for Workflow Syntax Validation

```bash
# Dry run to check syntax
act -n -W .github/workflows/build-profile.yml

# List all jobs
act -l
```

**Why**: Validates YAML structure without execution

### 4. Use GitHub Actions for Integration Testing

Push to a feature branch and let CI run the full workflows.

**Why**: Complete environment, all features work, true integration tests

## Specific Job Compatibility

### tests.yml Jobs

| Job | Status | Command | Alternative |
|-----|--------|---------|-------------|
| `test-python` | ⚠️ Limited | `act -j test-python` | `python -m pytest tests/ -v` |
| `test-shell` | ⚠️ Limited | `act -j test-shell` | `bash tests/test_*.sh` |

**Issue**: Uses `.github/actions/setup-environment` composite action

### build-profile.yml Jobs

The workflow has one large job (`build-profile`) that's difficult to test with act due to:
- Multiple API dependencies (GitHub, weather, location, etc.)
- Composite actions
- Resource requirements
- GitHub Pages deployment

**Recommendation**: Test individual scripts instead:

```bash
# Test developer stats
GITHUB_TOKEN=xxx python scripts/fetch-developer-stats.py username output.json

# Test card generation
python scripts/generate-developer-dashboard.py developer/stats.json output.svg

# Test with mock data
./scripts/dev-mode.sh developer
```

### monitoring.yml Jobs

| Job | Status | Command | Alternative |
|-----|--------|---------|-------------|
| `generate-status-page` | ✅ Works | `act -j generate-status-page` | Direct script execution |
| `log-megalinter-results` | ⚠️ Limited | N/A | Requires workflow_run event |
| `check-failures` | ⚠️ Limited | N/A | Requires GitHub API for issues |

### release.yml Jobs

| Job | Status | Command | Alternative |
|-----|--------|---------|-------------|
| `validate` | ✅ Works | `act -j validate` | Good for testing validation logic |
| `release` | ❌ No | N/A | Requires GitHub Releases API |

## Tips for Working with act

### 1. Use the Demo Workflow

The `act-demo.yml` workflow is specifically designed to work with act:

```bash
# Run all jobs
act -W .github/workflows/act-demo.yml

# Run specific job
act -j list-files -W .github/workflows/act-demo.yml
```

### 2. Test Individual Steps

Create temporary workflow files to test specific logic:

```bash
cat > /tmp/test-step.yml << 'EOF'
name: Test Step
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python scripts/my-script.py
EOF

act -W /tmp/test-step.yml
```

### 3. Use Dry Run

Check what would execute without actually running:

```bash
act -n -W .github/workflows/act-demo.yml
```

### 4. Direct Script Testing

Most reliable for this repository:

```bash
# All tests
python -m pytest tests/ -v
bash tests/test_retry_logic.sh

# Type checking
python -m mypy scripts/

# Card generation
./scripts/dev-mode.sh all
```

## Common act Commands

```bash
# List all workflows and jobs
act -l

# Run specific job
act -j <job-name>

# Run workflow file
act -W .github/workflows/act-demo.yml

# Dry run
act -n -j <job-name>

# With secrets
act -j <job-name> --secret-file .secrets

# Verbose output
act -v -j <job-name>

# Use different event
act push -W .github/workflows/act-demo.yml
act workflow_dispatch -W .github/workflows/release.yml
```

## Quick Start for New Users

1. **Install and Configure** (done automatically in devcontainer)
   ```bash
   act --version
   ```

2. **Test the Demo**
   ```bash
   act -j list-files -W .github/workflows/act-demo.yml
   ```

3. **Try Direct Testing**
   ```bash
   python -m pytest tests/ -v
   ```

4. **Read the Documentation**
   - [ACT_SETUP.md](ACT_SETUP.md) - Complete setup guide
   - [ACT_LIMITATIONS.md](ACT_LIMITATIONS.md) - Known issues and workarounds
   - [LOCAL_DEVELOPMENT.md](../../docs/LOCAL_DEVELOPMENT.md) - Full development guide

## When to Use What

| Need | Use This | Why |
|------|----------|-----|
| Test workflow syntax | `act -n` | Fast validation |
| Test simple workflow | `act-demo.yml` | No dependencies |
| Test Python code | `pytest` | Fastest, most reliable |
| Test shell scripts | Direct execution | No Docker overhead |
| Test card generation | `dev-mode.sh` | Mock data included |
| Integration testing | GitHub Actions | Full environment |
| Debug composite actions | GitHub Actions | act has limitations |

## Summary

**act works best for**:
- ✅ Workflow syntax validation
- ✅ Simple, linear workflows
- ✅ Testing environment setup
- ✅ Learning GitHub Actions

**For this repository, prefer**:
- 🎯 Direct script testing (`pytest`, shell scripts)
- 🎯 Development mode (`dev-mode.sh`)
- 🎯 GitHub Actions for full integration tests

---

**See Also**:
- [ACT_SETUP.md](ACT_SETUP.md) - Complete guide to using act
- [ACT_LIMITATIONS.md](ACT_LIMITATIONS.md) - Detailed limitations and workarounds
- [LOCAL_DEVELOPMENT.md](../../docs/LOCAL_DEVELOPMENT.md) - Full local development guide
