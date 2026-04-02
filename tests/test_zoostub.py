from zoo_runner_common.zoostub import ZooStub


def test_service_constants():
    zoo = ZooStub()
    assert zoo.SERVICE_ACCEPTED == 0
    assert zoo.SERVICE_STARTED == 1
    assert zoo.SERVICE_SUCCEEDED == 3
    assert zoo.SERVICE_FAILED == 4


def test_update_status_prints(capsys):
    zoo = ZooStub()
    zoo.update_status({}, 42)
    assert "Status 42" in capsys.readouterr().out


def test_underscore_method_prints(capsys):
    zoo = ZooStub()
    zoo._("hello world")
    assert "hello world" in capsys.readouterr().out


def test_logging_methods_do_not_crash():
    zoo = ZooStub()
    zoo.trace("trace msg")
    zoo.debug("debug msg")
    zoo.info("info msg")
    zoo.success("success msg")
    zoo.warning("warning msg")
    zoo.error("error msg")
    zoo.critical("critical msg")
