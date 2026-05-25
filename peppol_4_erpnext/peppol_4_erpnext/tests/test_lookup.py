import unittest
from unittest.mock import MagicMock, patch


class TestSmpParticipantLookup(unittest.TestCase):
	"""Tests for smp_participant_lookup in lookup.py."""

	def _import(self):
		from peppol_4_erpnext.peppol_4_erpnext.lookup import smp_participant_lookup

		return smp_participant_lookup

	@patch("peppol_4_erpnext.peppol_4_erpnext.lookup._resolve_smp_host")
	def test_validate_only_returns_registered_without_xml_fetch(self, mock_resolve):
		"""validate_only=True skips XML fetch; returns registered=True on DNS hit."""
		mock_resolve.return_value = "smp.example.com"
		smp_participant_lookup = self._import()

		with patch(
			"peppol_4_erpnext.peppol_4_erpnext.lookup._query_service_group"
		) as mock_query, patch(
			"peppol_4_erpnext.peppol_4_erpnext.lookup._load_doctypes"
		) as mock_load:
			result = smp_participant_lookup("0088:123456789", validate_only=True)

		mock_query.assert_not_called()
		mock_load.assert_not_called()
		self.assertTrue(result["registered"])
		self.assertIn("participant_id", result)

	@patch("peppol_4_erpnext.peppol_4_erpnext.lookup.frappe")
	@patch("peppol_4_erpnext.peppol_4_erpnext.lookup._resolve_smp_host")
	def test_validate_only_false_when_dns_fails(self, mock_resolve, mock_frappe):
		"""validate_only=True returns registered=False and logs error when DNS raises."""
		mock_resolve.side_effect = Exception("DNS lookup failed")
		mock_frappe.log_error = MagicMock()
		smp_participant_lookup = self._import()

		result = smp_participant_lookup("0088:999999999", validate_only=True)

		self.assertFalse(result["registered"])
		mock_frappe.log_error.assert_called_once()

	@patch("peppol_4_erpnext.peppol_4_erpnext.lookup._resolve_smp_host")
	@patch("peppol_4_erpnext.peppol_4_erpnext.lookup._query_service_group")
	@patch("peppol_4_erpnext.peppol_4_erpnext.lookup._load_doctypes")
	@patch("peppol_4_erpnext.peppol_4_erpnext.lookup._extract_doctypes")
	def test_full_lookup_calls_xml_fetch(self, mock_extract, mock_load, mock_query, mock_resolve):
		"""validate_only=False (default) performs XML fetch and loads doctypes."""
		mock_resolve.return_value = "smp.example.com"
		mock_query.return_value = "<root/>"
		mock_extract.return_value = []
		smp_participant_lookup = self._import()

		result = smp_participant_lookup("0088:123456789", validate_only=False)

		mock_load.assert_called_once()
		mock_query.assert_called_once()
		self.assertTrue(result["registered"])
