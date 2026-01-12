import frappe
import requests
from requests.exceptions import RequestException


class TAPRNextClient:
	"""HTTP client for communicating with TAPRNext"""

	def __init__(self):
		self.settings = self._get_settings()
		self.base_url = self.settings.taprnext_url
		self.auth_token = f"token {self.settings.api_key}:{self.settings.get_password('api_secret')}"

	def _get_settings(self):
		"""Get and validate PEPPOL Settings"""
		settings = frappe.get_single("PEPPOL Settings")
		if not settings.enabled:
			frappe.throw("PEPPOL integration is not enabled. Please configure PEPPOL Settings.")
		return settings

	def _get_headers(self):
		"""Get common headers for API requests"""
		return {
			"Authorization": self.auth_token,
			"Content-Type": "application/json",
			"Accept": "application/json",
		}

	def _make_request(self, method, endpoint, data=None):
		"""Make HTTP request to TAPRNext

		Args:
			method: HTTP method (GET, POST, PUT, DELETE)
			endpoint: API endpoint (e.g., /api/resource/Sales Invoice)
			data: Request payload (dict)

		Returns:
			dict: Response data

		Raises:
			frappe.ValidationError: On API errors
		"""
		url = f"{self.base_url}{endpoint}"
		headers = self._get_headers()

		try:
			response = requests.request(
				method=method,
				url=url,
				headers=headers,
				json=data,
				timeout=30,
			)

			# Parse response
			try:
				result = response.json()
			except ValueError:
				result = {"message": response.text}

			# Check for errors
			if not response.ok:
				error_msg = result.get("message") or result.get("exc") or response.text
				frappe.throw(
					f"TAPRNext API Error ({response.status_code}): {error_msg}",
					title="TAPRNext Error",
				)

			return result

		except RequestException as e:
			frappe.throw(
				f"Failed to connect to TAPRNext: {e!s}",
				title="Connection Error",
			)

	def create_sales_invoice(self, invoice_data):
		"""Create a Sales Invoice on TAPRNext

		Args:
			invoice_data: Invoice payload dict

		Returns:
			dict: Created document data including name
		"""
		response = self._make_request(
			method="POST",
			endpoint="/api/resource/Sales Invoice",
			data=invoice_data,
		)
		return response.get("data", response)

	def get_sales_invoice(self, document_name):
		"""Get a Sales Invoice from TAPRNext

		Args:
			document_name: TAPRNext document name

		Returns:
			dict: Document data
		"""
		response = self._make_request(
			method="GET",
			endpoint=f"/api/resource/Sales Invoice/{document_name}",
		)
		return response.get("data", response)

	def get_invoice_status(self, document_name):
		"""Get the status of an invoice on TAPRNext

		Args:
			document_name: TAPRNext document name

		Returns:
			str: Current status
		"""
		doc = self.get_sales_invoice(document_name)
		return doc.get("status", "Unknown")

	def test_connection(self):
		"""Test the connection to TAPRNext

		Returns:
			bool: True if connection successful
		"""
		try:
			response = self._make_request(
				method="GET",
				endpoint="/api/method/frappe.auth.get_logged_user",
			)
			return True
		except Exception:
			return False
