---
name: smart-commit
description: Format repository changes with ruff when available, separate style-only and logic changes into focused git commits, and push the current branch. Use automatically at the end of any completed repository task that modifies tracked files, unless the user explicitly says not to commit or not to push.
---

# Smart Commit

Execute this workflow automatically when a task in this repository finishes with tracked file changes in a reviewable state.

## Workflow

1. Inspect `git status --short` before staging anything.
2. Identify unrelated user changes and exclude them from the commit.
3. Check whether `ruff` is available.
4. If `ruff` is available, run `ruff format .`.
5. Inspect `git diff --name-only` after formatting.
6. If formatting changed files, stage only those formatting-only changes and commit them first.
7. Use the commit message `style: apply ruff formatting` for the formatting-only commit.
8. Re-check `git status --short` after the style commit.
9. Review the remaining diff and group only the task-relevant non-formatting changes.
10. Run the most relevant verification for those remaining changes before committing.
11. Write a focused non-interactive commit message for the remaining changes.
12. Stage only the files that belong in that logic commit.
13. Commit the remaining changes.
14. Push the current branch to `origin`.

## Rules

1. Keep style-only changes and logic changes in separate commits when both exist.
2. Do not create an empty formatting commit when `ruff format .` produces no diff.
3. Do not stage unrelated work just because it is already modified.
4. If `ruff` is unavailable, say so briefly and continue with only the non-formatting commit flow.
5. If verification fails, stop before committing and report the failure.
6. If the branch has no upstream, push with upstream creation.
7. If push fails because of auth, permissions, branch protection, or network issues, report the blocker immediately.
8. Skip the workflow only when the user explicitly says not to commit or not to push, or when the task produced no tracked file changes.
9. If unrelated modified files make a clean automatic commit ambiguous, stop and ask before committing.

## Commit Message Guidance

1. Prefer `type(scope): summary` when the scope is obvious.
2. Otherwise use `type: summary`.
3. Prefer `style`, `fix`, `feat`, `refactor`, `test`, `docs`, or `chore`.
4. Keep the summary imperative and specific to the finished unit.
