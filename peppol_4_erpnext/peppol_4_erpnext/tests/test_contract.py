"""Pin the wire contract tapr_next depends on.

tapr_next reaches this app in two ways: three whitelisted methods called by
dotted path, and a set of Purchase Invoice field names posted to
``/api/resource/Purchase Invoice``. Neither side had a test that named them, so
renaming a module, moving a function, renaming a keyword argument or dropping a
Custom Field passed green in both repos and failed only in production — as a 404,
a ``TypeError`` in a worker, or silently dropped data. See issues #12 and #15.

The tapr_next call sites each assertion mirrors are cited in the tests below.
Changing anything pinned here is a breaking change for every connected site: the
two apps are deployed separately, so a rename needs the receiving end to accept
both spellings until every site has upgraded.
"""

import inspect
import json
import os
import tempfile
import unittest
from unittest.mock import patch

# ── Whitelisted methods ───────────────────────────────────────────────────────

# path → (required kwargs, optional kwargs, allowed HTTP methods or None for the
# frappe default). Keys are exactly what tapr_next puts in the JSON body.
ENDPOINTS = {
	# tapr_next/accounts_receivable/adapters/erpnext_ar_client.py :: update_peppol_status.
	# The payload keys are this signature's parameter names: ERPNextARClient is the one
	# AR adapter that does NOT override ARERPClient.PEPPOL_STATUS_FIELDS, so it sends
	# the base identity map straight through.
	"peppol_4_erpnext.peppol_4_erpnext.api.update_peppol_status": (
		{"sales_invoice_name", "status"},
		{"document_name", "sent_on", "error", "mlr_status", "mlr_description"},
		None,
	),
	# tapr_next/peppol/code_list_forward.py :: _PUSH_ENDPOINT
	"peppol_4_erpnext.peppol_4_erpnext.code_list.update_peppol_code_list": (
		set(),
		{"code_list"},
		["POST"],
	),
	# tapr_next/peppol/code_list_forward.py :: _INFO_ENDPOINT
	"peppol_4_erpnext.peppol_4_erpnext.code_list.get_peppol_code_list_info": (
		set(),
		set(),
		["GET"],
	),
}

# tapr_next reads these off the info endpoint's reply (`message.version`).
CODE_LIST_INFO_KEYS = {"version", "entry_count", "source", "path", "modified"}

# Statuses tapr_next sends, in the order a delivered invoice moves through them.
# erp_sync.py lines 546 (Fetched), 651 (Sent), 625 (Delivered), 108 (Failed).
PEPPOL_STATUSES = ("Ready", "Fetched", "Sent", "Delivered", "Failed")


def _resolve(path):
	import frappe

	return frappe.get_attr(path)


