import frappe
from frappe.model.document import Document


class PEPPOLSettings(Document):
	pass


def is_peppol_enabled():
	"""Check if PEPPOL integration is enabled"""
	return frappe.db.get_single_value("PEPPOL Settings", "enabled")
