ROLE_PERMISSIONS = {
    "Admin": [
        # User management
        "user:create",
        "user:read",
        "user:update",
        "user:delete",

        # Product management
        "product:create",
        "product:read",
        "product:update",
        "product:delete",

        # Warehouse management
        "warehouse:create",
        "warehouse:read",
        "warehouse:update",
        "warehouse:delete",

        # Inventory management
        "inventory:create",
        "inventory:read",
        "inventory:update",
        "inventory:adjust",
        "inventory:reserve",
        "inventory:release",

        # Order management
        "order:create",
        "order:read",
        "order:update",
        "order:cancel",

        # Fulfillment management
        "fulfillment:create",
        "fulfillment:read",
        "fulfillment:update",
        "fulfillment:process",

        # Reports, notifications and audit
        "report:read",
        "notification:read",
        "audit:read",
    ],

    "Warehouse Manager": [
        "product:read",
        "warehouse:read",
        "warehouse:update",
        "inventory:create",
        "inventory:read",
        "inventory:update",
        "inventory:adjust",
        "inventory:reserve",
        "inventory:release",
        "order:read",
        "fulfillment:read",
        "fulfillment:update",
        "report:read",
        "notification:read",
    ],

    "Fulfillment Agent": [
        "product:read",
        "warehouse:read",
        "inventory:read",
        "inventory:reserve",
        "order:read",
        "fulfillment:read",
        "fulfillment:update",
        "fulfillment:process",
        "notification:read",
    ],

    "Customer": [
        "product:read",
        "warehouse:read",
        "order:create",
        "order:read",
        "order:cancel",
        "notification:read",
    ],
}
