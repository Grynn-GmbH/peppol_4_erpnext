"""Receive and store the official PEPPOL document type code list.

tapr_next pushes the code list to this app; it is stored as a plain file under
the site's private files and read in preference to the app-bundled copy, so a
registry release no longer needs an app release.

The derived lookup tables (see ``lookup.py``) are cached next to the raw list as
``peppol_document_types_index.json``. The cache is stamped with the identity of
the file it was built from, so validity costs one ``stat()`` — never a re-parse.
The index format is app-local; only the raw JSON travels on the wire.
"""

import datetime
import json
import os
import tempfile

import frappe

RAW_FILENAME = "peppol_document_types.json"
INDEX_FILENAME = "peppol_document_types_index.json"

# Doc type categories the user should NOT be able to send an invoice as.
# Deliberately different from tapr_next's set — do not copy that one.
EXCLUDED_CATEGORIES = {"Application Response", "Message Level Response"}

_REQUIRED_ENTRY_KEYS = ("scheme", "value", "name", "category", "state")


# ── Paths ─────────────────────────────────────────────────────────────────────


def site_dir() -> str:
	return frappe.get_site_path("private", "files", "peppol_4_erpnext")


def site_raw_path() -> str:
	return os.path.join(site_dir(), RAW_FILENAME)


def site_index_path() -> str:
	return os.path.join(site_dir(), INDEX_FILENAME)


def bundled_raw_path() -> str:
	return frappe.get_app_path("peppol_4_erpnext", RAW_FILENAME)


def active_raw_path() -> str:
	"""Site file if a list was ever pushed here, else the app-bundled copy."""
	path = site_raw_path()
	if os.path.exists(path):
		return path
	return bundled_raw_path()


# ── Validation ────────────────────────────────────────────────────────────────


def validate_code_list(data) -> None:
	"""Raise ValueError if `data` is not a usable PEPPOL document type code list."""
	if not isinstance(data, dict):
		raise ValueError("code_list must be an object")

	values = data.get("values")
	if not isinstance(values, list) or not values:
		raise ValueError("code_list.values must be a non-empty list")

	declared = data.get("entry-count")
	if declared is not None:
		try:
			declared = int(declared)
		except (TypeError, ValueError):
			raise ValueError(f"entry-count is not a number: {data.get('entry-count')!r}")
		if declared != len(values):
			raise ValueError(f"entry-count {declared} does not match {len(values)} values")

	for i, entry in enumerate(values):
		if not isinstance(entry, dict):
			raise ValueError(f"values[{i}] is not an object")
		for key in _REQUIRED_ENTRY_KEYS:
			if not entry.get(key):
				raise ValueError(f"values[{i}] is missing {key!r}")
		proc_ids = entry.get("process-ids")
		if not isinstance(proc_ids, list):
			raise ValueError(f"values[{i}].process-ids must be a list")
		for j, proc in enumerate(proc_ids):
			if not isinstance(proc, dict) or not proc.get("value"):
				raise ValueError(f"values[{i}].process-ids[{j}] is missing 'value'")


# ── Derived index ─────────────────────────────────────────────────────────────


def build_index(data: dict) -> dict:
	"""Derive the lookup tables from a raw code list, in a JSON-safe shape."""
	doctype_names: dict[str, list] = {}
	ids_meta: dict[str, list] = {}
	excluded: list[str] = []

	for e in data["values"]:
		full_id = f"{e['scheme']}::{e['value']}"
		proc_ids = e.get("process-ids") or []
		proc_id = proc_ids[0]["value"] if proc_ids else ""
		doctype_names[full_id] = [e["name"], proc_id]
		val = e["value"]
		cust_id = val.split("##")[1].rsplit("::", 1)[0] if "##" in val else val
		ids_meta[full_id] = [cust_id, proc_id]
		if e["category"] in EXCLUDED_CATEGORIES:
			excluded.append(full_id)

	return {
		"version": data.get("version"),
		"entry_count": len(data["values"]),
		"doctype_names": doctype_names,
		"ids_meta": ids_meta,
		"excluded": excluded,
	}


def file_stamp(path: str) -> dict:
	"""Identity of the raw list an index was built from: one stat()."""
	st = os.stat(path)
	return {"path": os.path.abspath(path), "size": st.st_size, "mtime": st.st_mtime}


