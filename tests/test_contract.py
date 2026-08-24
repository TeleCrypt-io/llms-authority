"""Offline contract tests for the llms-authority repository scaffold."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
VALIDATOR = ROOT / "scripts/validate-llms.py"
LLMS = ROOT / "llms.txt"


class RepositoryContractTests(unittest.TestCase):
    def test_authority_content_is_present_and_in_scope(self) -> None:
        self.assertTrue(LLMS.is_file())
        self.assertEqual(self.run_validator(LLMS).returncode, 0)
        self.assertIn("https://telecrypt-io.github.io/llms-authority/llms.txt", (ROOT / "README.md").read_text())
        self.assertTrue((ROOT / "LICENSE").read_text().startswith("Business Source License 1.1\n"))
        self.assertIn("Business Source License", (ROOT / "README.md").read_text())

    def test_authority_contains_current_public_contract(self) -> None:
        content = LLMS.read_text(encoding="utf-8")
        for phrase in (
            "Matrix",
            "Synapse",
            "Matrix Authentication Service",
            "Controlplane",
            "Cashier",
            "Janitor",
            "S3-compatible object store",
            "128 MiB",
            "50 GiB",
            "federation",
            "End-to-end encryption",
        ):
            self.assertIn(phrase, content)
        for private_or_operational in ("Dodo", "webhook", "private endpoint", "transaction mechanics"):
            self.assertNotIn(private_or_operational.lower(), content.lower())

    def test_workflow_is_release_only_and_pinned(self) -> None:
        self.assertIn("release:\n    types: [published]", WORKFLOW)
        self.assertNotRegex(WORKFLOW, r"(?m)^\s+(push|pull_request|workflow_dispatch|schedule):")
        self.assertIn("github.event.release.draft == false", WORKFLOW)
        self.assertIn("github.event.release.prerelease == false", WORKFLOW)
        self.assertIn(".immutable == true", WORKFLOW)
        self.assertIn(
            r"^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$",
            WORKFLOW,
        )
        self.assertIn("ref: ${{ github.event.release.tag_name }}", WORKFLOW)
        self.assertIn('git cat-file -t "refs/tags/$RELEASE_TAG"', WORKFLOW)
        self.assertIn('test "$release_commit" = "$(git rev-parse HEAD)"', WORKFLOW)
        self.assertNotRegex(WORKFLOW, r"refs/heads/main|ref:\s*main|github\.sha")
        for action in (
            "actions/checkout@v7.0.1",
            "actions/configure-pages@v6.0.0",
            "actions/upload-pages-artifact@v5.0.0",
            "actions/deploy-pages@v5.0.0",
        ):
            self.assertIn(action, WORKFLOW)
        self.assertIn("pages: write", WORKFLOW)
        self.assertIn("id-token: write", WORKFLOW)
        self.assertIn("python3 scripts/validate-llms.py llms.txt", WORKFLOW)
        self.assertIn("install -m 0644 -- llms.txt", WORKFLOW)
        self.assertIn("path: ${{ runner.temp }}/llms-pages-root", WORKFLOW)

    def run_validator(self, path: Path) -> subprocess.CompletedProcess[str]:
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        return subprocess.run(
            [sys.executable, str(VALIDATOR), str(path)],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_validator_accepts_minimal_public_content(self) -> None:
        with tempfile.TemporaryDirectory(prefix="llms-authority-test-") as directory:
            candidate = Path(directory) / "llms.txt"
            candidate.write_text(
                "# TeleCrypt\n\n"
                "TeleCrypt is a private-by-design service.\n"
                "Password login is disabled, credentials are never stored, and webhooks are not public.\n",
                encoding="utf-8",
            )
            result = self.run_validator(candidate)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_validator_rejects_missing_or_private_content(self) -> None:
        with tempfile.TemporaryDirectory(prefix="llms-authority-test-") as directory:
            base = Path(directory)
            missing = self.run_validator(base / "missing.txt")
            self.assertNotEqual(missing.returncode, 0)
            for content in (
                "# TeleCrypt\n\nProvider endpoint: https://test.checkout.dodopayments.com/session.\n",
                "# TeleCrypt\n\nPrivate endpoint: https://backend.telecrypt.io.\n",
                "# TeleCrypt\n\napi_key=sk_test_1234567890abcdefghijklmnop\n",
                "# TeleCrypt\n\nCard number: 4111 1111 1111 1111\n",
                "# TeleCrypt\n\nCVV: 123\n",
                "# Other\n\nPublic content.\n",
                "# TeleCrypt\n\nNo final newline",
            ):
                candidate = base / "candidate.txt"
                candidate.write_text(content, encoding="utf-8")
                self.assertNotEqual(self.run_validator(candidate).returncode, 0, content)


if __name__ == "__main__":
    unittest.main()
