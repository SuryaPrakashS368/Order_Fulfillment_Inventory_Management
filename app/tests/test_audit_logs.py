from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi.routing import APIRoute
from app.routes.audit_logs import router as audit_logs_router
from app.main import app
from app.dependencies.auth import get_current_user
from app.models.audit_log import AuditLog
from app.models.role import Role
from app.models.user import User


# ============================================================
# Helpers
# ============================================================

@pytest.fixture
def audit_admin(db_session):
    role = (
        db_session.query(Role)
        .filter(Role.name == "Admin")
        .first()
    )

    if role is None:
        role = Role(name="Admin")
        db_session.add(role)
        db_session.flush()

    user = User(
        name="Audit Admin",
        email="audit_admin_test@example.com",
        password_hash="test-password-hash",
        role_id=role.id,
        is_active=True,
    )

    db_session.add(user)
    db_session.flush()

    return user


@pytest.fixture
def audit_request(client):
    """
    Override authentication and the route permission checker.
    The audit route still performs its Admin role check.
    """

    def make_request(
        method,
        path,
        role_name="Admin",
        user_id=1,
        **kwargs,
    ):
        method = method.upper()
        route_path = path.split("?", 1)[0]

        route = next(
    (
        item
        for item in audit_logs_router.routes
        if isinstance(item, APIRoute)
        and method in item.methods
        and item.path_regex.match(route_path)
    ),
    None,
)

        if route is None:
            raise AssertionError(
                f"Route not found: {method} {route_path}"
            )

        test_user = SimpleNamespace(
            id=user_id,
            role_id=1,
            is_active=True,
            role=SimpleNamespace(name=role_name),
        )

        app.dependency_overrides[get_current_user] = (
            lambda: test_user
        )

        # require_permission() creates a permission_checker
        # dependency for each protected route.
        permission_checker = next(
            (
                dependency.call
                for dependency in route.dependant.dependencies
                if getattr(
                    dependency.call,
                    "__name__",
                    "",
                ) == "permission_checker"
            ),
            None,
        )

        if permission_checker is None:
            app.dependency_overrides.pop(
                get_current_user,
                None,
            )
            raise AssertionError(
                f"Permission checker not found for {route_path}"
            )

        app.dependency_overrides[permission_checker] = (
            lambda: test_user
        )

        try:
            return client.request(
                method,
                path,
                **kwargs,
            )
        finally:
            app.dependency_overrides.pop(
                permission_checker,
                None,
            )
            app.dependency_overrides.pop(
                get_current_user,
                None,
            )

    return make_request


def create_audit_log(
    db_session,
    user_id,
    action="CREATE",
    entity="product",
    entity_id=10,
    details=None,
    ip_address="127.0.0.1",
    created_at=None,
):
    record = AuditLog(
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        details=details or {"source": "test"},
        ip_address=ip_address,
        created_at=created_at or datetime.utcnow(),
    )

    db_session.add(record)
    db_session.flush()

    return record


# ============================================================
# Authentication and authorization
# ============================================================

def test_list_audit_logs_requires_authentication(client):
    response = client.get("/api/audit-logs")

    assert response.status_code in (401, 403)


def test_get_audit_log_requires_authentication(client):
    response = client.get("/api/audit-logs/1")

    assert response.status_code in (401, 403)


def test_non_admin_cannot_list_audit_logs(
    audit_request,
    audit_admin,
):
    response = audit_request(
        "GET",
        "/api/audit-logs",
        role_name="Customer",
        user_id=audit_admin.id,
    )

    assert response.status_code == 403


def test_non_admin_cannot_get_audit_log(
    db_session,
    audit_request,
    audit_admin,
):
    record = create_audit_log(
        db_session,
        user_id=audit_admin.id,
    )

    response = audit_request(
        "GET",
        f"/api/audit-logs/{record.id}",
        role_name="Customer",
        user_id=audit_admin.id,
    )

    assert response.status_code == 403


# ============================================================
# GET /api/audit-logs
# ============================================================

