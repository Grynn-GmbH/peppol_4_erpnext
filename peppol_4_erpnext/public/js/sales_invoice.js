frappe.ui.form.on("Sales Invoice", {
	refresh: function (frm) {
		// Only for submitted invoices
		if (frm.doc.docstatus !== 1) {
			return;
		}

		// Show PEPPOL status indicator
		show_peppol_status_indicator(frm);

		// Check if invoice can be marked for PEPPOL
		if (!frm.doc.send_via_peppol) {
			frappe.call({
				method: "peppol_4_erpnext.peppol_4_erpnext.api.can_mark_for_peppol",
				args: {
					sales_invoice_name: frm.doc.name,
				},
				callback: function (r) {
					if (r.message && r.message.can_mark) {
						frm.add_custom_button(
							__("Mark for PEPPOL"),
							function () {
								mark_for_peppol(frm);
							},
							__("Actions")
						);
					}
				},
			});
		}
	},

	send_via_peppol: function (frm) {
		// When checkbox is toggled, validate and set status
		if (frm.doc.send_via_peppol && frm.doc.docstatus === 1) {
			frappe.call({
				method: "peppol_4_erpnext.peppol_4_erpnext.api.can_mark_for_peppol",
				args: {
					sales_invoice_name: frm.doc.name,
				},
				callback: function (r) {
					if (r.message && !r.message.can_mark) {
						frappe.msgprint({
							title: __("Cannot Send via PEPPOL"),
							message: r.message.issues.join("<br>"),
							indicator: "red",
						});
						frm.set_value("send_via_peppol", 0);
					} else if (r.message && r.message.can_mark) {
						// Set status to Ready
						frappe.call({
							method: "peppol_4_erpnext.peppol_4_erpnext.api.mark_invoice_for_peppol",
							args: {
								sales_invoice_name: frm.doc.name,
							},
							callback: function (res) {
								if (res.message && res.message.success) {
									frappe.show_alert(
										{
											message: res.message.message,
											indicator: "green",
										},
										5
									);
									frm.reload_doc();
								}
							},
						});
					}
				},
			});
		}
	},
});

function mark_for_peppol(frm) {
	frappe.confirm(
		__("Mark this invoice for PEPPOL sending to {0}?", [frm.doc.customer_name]),
		function () {
			frappe.call({
				method: "peppol_4_erpnext.peppol_4_erpnext.api.mark_invoice_for_peppol",
				args: {
					sales_invoice_name: frm.doc.name,
				},
				freeze: true,
				freeze_message: __("Marking invoice for PEPPOL..."),
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
								title: __("Error"),
								message: r.message.message,
								indicator: "red",
							});
						}
					}
				},
			});
		}
	);
}

function show_peppol_status_indicator(frm) {
	if (!frm.doc.send_via_peppol) {
		return;
	}

	let indicator = get_status_indicator(frm.doc.peppol_status);
	let message = "";

	switch (frm.doc.peppol_status) {
		case "Ready":
			message = __("PEPPOL: Ready for pickup by TAPRNext");
			break;
		case "Fetched":
			message = __("PEPPOL: Fetched by TAPRNext — processing");
			break;
		case "Sent":
			message = __("PEPPOL: Sent via PEPPOL network");
			break;
		case "Delivered":
			message = __("PEPPOL: Delivered to recipient");
			break;
		case "Failed":
			message = __("PEPPOL: Failed - {0}", [frm.doc.peppol_error || "Unknown error"]);
			break;
		default:
			message = __("PEPPOL: Marked for sending");
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
		case "Ready":
			return "orange";
		case "Fetched":
			return "blue";
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
