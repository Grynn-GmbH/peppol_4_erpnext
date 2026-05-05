import frappe
from frappe import _


@frappe.whitelist()
def can_mark_for_peppol(sales_invoice_name):
	"""Check if a Sales Invoice can be marked for PEPPOL sending

	Args:
		sales_invoice_name: Name of the Sales Invoice

	Returns:
		dict: Eligibility status and any issues
	"""
	issues = []

	# Check if PEPPOL is enabled
	if not frappe.db.get_single_value("PEPPOL Settings", "enabled"):
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
		"can_mark": len(issues) == 0,
		"issues": issues,
	}


@frappe.whitelist()
def mark_invoice_for_peppol(sales_invoice_name):
	"""Mark a Sales Invoice for PEPPOL sending

	Args:
		sales_invoice_name: Name of the Sales Invoice

	Returns:
		dict: Result with success status and message
	"""
	# Check eligibility first
	eligibility = can_mark_for_peppol(sales_invoice_name)
	if not eligibility.get("can_mark"):
		return {
			"success": False,
			"message": ", ".join(eligibility.get("issues", [])),
		}

	try:
		# Update the invoice
		frappe.db.set_value(
			"Sales Invoice",
			sales_invoice_name,
			{
				"send_via_peppol": 1,
				"peppol_status": "Ready",
			},
			update_modified=False,
		)
		frappe.db.commit()

		return {
			"success": True,
			"message": _("Invoice marked for PEPPOL sending. TAPRNext will pick it up shortly."),
		}

	except Exception as e:
		frappe.log_error(
			message=f"Error marking invoice for PEPPOL {sales_invoice_name}: {e!s}",
			title="PEPPOL Mark Error",
		)
		return {
			"success": False,
			"message": str(e),
		}


@frappe.whitelist()
def update_peppol_status(
	sales_invoice_name,
	status,
	document_name=None,
	sent_on=None,
	error=None,
	mlr_status=None,
	mlr_description=None,
):
	"""Update peppol_status on a Sales Invoice. Called by tapr_next after fetch/send/MLR events.

	Args:
	    sales_invoice_name: ERPNext Sales Invoice name
	    status: One of Fetched, Sent, Delivered, Failed
	    document_name: tapr_next Sales Invoice name (set on Fetched)
	    sent_on: Datetime when invoice was sent via PEPPOL
	    error: Error message if status is Failed
	    mlr_status: MLR status string from PEPPOL network
	    mlr_description: Detailed MLR description

	Returns:
	    dict: success and status
	"""
	allowed_statuses = ("Fetched", "Sent", "Delivered", "Failed")
	if status not in allowed_statuses:
		frappe.throw(
			_("Invalid PEPPOL status: {0}. Allowed values: {1}").format(
				status, ", ".join(allowed_statuses)
			)
		)

	updates = {"peppol_status": status}
	if document_name is not None:
		updates["peppol_document_name"] = document_name
	if sent_on is not None:
		updates["peppol_sent_on"] = sent_on
	if error is not None:
		updates["peppol_error"] = error
	if mlr_status is not None:
		updates["peppol_mlr_status"] = mlr_status
	if mlr_description is not None:
		updates["peppol_mlr_description"] = mlr_description

	frappe.db.set_value("Sales Invoice", sales_invoice_name, updates, update_modified=False)
	frappe.db.commit()

	return {"success": True, "status": status}


@frappe.whitelist()
def get_peppol_status(sales_invoice_name):
	"""Get the current PEPPOL status of a Sales Invoice

	Args:
		sales_invoice_name: Name of the Sales Invoice

	Returns:
		dict: Status information
	"""
	si = frappe.get_doc("Sales Invoice", sales_invoice_name)

	return {
		"send_via_peppol": si.get("send_via_peppol") or 0,
		"status": si.get("peppol_status") or "",
		"document_name": si.get("peppol_document_name") or "",
		"sent_on": si.get("peppol_sent_on") or "",
		"error": si.get("peppol_error") or "",
		"mlr_status": si.get("peppol_mlr_status") or "",
		"mlr_description": si.get("peppol_mlr_description") or "",
	}
