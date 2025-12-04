# Master Repository Repair Plan

**Generated**: 2025-12-04

**Status**: CRITICAL - Multiple Workflow Failures

**Total Issues**: 5 critical, 24 warnings

---

## Executive Summary

The repository audit has identified a **critical architectural issue** causing all dashboard workflows to fail:

### Root Cause
Workflows are attempting to use a composite action (`.github/actions/setup-environment`) **before** checking out the repository code. The composite action includes the checkout step, but the workflow runner cannot access the action definition because the repository hasn't been checked out yet.

### Impact
- ❌ Developer Dashboard workflow: **FAILING**
- ❌ SoundCloud Card workflow: **FAILING**  
- ❌ Oura Health Dashboard workflow: **FAILING**
- ❌ Weather Card workflow: **FAILING** (recent failure)
- ⚠️ Location Card workflow: **CANCELLED**
- ⚠️ All data files missing (workflows never execute successfully)
- ⚠️ README markers exist but cards not updated

---

## Critical Fix Required

### Issue #1: Composite Action Ordering (CRITICAL)

**Problem**: Workflows reference `.github/actions/setup-environment` before checkout

**Error Message**:
```
Can't find 'action.yml', 'action.yaml' or 'Dockerfile' under 
'/home/runner/work/profile/profile/.github/actions/setup-environment'. 
Did you forget to run actions/checkout before running your local action?
```

**Affected Workflows**:
- `.github/workflows/developer.yml`
- `.github/workflows/soundcloud-card.yml`
- `.github/workflows/oura.yml`
- `.github/workflows/weather.yml`
- `.github/workflows/location-card.yml`
- `.github/workflows/parallel-fetch.yml`

**Solution**: Add explicit `actions/checkout@v4` step BEFORE using composite action

**Implementation**:

For each affected workflow, change from:
```yaml
steps:
  - name: Setup environment
    uses: ./.github/actions/setup-environment
    with:
      extra-apt-packages: ''
```

To:
```yaml
steps:
  - name: Checkout repository
    uses: actions/checkout@v4
    with:
      fetch-depth: 1
      
  - name: Setup environment
    uses: ./.github/actions/setup-environment
    with:
      extra-apt-packages: ''
```

**Note**: The composite action still includes checkout internally, which will be a no-op on second execution (GitHub Actions handles this gracefully). Alternatively, remove checkout from the composite action.

---

## Secondary Issues

### Issue #2: Missing Data Files

**Problem**: All API data files are missing
- `data/developer/stats.json` - Missing
- `data/soundcloud/latest_track.json` - Missing  
- `data/weather/current.json` - Missing
- `data/location/current.json` - Missing
- `data/oura/daily_summary.json` - Missing

**Root Cause**: Workflows have been failing so data never gets created

**Solution**: Will resolve automatically once Issue #1 is fixed and workflows run successfully

---

### Issue #3: Missing Output SVG

**Problem**: Location card SVG is missing
- `location/location-card.svg` - Not found

**Root Cause**: Same as Issue #2 - workflow failures

**Solution**: Will resolve automatically once workflows run

---

### Issue #4: Token Reference Warnings

**Problem**: Several workflows have inconsistent token references

**Affected Files**:
- `developer.yml` - Line ~38
- `location-card.yml`
- `parallel-fetch.yml`  
- `weather.yml`
- `deploy-dashboard.yml`

**Current Pattern**: Mix of `${{ github.token }}` and `${{ secrets.GITHUB_TOKEN }}`

**Recommended**: Use `${{ secrets.GITHUB_TOKEN }}` consistently for clarity

**Priority**: LOW (current pattern works, but inconsistent)

---

## Implementation Plan

### Phase 1: Fix Critical Composite Action Issue (IMMEDIATE)

**Files to modify**:
1. `.github/workflows/developer.yml`
2. `.github/workflows/soundcloud-card.yml`
3. `.github/workflows/oura.yml`
4. `.github/workflows/weather.yml`
5. `.github/workflows/location-card.yml`
6. `.github/workflows/parallel-fetch.yml`

**Change**: Add explicit `actions/checkout@v4` before composite action call

**Expected Result**: All workflows should execute successfully

**Verification**:
- Monitor workflow runs
- Check for data file creation in `data/` directory
- Verify SVG generation
- Confirm README updates

---

### Phase 2: Refactor Composite Action (OPTIONAL)

**Two Options**:

**Option A**: Keep checkout in composite action (current)
- Pro: Single action handles everything
- Con: Requires explicit checkout before use (current issue)
- Implementation: Keep as-is, require checkout before use

