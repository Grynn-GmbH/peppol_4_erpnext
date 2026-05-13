import frappe
import requests
from frappe import _
from frappe.model.document import Document


class PEPPOLSettings(Document):
	def validate(self):
		if self.tapr_next_url:
			if not self.tapr_next_api_key:
				frappe.throw(_("API Key is required"))
			if not self.tapr_next_api_secret:
				frappe.throw(_("API Secret is required"))
		if self.enabled:
			self._ping_tapr_next()

	def _ping_tapr_next(self):
		if self.tapr_next_url is None:
			return
		if not (
			self.has_value_changed("tapr_next_url")
			or self.has_value_changed("tapr_next_api_key")
			or self.has_value_changed("tapr_next_api_secret")
		):
			return
		url = self.tapr_next_url
		if not url.startswith(("http://", "https://")):
			url = "https://" + url

		api_key = self.get("tapr_next_api_key")
		api_secret = self.get_password("tapr_next_api_secret") if self.get("tapr_next_api_secret") else None

		headers = {}
		if api_key and api_secret:
			headers["Authorization"] = f"token {api_key}:{api_secret}"

		try:
			resp = requests.get(
				f"{url.rstrip('/')}/api/method/frappe.ping",
				headers=headers,
				timeout=10,
			)
			resp.raise_for_status()
		except Exception as e:
			frappe.msgprint(
				_("Could not connect to TAPRNext: {0}").format(str(e)),
				indicator="red",
				title=_("Connection Failed"),
			)


def is_peppol_enabled():
	"""Check if PEPPOL integration is enabled"""
	return frappe.db.get_single_value("PEPPOL Settings", "enabled")
