["Company", "Supplier"].forEach((doctype) => {
	frappe.ui.form.on(doctype, {
		peppol_id(frm) {
			if (frm.doc.peppol_id) {
				validate_peppol_id(frm);
			} else {
				clearTimeout(frm._peppol_debounce);
			}
		},
	});
});

function validate_peppol_id(frm) {
	clearTimeout(frm._peppol_debounce);
	frm._peppol_debounce = setTimeout(() => {
		const seq = (frm._peppol_seq = (frm._peppol_seq || 0) + 1);
		frappe.show_alert({ message: __("Validating PEPPOL ID..."), indicator: "blue" }, 3);
		frappe.call({
			method: "peppol_4_erpnext.peppol_4_erpnext.api.lookup_peppol_participant",
			args: { participant_id: frm.doc.peppol_id, validate_only: 1 },
			callback(r) {
				if (seq !== frm._peppol_seq) return;
				if (!r.message) {
					frappe.show_alert(
						{ message: __("Could not validate PEPPOL ID"), indicator: "orange" },
						5,
					);
					return;
				}
				if (!r.message.registered) {
					frappe.show_alert(
						{
							message: __("PEPPOL ID is not registered on the network"),
							indicator: "red",
						},
						7,
					);
					return;
				}
				frappe.show_alert(
					{ message: __("PEPPOL ID is registered on the network"), indicator: "green" },
					5,
				);
			},
			error() {
				frappe.show_alert(
					{ message: __("Failed to reach PEPPOL lookup service"), indicator: "red" },
					5,
				);
			},
		});
	}, 300);
}
