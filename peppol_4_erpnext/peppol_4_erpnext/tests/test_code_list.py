import json
import os
import tempfile
import unittest
from unittest.mock import patch


def _entry(name="Invoice", category="Invoice", value=None, scheme="busdox-docid-qns"):
	return {
		"name": name,
		"scheme": scheme,
		"value": value or "urn:x::Invoice##urn:cen.eu:en16931:2017::2.1",
		"category": category,
		"state": "active",
		"process-ids": [{"scheme": "cenbii-procid-ubl", "value": "urn:proc:01:1.0"}],
	}


def _list(entries=None, version="9.7"):
	entries = entries or [_entry()]
	return {"version": version, "entry-count": len(entries), "values": entries}


class TestValidateCodeList(unittest.TestCase):
	def setUp(self):
		from peppol_4_erpnext.peppol_4_erpnext import code_list

		self.code_list = code_list

	def test_accepts_wellformed_list(self):
		self.code_list.validate_code_list(_list())

	def test_rejects_non_object(self):
		for payload in ([], "x", None):
			with self.assertRaises(ValueError):
				self.code_list.validate_code_list(payload)

	def test_rejects_empty_values(self):
		with self.assertRaises(ValueError):
			self.code_list.validate_code_list({"version": "9.7", "values": []})

	def test_rejects_entry_count_mismatch(self):
		payload = _list()
		payload["entry-count"] = 99
		with self.assertRaises(ValueError):
			self.code_list.validate_code_list(payload)

	def test_accepts_missing_entry_count(self):
		payload = _list()
		del payload["entry-count"]
		self.code_list.validate_code_list(payload)

	def test_rejects_entry_missing_required_key(self):
		for key in ("scheme", "value", "name", "category", "state"):
			payload = _list()
			del payload["values"][0][key]
			with self.assertRaises(ValueError, msg=key):
				self.code_list.validate_code_list(payload)

	def test_rejects_process_id_without_value(self):
		payload = _list()
		payload["values"][0]["process-ids"] = [{"scheme": "cenbii-procid-ubl"}]
		with self.assertRaises(ValueError):
			self.code_list.validate_code_list(payload)

	def test_rejects_non_list_process_ids(self):
		payload = _list()
		payload["values"][0]["process-ids"] = "nope"
		with self.assertRaises(ValueError):
			self.code_list.validate_code_list(payload)


class TestBuildIndex(unittest.TestCase):
	def setUp(self):
		from peppol_4_erpnext.peppol_4_erpnext import code_list

		self.code_list = code_list

	def test_derives_names_meta_and_exclusions(self):
		entries = [
			_entry(name="Invoice", category="Invoice"),
			_entry(
				name="Message Level Response",
				category="Message Level Response",
				value="urn:x::ApplicationResponse##urn:mlr:ver3.0::2.1",
			),
		]
		index = self.code_list.build_index(_list(entries))

		self.assertEqual(index["version"], "9.7")
		self.assertEqual(index["entry_count"], 2)

		invoice_id = "busdox-docid-qns::urn:x::Invoice##urn:cen.eu:en16931:2017::2.1"
		self.assertEqual(index["doctype_names"][invoice_id], ["Invoice", "urn:proc:01:1.0"])
		# customization id = between '##' and the trailing '::<version>'
		self.assertEqual(
			index["ids_meta"][invoice_id], ["urn:cen.eu:en16931:2017", "urn:proc:01:1.0"]
		)

		mlr_id = "busdox-docid-qns::urn:x::ApplicationResponse##urn:mlr:ver3.0::2.1"
		self.assertEqual(index["excluded"], [mlr_id])

	def test_value_without_hashes_is_its_own_customization_id(self):
		entries = [_entry(value="urn:plain:doctype")]
		index = self.code_list.build_index(_list(entries))
		self.assertEqual(
			index["ids_meta"]["busdox-docid-qns::urn:plain:doctype"][0], "urn:plain:doctype"
		)

	def test_entry_without_process_ids_gets_empty_process_id(self):
		entry = _entry()
		entry["process-ids"] = []
		index = self.code_list.build_index(_list([entry]))
		self.assertEqual(next(iter(index["doctype_names"].values()))[1], "")

	def test_bundled_list_indexes(self):
		import peppol_4_erpnext

		path = os.path.join(os.path.dirname(peppol_4_erpnext.__file__), "peppol_document_types.json")
		with open(path, encoding="utf-8") as fh:
			data = json.load(fh)

		self.code_list.validate_code_list(data)
		index = self.code_list.build_index(data)

		self.assertEqual(index["entry_count"], len(data["values"]))
		self.assertEqual(len(index["doctype_names"]), index["entry_count"])
		self.assertTrue(index["excluded"])


