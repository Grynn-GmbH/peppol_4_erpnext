"""Pin what Frappe Cloud checks before it will install this app.

`press/api/github.py::app` is the "Add App from GitHub" gate. It is not a
warning path — each of these is a hard `frappe.throw` that stops the app being
added at all:

  * `pyproject.toml` at the repository root
  * a top-level directory holding both `hooks.py` and `patches.txt`
  * `app_title = "..."` in that hooks.py, matched by regex
  * `[tool.bench.frappe-dependencies]` with a `frappe` key

The last one is the easy one to lose: nothing in a local bench needs it, so it
can be deleted and every test but this one still passes, right up until someone
tries to deploy. bench reads the same table to warn on a mismatched bench
(`bench/app.py::validate_app_dependencies`).
"""

import os
import re
import unittest

try:  # tomllib is 3.11+; a Frappe 15 bench may be on 3.10
	import tomllib
except ModuleNotFoundError:  # pragma: no cover
	try:
		import tomli as tomllib
	except ModuleNotFoundError:
		tomllib = None

APP = "peppol_4_erpnext"


def _repo_root():
	import peppol_4_erpnext

	return os.path.dirname(os.path.dirname(os.path.abspath(peppol_4_erpnext.__file__)))


def _spec_majors(spec: str) -> tuple[int, int]:
	"""(lower, upper) major versions out of a '>=15.0.0,<17.0.0' SimpleSpec."""
	lower = re.search(r">=\s*(\d+)", spec)
	upper = re.search(r"<\s*(\d+)", spec)
	assert lower and upper, spec
	return int(lower.group(1)), int(upper.group(1))


@unittest.skipIf(tomllib is None, "no TOML parser available")
class TestFrappeCloudPackaging(unittest.TestCase):
	def setUp(self):
		path = os.path.join(_repo_root(), "pyproject.toml")
		self.assertTrue(os.path.exists(path), "pyproject.toml must sit at the repository root")
		with open(path, "rb") as fh:
			self.pyproject = tomllib.load(fh)

	def test_frappe_dependencies_table_exists(self):
		"""Without this, Frappe Cloud refuses to add the app from GitHub."""
		deps = self.pyproject.get("tool", {}).get("bench", {}).get("frappe-dependencies", {})
		self.assertTrue(deps.get("frappe"), "[tool.bench.frappe-dependencies] frappe is required")
		self.assertTrue(deps.get("erpnext"), "erpnext is a required_app, so pin it too")

	def test_declared_range_matches_the_versions_the_app_claims(self):
		"""pyproject and install.py must not drift apart."""
		from peppol_4_erpnext import install

		deps = self.pyproject["tool"]["bench"]["frappe-dependencies"]
		for app in ("frappe", "erpnext"):
			with self.subTest(app=app):
				lower, upper = _spec_majors(deps[app])
				self.assertEqual(lower, install.MIN_MAJOR)
				self.assertEqual(upper, install.MAX_TESTED_MAJOR + 1)


class TestAppStructure(unittest.TestCase):
	"""The structural gates in press/api/github.py."""

	def test_app_directory_holds_hooks_and_patches(self):
		app_dir = os.path.join(_repo_root(), APP)
		for name in ("hooks.py", "patches.txt"):
			with self.subTest(name=name):
				self.assertTrue(os.path.exists(os.path.join(app_dir, name)))

	def test_hooks_declares_app_title_in_the_form_press_parses(self):
		with open(os.path.join(_repo_root(), APP, "hooks.py"), encoding="utf-8") as fh:
			content = fh.read()
		# The exact regex press uses.
		match = re.search(r'app_title\s*=\s*["\']([^"\']+)["\']', content)
		self.assertIsNotNone(match, "press cannot read app_title out of hooks.py")

	def test_app_name_matches_the_directory(self):
		from peppol_4_erpnext import hooks

		# press returns the directory name as the app name; bench needs it to agree.
		self.assertEqual(hooks.app_name, APP)
