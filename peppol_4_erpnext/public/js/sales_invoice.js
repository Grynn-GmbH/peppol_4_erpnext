frappe.ui.form.on("Sales Invoice", {
	refresh: function (frm) {
		// Only show button for submitted invoices
		if (frm.doc.docstatus !== 1) {
			return;
		}

		// Check if invoice can be sent
		frappe.call({
			method: "peppol_4_erpnext.peppol_4_erpnext.api.can_send_to_peppol",
			args: {
				sales_invoice_name: frm.doc.name,
			},
			callback: function (r) {
				if (r.message && r.message.can_send) {
					frm.add_custom_button(
						__("Send to PEPPOL"),
						function () {
							send_to_peppol(frm);
						},
						__("Actions")
					);
				}

				// Add refresh status button if already sent
				if (
					frm.doc.peppol_status &&
					frm.doc.peppol_status !== "Not Sent" &&
					frm.doc.peppol_document_name
				) {
					frm.add_custom_button(
						__("Refresh PEPPOL Status"),
						function () {
							refresh_peppol_status(frm);
						},
						__("Actions")
					);
				}
			},
		});

		// Show PEPPOL status indicator
		show_peppol_status_indicator(frm);
	},
});

function send_to_peppol(frm) {
	frappe.confirm(
		__("Send this invoice to {0} via PEPPOL?", [frm.doc.customer_name]),
		function () {
			frappe.call({
				method: "peppol_4_erpnext.peppol_4_erpnext.api.send_sales_invoice_to_peppol",
				args: {
					sales_invoice_name: frm.doc.name,
				},
				freeze: true,
				freeze_message: __("Sending invoice to PEPPOL..."),
				callback: function (r) {
					if (r.message) {
						if (r.message.success) {
							frappe.show_alert(
								{
									message: r.message.message,
									indicator: "green",
								},
								5
							);
							frm.reload_doc();
						} else {
							frappe.msgprint({
								title: __("PEPPOL Error"),
								message: r.message.message,
								indicator: "red",
							});
							frm.reload_doc();
						}
					}
				},
				error: function (r) {
					frappe.msgprint({
						title: __("Error"),
						message: __("Failed to send invoice. Please try again."),
						indicator: "red",
					});
					frm.reload_doc();
				},
			});
		}
	);
}

function refresh_peppol_status(frm) {
	frappe.call({
		method: "peppol_4_erpnext.peppol_4_erpnext.api.get_peppol_invoice_status",
		args: {
			sales_invoice_name: frm.doc.name,
		},
		freeze: true,
		freeze_message: __("Checking PEPPOL status..."),
		callback: function (r) {
			if (r.message) {
				frappe.show_alert(
					{
						message: __("Status: {0}", [r.message.status]),
						indicator: get_status_indicator(r.message.status),
					},
					5
				);
				frm.reload_doc();
			}
		},
	});
}

function show_peppol_status_indicator(frm) {
	if (!frm.doc.peppol_status || frm.doc.peppol_status === "Not Sent") {
		return;
	}

	let indicator = get_status_indicator(frm.doc.peppol_status);
	let message = "";

	switch (frm.doc.peppol_status) {
		case "Sending":
			message = __("PEPPOL: Sending...");
			break;
		case "Sent":
			message = __("PEPPOL: Sent to TAPRNext");
			break;
		case "Delivered":
			message = __("PEPPOL: Delivered to recipient");
			break;
		case "Failed":
			message = __("PEPPOL: Failed - {0}", [frm.doc.peppol_error || "Unknown error"]);
			break;
	}

	if (message) {
		frm.dashboard.set_headline_alert(
			`<div class="row">
				<div class="col-xs-12">
					<span class="indicator whitespace-nowrap ${indicator}">
						${message}
					</span>
				</div>
			</div>`
		);
	}
}

function get_status_indicator(status) {
	switch (status) {
		case "Sending":
			return "orange";
		case "Sent":
			return "blue";
		case "Delivered":
			return "green";
		case "Failed":
			return "red";
		default:
			return "grey";
	}
}