class TestIndexCache(unittest.TestCase):
	"""read_index/write_index against a temp dir standing in for the site dir."""

	def setUp(self):
		from peppol_4_erpnext.peppol_4_erpnext import code_list

		self.code_list = code_list
		self.tmp = tempfile.TemporaryDirectory()
		self.addCleanup(self.tmp.cleanup)

		patcher = patch.object(code_list, "site_dir", return_value=self.tmp.name)
		patcher.start()
		self.addCleanup(patcher.stop)

		self.raw_path = os.path.join(self.tmp.name, code_list.RAW_FILENAME)
		with open(self.raw_path, "w", encoding="utf-8") as fh:
			json.dump(_list(), fh)

	def _write_index(self):
		index = self.code_list.build_index(_list())
		self.code_list.write_index(self.raw_path, index)
		return index

	def test_roundtrip(self):
		written = self._write_index()
		read = self.code_list.read_index(self.raw_path)
		self.assertIsNotNone(read)
		self.assertEqual(read["doctype_names"], written["doctype_names"])
		self.assertEqual(read["entry_count"], written["entry_count"])

	def test_written_index_is_not_world_readable(self):
		self._write_index()
		mode = os.stat(self.code_list.site_index_path()).st_mode & 0o777
		self.assertEqual(mode, 0o640)

	def test_missing_index_returns_none(self):
		self.assertIsNone(self.code_list.read_index(self.raw_path))

	def test_corrupt_index_returns_none(self):
		self._write_index()
		with open(self.code_list.site_index_path(), "w", encoding="utf-8") as fh:
			fh.write("{not json")
		self.assertIsNone(self.code_list.read_index(self.raw_path))

	def test_stamp_mismatch_returns_none(self):
		self._write_index()
		# Same content length would keep size equal; change size to force a mismatch.
		with open(self.raw_path, "w", encoding="utf-8") as fh:
			json.dump(_list([_entry(), _entry(value="urn:other")]), fh)
		self.assertIsNone(self.code_list.read_index(self.raw_path))

	def test_index_built_for_another_file_returns_none(self):
		self._write_index()
		other = os.path.join(self.tmp.name, "other.json")
		with open(other, "w", encoding="utf-8") as fh:
			json.dump(_list(), fh)
		self.assertIsNone(self.code_list.read_index(other))

	def test_drop_index_is_idempotent(self):
		self._write_index()
		self.code_list.drop_index()
		self.code_list.drop_index()
		self.assertFalse(os.path.exists(self.code_list.site_index_path()))


