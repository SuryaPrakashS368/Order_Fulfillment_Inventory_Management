import os

import pytest
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.database import Base, get_db
from app.models.role import Role
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from app.models.user import User
from app.models.role import Role
from app.core.security import hash_password
import app.models
from app.main import app
from types import SimpleNamespace
from fastapi.routing import APIRoute


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError(
        "TEST_DATABASE_URL is required. "
        "Configure a separate PostgreSQL test database."
    )

if "order_fulfillment_test_db" not in TEST_DATABASE_URL.lower():
    raise RuntimeError(
        "Safety check failed. TEST_DATABASE_URL must point "
        "to order_fulfillment_test_db."
    )



test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
    join_transaction_mode="create_savepoint",
)


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database():
    """
    Create test tables and remove them after the test session.

    Use only a dedicated test database.
    For migration testing, prefer applying Alembic migrations.
    """
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture
def db_session(prepare_test_database):
    connection = test_engine.connect()
    outer_transaction = connection.begin()

    db = TestingSessionLocal(bind=connection)

    try:
        yield db
    finally:
        db.close()

        if outer_transaction.is_active:
            outer_transaction.rollback()

        connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture(autouse=True)
def create_test_roles(db_session):
    """Create required roles before each test."""

    role_names = [
        "Admin",
        "Warehouse Manager",
        "Fulfillment Agent",
        "Customer",
    ]

    for role_name in role_names:
        existing_role = (
            db_session.query(Role)
            .filter(Role.name == role_name)
            .first()
        )

        if existing_role is None:
            db_session.add(Role(name=role_name))

    db_session.flush()


@pytest.fixture
def authenticated_request(client, db_session):
    """Send requests while overriding the route permission dependency."""

    import re
    import app.main as main_module

    # Get the Admin role, creating it only if it does not exist.
    admin_role = (
        db_session.query(Role)
        .filter(Role.name == "Admin")
        .first()
    )

    if admin_role is None:
        admin_role = Role(name="Admin")
        db_session.add(admin_role)
        db_session.flush()

    # Get or create the test admin user, regardless of whether
    # the Admin role already existed.
    test_user = (
        db_session.query(User)
        .filter(User.email == "admin_test@example.com")
        .first()
    )

    if test_user is None:
        test_user = User(
            name="Test Admin",
            email="admin_test@example.com",
            password_hash=hash_password("test_password"),
            role_id=admin_role.id,
            is_active=True,
        )
        db_session.add(test_user)
        db_session.flush()

    def make_request(method, path, **kwargs):
        method = method.upper()
        route_path = path.split("?", 1)[0]

        # Use the specified user, or the default test admin.
        request_user = kwargs.pop("_current_user", test_user)

        # Reload the user and eagerly load the role relationship.
        request_user = (
            db_session.query(User)
            .options(joinedload(User.role))
            .filter(User.id == request_user.id)
            .first()
        )

        if request_user is None:
            raise AssertionError("The requested test user was not found.")

        route = None

        for name, candidate_router in vars(main_module).items():
            if not name.endswith("_router"):
                continue

            for item in getattr(candidate_router, "routes", []):
                if not isinstance(item, APIRoute):
                    continue

                if method not in item.methods:
                    continue

                # Match paths such as /api/users/4
                # against /api/users/{user_id}.
                route_pattern = re.sub(
                    r"\{[^{}]+\}",
                    r"[^/]+",
                    item.path,
                    )

                if re.fullmatch(route_pattern, route_path):
                    route = item
                    break

            if route is not None:
                break

        if route is None:
            raise AssertionError(
                f"Route not found: {method} {route_path}. "
                "Check the actual route prefix and HTTP method."
            )

        
        # Find permission_checker, including nested dependencies.
        def walk_dependencies(dependant):
            for dependency in dependant.dependencies:
                yield dependency
                yield from walk_dependencies(dependency)

        dependencies = list(
            walk_dependencies(route.dependant)
        )

        permission_dependency = next(
            (
                dependency.call
                for dependency in dependencies
                if getattr(
                    dependency.call,
                    "__name__",
                    "",
                ) == "permission_checker"
            ),
            None,
        )

        # if permission_dependency is None:
        #     raise AssertionError(
        #         f"Permission dependency not found for {route.path}"
        #     )

        # Find authentication dependencies.
        auth_names = {
            "get_current_user",
            "get_current_active_user",
            "get_authenticated_user",
        }

        auth_dependencies = {
            dependency.call
            for dependency in dependencies
            if getattr(
                dependency.call,
                "__name__",
                "",
            ) in auth_names
        }

        # Override authentication and permission checks.
        overridden_dependencies = set(auth_dependencies)

        if permission_dependency is not None:
            overridden_dependencies.add(
                permission_dependency
            )

        for dependency in overridden_dependencies:
            app.dependency_overrides[dependency] = (
                lambda user=request_user: user
            )

        try:
            response = client.request(method, path, **kwargs)

            if response.status_code >= 500:
                print("\n========== SERVER ERROR ==========")
                print("Request:", method, path)
                print("Status:", response.status_code)
                print("Response body:", response.text)
                print("==================================\n")

            return response

        finally:
            for dependency in overridden_dependencies:
                app.dependency_overrides.pop(
                    dependency,
                    None,
                )


    return make_request



@pytest.fixture(autouse=True)
def configure_test_permissions(db_session):
    """Create required permissions and assign them to Admin."""

    admin_role = (
        db_session.query(Role)
        .filter(Role.name == "Admin")
        .first()
    )

    if admin_role is None:
        admin_role = Role(name="Admin")
        db_session.add(admin_role)
        db_session.flush()

    permission_names = [
        "inventory:read",
        "inventory:adjust",
        "fulfillment:assign",
        "fulfillment:read",
        "order:assign",
        "order:read",
    ]

    for permission_name in permission_names:
        permission = (
            db_session.query(Permission)
            .filter(Permission.name == permission_name)
            .first()
        )

        if permission is None:
            permission = Permission(
                name=permission_name,
                description=f"Test permission: {permission_name}",
            )
            db_session.add(permission)
            db_session.flush()

        role_permission = (
            db_session.query(RolePermission)
            .filter(
                RolePermission.role_id == admin_role.id,
                RolePermission.permission_id == permission.id,
            )
            .first()
        )

        if role_permission is None:
            db_session.add(
                RolePermission(
                    role_id=admin_role.id,
                    permission_id=permission.id,
                )
            )

    db_session.flush()
