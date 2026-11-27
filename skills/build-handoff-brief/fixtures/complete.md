# Build brief

## Goal
Add a CSV export to the trips report.

## Repo
- Remote: https://github.com/example/trips
- Default branch: main

## Constraints
- Python 3.12, no new dependencies.

## Assumptions
- The trips API connector already works; auth is out of scope.

## Who runs it
- The requester runs the export by hand from the CLI.

## Deliverables

### Builder ships
- A PR adding `export_csv.py` and a test.

### Requester runs
- Runs `python export_csv.py` monthly and uploads the file.

## Success criteria
- [ ] Tests pass.

## Out of scope
- Scheduling and token refresh.

## Merge policy
- PR target: main

## Who to notify
- On PR ready: open the PR.