def test_list_audit_logs_success(
    db_session,
    audit_request,
    audit_admin,
):
    create_audit_log(
        db_session,
        user_id=audit_admin.id,
        action="CREATE",
        entity="product",
        entity_id=101,
    )

    create_audit_log(
        db_session,
        user_id=audit_admin.id,
        action="UPDATE",
        entity="order",
        entity_id=202,
    )

    response = audit_request(
        "GET",
        "/api/audit-logs",
        user_id=audit_admin.id,
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 2


def test_filter_audit_logs_by_user(
    db_session,
    audit_request,
    audit_admin,
):
    other_user = User(
        name="Another Audit User",
        email="another_audit_user@example.com",
        password_hash="test-password-hash",
        role_id=audit_admin.role_id,
        is_active=True,
    )
    db_session.add(other_user)
    db_session.flush()

    create_audit_log(
        db_session,
        user_id=audit_admin.id,
        action="CREATE",
    )

    create_audit_log(
        db_session,
        user_id=other_user.id,
        action="DELETE",
    )

    response = audit_request(
        "GET",
        f"/api/audit-logs?user_id={audit_admin.id}",
        user_id=audit_admin.id,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1
    assert all(
        item["user_id"] == audit_admin.id
        for item in data
    )


def test_filter_audit_logs_by_action(
    db_session,
    audit_request,
    audit_admin,
):
    create_audit_log(
        db_session,
        user_id=audit_admin.id,
        action="CREATE",
    )

    create_audit_log(
        db_session,
        user_id=audit_admin.id,
        action="DELETE",
    )

    response = audit_request(
        "GET",
        "/api/audit-logs?action=CREATE",
        user_id=audit_admin.id,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1
    assert all(
        item["action"] == "CREATE"
        for item in data
    )


def test_filter_audit_logs_by_entity(
    db_session,
    audit_request,
    audit_admin,
):
    create_audit_log(
        db_session,
        user_id=audit_admin.id,
        entity="product",
    )

    create_audit_log(
        db_session,
        user_id=audit_admin.id,
        entity="order",
    )

    response = audit_request(
        "GET",
        "/api/audit-logs?entity=product",
        user_id=audit_admin.id,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1
    assert all(
        item["entity"] == "product"
        for item in data
    )


def test_filter_audit_logs_by_entity_id(
    db_session,
    audit_request,
    audit_admin,
):
    create_audit_log(
        db_session,
        user_id=audit_admin.id,
        entity_id=111,
    )

    create_audit_log(
        db_session,
        user_id=audit_admin.id,
        entity_id=222,
    )

    response = audit_request(
        "GET",
        "/api/audit-logs?entity_id=111",
        user_id=audit_admin.id,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1
    assert all(
        item["entity_id"] == 111
        for item in data
    )


def test_audit_logs_pagination(
    db_session,
    audit_request,
    audit_admin,
):
    for index in range(5):
        create_audit_log(
            db_session,
            user_id=audit_admin.id,
            action=f"ACTION_{index}",
            entity="test",
            entity_id=index + 1,
        )

    response = audit_request(
        "GET",
        "/api/audit-logs?skip=0&limit=2",
        user_id=audit_admin.id,
    )

    assert response.status_code == 200
    assert len(response.json()) <= 2


@pytest.mark.parametrize(
    "query",
    [
        "?skip=-1",
        "?limit=0",
        "?limit=101",
        "?user_id=0",
        "?entity_id=0",
        "?action=",
        "?entity=",
    ],
)
def test_audit_logs_reject_invalid_query_parameters(
    audit_request,
    audit_admin,
    query,
):
    response = audit_request(
        "GET",
        f"/api/audit-logs{query}",
        user_id=audit_admin.id,
    )

    assert response.status_code == 422


# ============================================================
# GET /api/audit-logs/{audit_log_id}
# ============================================================

def test_get_audit_log_success(
    db_session,
    audit_request,
    audit_admin,
):
    record = create_audit_log(
        db_session,
        user_id=audit_admin.id,
        action="UPDATE",
        entity="product",
        entity_id=123,
        details={"field": "price"},
        ip_address="192.168.1.10",
    )

    response = audit_request(
        "GET",
        f"/api/audit-logs/{record.id}",
        user_id=audit_admin.id,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == record.id
    assert data["user_id"] == audit_admin.id
    assert data["action"] == "UPDATE"
    assert data["entity"] == "product"
    assert data["entity_id"] == 123
    assert data["details"] == {"field": "price"}
    assert data["ip_address"] == "192.168.1.10"
    assert "created_at" in data


def test_get_audit_log_not_found(
    audit_request,
    audit_admin,
):
    response = audit_request(
        "GET",
        "/api/audit-logs/999999",
        user_id=audit_admin.id,
    )

    assert response.status_code == 404
    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "NOT_FOUND"
    assert data["error"]["message"] == "Audit log not found"


def test_audit_logs_are_returned_newest_first(
    db_session,
    audit_request,
    audit_admin,
):
    older = create_audit_log(
        db_session,
        user_id=audit_admin.id,
        action="OLDER",
        created_at=datetime.utcnow() - timedelta(days=1),
    )

    newer = create_audit_log(
        db_session,
        user_id=audit_admin.id,
        action="NEWER",
        created_at=datetime.utcnow(),
    )

    response = audit_request(
        "GET",
        "/api/audit-logs?limit=100",
        user_id=audit_admin.id,
    )

    assert response.status_code == 200

    data = response.json()
    ids = [item["id"] for item in data]

    assert ids.index(newer.id) < ids.index(older.id)
