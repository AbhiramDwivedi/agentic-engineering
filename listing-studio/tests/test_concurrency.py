import pytest

from concurrency.lease import LeaseManager, PriceStore
from concurrency.occ import Row, VersionedStore
from concurrency.redact import pseudonymise, redact_record, restore


def test_stale_holder_write_is_rejected():
    mgr, store = LeaseManager(ttl=30), PriceStore()
    a = mgr.acquire("run-a", now=0)
    assert a and a.token == 1
    assert mgr.acquire("run-b", now=10) is None  # still held
    b = mgr.acquire("run-b", now=31)  # a's lease expired during a slow model call
    assert b and b.token == 2
    assert store.write("SKU-1", 1999, b.token) is True
    assert store.write("SKU-1", 1500, a.token) is False  # a wakes up and is fenced out
    assert store.prices["SKU-1"] == 1999


def test_version_conflict_returns_structured_result():
    s = VersionedStore()
    s.rows["SKU-1"] = Row(1000, 1)
    first = s.read("SKU-1")
    second = s.read("SKU-1")
    assert s.write_if_version("SKU-1", 1100, first.version) == {"ok": True, "version": 2}
    res = s.write_if_version("SKU-1", 900, second.version)
    assert res == {"ok": False, "error": "conflict", "action": "re-read"}
    assert "1100" not in str(res)
    assert s.rows["SKU-1"].cents == 1100


def test_redact_record_drops_pii_fields():
    out = redact_record({"sku": "SKU-1", "contact_email": "a@b.com", "contact_name": "Ann"})
    assert out == {"sku": "SKU-1"}


def test_pseudonymise_round_trip():
    text, m = pseudonymise("Write to a@b.com or c@d.org")
    assert "@" not in text and len(m) == 2
    assert restore(text, m) == "Write to a@b.com or c@d.org"


def test_restore_rejects_dropped_and_invented_placeholders():
    text, m = pseudonymise("mail a@b.com")
    with pytest.raises(ValueError, match="dropped"):
        restore("mail someone", m)
    with pytest.raises(ValueError, match="invented"):
        restore(text + " <EMAIL_9>", m)
