import unittest
from unittest.mock import patch


class TestMajor(unittest.TestCase):
	def setUp(self):
		from peppol_4_erpnext import install

		self.install = install

	def test_parses_release_and_dev_versions(self):
		for version, expected in (("15.0.0", 15), ("16.34.0", 16), ("16.0.0-dev", 16), ("17.1", 17)):
			self.assertEqual(self.install._major(version), expected, msg=version)

	def test_unparseable_version_raises_value_error(self):
		with self.assertRaises(ValueError):
			self.install._major("develop")


class TestCheck(unittest.TestCase):
	def setUp(self):
		from peppol_4_erpnext import install

		self.install = install

	def _check(self, version):
		"""Run _check with frappe patched out; return the mock for assertions."""
		with patch.object(self.install, "frappe") as mock_frappe:
			mock_frappe.throw.side_effect = RuntimeError("thrown")
			self.install._check("frappe", version)
		return mock_frappe

	def test_supported_majors_pass_silently(self):
		for version in ("15.0.0", "15.78.1", "16.0.0-dev", "16.34.0"):
			with patch("builtins.print") as mock_print:
				mock_frappe = self._check(version)
			mock_frappe.throw.assert_not_called()
			mock_print.assert_not_called()

	def test_older_major_is_rejected(self):
		with patch.object(self.install, "frappe") as mock_frappe:
			mock_frappe.throw.side_effect = RuntimeError("thrown")
			with self.assertRaises(RuntimeError):
				self.install._check("frappe", "14.9.0")
		mock_frappe.throw.assert_called_once()

	def test_newer_major_warns_but_installs(self):
		with patch("builtins.print") as mock_print:
			mock_frappe = self._check("17.0.0")
		mock_frappe.throw.assert_not_called()
		mock_print.assert_called_once()

	def test_unparseable_version_neither_throws_nor_warns(self):
		with patch("builtins.print") as mock_print:
			mock_frappe = self._check("develop")
		mock_frappe.throw.assert_not_called()
		mock_print.assert_not_called()
