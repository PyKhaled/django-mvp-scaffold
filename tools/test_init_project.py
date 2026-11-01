import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from init_project import initialize


class InitializeTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        (self.root / "product" / "settings").mkdir(parents=True)
        (self.root / "product" / "settings" / "common.py").write_text("")
        (self.root / "product" / "imports.py").write_text("from helpdesk.models import Ticket\n")
        (self.root / ".env.example").write_text("SECRET_KEY=\n")
        (self.root / "pyproject.toml").write_text(
            '[dependency-groups]\nbase = ["Django==5.2.17", "Pillow==13.0.0"]\n'
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_rejects_django_package_name(self):
        with self.assertRaisesRegex(ValueError, "does not shadow"):
            initialize(self.root, "my-project", "django", "owner/repository", dry_run=True)

    def test_rejects_dependency_import_name(self):
        with self.assertRaisesRegex(ValueError, "does not shadow"):
            initialize(self.root, "my-project", "helpdesk", "owner/repository", dry_run=True)

    def test_rejects_distribution_module_alias(self):
        with self.assertRaisesRegex(ValueError, "does not shadow"):
            initialize(self.root, "my-project", "pil", "owner/repository", dry_run=True)

    def test_accepts_a_nonconflicting_package_name(self):
        with (
            patch("init_project.subprocess.check_output", return_value=b"\0"),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            initialize(self.root, "my-project", "my_project", "owner/repository", dry_run=True)


if __name__ == "__main__":
    unittest.main()
