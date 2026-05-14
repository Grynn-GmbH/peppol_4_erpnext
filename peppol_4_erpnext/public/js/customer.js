frappe.ui.form.on("Customer", {
	refresh(frm) {
		if (frm.doc.peppol_id) {
			fetch_peppol_data(frm, false);
		} else {
			toggle_format_fields(frm, false);
		}
	},

	peppol_id(frm) {
		if (frm.doc.peppol_id) {
			fetch_peppol_data(frm, true);
		} else {
			clear_peppol_format_fields(frm);
		}
	},

	default_invoice_format(frm) {
		set_format_ids(frm, "invoice");
	},

	default_credit_note_format(frm) {
		set_format_ids(frm, "credit_note");
	},
});

function fetch_peppol_data(frm, show_feedback) {
	clearTimeout(frm._peppol_debounce);
	frm._peppol_debounce = setTimeout(() => {
		_do_fetch_peppol_data(frm, show_feedback);
	}, 300);
}

function _do_fetch_peppol_data(frm, show_feedback) {
	if (show_feedback) {
		frappe.show_alert({ message: __("Validating PEPPOL ID..."), indicator: "blue" }, 3);
	}
	frappe.call({
		method: "peppol_4_erpnext.peppol_4_erpnext.api.lookup_peppol_participant",
		args: { participant_id: frm.doc.peppol_id },
		callback(r) {
			if (!r.message) {
				clear_peppol_format_fields(frm);
				if (show_feedback) {
					frappe.show_alert(
						{ message: __("Could not validate PEPPOL ID"), indicator: "orange" },
						5,
					);
				}
				return;
			}
			if (!r.message.registered) {
				clear_peppol_format_fields(frm);
				if (show_feedback) {
					frappe.show_alert(
						{ message: __("PEPPOL ID is not registered on the network"), indicator: "red" },
						7,
					);
				}
				return;
			}
			frm._peppol_lookup = r.message;
			const { document_names = [] } = r.message;
			if (show_feedback) {
				frappe.show_alert(
					{ message: __("PEPPOL ID is registered on the network"), indicator: "green" },
					5,
				);
			}
			const invoice_names = document_names.filter((n) => n.includes("Invoice"));
			const credit_note_names = document_names.filter((n) => n.includes("Credit Note"));
			frm.set_df_property(
				"default_invoice_format",
				"options",
				["", ...invoice_names].join("\n"),
			);
			frm.set_df_property(
				"default_credit_note_format",
				"options",
				["", ...credit_note_names].join("\n"),
			);
			frm.refresh_fields(["default_invoice_format", "default_credit_note_format"]);
			toggle_format_fields(frm, true);
		},
		error() {
			clear_peppol_format_fields(frm);
			if (show_feedback) {
				frappe.show_alert(
					{ message: __("Failed to reach PEPPOL lookup service"), indicator: "red" },
					5,
				);
			}
		},
	});
}

function set_format_ids(frm, type) {
	const lookup = frm._peppol_lookup;
	if (!lookup) return;
	const { document_names = [], document_types = [], process_ids = [] } = lookup;

	const selected =
		type === "invoice" ? frm.doc.default_invoice_format : frm.doc.default_credit_note_format;

	const idx = document_names.indexOf(selected);
	if (type === "invoice") {
		frm.set_value("invoice_format_id", idx >= 0 ? document_types[idx] : "");
		frm.set_value("invoice_process_id", idx >= 0 ? process_ids[idx] : "");
	} else {
		frm.set_value("credit_note_format_id", idx >= 0 ? document_types[idx] : "");
		frm.set_value("credit_note_process_id", idx >= 0 ? process_ids[idx] : "");
	}
}

function toggle_format_fields(frm, show) {
	[
		"default_invoice_format",
		"invoice_format_id",
		"invoice_process_id",
		"default_credit_note_format",
		"credit_note_format_id",
		"credit_note_process_id",
	].forEach((f) => frm.toggle_display(f, show));
}

function clear_peppol_format_fields(frm) {
	frm._peppol_lookup = null;
	frm.set_df_property("default_invoice_format", "options", "");
	frm.set_df_property("default_credit_note_format", "options", "");
	[
		"default_invoice_format",
		"invoice_format_id",
		"invoice_process_id",
		"default_credit_note_format",
		"credit_note_format_id",
		"credit_note_process_id",
	].forEach((f) => frm.set_value(f, ""));
	toggle_format_fields(frm, false);
}