**Option B**: Remove checkout from composite action
- Pro: More flexible, clearer separation of concerns
- Con: Requires explicit checkout in every workflow
- Implementation: Remove checkout step from `.github/actions/setup-environment/action.yml`

**Recommendation**: Option A (current) + Fix workflow ordering

---

### Phase 3: Consistency Improvements (OPTIONAL)

1. **Token References**: Standardize to `secrets.GITHUB_TOKEN`
2. **Caching**: Add caching to workflows currently missing it:
   - `monitoring.yml`
   - `tests.yml`
   - `megalinter.yml`
3. **Python Caching**: Ensure all Python workflows use cache
4. **Documentation**: Update workflow documentation

---

## Audit Findings Summary

### Workflow Audit (`workflow_audit.md`)
- ✅ All workflows have valid YAML syntax
- ❌ 5 workflows have token reference issues
- ⚠️ 12 warnings about missing checkout actions
- ⚠️ Several workflows missing caching optimization

### Pipeline Status (`pipeline_status.md`)
- ✅ All scripts exist
- ✅ All generators exist  
- ✅ All SVGs exist (except location)
- ❌ ALL data files missing
- ✅ All README markers present

### README Audit (`readme_audit.md`)
- ✅ All injection markers present and correctly ordered
- ✅ All image paths valid (SVGs exist in repo)
- ✅ No malformed HTML/Markdown
- ✅ No broken links to internal files

### File System Audit (`filesystem_audit.txt`)
- ✅ No orphaned temp files
- ✅ No large files (>1MB) causing bloat
- ✅ Log directories properly structured
- ✅ Data directories exist with proper structure

### Theme & Schema Audit (`theme_schema_audit.md`)
- ✅ `theme.json` valid and complete
- ✅ All required sections present (colors, fonts, spacing)
- ✅ All schema files valid JSON
- ✅ No schema validation errors

### Script Health (`script_health.md`)
- ✅ All Python scripts readable
- ⚠️ Some scripts missing shebangs
- ⚠️ Some scripts missing docstrings
- ⚠️ Some scripts have hardcoded paths

### Data Integrity (`data_integrity.md`)
- ✅ All existing JSON files valid
- ✅ Metrics files populated correctly
- ✅ Mock data files present and valid
- ✅ Snapshot files structured correctly
- ❌ Production data files missing (expected due to workflow failures)

---

## Success Criteria

### Phase 1 Complete When:
- [ ] All 6 workflows modified with explicit checkout
- [ ] All workflows run without errors
- [ ] Data files created successfully
- [ ] SVG cards generated
- [ ] README updated with current cards

### System Healthy When:
- [ ] No workflow failures for 24 hours
- [ ] All cards displaying in README
- [ ] All data files present and < 24 hours old
- [ ] All scheduled runs completing successfully

---

## Risk Assessment

**Risk Level**: LOW  
**Complexity**: LOW  
**Testing Required**: MEDIUM

**Risks**:
- Minimal code change required (6 workflow files)
- Change is additive (adding checkout step)
- No breaking changes to existing functionality
- Easily reversible if issues occur

**Mitigation**:
- Test on one workflow first (e.g., weather.yml)
- Monitor for successful completion
- Roll out to remaining workflows incrementally
- Keep composite action unchanged initially

---

## Estimated Timeline

- **Phase 1 (Critical Fix)**: 15 minutes
  - Modify 6 workflow files: 10 min
  - Test first workflow: 3 min
  - Deploy remaining: 2 min

- **Phase 2 (Verification)**: 30-60 minutes
  - Wait for scheduled runs
  - Verify data generation
  - Check README updates

- **Phase 3 (Optional Improvements)**: 1-2 hours
  - Token standardization
  - Add caching
  - Documentation updates

**Total Critical Fix**: 15 minutes  
**Total with Verification**: 45-75 minutes

---

## Next Steps

1. ✅ Audit Complete
2. **→ Implement Phase 1 Fix** (6 workflow files)
3. **→ Test & Verify** (monitor workflow runs)
4. **→ Optional: Phase 2 & 3 improvements**

---

## Notes

- The composite action design is sound, just needs proper usage
- No code quality issues detected in scripts or generators
- Theme and schema system working correctly  
- File structure is clean and well-organized
- Issue is purely a workflow configuration problem

**Conclusion**: This is a **simple fix** with **high impact**. Adding 5 lines to each of 6 workflows will restore full functionality to all dashboard cards.
