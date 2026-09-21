import unittest
from unittest.mock import patch


class _Doc:
	"""Minimal stand-in for a Sales Invoice document."""

	def __init__(self, send_via_peppol=0, is_new=False, changed=False):
		self._values = {"send_via_peppol": send_via_peppol}
		self._is_new = is_new
		self._changed = changed

	def get(self, key, default=None):
		return self._values.get(key, default)

	def is_new(self):
		return self._is_new

	def has_value_changed(self, key):
		return self._changed


class TestValidatePeppolEnabled(unittest.TestCase):
	def setUp(self):
		from peppol_4_erpnext.peppol_4_erpnext import sales_invoice

		self.sales_invoice = sales_invoice

	def _validate(self, doc, enabled):
		"""Run the guard with PEPPOL Settings.enabled forced to *enabled*.

		Returns the frappe mock; a throw surfaces as RuntimeError.
		"""
		with patch.object(self.sales_invoice, "frappe") as mock_frappe:
			mock_frappe.db.get_single_value.return_value = enabled
			mock_frappe.throw.side_effect = RuntimeError("thrown")
			self.sales_invoice.validate_peppol_enabled(doc)
		return mock_frappe

	def test_unflagged_invoice_is_never_checked(self):
		"""Not marked for PEPPOL: the setting is not even read."""
		for is_new in (True, False):
			with self.subTest(is_new=is_new):
				mock_frappe = self._validate(_Doc(send_via_peppol=0, is_new=is_new), enabled=0)
				mock_frappe.db.get_single_value.assert_not_called()

	def test_new_invoice_may_be_flagged_when_enabled(self):
		self._validate(_Doc(send_via_peppol=1, is_new=True), enabled=1)

	def test_new_invoice_may_not_be_flagged_when_disabled(self):
		with self.assertRaises(RuntimeError):
			self._validate(_Doc(send_via_peppol=1, is_new=True), enabled=0)

	def test_raising_the_flag_when_disabled_is_blocked(self):
		with self.assertRaises(RuntimeError):
			self._validate(_Doc(send_via_peppol=1, is_new=False, changed=True), enabled=0)

	def test_raising_the_flag_when_enabled_is_allowed(self):
		self._validate(_Doc(send_via_peppol=1, is_new=False, changed=True), enabled=1)

	def test_already_flagged_invoice_stays_saveable_after_the_toggle_goes_off(self):
		"""Turning PEPPOL off must not make existing marked invoices unsaveable."""
		mock_frappe = self._validate(_Doc(send_via_peppol=1, is_new=False, changed=False), enabled=0)
		mock_frappe.throw.assert_not_called()
		mock_frappe.db.get_single_value.assert_not_called()

	def test_guard_is_registered_for_both_doc_events(self):
		from peppol_4_erpnext import hooks

		events = hooks.doc_events["Sales Invoice"]
		path = "peppol_4_erpnext.peppol_4_erpnext.sales_invoice.validate_peppol_enabled"
		self.assertEqual(events["validate"], path)
		self.assertEqual(events["on_update_after_submit"], path)
