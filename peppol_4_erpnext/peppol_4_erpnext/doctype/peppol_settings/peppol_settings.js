frappe.ui.form.on("PEPPOL Settings", {
	refresh: function (frm) {
		if (frm.doc.enabled && frm.doc.taprnext_url && frm.doc.api_key) {
			frm.add_custom_button(__("Test Connection"), function () {
				frappe.call({
					method: "peppol_4_erpnext.peppol_4_erpnext.api.test_peppol_connection",
					freeze: true,
					freeze_message: __("Testing connection to TAPRNext..."),
					callback: function (r) {
						if (r.message) {
							if (r.message.success) {
								frappe.msgprint({
									title: __("Success"),
									message: r.message.message,
									indicator: "green",
								});
							} else {
								frappe.msgprint({
									title: __("Connection Failed"),
									message: r.message.message,
									indicator: "red",
								});
							}
						}
					},
				});
			});
		}
	},
});
