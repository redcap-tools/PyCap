---
name: Release
about: Checklist for releases
title: 'Release version:'
labels: ''
assignees: ''

---

## To do
- [ ] Draft GitHub release
- [ ] Bump version: `poetry version minor`
- [ ] Run all tests/styling/linting: `pytest`
- [ ] Merge release PR
- [ ] Update cannonical documentation: `mkdocs gh-deploy`
- [ ] Publish to pypi: `poetry publish`
