# TeleCrypt public LLM authority

This repository will publish TeleCrypt's single canonical public `llms.txt` through GitHub Pages:

<https://telecrypt-io.github.io/llms-authority/llms.txt>

The file is intentionally absent until its reviewed public content is ready. Do not add a
placeholder to make a local build appear complete. The Pages workflow refuses a missing or invalid
file and deploys only that file from the exact immutable Release tag commit.

The repository is source-only and uses the Business Source License 1.1. Releases use exact
numeric tags such as `v1.2.3`, are published without assets, and are eligible for Pages only after
GitHub reports them as immutable and non-prerelease.

Run the offline repository/workflow checks from the repository root:

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests

The validator is intentionally local and deterministic; it does not fetch content or call GitHub.
