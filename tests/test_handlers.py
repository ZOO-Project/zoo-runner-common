import pytest

from zoo_runner_common.handlers import ExecutionHandler


class ConcreteHandler(ExecutionHandler):
    def pre_execution_hook(self):
        pass

    def post_execution_hook(self, log, output, usage_report, tool_logs):
        pass

    def get_secrets(self):
        return {}

    def get_pod_env_vars(self):
        return {}

    def get_pod_node_selector(self):
        return {}

    def handle_outputs(self, log, output, usage_report, tool_logs):
        pass

    def get_additional_parameters(self):
        return {}


def test_execution_handler_is_abstract():
    with pytest.raises(TypeError):
        ExecutionHandler()


def test_concrete_subclass_instantiates():
    handler = ConcreteHandler()
    assert handler is not None


def test_set_job_id():
    handler = ConcreteHandler()
    handler.set_job_id("job-456")
    assert handler.job_id == "job-456"


def test_init_accepts_kwargs():
    handler = ConcreteHandler(conf={"lenv": {}}, outputs={"stac": {}})
    assert handler.conf == {"lenv": {}}
    assert handler.outputs == {"stac": {}}


def test_job_id_defaults_to_none():
    handler = ConcreteHandler()
    assert handler.job_id is None


def test_results_defaults_to_none():
    handler = ConcreteHandler()
    assert handler.results is None


def test_outputs_defaults_to_empty_dict():
    handler = ConcreteHandler()
    assert handler.outputs == {}
