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
							__("Actions"),
						);
					}
				},
			});
		}
	},

	send_via_peppol: function (frm) {
		if (!frm.doc.send_via_peppol || frm.doc.docstatus !== 1) return;

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
									5,
								);
								frm.reload_doc();
							}
						},
					});
				}
			},
		});
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
								5,
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
		},
	);
}

function show_peppol_status_indicator(frm) {
	if (!frm.doc.send_via_peppol) {
		return;
	}
	const statuses = {
		Ready: [__("PEPPOL: Ready for pickup by TAPRNext"), "orange"],
		Fetched: [__("PEPPOL: Fetched by TAPRNext — processing"), "yellow"],
		Sent: [__("PEPPOL: Sent via PEPPOL network"), "blue"],
		Delivered: [__("PEPPOL: Delivered to recipient"), "green"],
		Failed: [__("PEPPOL: Failed - {0}", [frm.doc.peppol_error || "Unknown error"]), "red"],
		Unknown: [__("PEPPOL: Marked for sending"), "grey"],
	};
	let [message, indicator] = statuses[frm.doc.peppol_status] || statuses.Unknown;

	if (message) {
		frm.dashboard.set_headline_alert(
			`<div class="row">
				<div class="col-xs-12">
					<span class="indicator whitespace-nowrap ${indicator}">
						${message}
					</span>
				</div>
			</div>`,
		);
	}
}