def read_index(raw_path: str) -> dict | None:
	"""Return the cached index for `raw_path`, or None if it must be rebuilt.

	Never raises: a broken cache costs a rebuild, not an import failure.
	"""
	try:
		with open(site_index_path(), encoding="utf-8") as fh:
			index = json.load(fh)
		if not isinstance(index, dict):
			return None
		if index.get("source") != file_stamp(raw_path):
			return None
		if not isinstance(index.get("doctype_names"), dict):
			return None
		return index
	except Exception:
		return None


def write_index(raw_path: str, index: dict) -> None:
	"""Persist the derived index stamped with the raw file's identity. Best effort."""
	try:
		payload = dict(index)
		payload["source"] = file_stamp(raw_path)
		_atomic_write(site_index_path(), json.dumps(payload).encode("utf-8"))
	except Exception as exc:
		frappe.log_error(str(exc)[:140], "PEPPOL code list index write failed")


def drop_index() -> None:
	try:
		os.remove(site_index_path())
	except FileNotFoundError:
		pass
	except Exception as exc:
		frappe.log_error(str(exc)[:140], "PEPPOL code list index delete failed")


# ── Storage ───────────────────────────────────────────────────────────────────


def _atomic_write(path: str, payload: bytes) -> None:
	directory = os.path.dirname(path)
	os.makedirs(directory, exist_ok=True)
	fd, tmp = tempfile.mkstemp(dir=directory, prefix=".tmp-", suffix=".json")
	try:
		with os.fdopen(fd, "wb") as fh:
			fh.write(payload)
			fh.flush()
			os.fsync(fh.fileno())
		os.chmod(tmp, 0o640)
		os.replace(tmp, path)
	except Exception:
		try:
			os.remove(tmp)
		except OSError:
			pass
		raise


def _store_code_list(data: dict) -> str:
	"""Replace the site's raw list with `data`, restoring the previous bytes on failure."""
	path = site_raw_path()
	try:
		with open(path, "rb") as fh:
			previous = fh.read()
	except OSError:
		previous = None

	try:
		_atomic_write(path, json.dumps(data).encode("utf-8"))
	except Exception:
		# A half-written list is worse than a stale one.
		if previous is not None:
			try:
				_atomic_write(path, previous)
			except Exception:
				pass
		drop_index()
		raise

	return path


def code_list_info() -> dict:
	"""Version/count of the list currently in use, without re-parsing when cached."""
	path = active_raw_path()
	source = "site" if path == site_raw_path() else "app"

	index = read_index(path)
	if index:
		version, entry_count = index.get("version"), index.get("entry_count")
	else:
		with open(path, encoding="utf-8") as fh:
			data = json.load(fh)
		version = data.get("version")
		entry_count = len(data.get("values") or [])

	return {
		"version": version,
		"entry_count": entry_count,
		"source": source,
		"path": path,
		"modified": datetime.datetime.fromtimestamp(os.stat(path).st_mtime).strftime(
			"%Y-%m-%d %H:%M:%S"
		),
	}


# ── Endpoints called by tapr_next ─────────────────────────────────────────────


@frappe.whitelist(allow_guest=False, methods=["POST"])
def update_peppol_code_list(code_list=None):
	"""Replace the site's PEPPOL document type code list with the pushed one.

	The sender is authoritative: the list is always replaced, whatever version it
	carries, so a deliberate rollback to an older list works. tapr_next uses
	`get_peppol_code_list_info` to skip a redundant push.
	"""
	frappe.only_for("System Manager")

	if isinstance(code_list, str):
		try:
			code_list = json.loads(code_list)
		except ValueError as exc:
			frappe.throw(f"code_list is not valid JSON: {exc}", frappe.ValidationError)

	try:
		validate_code_list(code_list)
	except ValueError as exc:
		frappe.throw(f"Invalid PEPPOL code list: {exc}", frappe.ValidationError)

	# Build the index before touching the raw file: a payload that cannot be
	# indexed never replaces a working list.
	index = build_index(code_list)
	path = _store_code_list(code_list)
	write_index(path, index)

	from peppol_4_erpnext.peppol_4_erpnext.lookup import invalidate_doctypes

	invalidate_doctypes()

	return code_list_info()


@frappe.whitelist(allow_guest=False, methods=["GET"])
def get_peppol_code_list_info():
	"""Report the code list currently in use, so a redundant push can be skipped."""
	frappe.only_for("System Manager")
	return code_list_info()
