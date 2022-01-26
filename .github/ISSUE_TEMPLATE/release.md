---
name: Release
about: Checklist for releases
title: 'Release version:'
labels: ''
assignees: ''

---

## To do
- [ ] Bump version: `poetry version minor`
- [ ] Run all tests/styling/linting: `pytest`
- [ ] Update cannonical documentation: `mkdocs gh-deploy`
- [ ] Merge release PR
- [ ] Publish to pypi: `poetry publish`