class TestStoreCodeList(unittest.TestCase):
	def setUp(self):
		from peppol_4_erpnext.peppol_4_erpnext import code_list

		self.code_list = code_list
		self.tmp = tempfile.TemporaryDirectory()
		self.addCleanup(self.tmp.cleanup)

		patcher = patch.object(code_list, "site_dir", return_value=self.tmp.name)
		patcher.start()
		self.addCleanup(patcher.stop)

	def test_first_store_creates_site_file_and_switches_active_path(self):
		self.assertEqual(self.code_list.active_raw_path(), self.code_list.bundled_raw_path())

		path = self.code_list._store_code_list(_list())

		self.assertEqual(path, self.code_list.site_raw_path())
		self.assertEqual(self.code_list.active_raw_path(), path)
		with open(path, encoding="utf-8") as fh:
			self.assertEqual(json.load(fh)["version"], "9.7")

	def test_stored_file_is_not_world_readable(self):
		path = self.code_list._store_code_list(_list())
		self.assertEqual(os.stat(path).st_mode & 0o777, 0o640)

	def test_older_version_replaces_newer_one(self):
		self.code_list._store_code_list(_list(version="9.7"))
		self.code_list._store_code_list(_list(version="9.6"))
		with open(self.code_list.site_raw_path(), encoding="utf-8") as fh:
			self.assertEqual(json.load(fh)["version"], "9.6")

	def test_failed_write_restores_previous_bytes_and_drops_index(self):
		self.code_list._store_code_list(_list(version="9.7"))
		self.code_list.write_index(
			self.code_list.site_raw_path(), self.code_list.build_index(_list())
		)
		with open(self.code_list.site_raw_path(), "rb") as fh:
			before = fh.read()

		real_write = self.code_list._atomic_write
		calls = {"n": 0}

		def flaky(path, payload):
			calls["n"] += 1
			if calls["n"] == 1:
				raise OSError("disk full")
			return real_write(path, payload)

		with patch.object(self.code_list, "_atomic_write", side_effect=flaky):
			with self.assertRaises(OSError):
				self.code_list._store_code_list(_list(version="9.8"))

		with open(self.code_list.site_raw_path(), "rb") as fh:
			self.assertEqual(fh.read(), before)
		self.assertFalse(os.path.exists(self.code_list.site_index_path()))


class TestLoadDoctypes(unittest.TestCase):
	def setUp(self):
		from peppol_4_erpnext.peppol_4_erpnext import code_list, lookup

		self.code_list = code_list
		self.lookup = lookup
		self.tmp = tempfile.TemporaryDirectory()
		self.addCleanup(self.tmp.cleanup)

		patcher = patch.object(code_list, "site_dir", return_value=self.tmp.name)
		patcher.start()
		self.addCleanup(patcher.stop)

		lookup.invalidate_doctypes()
		self.addCleanup(lookup.invalidate_doctypes)

	def test_falls_back_to_bundled_list(self):
		self.lookup._load_doctypes()
		self.assertTrue(self.lookup._DOCTYPE_NAMES)
		self.assertTrue(self.lookup._EXCLUDED_DOCTYPE_IDS)

	def test_warm_load_does_not_reparse_raw_list(self):
		self.lookup._load_doctypes()
		with patch.object(self.code_list, "read_index") as mock_read:
			self.lookup._load_doctypes()
		mock_read.assert_not_called()

	def test_deleting_index_rebuilds_it(self):
		self.lookup._load_doctypes()
		self.code_list.drop_index()
		self.lookup.invalidate_doctypes()

		self.lookup._load_doctypes()
		self.assertTrue(os.path.exists(self.code_list.site_index_path()))
		self.assertTrue(self.lookup._DOCTYPE_NAMES)

	def test_site_list_replaces_bundled_entries(self):
		self.lookup._load_doctypes()
		bundled_count = len(self.lookup._DOCTYPE_NAMES)

		self.code_list._store_code_list(_list())
		self.lookup.invalidate_doctypes()
		self.lookup._load_doctypes()

		self.assertEqual(len(self.lookup._DOCTYPE_NAMES), 1)
		self.assertNotEqual(bundled_count, 1)

	def test_broken_site_list_does_not_raise(self):
		with open(self.code_list.site_raw_path(), "w", encoding="utf-8") as fh:
			fh.write("{not json")

		with patch.object(self.lookup, "frappe") as mock_frappe:
			self.lookup._load_doctypes()

		mock_frappe.log_error.assert_called_once()
