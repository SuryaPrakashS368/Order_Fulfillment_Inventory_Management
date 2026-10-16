class Roles:
    ADMIN = "Admin"
    WAREHOUSE_MANAGER = "Warehouse Manager"
    FULFILLMENT_AGENT = "Fulfillment Agent"
    CUSTOMER = "Customer"


# Valid normal order transitions.
#
# Cancellation is handled by Module 11.
# Returns are handled by Module 13.
ORDER_TRANSITIONS = {
    "PENDING": ["CONFIRMED"],
    "CONFIRMED": ["PROCESSING"],
    "PROCESSING": ["PACKED"],
    "PACKED": ["SHIPPED"],
    "SHIPPED": ["DELIVERED"],
    "DELIVERED": [],
    "CANCELLED": [],
    "FAILED": [],
    "RETURNED": [],
}


# Which roles can perform which transitions.
ROLE_STATUS_TRANSITIONS = {
    Roles.ADMIN: {
        ("PENDING", "CONFIRMED"),
        ("CONFIRMED", "PROCESSING"),
        ("PROCESSING", "PACKED"),
        ("PACKED", "SHIPPED"),
        ("SHIPPED", "DELIVERED"),
    },

    Roles.WAREHOUSE_MANAGER: {
        ("PENDING", "CONFIRMED"),
        ("CONFIRMED", "PROCESSING"),
        ("PROCESSING", "PACKED"),
        ("PACKED", "SHIPPED"),
        ("SHIPPED", "DELIVERED"),
    },

    Roles.FULFILLMENT_AGENT: {
        ("PROCESSING", "PACKED"),
        ("PACKED", "SHIPPED"),
    },

    Roles.CUSTOMER: set(),
}

class Permissions:

    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DEACTIVATE = "user:deactivate"

    PRODUCT_CREATE = "product:create"
    PRODUCT_READ = "product:read"
    PRODUCT_UPDATE = "product:update"
    PRODUCT_DELETE = "product:delete"

    WAREHOUSE_CREATE = "warehouse:create"
    WAREHOUSE_READ = "warehouse:read"
    WAREHOUSE_UPDATE = "warehouse:update"
    WAREHOUSE_ASSIGN_USER = "warehouse:assign_user"

    INVENTORY_READ = "inventory:read"
    INVENTORY_ADJUST = "inventory:adjust"
    INVENTORY_TRANSFER = "inventory:transfer"
    INVENTORY_RESERVE = "inventory:reserve"

    ORDER_CREATE = "order:create"
    ORDER_READ = "order:read"
    ORDER_UPDATE = "order:update"
    ORDER_CANCEL = "order:cancel"
    ORDER_ASSIGN = "order:assign"

    FULFILLMENT_PROCESS = "fulfillment:process"

    RETURN_CREATE = "return:create"
    RETURN_APPROVE = "return:approve"
    RETURN_RECEIVE = "return:receive"

    NOTIFICATION_READ = "notification:read"

    AUDIT_READ = "audit:read"


ALL_PERMISSIONS = [
    Permissions.USER_CREATE,
    Permissions.USER_READ,
    Permissions.USER_UPDATE,
    Permissions.USER_DEACTIVATE,

    Permissions.PRODUCT_CREATE,
    Permissions.PRODUCT_READ,
    Permissions.PRODUCT_UPDATE,
    Permissions.PRODUCT_DELETE,

    Permissions.WAREHOUSE_CREATE,
    Permissions.WAREHOUSE_READ,
    Permissions.WAREHOUSE_UPDATE,
    Permissions.WAREHOUSE_ASSIGN_USER,

    Permissions.INVENTORY_READ,
    Permissions.INVENTORY_ADJUST,
    Permissions.INVENTORY_TRANSFER,
    Permissions.INVENTORY_RESERVE,

    Permissions.ORDER_CREATE,
    Permissions.ORDER_READ,
    Permissions.ORDER_UPDATE,
    Permissions.ORDER_CANCEL,
    Permissions.ORDER_ASSIGN,

    Permissions.FULFILLMENT_PROCESS,

    Permissions.RETURN_CREATE,
    Permissions.RETURN_APPROVE,
    Permissions.RETURN_RECEIVE,

    Permissions.NOTIFICATION_READ,

    Permissions.AUDIT_READ,
]