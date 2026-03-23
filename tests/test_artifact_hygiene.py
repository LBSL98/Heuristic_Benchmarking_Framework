from hpc_framework.artifact_hygiene import is_legacy_result_name, is_legacy_workdir_name


def test_is_legacy_result_name_detects_old_and_new_json_names():
    assert is_legacy_result_name("n2000_p50.json.gz__metis__seed42.json") is True
    assert is_legacy_result_name("n2000_p50.json.gz__kahip__seed42.json") is True
    assert is_legacy_result_name("n2000_p50.json.gz__greedy__seed42.json") is True

    assert is_legacy_result_name("n2000_p50.json.gz__metis__k8__b0.03__seed42.json") is False
    assert is_legacy_result_name("n2000_p50.json.gz__kahip__k8__b0.03__seed42.json") is False
    assert is_legacy_result_name("n2000_p50.json.gz__greedy__dv0.10__seed42.json") is False


def test_is_legacy_workdir_name_detects_old_and_new_workdirs():
    assert is_legacy_workdir_name("run_metis__n2000_p50.json.gz__seed42") is True
    assert is_legacy_workdir_name("run_kahip__n2000_p50.json.gz__seed42") is True

    assert is_legacy_workdir_name("run_metis__n2000_p50.json.gz__k8__b0.03__seed42") is False
    assert is_legacy_workdir_name("run_kahip__n2000_p50.json.gz__k8__b0.03__seed42") is False
