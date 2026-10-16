import pytest
from types import SimpleNamespace

from app.models.notification import Notification
from app.models.role import Role
from app.models.user import User
from app.models.user import User
from app.models.role import Role
from app.core.security import hash_password

@pytest.fixture
def notification_test_user(db_session):
    role = (
        db_session.query(Role)
        .filter(Role.name == "Admin")
        .first()
    )

    if role is None:
        role = Role(name="Admin")
        db_session.add(role)
        db_session.flush()

    user = (
        db_session.query(User)
        .filter(User.email == "admin_test@example.com")
        .first()
    )

    if user is None:
        user = User(
            name="Test Admin",
            email="admin_test@example.com",
            password_hash=hash_password("test_password"),
            role_id=role.id,
            is_active=True,
        )
        db_session.add(user)
        db_session.flush()

    return user

@pytest.fixture
def notification_other_user(db_session):
    role = (
        db_session.query(Role)
        .filter(Role.name == "Customer")
        .first()
    )

    if role is None:
        role = Role(name="Customer")
        db_session.add(role)
        db_session.flush()

    user = (
        db_session.query(User)
        .filter(User.email == "notification_other@example.com")
        .first()
    )

    if user is None:
        user = User(
            name="Other Test User",
            email="notification_other@example.com",
            password_hash=hash_password("test_password"),
            role_id=role.id,
            is_active=True,
        )
        db_session.add(user)
        db_session.flush()

    return user

# ============================================================
# Helper
# ============================================================

def create_test_user(db_session, email="notification_test@example.com"):
    role = (
        db_session.query(Role)
        .filter(Role.name == "Admin")
        .first()
    )

    if not role:
        role = Role(name="Admin")
        db_session.add(role)
        db_session.flush()

    user = User(
        name="Notification Test User",
        email=email,
        password_hash="hashed-password",
        role_id=role.id,
        is_active=True,
    )

    db_session.add(user)
    db_session.flush()

    return user


def create_notification(
    db_session,
    user_id,
    title="Test Notification",
    message="This is a test notification",
    notification_type="TEST",
    reference_entity=None,
    reference_id=None,
    is_read=False,
):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        reference_entity=reference_entity,
        reference_id=reference_id,
        is_read=is_read,
    )

    db_session.add(notification)
    db_session.flush()

    return notification


# ============================================================
# Authentication
# ============================================================

def test_notifications_require_authentication(client):
    response = client.get("/api/notifications")

    assert response.status_code in (401, 403)


def test_unread_count_requires_authentication(client):
    response = client.get(
        "/api/notifications/unread-count"
    )

    assert response.status_code in (401, 403)


def test_mark_all_read_requires_authentication(client):
    response = client.patch(
        "/api/notifications/read-all"
    )

    assert response.status_code in (401, 403)


def test_mark_one_read_requires_authentication(client):
    response = client.patch(
        "/api/notifications/1/read"
    )

    assert response.status_code in (401, 403)

# ============================================================
# GET /api/notifications
# ============================================================

