import frappe
from frappe import _
from frappe.utils import now_datetime

from peppol_4_erpnext.peppol_4_erpnext.invoice_mapper import map_sales_invoice_to_taprnext
from peppol_4_erpnext.peppol_4_erpnext.taprnext_client import TAPRNextClient


@frappe.whitelist()
def send_sales_invoice_to_peppol(sales_invoice_name):
	"""Send a Sales Invoice to TAPRNext for PEPPOL delivery

	Args:
		sales_invoice_name: Name of the Sales Invoice to send

	Returns:
		dict: Result with success status and message
	"""
	# Get the Sales Invoice
	si = frappe.get_doc("Sales Invoice", sales_invoice_name)

	# Validate invoice state
	if si.docstatus != 1:
		frappe.throw(_("Only submitted Sales Invoices can be sent via PEPPOL"))

	if si.get("peppol_status") == "Sent":
		frappe.throw(_("This invoice has already been sent via PEPPOL"))

	if si.get("peppol_status") == "Sending":
		frappe.throw(_("This invoice is currently being sent"))

	try:
		# Update status to Sending
		frappe.db.set_value(
			"Sales Invoice",
			sales_invoice_name,
			{
				"peppol_status": "Sending",
				"peppol_error": "",
			},
			update_modified=False,
		)
		frappe.db.commit()

		# Map the invoice to TAPRNext format
		payload = map_sales_invoice_to_taprnext(sales_invoice_name)

		# Send to TAPRNext
		client = TAPRNextClient()
		response = client.create_sales_invoice(payload)

		# Extract document name from response
		document_name = response.get("name", "")

		# Update Sales Invoice with success status
		frappe.db.set_value(
			"Sales Invoice",
			sales_invoice_name,
			{
				"peppol_status": "Sent",
				"peppol_document_name": document_name,
				"peppol_sent_on": now_datetime(),
				"peppol_error": "",
			},
			update_modified=False,
		)
		frappe.db.commit()

		return {
			"success": True,
			"message": _("Invoice sent successfully to TAPRNext"),
			"document_name": document_name,
		}

	except Exception as e:
		# Update Sales Invoice with error status
		frappe.db.set_value(
			"Sales Invoice",
			sales_invoice_name,
			{
				"peppol_status": "Failed",
				"peppol_error": str(e),
			},
			update_modified=False,
		)
		frappe.db.commit()

		frappe.log_error(
			message=f"PEPPOL Send Error for {sales_invoice_name}: {e!s}",
			title="PEPPOL Send Error",
		)

		return {
			"success": False,
			"message": str(e),
		}


@frappe.whitelist()
def get_peppol_invoice_status(sales_invoice_name):
	"""Get the current PEPPOL status of an invoice from TAPRNext

	Args:
		sales_invoice_name: Name of the Sales Invoice

	Returns:
		dict: Status information
	"""
	si = frappe.get_doc("Sales Invoice", sales_invoice_name)

	if not si.get("peppol_document_name"):
		return {
			"status": si.get("peppol_status") or "Not Sent",
			"message": _("Invoice has not been sent to TAPRNext"),
		}

	try:
		client = TAPRNextClient()
		status = client.get_invoice_status(si.peppol_document_name)

		# Map TAPRNext status to our status
		status_mapping = {
			"Draft": "Sent",
			"Manual Review": "Sent",
			"Matching": "Sent",
			"Needs Approval": "Sent",
			"Ready for ERP": "Sent",
			"Posted to ERP": "Delivered",
			"Rejected": "Failed",
			"Error": "Failed",
		}

		mapped_status = status_mapping.get(status, "Sent")

		# Update local status if changed
		if si.get("peppol_status") != mapped_status:
			frappe.db.set_value(
				"Sales Invoice",
				sales_invoice_name,
				"peppol_status",
				mapped_status,
				update_modified=False,
			)

		return {
			"status": mapped_status,
			"taprnext_status": status,
			"message": _("Status retrieved from TAPRNext"),
		}

	except Exception as e:
		return {
			"status": si.get("peppol_status") or "Unknown",
			"message": str(e),
		}


@frappe.whitelist()
def test_peppol_connection():
	"""Test the connection to TAPRNext

	Returns:
		dict: Connection test result
	"""
	try:
		client = TAPRNextClient()
		success = client.test_connection()

		if success:
			return {
				"success": True,
				"message": _("Successfully connected to TAPRNext"),
			}
		else:
			return {
				"success": False,
				"message": _("Failed to connect to TAPRNext"),
			}

	except Exception as e:
		return {
			"success": False,
			"message": str(e),
		}


@frappe.whitelist()
def can_send_to_peppol(sales_invoice_name):
	"""Check if a Sales Invoice can be sent via PEPPOL

	Args:
		sales_invoice_name: Name of the Sales Invoice

	Returns:
		dict: Eligibility status and any issues
	"""
	issues = []

	# Check if PEPPOL is enabled
	settings = frappe.get_single("PEPPOL Settings")
	if not settings.enabled:
		issues.append(_("PEPPOL integration is not enabled"))

	# Get the Sales Invoice
	si = frappe.get_doc("Sales Invoice", sales_invoice_name)

	# Check docstatus
	if si.docstatus != 1:
		issues.append(_("Invoice must be submitted"))

	# Check if already sent
	if si.get("peppol_status") in ("Sent", "Delivered"):
		issues.append(_("Invoice has already been sent via PEPPOL"))

	# Check Company PEPPOL ID
	company_peppol_id = frappe.db.get_value("Company", si.company, "peppol_id")
	if not company_peppol_id:
		issues.append(_("Company does not have a PEPPOL Participant ID"))

	# Check Customer PEPPOL ID
	customer_peppol_id = frappe.db.get_value("Customer", si.customer, "peppol_id")
	if not customer_peppol_id:
		issues.append(_("Customer does not have a PEPPOL Participant ID"))

	return {
		"can_send": len(issues) == 0,
		"issues": issues,
	}
