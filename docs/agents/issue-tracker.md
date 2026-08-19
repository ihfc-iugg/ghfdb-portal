# Issue tracker: GitHub

Issues for this repo live as GitHub issues. Use the `gh` CLI for all operations.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v` — `gh` does this automatically when run inside a clone.

## Pull requests as a triage surface

**PRs as a request surface: no.**

The portal accepts community bug reports through issues and gathers feature input through GitHub
Discussions, not through unsolicited pull requests. The contributing guide asks contributors to
discuss new features with the maintainers before starting work.

GitHub shares one number space across issues and PRs, so a bare `#42` may be either — resolve with
`gh pr view 42` and fall back to `gh issue view 42`.

## Discussions

This repo uses GitHub Discussions for feature prioritisation, including standing polls on portal
and map-viewer priorities. Discussions are a source of user demand, not a work queue: a discussion
that turns into committed work gets an issue.

## Vocabulary

A written process that says "publish to the issue tracker" means create a GitHub issue. One that
says "fetch the relevant ticket" means run `gh issue view <number> --comments`.
