"""Install-time guards.

The app targets Frappe/ERPNext v15 and v16. Both are supported by the same code:
every framework API this app touches (`frappe.whitelist`, `frappe.only_for`,
`frappe.throw`, `frappe.log_error`, `frappe.get_site_path`, `frappe.get_app_path`,
`frappe.db.set_value`, `frappe.db.get_single_value`) has an identical signature in
both, and the client scripts use form APIs that are unchanged across the two.

Note the interpreter differs: a v15 bench runs Python 3.10-3.14, a v16 bench runs
3.14. The app therefore stays within Python 3.10 syntax (see `target-version` in
pyproject.toml) so one codebase installs on either.
"""

import frappe

MIN_MAJOR = 15
MAX_TESTED_MAJOR = 16


def _major(version: str) -> int:
	"""Major version as an int, tolerating suffixes like '16.0.0-dev'."""
	return int(version.split(".", 1)[0].split("-", 1)[0])


def _check(app: str, version: str) -> None:
	try:
		major = _major(version)
	except ValueError:
		# Unparseable version: not a reason to block an install.
		return

	if major < MIN_MAJOR:
		frappe.throw(
			f"peppol_4_erpnext requires {app} v{MIN_MAJOR} or newer, found {version}.",
			frappe.ValidationError,
		)

	if major > MAX_TESTED_MAJOR:
		print(
			f"peppol_4_erpnext: {app} {version} is newer than the latest tested "
			f"version (v{MAX_TESTED_MAJOR}). Installing anyway."
		)


def before_install() -> None:
	import erpnext

	_check("frappe", frappe.__version__)
	_check("erpnext", erpnext.__version__)