class TestWhitelistedEndpointContract(unittest.TestCase):
	def test_every_endpoint_resolves(self):
		for path in ENDPOINTS:
			with self.subTest(path=path):
				self.assertTrue(callable(_resolve(path)))

	def test_every_endpoint_is_whitelisted(self):
		import frappe

		for path in ENDPOINTS:
			with self.subTest(path=path):
				# `whitelisted` is a list in v15 and a set in v16; `in` covers both.
				self.assertIn(_resolve(path), frappe.whitelisted)

	def test_allowed_http_methods(self):
		import frappe

		for path, (_required, _optional, methods) in ENDPOINTS.items():
			with self.subTest(path=path):
				registered = frappe.allowed_http_methods_for_whitelisted_func[_resolve(path)]
				if methods is None:
					# frappe's default when the decorator names none.
					self.assertEqual(sorted(registered), ["DELETE", "GET", "POST", "PUT"])
				else:
					self.assertEqual(registered, methods)

	def test_signatures_accept_what_tapr_next_sends(self):
		for path, (required, optional, _methods) in ENDPOINTS.items():
			with self.subTest(path=path):
				# @frappe.whitelist wraps with functools.wraps, so signature() follows
				# __wrapped__ back to the real function.
				params = inspect.signature(_resolve(path)).parameters
				accepted = set(params)

				missing = (required | optional) - accepted
				self.assertFalse(missing, f"{path} no longer accepts {sorted(missing)}")

				for name in required:
					self.assertIs(
						params[name].default,
						inspect.Parameter.empty,
						f"{path}: {name} must stay required",
					)
				for name in optional:
					self.assertIsNot(
						params[name].default,
						inspect.Parameter.empty,
						f"{path}: {name} must stay optional",
					)

	def test_update_peppol_status_accepts_every_status_tapr_next_pushes(self):
		"""The endpoint's allowlist must not drift from the statuses tapr_next sends."""
		from peppol_4_erpnext.peppol_4_erpnext import api

		# "Ready" is set locally by mark_invoice_for_peppol and never pushed in.
		pushed = [s for s in PEPPOL_STATUSES if s != "Ready"]

		for status in pushed:
			with self.subTest(status=status), patch.object(api, "frappe") as mock_frappe:
				mock_frappe.db.get_value.return_value = 1  # submitted
				mock_frappe.throw.side_effect = AssertionError(f"{status} was rejected")

				result = api.update_peppol_status("SINV-1", status)

				self.assertEqual(result, {"success": True, "status": status})

	def test_update_peppol_status_rejects_an_unknown_status(self):
		from peppol_4_erpnext.peppol_4_erpnext import api

		with patch.object(api, "frappe") as mock_frappe:
			mock_frappe.db.get_value.return_value = 1
			mock_frappe.throw.side_effect = RuntimeError("rejected")

			with self.assertRaises(RuntimeError):
				api.update_peppol_status("SINV-1", "Bogus")

	def test_status_callback_requires_a_role(self):
		"""update_peppol_status must gate access like the code list endpoints already do.

		tapr_next's single api_key/api_secret must already hold one of these roles for
		the code list push to work, so this is a no-op for a correctly configured
		integration. A site provisioned with a narrower role for this callback alone
		needs "PEPPOL Integration" granted explicitly. See issue #14.
		"""
		from peppol_4_erpnext.peppol_4_erpnext import api

		with patch.object(api, "frappe") as mock_frappe:
			mock_frappe.only_for.side_effect = RuntimeError("blocked")
			with self.assertRaises(RuntimeError):
				api.update_peppol_status("SINV-1", "Sent")

		mock_frappe.only_for.assert_called_once_with(api.STATUS_CALLBACK_ROLES)

	def test_code_list_info_reply_keys(self):
		"""tapr_next skips a redundant push by reading `version` off this reply."""
		from peppol_4_erpnext.peppol_4_erpnext import code_list

		# An empty site dir makes active_raw_path() fall back to the bundled list,
		# so this exercises the real reply without a pushed file.
		with tempfile.TemporaryDirectory() as tmp:
			with patch.object(code_list, "site_dir", return_value=tmp):
				info = code_list.code_list_info()

		self.assertEqual(set(info), CODE_LIST_INFO_KEYS)
		self.assertTrue(info["version"])
		self.assertEqual(info["source"], "app")

	def test_code_list_endpoints_accept_the_same_roles_as_the_status_callback(self):
		"""The three endpoints must not drift apart on who is allowed to call them."""
		from peppol_4_erpnext.peppol_4_erpnext import api, code_list

		with patch.object(code_list, "frappe") as mock_frappe:
			mock_frappe.only_for.side_effect = RuntimeError("blocked")
			with self.assertRaises(RuntimeError):
				code_list.get_peppol_code_list_info()
		mock_frappe.only_for.assert_called_once_with(code_list.CODE_LIST_ROLES)

		with patch.object(code_list, "frappe") as mock_frappe:
			mock_frappe.only_for.side_effect = RuntimeError("blocked")
			with self.assertRaises(RuntimeError):
				code_list.update_peppol_code_list(code_list={"values": []})
		mock_frappe.only_for.assert_called_once_with(code_list.CODE_LIST_ROLES)

		self.assertEqual(set(code_list.CODE_LIST_ROLES), set(api.STATUS_CALLBACK_ROLES))
		self.assertIn("System Manager", code_list.CODE_LIST_ROLES)
		self.assertIn("PEPPOL Integration", code_list.CODE_LIST_ROLES)

	def test_integration_role_is_defined_and_exported(self):
		"""A role every endpoint checks for but that no fixture ships is useless."""
		import peppol_4_erpnext
		from peppol_4_erpnext import hooks
		from peppol_4_erpnext.peppol_4_erpnext import api

		path = os.path.join(os.path.dirname(peppol_4_erpnext.__file__), "fixtures", "role.json")
		with open(path, encoding="utf-8") as fh:
			roles = {r["name"] for r in json.load(fh)}

		self.assertIn("PEPPOL Integration", roles)

		role_fixture = next(f for f in hooks.fixtures if f["doctype"] == "Role")
		self.assertEqual(set(role_fixture["filters"][0][2]), roles)
		self.assertIn("PEPPOL Integration", api.STATUS_CALLBACK_ROLES)


