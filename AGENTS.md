# llms-authority repository rules

This public repository contains the one canonical public `llms.txt` authority for TeleCrypt.
It is deliberately small: do not add a second architecture description, generated site, build
system, or operational procedure here.

## Scope

- Keep `llms.txt` limited to public product and architecture facts, named component
  responsibilities, security and privacy principles, and current user-visible behavior and
  limits.
- Keep billing transaction mechanics, provider operations, internal rationale, history, private
  endpoints, credentials, and deployment procedures in their owning private or operational
  repositories. Do not copy them here.
- Do not add placeholder or example `llms.txt` content. A release is invalid until the reviewed
  file exists and passes the local validator.
- TeleCrypt Messenger (`TeleCrypt-app`) and Flexisip are separate applications and are outside
  this repository's scope.

## Release and Pages contract

- The only deploy workflow is `.github/workflows/pages.yml`.
- Pages runs only from a published, non-draft, non-prerelease, immutable GitHub Release whose tag
  is an exact numeric semantic version (`vMAJOR.MINOR.PATCH`).
- The workflow checks out and verifies that exact annotated tag's commit. It must never deploy
  from a branch or a mutable default-branch ref.
- The repository is source-only for release purposes: Releases have no uploaded assets. Pages
  receives only the reviewed `llms.txt` file.
- Pin every GitHub Action to an exact version. Keep workflow permissions to the minimum needed for
  read-only source/release inspection and Pages deployment.

Run the offline contract tests with `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`.
