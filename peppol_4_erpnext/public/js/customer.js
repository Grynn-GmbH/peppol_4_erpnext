frappe.ui.form.on("Customer", {
	refresh(frm) {
		if (frm.doc.peppol_id) {
			fetch_and_set_peppol_options(frm);
		}
	},

	peppol_id(frm) {
		if (frm.doc.peppol_id) {
			fetch_and_set_peppol_options(frm);
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

function fetch_and_set_peppol_options(frm) {
	frappe.call({
		method: "peppol_4_erpnext.peppol_4_erpnext.api.lookup_peppol_participant",
		args: { participant_id: frm.doc.peppol_id },
		callback(r) {
			if (!r.message || !r.message.registered) {
				clear_peppol_format_fields(frm);
				return;
			}
			frm._peppol_lookup = r.message;
			const { document_names = [] } = r.message;

			const invoice_names = document_names.filter((n) => n.includes("Invoice"));
			const credit_note_names = document_names.filter((n) => n.includes("Credit Note"));

			frm.set_df_property(
				"default_invoice_format",
				"options",
				["", ...invoice_names].join("\n")
			);
			frm.set_df_property(
				"default_credit_note_format",
				"options",
				["", ...credit_note_names].join("\n")
			);
			frm.refresh_fields([
				"default_invoice_format",
				"default_credit_note_format",
			]);
		},
		error() {
			clear_peppol_format_fields(frm);
		},
	});
}

function set_format_ids(frm, type) {
	const lookup = frm._peppol_lookup;
	if (!lookup) return;
	const { document_names = [], document_types = [], process_id = [] } = lookup;

	const selected =
		type === "invoice"
			? frm.doc.default_invoice_format
			: frm.doc.default_credit_note_format;

	const idx = document_names.indexOf(selected);
	if (type === "invoice") {
		frm.set_value("invoice_format_id", idx >= 0 ? document_types[idx] : "");
		frm.set_value("invoice_process_id", idx >= 0 ? process_id[idx] : "");
	} else {
		frm.set_value("credit_note_format_id", idx >= 0 ? document_types[idx] : "");
		frm.set_value("credit_note_process_id", idx >= 0 ? process_id[idx] : "");
	}
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
}
