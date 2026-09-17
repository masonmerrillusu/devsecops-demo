from app.main import app, build_checks


def test_page_loads():
    response = app.test_client().get("/")
    assert response.status_code == 200
    assert b"Container Security Self-Check" in response.data


def test_health_check():
    response = app.test_client().get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_non_root_passes():
    checks = build_checks("appuser", 1000, 8000)
    assert all(check["passed"] for check in checks)


def test_root_fails():
    user_check = build_checks("root", 0, 8000)[0]
    assert user_check["passed"] is False


def test_privileged_port_fails():
    port_check = build_checks("appuser", 1000, 80)[1]
    assert port_check["passed"] is False