def test_get_my_notifications(
    db_session,
    authenticated_request,
    notification_test_user,
):
    user = create_test_user(
        db_session,
        "notifications_list@example.com",
    )

    # authenticated_request uses user id 1
    # Make sure notification belongs to that user.
    create_notification(
        db_session,
        user_id=notification_test_user.id,
        title="Order Created",
        message="Your order was created.",
        notification_type="ORDER_CREATED",
        reference_entity="order",
        reference_id=10,
    )

    create_notification(
        db_session,
        user_id=notification_test_user.id,
        title="Order Shipped",
        message="Your order has been shipped.",
        notification_type="ORDER_SHIPPED",
        reference_entity="order",
        reference_id=10,
    )

    response = authenticated_request(
        "GET",
        "/api/notifications",
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 2

    assert all(
    item["user_id"] == notification_test_user.id
    for item in data
    )


def test_get_notifications_unread_only(
    db_session,
    authenticated_request,
    notification_test_user,
):
    create_notification(
    db_session,
    user_id=notification_test_user.id,
    title="Unread Notification",
    message="Unread message",
    notification_type="TEST",
    is_read=False,
)

    create_notification(
        db_session,
        user_id=notification_test_user.id,
        title="Read Notification",
        message="Read message",
        notification_type="TEST",
        is_read=True,
    )

    response = authenticated_request(
        "GET",
        "/api/notifications?unread_only=true",
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    assert all(
        item["is_read"] is False
        for item in data
    )


def test_notifications_do_not_return_other_users(
    db_session,
    authenticated_request,
    notification_test_user,
    notification_other_user,
):
    # Notification for authenticated user.
    create_notification(
        db_session,
        user_id=notification_test_user.id,
        title="My Notification",
        message="My message",
        notification_type="TEST",
    )

    # Different user.
    other_user = create_test_user(
        db_session,
        "other_notification_user@example.com",
    )

    create_notification(
        db_session,
        user_id=notification_other_user.id,
        title="Other Notification",
        message="Other message",
        notification_type="TEST",
    )

    response = authenticated_request(
        "GET",
        "/api/notifications",
    )

    assert response.status_code == 200

    data = response.json()

    assert all(
    item["user_id"] == notification_test_user.id
    for item in data
    )


# ============================================================
# GET /api/notifications/unread-count
# ============================================================

def test_get_unread_notification_count(
    db_session,
    authenticated_request,
    notification_test_user,
):
    create_notification(
        db_session,
        user_id=notification_test_user.id,
        title="Unread 1",
        message="Message 1",
        notification_type="TEST",
        is_read=False,
    )

    create_notification(
        db_session,
        user_id=notification_test_user.id,
        title="Unread 2",
        message="Message 2",
        notification_type="TEST",
        is_read=False,
    )

    create_notification(
        db_session,
        user_id=notification_test_user.id,
        title="Read",
        message="Message 3",
        notification_type="TEST",
        is_read=True,
    )

    response = authenticated_request(
        "GET",
        "/api/notifications/unread-count",
    )

    assert response.status_code == 200

    data = response.json()

    assert "unread_count" in data
    assert data["unread_count"] == 2


def test_unread_count_only_counts_current_user(
    db_session,
    authenticated_request,
    notification_test_user,
    notification_other_user,
):
    create_notification(
        db_session,
        user_id=notification_test_user.id,
        title="My Unread",
        message="Message",
        notification_type="TEST",
        is_read=False,
    )


    create_notification(
        db_session,
        user_id=notification_other_user.id,
        title="Other Unread",
        message="Message",
        notification_type="TEST",
        is_read=False,
    )

    response = authenticated_request(
        "GET",
        "/api/notifications/unread-count",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["unread_count"] == 1


# ============================================================
# PATCH /api/notifications/{notification_id}/read
# ============================================================

def test_mark_notification_as_read(
    db_session,
    authenticated_request,
    notification_test_user,
):
    notification = create_notification(
        db_session,
        user_id=notification_test_user.id,
        title="Unread Notification",
        message="Please read this.",
        notification_type="TEST",
        is_read=False,
    )

    response = authenticated_request(
        "PATCH",
        f"/api/notifications/{notification.id}/read",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == notification.id
    assert data["is_read"] is True
    assert data["read_at"] is not None


def test_mark_already_read_notification(
    db_session,
    authenticated_request,
    notification_test_user,
):
    notification = create_notification(
        db_session,
        user_id=notification_test_user.id,
        title="Already Read",
        message="Already read message.",
        notification_type="TEST",
        is_read=True,
    )

    response = authenticated_request(
        "PATCH",
        f"/api/notifications/{notification.id}/read",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == notification.id
    assert data["is_read"] is True


def test_mark_notification_not_found(
    authenticated_request,
):
    response = authenticated_request(
        "PATCH",
        "/api/notifications/999999/read",
    )

    assert response.status_code == 404


def test_cannot_mark_other_users_notification_as_read(
    db_session,
    authenticated_request,
):
    other_user = create_test_user(
        db_session,
        "notification_owner@example.com",
    )

    notification = create_notification(
        db_session,
        user_id=other_user.id,
        title="Private Notification",
        message="Private message.",
        notification_type="TEST",
        is_read=False,
    )

    response = authenticated_request(
        "PATCH",
        f"/api/notifications/{notification.id}/read",
    )

    assert response.status_code == 403


# ============================================================
# PATCH /api/notifications/read-all
# ============================================================

def test_mark_all_notifications_as_read(
    db_session,
    authenticated_request,
    notification_test_user,
):
    create_notification(
        db_session,
        user_id=notification_test_user.id,
        title="Unread 1",
        message="Message 1",
        notification_type="TEST",
        is_read=False,
    )

    create_notification(
        db_session,
        user_id=notification_test_user.id,
        title="Unread 2",
        message="Message 2",
        notification_type="TEST",
        is_read=False,
    )

    create_notification(
        db_session,
        user_id=notification_test_user.id,
        title="Already Read",
        message="Message 3",
        notification_type="TEST",
        is_read=True,
    )

    response = authenticated_request(
        "PATCH",
        "/api/notifications/read-all",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Notifications marked as read"
    assert data["updated_count"] == 2


def test_mark_all_notifications_when_none_unread(
    db_session,
    authenticated_request,
    notification_test_user,
):
    create_notification(
        db_session,
        user_id=notification_test_user.id,
        title="Already Read",
        message="Message",
        notification_type="TEST",
        is_read=True,
    )

    response = authenticated_request(
        "PATCH",
        "/api/notifications/read-all",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Notifications marked as read"
    assert data["updated_count"] == 0


def test_mark_all_does_not_update_other_users(
    db_session,
    authenticated_request,
    notification_test_user,
    notification_other_user,
):
    create_notification(
        db_session,
        user_id=notification_test_user.id,
        title="My Notification",
        message="My message",
        notification_type="TEST",
        is_read=False,
    )


    other_notification = create_notification(
        db_session,
        user_id=notification_other_user.id,
        title="Other Notification",
        message="Other message",
        notification_type="TEST",
        is_read=False,
    )

    response = authenticated_request(
        "PATCH",
        "/api/notifications/read-all",
    )

    assert response.status_code == 200

    db_session.refresh(other_notification)

    assert other_notification.is_read is False
    assert other_notification.read_at is None
