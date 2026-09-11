"""Offline behavior tests for the llms.txt authority validator."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate-llms.py"
LLMS = ROOT / "llms.txt"


class AuthorityValidatorTests(unittest.TestCase):
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

    def test_authority_content_is_present_and_valid(self) -> None:
        self.assertTrue(LLMS.is_file())
        result = self.run_validator(LLMS)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_validator_accepts_minimal_public_content(self) -> None:
        with tempfile.TemporaryDirectory(delete=False, prefix="llms-authority-test-") as directory:
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
        with tempfile.TemporaryDirectory(delete=False, prefix="llms-authority-test-") as directory:
            base = Path(directory)
            missing = self.run_validator(base / "missing.txt")
            self.assertNotEqual(missing.returncode, 0)
            for content in (
                "# TeleCrypt\n\nProvider endpoint: https://test.checkout.dodopayments.com/session.\n",
                "# TeleCrypt\n\nPrivate endpoint: https://sss.telecrypt.io.\n",
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
