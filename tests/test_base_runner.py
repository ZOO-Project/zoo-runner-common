import pytest
from unittest.mock import MagicMock, patch

from zoo_runner_common.base_runner import BaseRunner

DUMMY_CWL = {
    "cwlVersion": "v1.2",
    "$graph": [{"class": "Workflow", "id": "#main", "inputs": [], "outputs": [], "steps": []}],
}
DUMMY_CONF = {"lenv": {"Identifier": "main", "usid": "test-123", "message": ""}}


class ConcreteRunner(BaseRunner):
    def wrap(self):
        return {"wrapped": True}

    def execute(self):
        return "done"


@pytest.fixture
def runner():
    with patch("zoo_runner_common.base_runner.CWLWorkflow") as mock_cwl_cls:
        mock_cwl = MagicMock()
        mock_cwl.get_workflow.return_value = MagicMock(inputs=[])
        mock_cwl.eval_resource.return_value = {
            "coresMin": [], "coresMax": [], "ramMin": [], "ramMax": [],
            "tmpdirMin": [], "tmpdirMax": [], "outdirMin": [], "outdirMax": [],
        }
        mock_cwl_cls.return_value = mock_cwl
        yield ConcreteRunner(cwl=DUMMY_CWL, inputs={}, conf=DUMMY_CONF, outputs={"stac": {"value": None}})


def test_get_workflow_id(runner):
    assert runner.get_workflow_id() == "main"


def test_update_status_calls_zoo(runner, capsys):
    runner.update_status(10, "testing")
    out = capsys.readouterr().out
    assert "Status 10" in out
    assert runner.conf.conf["lenv"]["message"] == "testing"


def test_get_namespace_name_format(runner):
    name = runner.get_namespace_name()
    assert name.startswith("main-")
    # format: "{workflow_id}-{8 hex chars}"
    assert len(name) == len("main-") + 8


def test_get_namespace_name_is_stable(runner):
    assert runner.get_namespace_name() == runner.get_namespace_name()


def test_get_namespace_name_is_lowercase(runner):
    assert runner.get_namespace_name() == runner.get_namespace_name().lower()


def test_validate_inputs_returns_true(runner):
    assert runner.validate_inputs() is True


def test_log_output_does_not_crash(runner):
    runner.log_output({"key": "value"})


def test_execute(runner):
    assert runner.execute() == "done"


def test_wrap(runner):
    assert runner.wrap() == {"wrapped": True}


def test_get_max_cores_uses_env_default(runner, monkeypatch):
    monkeypatch.setenv("DEFAULT_MAX_CORES", "8")
    assert runner.get_max_cores() == 8


def test_get_max_ram_returns_mi_format(runner, monkeypatch):
    monkeypatch.setenv("DEFAULT_MAX_RAM", "2048")
    assert runner.get_max_ram() == "2048Mi"


def test_get_volume_size_returns_env_default_when_unit_matches(runner, monkeypatch):
    # When the unit in DEFAULT_VOLUME_SIZE matches the requested unit, value is returned as-is
    monkeypatch.setenv("DEFAULT_VOLUME_SIZE", "20Mi")
    assert runner.get_volume_size() == "20Mi"  # unit="Mi" by default


def test_get_volume_size_fallback_to_10_when_unit_mismatch(runner, monkeypatch):
    # When unit doesn't match the default string (e.g. asking for Mi but default is Gi),
    # the method returns hardcoded "10{unit}"
    monkeypatch.setenv("DEFAULT_VOLUME_SIZE", "20Gi")
    assert runner.get_volume_size(unit="Mi") == "10Mi"


def test_get_volume_size_gi_unit_uses_default(runner, monkeypatch):
    monkeypatch.setenv("DEFAULT_VOLUME_SIZE", "20Gi")
    assert runner.get_volume_size(unit="Gi") == "20Gi"


def test_assert_parameters_true_when_no_required_inputs(runner):
    runner.workflow.get_workflow_inputs.return_value = []
    assert runner.assert_parameters() is True


def test_assert_parameters_false_when_input_missing(runner):
    runner.workflow.get_workflow_inputs.return_value = ["required_input"]
    assert runner.assert_parameters() is False


def test_prepare_calls_pre_execution_hook(runner):
    handler = MagicMock()
    handler.get_additional_parameters.return_value = {}
    runner.execution_handler = handler
    runner.prepare()
    handler.pre_execution_hook.assert_called_once()


def test_prepare_returns_namespace_with_cwl_and_params(runner):
    result = runner.prepare()
    assert hasattr(result, "cwl")
    assert hasattr(result, "params")
    assert result.cwl == {"wrapped": True}


def test_finalize_calls_post_execution_hook_and_handle_outputs(runner):
    handler = MagicMock()
    runner.execution_handler = handler
    runner.finalize("log", {"output": 1}, {}, [])
    handler.post_execution_hook.assert_called_once_with("log", {"output": 1}, {}, [])
    handler.handle_outputs.assert_called_once_with("log", {"output": 1}, {}, [])


def test_default_handler_has_all_required_methods(runner):
    handler = runner.execution_handler
    for method in [
        "pre_execution_hook", "post_execution_hook", "get_secrets",
        "get_additional_parameters", "get_pod_env_vars", "get_pod_node_selector",
        "handle_outputs", "set_job_id",
    ]:
        assert callable(getattr(handler, method)), f"Missing method: {method}"


def test_zoo_conf_wraps_conf(runner):
    assert runner.conf.conf is DUMMY_CONF


def test_legacy_zoo_conf_namespace(runner):
    assert runner.zoo_conf.conf is DUMMY_CONF
