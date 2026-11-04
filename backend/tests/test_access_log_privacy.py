"""Real h11 HTTP records through Uvicorn's configured AccessFormatter."""

from copy import deepcopy
import io
import logging
import socket
import threading
import time

import httpx
import pytest
import uvicorn

from app.core.access_logging import PatientListAccessFilter, configure_access_log_privacy
from app.db.session import get_db
from app.main import app
import app.api.patients as patients_api


@pytest.fixture
def live_server(monkeypatch):
    output = io.StringIO()
    config = deepcopy(uvicorn.config.LOGGING_CONFIG)
    config["handlers"]["access"]["stream"] = output
    config["formatters"]["access"]["use_colors"] = False
    loggers = [logging.getLogger(name) for name in ("uvicorn", "uvicorn.error", "uvicorn.access")]
    saved = [(logger, logger.handlers[:], logger.filters[:], logger.level, logger.propagate)
             for logger in loggers]
    overrides = app.dependency_overrides.copy()
    received = []
    route = next(route for route in patients_api.router.routes
                 if getattr(route, "endpoint", None) is patients_api.read_patients)
    app.dependency_overrides[route.dependant.dependencies[0].call] = lambda: object()
    app.dependency_overrides[get_db] = lambda: None

    def search(db, membership, q, limit, offset):
        received.append(q)
        return {"items": [], "total": 0, "limit": limit, "offset": offset}

    monkeypatch.setattr(patients_api, "list_patients", search)
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    server = uvicorn.Server(uvicorn.Config(app, log_config=config, http="h11", lifespan="off"))
    thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
    try:
        # Config must retain the application's logger filter; no test-only install.
        assert sum(isinstance(f, PatientListAccessFilter) for f in loggers[-1].filters) == 1
        thread.start()
        deadline = time.monotonic() + 5
        while not server.started and thread.is_alive() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert server.started
        with httpx.Client(base_url=f"http://127.0.0.1:{sock.getsockname()[1]}") as client:
            yield client, output, received
    finally:
        server.should_exit = True
        if thread.ident is not None:
            thread.join(timeout=5)
        sock.close()
        app.dependency_overrides.clear()
        app.dependency_overrides.update(overrides)
        for logger, handlers, filters, level, propagate in saved:
            logger.handlers = handlers
            logger.filters = filters
            logger.setLevel(level)
            logger.propagate = propagate
        assert not thread.is_alive()


@pytest.mark.parametrize("query,original", [
    ("q=synthetic-phone", "synthetic-phone"),
    ("q=synthetic-name", "synthetic-name"),
    ("q=synthetic%20name%2B%25", "synthetic name+%"),
    ("unexpected=synthetic-private&%73ecret=synthetic-other", None),
])
def test_actual_patient_list_access_log(live_server, query, original):
    client, output, received = live_server
    response = client.get(f"/clinics/279/patients?{query}")
    assert response.status_code == 200
    assert received == [original]
    lines = output.getvalue().splitlines()
    assert len(lines) == 1
    assert '"GET /clinics/279/patients HTTP/1.1" 200 OK' in lines[0]
    assert "?" not in lines[0]
    assert "synthetic" not in lines[0]
    assert "unexpected" not in lines[0] and "%73ecret" not in lines[0]


@pytest.mark.parametrize("method,path", [
    ("GET", "/"), ("GET", "/clinics/279/patients/1"),
    ("POST", "/clinics/279/patients"), ("GET", "/clinics/0/patients"),
    ("GET", "/clinics/-1/patients"), ("GET", "/clinics/279/patients-extra"),
])
def test_actual_unrelated_access_log_unchanged(live_server, method, path):
    client, output, _ = live_server
    response = client.request(method, path + "?q=synthetic-public")
    lines = output.getvalue().splitlines()
    assert len(lines) == 1
    assert f'"{method} {path}?q=synthetic-public HTTP/1.1" {response.status_code}' in lines[0]


def test_filter_sanitizes_args_and_generic_message():
    record = logging.LogRecord("uvicorn.access", logging.INFO, "", 0,
                               '%s - "%s %s HTTP/%s" %d',
                               ("127.0.0.1:123", "GET", "/clinics/00042/patients?q=synthetic", "1.1", 401), None)
    record.message = record.getMessage()
    assert PatientListAccessFilter().filter(record)
    assert record.args[2] == "/clinics/00042/patients"
    assert "synthetic" not in logging.Formatter("%(message)s").format(record)
    assert 'GET /clinics/00042/patients HTTP/1.1" 401' in record.getMessage()


def test_configuration_is_idempotent():
    logger = logging.getLogger("uvicorn.access")
    handlers = logger.handlers[:]
    configure_access_log_privacy()
    configure_access_log_privacy()
    assert logger.handlers == handlers
    assert sum(isinstance(f, PatientListAccessFilter) for f in logger.filters) == 1


def render_access_record(record):
    """Apply the filter before the real Uvicorn formatter, as a logger does."""
    output = io.StringIO()
    logger = logging.Logger("uvicorn.access", logging.INFO)
    logger.propagate = False
    logger.addFilter(PatientListAccessFilter())
    handler = logging.StreamHandler(output)
    handler.setFormatter(uvicorn.logging.AccessFormatter(
        fmt='%(client_addr)s - "%(request_line)s" %(status_code)s', use_colors=False,
    ))
    logger.addHandler(handler)
    logger.handle(record)
    return output.getvalue()


@pytest.mark.parametrize("message", [
    '%s - "%s %s HTTP/%s" %d',
    'Changed template: %s %s %s %s %s',
    'Already formatted GET /clinics/42/patients?q=synthetic-template',
])
def test_compatible_args_use_safe_template_and_real_formatter(message):
    record = logging.LogRecord("uvicorn.access", logging.INFO, "", 0, message,
                               ("127.0.0.1:123", "GET",
                                "/clinics/42/patients?q=synthetic%20private&other=synthetic-other",
                                "1.1", 422), None)
    record.message = "synthetic-cached"
    record.color_message = "synthetic-colored"
    rendered = render_access_record(record)
    assert rendered.splitlines() == ['127.0.0.1:123 - "GET /clinics/42/patients HTTP/1.1" 422 Unprocessable Entity']
    assert "synthetic" not in rendered and "?" not in rendered
    assert "synthetic" not in record.getMessage()


@pytest.mark.parametrize("args", [
    (),
    ("GET", "/clinics/42/patients?q=synthetic-short", "1.1", 200),
    ("127.0.0.1", "GET", "/clinics/42/patients?q=synthetic-extra", "1.1", 200, "extra"),
    ["127.0.0.1", "GET", "/clinics/42/patients?q=synthetic-list", "1.1", 200],
    {"target": "/clinics/42/patients?q=synthetic-dict"},
    "GET /clinics/42/patients?q=synthetic-string",
    ("127.0.0.1", "GET", b"/clinics/42/patients?q=synthetic-bytes", "1.1", 200),
    ("127.0.0.1", "GET", "/clinics/42/patients?q=synthetic-status", "1.1", "200"),
    ("127.0.0.1", "/clinics/42/patients?q=synthetic-moved", "GET", "1.1", 200),
])
def test_unrecognized_records_are_not_emitted(args):
    record = logging.LogRecord("uvicorn.access", logging.INFO, "", 0,
                               "GET /clinics/42/patients?q=synthetic-unrecognized", (), None)
    record.args = args
    assert render_access_record(record) == ""


def test_installed_uvicorn_matches_pin():
    assert uvicorn.__version__ == "0.52.4"
