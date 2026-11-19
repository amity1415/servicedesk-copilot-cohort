from copilot.rag.loaders import is_allowed, load_document


def test_scope_aliases_and_policy_register_are_enforced(tmp_path):
    metadata = {"audience": "it-staff", "os": "Mac OS", "region": "Asia-Pacific"}
    assert is_allowed(metadata, "analyst", "macos", " APAC ")
    assert not is_allowed(metadata, "employee", "macos", "APAC")
    assert not is_allowed(metadata, "analyst", "windows", "APAC")
    assert not is_allowed(metadata, "analyst", "macos", "EMEA")
    assert not is_allowed({**metadata, "effective_date": "9999-01-01"}, "analyst")
    policies = tmp_path / "data" / "policies"
    policies.mkdir(parents=True)
    policy = policies / "POL-123_v2.md"
    policy.write_text("---\naudience: employee\nstatus: current\n---\nPolicy", encoding="utf-8")
    assert not is_allowed(load_document(policy).metadata)
    register = policies / "register.csv"
    register.write_text("id,file,status\nPOL-123,POL-123_v2.md,superseded\n", encoding="utf-8")
    assert not is_allowed(load_document(policy).metadata)
    register.write_text("id,file,status\nPOL-123,POL-123_v2.md,current\n", encoding="utf-8")
    assert is_allowed(load_document(policy).metadata)
