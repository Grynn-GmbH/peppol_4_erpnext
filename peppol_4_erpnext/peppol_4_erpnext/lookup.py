import base64
import hashlib
import json
import urllib.parse
import xml.etree.ElementTree as ET

import dns.resolver
import frappe
import requests
from dns.resolver import Answer

_SML_PROD = "edelivery.tech.ec.europa.eu"
_SML_TEST = "acc.edelivery.tech.ec.europa.eu"

_BUSDOX_NS = "http://busdox.org/serviceMetadata/publishing/1.0/"
_DOCTYPES_FILE = frappe.get_app_path("peppol_4_erpnext", "peppol_document_types.json")

_DOCTYPE_NAMES: dict[str, list] = {}
# Doc type IDs the user should NOT be able to send an invoice as
_EXCLUDED_DOCTYPE_IDS: set[str] = set()
# Maps full doc type ID → (customization_id, first_process_id)
_DOCTYPE_IDS_META: dict[str, tuple[str, str]] = {}

_EXCLUDED_CATEGORIES = {"Application Response", "Message Level Response"}

with open(_DOCTYPES_FILE, encoding="utf-8") as _fh:
	for _e in json.load(_fh)["values"]:
		_full_id = f"{_e['scheme']}::{_e['value']}"
		_DOCTYPE_NAMES[_full_id] = [_e["name"], _e["process-ids"][0]["value"]]
		_val = _e["value"]
		_cust_id = _val.split("##")[1].rsplit("::", 1)[0] if "##" in _val else _val
		_proc_ids = _e.get("process-ids") or []
		_proc_id = _proc_ids[0]["value"] if _proc_ids else ""
		_DOCTYPE_IDS_META[_full_id] = (_cust_id, _proc_id)
		if _e["category"] in _EXCLUDED_CATEGORIES:
			_EXCLUDED_DOCTYPE_IDS.add(_full_id)


def _query_service_group(smp_host: str, full_participant_id: str) -> str:
	encoded = urllib.parse.quote(full_participant_id, safe="")
	try:
		response = requests.get(f"https://{smp_host}/{encoded}", timeout=20)
		response.raise_for_status()
		return response.text
	except requests.exceptions.SSLError:
		response = requests.get(f"http://{smp_host}/{encoded}", timeout=20)
		response.raise_for_status()
		return response.text


def _extract_doctypes(xml_text: str) -> list[str]:
	doctypes = []
	try:
		root = ET.fromstring(xml_text)
	except ET.ParseError:
		return doctypes
	for ref in root.iter(f"{{{_BUSDOX_NS}}}ServiceMetadataReference"):
		href = ref.get("href", "")
		doctype = urllib.parse.unquote(href.split("/")[-1])
		if doctype:
			doctypes.append(doctype)
	return doctypes


def _normalise_participant_id(participant_id: str) -> tuple[str, str]:
	"""Return (scheme, value). Accepts '0088:123' or 'scheme::0088:123'."""
	if "::" in participant_id:
		scheme, value = participant_id.split("::", 1)
	else:
		scheme = "iso6523-actorid-upis"
		value = participant_id
	return scheme, value


def _smp_url_from_naptr(regexp: str) -> str:
	"""Extract the SMP URL from a NAPTR regexp field like !^.*$!http://smp.example.com!"""
	delim = regexp[0]
	parts = regexp.split(delim)
	# parts: ['', pattern, replacement, flags]
	return parts[2]


def peppol_dns_name(scheme: str, value: str, test: bool = False) -> str:
	"""
	Compute the BDXL DNS name for a PEPPOL participant identifier.

	Args:
	    participant_id: Either "0088:1234567890" or
	                    "iso6523-actorid-upis::0088:1234567890"
	    test: True for the test SML (acc.edelivery.tech.ec.europa.eu),
	          False for production (edelivery.tech.ec.europa.eu)

	Returns:
	    The DNS name that the Helger BDXLURLProvider would look up, e.g.:
	    "bdxr-as4--0088-grynn-in.iso6523-actorid-upis.edelivery.tech.ec.europa.eu"
	"""

	# Lowercase only the value before hashing (bAddIdentifierSchemeToZone=true)
	value_lower = value.lower()

	digest = hashlib.sha256(value_lower.encode("utf-8")).digest()
	b32 = base64.b32encode(digest).decode("ascii").rstrip("=").lower()

	sml_zone = _SML_TEST if test else _SML_PROD

	return f"{b32}.{scheme}.{sml_zone}"


def _resolve_smp_host(scheme: str, value: str) -> str:
	"""Resolve the SMP hostname via BDXL NAPTR DNS lookup (same as Helger BDXLURLProvider)."""

	dns_name = peppol_dns_name(scheme, value, test=frappe.conf.get("peppol_use_test_sml"))
	resolver = dns.resolver.Resolver()
	resolver.lifetime = 10

	answers: Answer = resolver.resolve(dns_name, "NAPTR")
	for rdata in answers:
		flags = rdata.flags.decode()
		service = rdata.service.decode()
		regexp = rdata.regexp.decode()
		print(regexp)
		if flags.upper() == "U" and service == "Meta:SMP":
			return urllib.parse.urlparse(_smp_url_from_naptr(regexp)).netloc
	return None


def smp_participant_lookup(participant_id: str) -> dict:
	scheme, value = _normalise_participant_id(participant_id)
	full_id = f"{scheme}::{value}"
	not_registered = {
		"registered": False,
		"participant_id": full_id,
		"document_types": [],
		"document_names": [],
	}

	try:
		smp_host = _resolve_smp_host(scheme, value)
	except Exception as exc:
		frappe.log_error(str(exc)[:140], "PEPPOL SMP Lookup")
		return {**not_registered, "error": str(exc)}

	try:
		xml_text = _query_service_group(smp_host, full_id)
	except requests.exceptions.HTTPError as exc:
		if exc.response is not None and exc.response.status_code == 404:
			return {
				**not_registered,
				"smp_host": smp_host,
				"error": f"SMP 404 — not registered. SMP: {smp_host}",
			}
		frappe.log_error(str(exc)[:140], "PEPPOL SMP Lookup")
		return {**not_registered, "smp_host": smp_host, "error": str(exc)}
	except requests.exceptions.RequestException as exc:
		frappe.log_error(str(exc)[:140], "PEPPOL SMP Lookup")
		return {**not_registered, "smp_host": smp_host, "error": str(exc)}

	doc_types = _extract_doctypes(xml_text)
	doc_names = [(_DOCTYPE_NAMES.get(dt) or [dt])[0] for dt in doc_types]
	process_ids = [(_DOCTYPE_NAMES.get(dt) or [None, ""])[1] for dt in doc_types]
	return {
		"registered": True,
		"participant_id": full_id,
		"document_types": doc_types,
		"document_names": doc_names,
		"process_id": process_ids,
	}
