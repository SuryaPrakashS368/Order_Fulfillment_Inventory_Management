def test_notifications_require_authentication(client):
    response = client.get("/api/notifications")

    assert response.status_code in (401, 403)


def test_unread_notification_count_requires_authentication(client):
    response = client.get(
        "/api/notifications/unread-count"
    )

    assert response.status_code in (401, 403)


def test_mark_notification_read_requires_authentication(client):
    response = client.patch(
        "/api/notifications/1/read"
    )

    assert response.status_code in (401, 403)


def test_mark_all_notifications_read_requires_authentication(client):
    response = client.patch(
        "/api/notifications/read-all"
    )

    assert response.status_code in (401, 403)


def test_audit_logs_require_authentication(client):
    response = client.get("/api/audit-logs")

    assert response.status_code in (401, 403)


def test_dashboard_requires_authentication(client):
    response = client.get("/api/dashboard/summary")

    assert response.status_code in (401, 403)


def test_low_stock_report_requires_authentication(client):
    response = client.get("/api/dashboard/low-stock")

    assert response.status_code in (401, 403)