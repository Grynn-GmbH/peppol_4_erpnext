import frappe
from frappe.model.document import Document


class PEPPOLSettings(Document):
	def validate(self):
		if self.enabled:
			if not self.taprnext_url:
				frappe.throw("TAPRNext URL is required when PEPPOL is enabled")
			if not self.api_key:
				frappe.throw("API Key is required when PEPPOL is enabled")
			if not self.api_secret:
				frappe.throw("API Secret is required when PEPPOL is enabled")

			# Normalize URL - remove trailing slash
			if self.taprnext_url:
				self.taprnext_url = self.taprnext_url.rstrip("/")


def get_peppol_settings():
	"""Get PEPPOL Settings as a dict"""
	settings = frappe.get_single("PEPPOL Settings")
	if not settings.enabled:
		frappe.throw("PEPPOL integration is not enabled. Please configure PEPPOL Settings.")
	return settings
