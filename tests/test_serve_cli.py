import pytest

from copilot.cli import main


@pytest.mark.parametrize(
    "arguments,host,port",
    [
        (["serve"], "127.0.0.1", 8082),
        (["serve", "--host", "0.0.0.0", "--port", "8095"], "0.0.0.0", 8095),
    ],
)
def test_server_binding_is_configurable(monkeypatch, arguments, host, port):
    calls = []
    monkeypatch.setattr("uvicorn.run", lambda *args, **kwargs: calls.append(kwargs))
    assert main(arguments) == 0
    assert calls[0]["host"] == host and calls[0]["port"] == port


@pytest.mark.parametrize("port", ["0", "-1", "65536"])
def test_invalid_port_is_rejected(port):
    with pytest.raises(SystemExit) as error:
        main(["serve", "--port", port])
    assert error.value.code == 2
