# Description

Please include a summary of the change and which issue is fixed. Please also include relevant motivation and context. List any dependencies that are required for this change.

Fixes # (issue)

## Type of change

Please add a line in the relevant section of [CHANGELOG.md]() to document the change (include PR #) - note reverse order of PR #s. If necessary, also add to the list of breaking changes.

- [ ] New feature (non-breaking change which adds functionality)
- [ ] Optimization (back-end change that improves speed/readability/etc.)
- [ ] Bug fix (non-breaking change which fixes an issue)

# Key checklist:

- [ ] No style issues: `$ nox -s linter [-- format]` (the `format` option will try to fix errors)
- [ ] Docstrings/comments are free of misspellings: `$ nox -s codespell [-- write]` (the `write` option will try to fix errors)
- [ ] All tests pass: `$ nox -s tests`
- [ ] New badges have been generated: `$ nox -s badges`

You can also run all of the above checks using `$ nox -s pre-commit` instead of running them individually.

## Further checks:

- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Tests are added that prove fix is effective or that feature works
