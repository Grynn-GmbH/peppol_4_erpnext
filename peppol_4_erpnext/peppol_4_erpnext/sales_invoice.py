"""Sales Invoice doc events.

`PEPPOL Settings.enabled` used to gate only the client script: `api.can_mark_for_peppol`
backs the "Mark for PEPPOL" button and the `send_via_peppol` checkbox handler, and both
run in the browser. tapr_next pulls with a plain resource query that never consults the
setting, so anything setting the flag outside the form — the REST API, a bulk edit, a
server script — produced an invoice that was dispatched from a site with PEPPOL switched
off. See issue #13.
"""

import frappe
from frappe import _


def validate_peppol_enabled(doc, method=None):
	"""Refuse to flag an invoice for PEPPOL while the integration is disabled.

	Only the transition is blocked. An invoice marked while PEPPOL was enabled stays
	editable after the setting is switched off, so turning the toggle off never makes
	existing documents unsaveable.
	"""
	if not doc.get("send_via_peppol"):
		return

	# A flag that was already set is not this save's doing.
	if not doc.is_new() and not doc.has_value_changed("send_via_peppol"):
		return

	if frappe.db.get_single_value("PEPPOL Settings", "enabled"):
		return

	frappe.throw(
		_("PEPPOL integration is not enabled. Enable it in PEPPOL Settings before marking invoices."),
		frappe.ValidationError,
	)
