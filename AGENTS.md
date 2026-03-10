## Skills
### Available skills
- smart-commit: Format repository changes with `ruff` when available, separate style-only and logic changes into focused git commits, and push the current branch. Use automatically at the end of any completed repository task that modifies tracked files, unless the user explicitly says not to commit or not to push. (file: /home/lys74/DEV/Macro-Pulse/.agent/skills/smart-commit/SKILL.md)

### How to use skills
- Discovery: The list above is the repository-local skills available in this workspace. Skill bodies live on disk at the listed path.
- Trigger rules: Apply `smart-commit` automatically for any turn in this repository that ends with file changes in a reviewable state. Do not wait for the user to name the skill. Skip only when the user explicitly says not to commit or not to push, or when no tracked files changed.
- Missing/blocked: If the skill path cannot be read, say so briefly and continue with the best fallback.