# ── Custom Fields ─────────────────────────────────────────────────────────────

# Keys tapr_next posts to /api/resource/Purchase Invoice that only exist because
# this app defines them. Anything Frappe does not find in the doctype meta is
# dropped by get_valid_dict() before the insert — no error, no data.
# tapr_next/accounts_payable/adapters/erpnext_client.py :: _append_payload_metadata
PURCHASE_INVOICE_KEYS = {
	"peppol_reference",
	"is_peppol_invoice",
	"peppol_sender_id",
	"peppol_received_on",
	"schedule_date",
	"payment_reference",
	"supplier_address_line1",
	"supplier_address_line2",
	"supplier_city",
	"supplier_state",
	"supplier_postal_code",
	"supplier_country",
}

# Read off the Sales Invoice detail by tapr_next/accounts_receivable/erp_sync.py.
SALES_INVOICE_KEYS = {
	"send_via_peppol",
	"peppol_status",
	"peppol_document_format",
	"peppol_process_id",
}


def _fixture_fields():
	import peppol_4_erpnext

	path = os.path.join(os.path.dirname(peppol_4_erpnext.__file__), "fixtures", "custom_field.json")
	with open(path, encoding="utf-8") as fh:
		return json.load(fh)


class TestCustomFieldContract(unittest.TestCase):
	"""Runs off the fixture file — no site, no bench."""

	def setUp(self):
		self.fields = _fixture_fields()

	def _names_for(self, doctype):
		return {f["fieldname"] for f in self.fields if f["dt"] == doctype}

	def test_purchase_invoice_fields_exist(self):
		missing = PURCHASE_INVOICE_KEYS - self._names_for("Purchase Invoice")
		self.assertFalse(missing, f"tapr_next posts these and nothing would receive them: {sorted(missing)}")

	def test_sales_invoice_fields_exist(self):
		missing = SALES_INVOICE_KEYS - self._names_for("Sales Invoice")
		self.assertFalse(missing, f"tapr_next reads these off the invoice: {sorted(missing)}")

	def test_customer_peppol_id_exists(self):
		"""erpnext_ar_client.get_customer_peppol_id requests exactly this field."""
		self.assertIn("peppol_id", self._names_for("Customer"))

	def test_peppol_status_options_cover_every_status(self):
		options = next(
			f for f in self.fields if f["dt"] == "Sales Invoice" and f["fieldname"] == "peppol_status"
		)["options"].split("\n")
		for status in PEPPOL_STATUSES:
			with self.subTest(status=status):
				self.assertIn(status, options)

	def test_export_filter_names_every_field(self):
		"""A field missing from the hooks filter is dropped by the next export-fixtures."""
		from peppol_4_erpnext import hooks

		listed = set(hooks.fixtures[0]["filters"][0][2])
		self.assertEqual(listed, {f["name"] for f in self.fields})

	def test_provenance_fields_are_no_copy(self):
		"""Duplicating or amending an invoice must not carry over network provenance.

		A copied peppol_reference in particular would claim to be a PEPPOL instance ID
		that was never transmitted. See issue #18.
		"""
		skip_fieldtypes = {"Section Break", "Column Break"}
		for f in self.fields:
			if f["dt"] not in ("Sales Invoice", "Purchase Invoice") or f["fieldtype"] in skip_fieldtypes:
				continue
			with self.subTest(dt=f["dt"], fieldname=f["fieldname"]):
				self.assertEqual(f.get("no_copy"), 1)
