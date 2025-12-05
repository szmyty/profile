# Running GitHub Actions Locally with `act`

This repository is configured to run GitHub Actions workflows locally using [act](https://github.com/nektos/act).

## Prerequisites

- Docker must be running
- `act` CLI tool (automatically installed in devcontainer)

## Quick Start

### List Available Workflows

```bash
# List all jobs in all workflows
act -l

# List jobs for a specific event
act push -l
act pull_request -l
act workflow_dispatch -l
```

### Run Individual Jobs

```bash
# Run Python tests
act -j test-python

# Run shell script tests
act -j test-shell

# Run the entire tests workflow
act -W .github/workflows/tests.yml

# Run with specific event
act push -W .github/workflows/tests.yml
```

## Configuration

### Secrets

Create a `.secrets` file in the repository root (already in `.gitignore`):

```bash
# Copy the example file
cp .secrets.example .secrets

# Edit with your tokens
nano .secrets
```

The `.secrets` file should contain:

```
GITHUB_TOKEN=your_github_token_here
MAPBOX_TOKEN=your_mapbox_token_here
OURA_PAT=your_oura_token_here
```

### Environment Variables

The `.actrc` file in the repository root contains default configuration:

- Uses `catthehacker/ubuntu:act-latest` as the default runner image
- Enables verbose output
- Automatically uses `GITHUB_TOKEN` from environment

## Testing Individual Workflows

### 1. Tests Workflow

```bash
# Run all test jobs
act -W .github/workflows/tests.yml

# Run only Python tests
act -j test-python

# Run only shell tests
act -j test-shell
```

### 2. Build Profile Workflow

```bash
# Run the entire build profile workflow
act -W .github/workflows/build-profile.yml

# Note: This workflow is complex and may require secrets
# Use with --secret-file flag:
act -W .github/workflows/build-profile.yml --secret-file .secrets
```

### 3. Monitoring Workflow

```bash
# Run monitoring job
act -j generate-status-page -W .github/workflows/monitoring.yml
```

### 4. Release Workflow

```bash
# Run release validation (requires manual trigger)
act workflow_dispatch -W .github/workflows/release.yml --eventpath .github/workflows/act-events/workflow_dispatch.json
```

## Advanced Usage

### Custom Event Payloads

Use custom event payloads from `.github/workflows/act-events/`:

```bash
# Push event
act push --eventpath .github/workflows/act-events/push.json

# Pull request event
act pull_request --eventpath .github/workflows/act-events/pull_request.json

# Workflow dispatch
act workflow_dispatch --eventpath .github/workflows/act-events/workflow_dispatch.json
```

### Dry Run

See what would run without actually executing:

```bash
act -n -W .github/workflows/tests.yml
```

### Debugging

```bash
# Extra verbose output
act -v -W .github/workflows/tests.yml

# Show environment variables
act --env-file .env -W .github/workflows/tests.yml
```

### Specify Container Architecture

```bash
# Run with specific architecture (useful for M1/M2 Macs)
act -j test-python --container-architecture linux/amd64
```

## Known Limitations

⚠️ **Important**: This repository uses custom composite actions that have limited support in act. See [ACT_LIMITATIONS.md](ACT_LIMITATIONS.md) for details and workarounds.

**Key limitations**:
- Workflows using `.github/actions/setup-environment` may not run correctly
- Consider testing scripts directly or using simplified workflow versions
- Full integration testing should use actual GitHub Actions

## Common Issues

### Composite Action Errors

If you see: `failed to read 'action.yml' from action 'Setup environment'`

This is a known limitation with local composite actions. See [ACT_LIMITATIONS.md](ACT_LIMITATIONS.md) for workarounds.

**Quick fix**: Test scripts directly instead:
```bash
# Instead of: act -j test-python
python -m pytest tests/ -v
```

### Docker Socket Permission

If you see permission errors with Docker:

```bash
sudo chmod 666 /var/run/docker.sock
```

### Large Workflows

Some workflows (like `build-profile.yml`) are resource-intensive. Consider:

1. Running individual jobs instead of the full workflow
2. Using a larger Docker image
3. Increasing Docker resource limits

### Composite Actions

The repository uses custom composite actions (`.github/actions/*`). These are supported by `act` but may need:

- Docker-in-Docker to be properly configured
- All dependencies to be available in the runner image

### Missing Secrets

If a workflow fails due to missing secrets:

1. Check that `.secrets` file exists and contains required tokens
2. Use `--secret-file .secrets` flag
3. Or set environment variables: `export GITHUB_TOKEN=your_token`

## Best Practices

1. **Start Small**: Test individual jobs before running entire workflows
2. **Use Secrets File**: Keep sensitive data in `.secrets` (not committed)
3. **Check Event Types**: Use `act -l` to see which events trigger which jobs
4. **Resource Management**: Large workflows may need more Docker resources
5. **Iterate Quickly**: Use `act -j <job-name>` for fast feedback loops

## Workflow-Specific Notes

### `tests.yml`

- Runs fast and requires no secrets
- Good starting point for testing act setup
- Uses composite action `.github/actions/setup-environment`

### `build-profile.yml`

- Requires multiple secrets (MAPBOX_TOKEN, OURA_PAT, etc.)
- Resource-intensive (installs Node, Python, system packages)
- Consider running specific phases/jobs instead of the entire workflow
- Some steps may be skipped in local runs (e.g., GitHub Pages deployment)

### `monitoring.yml`

- Requires workflow_run event to fully test
- Some jobs check for previous workflow runs (may not work locally)

### `release.yml`

- Requires tag or workflow_dispatch event
- Validation steps work well locally
- GitHub Release creation will fail (requires actual GitHub API)

## Troubleshooting

### Check Docker is Running

```bash
docker ps
```

### Verify act Installation

```bash
act --version
```

### Test with Minimal Workflow

```bash
# Create a simple test
act -j test-python --dryrun
```

### View Logs

```bash
# Run with verbose output
act -v -j test-python 2>&1 | tee act-debug.log
```

## Resources

- [act Documentation](https://github.com/nektos/act)
- [nektos/act Wiki](https://nektosact.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
