"""Chain tests: append, verify, tamper detection."""

from news_network.chain import DossierChain


def _chain(tmp_path):
    return DossierChain(tmp_path / "chain.jsonl")


def test_append_and_verify(tmp_path):
    chain = _chain(tmp_path)
    # a properly sealed judgment (verify() recomputes the seal)
    import hashlib, json
    judgment = {"assessor_id": "hermes", "verdict": "aligned"}
    unsigned = {k: v for k, v in judgment.items() if k != "integrity_hash"}
    judgment["integrity_hash"] = hashlib.sha256(
        json.dumps(unsigned, sort_keys=True, separators=(",", ":"),
                   default=str).encode()).hexdigest()
    rec = chain.append(
        event_id="evt1",
        evidence_pack={"claims": [{"id": "c1", "text": "X happened"}]},
        judgments=[judgment],
        panel={"verdict": "aligned"},
        dossier_markdown="# dossier",
    )
    assert rec.prev_hash == chain.records[0].record_hash
    ok, details = chain.verify()
    assert ok, details["failures"]
    assert details["records"] == 2  # genesis + 1


def test_tamper_detected(tmp_path):
    chain = _chain(tmp_path)
    chain.append("evt1", {"a": 1}, [], {"verdict": "aligned"}, "# d")
    # tamper with the chained evidence
    chain.records[1].evidence_pack["a"] = 999
    ok, details = chain.verify()
    assert not ok
    assert details["failures"]


def test_chain_persists_across_reopen(tmp_path):
    chain = _chain(tmp_path)
    chain.append("evt1", {"a": 1}, [], {"verdict": "aligned"}, "# d")
    chain2 = _chain(tmp_path)  # reloads from the same file
    ok, _ = chain2.verify()
    assert ok
    assert len(chain2.records) == 2
