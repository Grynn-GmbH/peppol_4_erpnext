import frappe
from frappe.utils import flt, getdate


def map_sales_invoice_to_taprnext(sales_invoice_name):
	"""Map an ERPNext Sales Invoice to TAPRNext Sales Invoice format

	Args:
		sales_invoice_name: Name of the ERPNext Sales Invoice

	Returns:
		dict: TAPRNext-compatible invoice payload
	"""
	# Get the Sales Invoice with all related data
	si = frappe.get_doc("Sales Invoice", sales_invoice_name)

	# Get Company PEPPOL details
	company = frappe.get_doc("Company", si.company)
	company_peppol_id = company.get("peppol_id") or ""
	company_peppol_scheme = company.get("peppol_scheme") or ""

	# Get Customer PEPPOL details
	customer = frappe.get_doc("Customer", si.customer)
	customer_peppol_id = customer.get("peppol_id") or ""
	customer_peppol_scheme = customer.get("peppol_scheme") or ""

	# Validate PEPPOL IDs
	if not company_peppol_id:
		frappe.throw(
			f"Company '{si.company}' does not have a PEPPOL Participant ID configured.",
			title="Missing PEPPOL ID",
		)

	if not customer_peppol_id:
		frappe.throw(
			f"Customer '{si.customer}' does not have a PEPPOL Participant ID configured.",
			title="Missing PEPPOL ID",
		)

	# Get PEPPOL Settings for defaults
	settings = frappe.get_single("PEPPOL Settings")

	# Map items
	items = []
	for item in si.items:
		items.append({
			"item_description": item.description or item.item_name,
			"item_code": item.item_code,
			"quantity": flt(item.qty),
			"uom": item.uom,
			"unit_price": flt(item.rate),
			"net_amount": flt(item.net_amount or item.amount),
			"tax_rate": get_item_tax_rate(si, item),
			"tax_amount": flt(item.net_amount or item.amount) * get_item_tax_rate(si, item) / 100,
		})

	# Map taxes
	taxes = []
	for tax in si.taxes:
		if flt(tax.tax_amount) != 0:
			taxes.append({
				"tax_name": tax.description or tax.account_head,
				"tax_rate": flt(tax.rate) if tax.rate else 0,
				"taxable_amount": flt(tax.base_total) if hasattr(tax, "base_total") else flt(si.net_total),
				"tax_amount": flt(tax.tax_amount),
			})

	# Build the payload
	payload = {
		# Sender (Company) Information
		"legal_entity": si.company,
		"sender_peppol_id": format_peppol_id(company_peppol_scheme, company_peppol_id),
		"sender_name": si.company,
		"sender_vat_number": company.tax_id or "",
		"sender_address": get_company_address(si.company),

		# Receiver (Customer) Information
		"receiver_peppol_id": format_peppol_id(customer_peppol_scheme, customer_peppol_id),
		"receiver_name": si.customer_name or si.customer,
		"receiver_vat_number": customer.tax_id or "",
		"receiver_address": si.customer_address or "",

		# Invoice Details
		"invoice_number": si.name,
		"invoice_date": str(getdate(si.posting_date)),
		"due_date": str(getdate(si.due_date)) if si.due_date else str(getdate(si.posting_date)),
		"currency": si.currency,

		# Amounts
		"net_total": flt(si.net_total),
		"tax_total": flt(si.total_taxes_and_charges),
		"grand_total": flt(si.grand_total),

		# Line Items
		"items": items,

		# Taxes Summary
		"taxes": taxes,

		# Metadata
		"source_channel": "API",
		"target_erp": settings.default_target_erp or "erpnext",
		"source_reference": si.name,

		# Payment Terms
		"payment_terms": si.payment_terms_template or "",

		# Additional fields
		"remarks": si.remarks or "",
		"po_no": si.po_no or "",
	}

	return payload


def get_item_tax_rate(sales_invoice, item):
	"""Get the effective tax rate for an item

	Args:
		sales_invoice: Sales Invoice document
		item: Sales Invoice Item

	Returns:
		float: Tax rate percentage
	"""
	# Check if item has specific tax template
	if item.item_tax_template:
		tax_template = frappe.get_doc("Item Tax Template", item.item_tax_template)
		if tax_template.taxes:
			return flt(tax_template.taxes[0].tax_rate)

	# Fall back to invoice-level tax rate
	for tax in sales_invoice.taxes:
		if tax.charge_type in ("On Net Total", "On Previous Row Total"):
			return flt(tax.rate)

	return 0.0


def format_peppol_id(scheme, participant_id):
	"""Format PEPPOL ID with scheme prefix

	Args:
		scheme: PEPPOL scheme (e.g., "9959:CH:UID")
		participant_id: Participant ID

	Returns:
		str: Formatted PEPPOL ID (e.g., "9959:CHE123456789")
	"""
	if not scheme or not participant_id:
		return participant_id

	# Extract numeric scheme code (e.g., "9959" from "9959:CH:UID")
	scheme_code = scheme.split(":")[0] if ":" in scheme else scheme

	# Check if ID already has scheme prefix
	if participant_id.startswith(scheme_code):
		return participant_id

	return f"{scheme_code}:{participant_id}"


def get_company_address(company_name):
	"""Get the primary address for a company

	Args:
		company_name: Company name

	Returns:
		str: Formatted address string
	"""
	try:
		address = frappe.db.get_value(
			"Dynamic Link",
			{"link_doctype": "Company", "link_name": company_name, "parenttype": "Address"},
			"parent",
		)
		if address:
			addr_doc = frappe.get_doc("Address", address)
			parts = [
				addr_doc.address_line1,
				addr_doc.address_line2,
				addr_doc.city,
				addr_doc.pincode,
				addr_doc.country,
			]
			return ", ".join(filter(None, parts))
	except Exception:
		pass
	return ""
