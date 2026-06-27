import random
import uuid

DOMAINS = {
    "api": {
        "description": "REST API endpoint design",
        "specs": [
            {
                "task": "Build a user authentication endpoint",
                "ground_truth": {
                    "endpoint": "POST /auth/login",
                    "request_fields": ["email", "password"],
                    "response_fields": ["userId", "token", "expiresAt"]
                }
            },
            {
                "task": "Build a product listing endpoint",
                "ground_truth": {
                    "endpoint": "GET /products",
                    "response_fields": ["productId", "name", "price", "inventory"]
                }
            },
            {
                "task": "Build a user profile endpoint",
                "ground_truth": {
                    "endpoint": "GET /users/{userId}",
                    "response_fields": ["userId", "name", "email", "createdAt"]
                }
            },
            {
                "task": "Build an order creation endpoint",
                "ground_truth": {
                    "endpoint": "POST /orders",
                    "request_fields": ["userId", "items", "shippingAddress", "paymentMethod"],
                    "response_fields": ["orderId", "status", "totalAmount", "estimatedDelivery"]
                }
            },
            {
                "task": "Build a password reset endpoint",
                "ground_truth": {
                    "endpoint": "POST /auth/reset-password",
                    "request_fields": ["email", "resetToken", "newPassword"],
                    "response_fields": ["success", "message"]
                }
            },
            {
                "task": "Build a refresh token endpoint",
                "ground_truth": {
                    "endpoint": "POST /auth/refresh",
                    "request_fields": ["refreshToken"],
                    "response_fields": ["accessToken", "refreshToken", "expiresIn"]
                }
            },
            {
                "task": "Build a search endpoint with pagination",
                "ground_truth": {
                    "endpoint": "GET /search",
                    "request_fields": ["query", "page", "pageSize", "sortBy"],
                    "response_fields": ["results", "totalCount", "page", "hasMore"]
                }
            },
            {
                "task": "Build a file upload endpoint",
                "ground_truth": {
                    "endpoint": "POST /files/upload",
                    "request_fields": ["fileName", "contentType", "fileSize", "fileData"],
                    "response_fields": ["fileId", "url", "uploadedAt"]
                }
            },
        ]
    },
    "database": {
        "description": "Database schema design",
        "specs": [
            {
                "task": "Design a users table for authentication",
                "ground_truth": {
                    "table": "users",
                    "fields": ["user_id", "email", "password_hash", "created_at"]
                }
            },
            {
                "task": "Design an orders table",
                "ground_truth": {
                    "table": "orders",
                    "fields": ["order_id", "user_id", "product_id", "quantity", "total_price"]
                }
            },
            {
                "task": "Design a products inventory table",
                "ground_truth": {
                    "table": "products",
                    "fields": ["product_id", "sku", "name", "price", "stock_count", "category_id"]
                }
            },
            {
                "task": "Design a sessions table for token tracking",
                "ground_truth": {
                    "table": "sessions",
                    "fields": ["session_id", "user_id", "token_hash", "issued_at", "expires_at", "ip_address"]
                }
            },
            {
                "task": "Design an audit log table",
                "ground_truth": {
                    "table": "audit_log",
                    "fields": ["log_id", "user_id", "action", "resource_type", "resource_id", "timestamp"]
                }
            },
            {
                "task": "Design a payments table",
                "ground_truth": {
                    "table": "payments",
                    "fields": ["payment_id", "order_id", "amount", "currency", "status", "processed_at"]
                }
            },
            {
                "task": "Design a notifications table",
                "ground_truth": {
                    "table": "notifications",
                    "fields": ["notification_id", "user_id", "type", "message", "read_at", "created_at"]
                }
            },
        ]
    },
    "config": {
        "description": "Service configuration",
        "specs": [
            {
                "task": "Configure a REST service with timeout and retry",
                "ground_truth": {
                    "fields": ["timeout_ms", "max_retries", "retry_delay_ms"],
                    "timeout_ms": 5000,
                    "max_retries": 3,
                    "retry_delay_ms": 1000
                }
            },
            {
                "task": "Configure a database connection pool",
                "ground_truth": {
                    "fields": ["host", "port", "database", "max_connections", "idle_timeout_ms"],
                    "host": "localhost",
                    "port": 5432
                }
            },
            {
                "task": "Configure a rate limiter",
                "ground_truth": {
                    "fields": ["requests_per_minute", "burst_size", "window_seconds", "block_duration_ms"]
                }
            },
            {
                "task": "Configure a cache layer",
                "ground_truth": {
                    "fields": ["cache_ttl_seconds", "max_size_mb", "eviction_policy", "compression_enabled"]
                }
            },
            {
                "task": "Configure a circuit breaker",
                "ground_truth": {
                    "fields": ["failure_threshold", "success_threshold", "open_state_timeout_ms", "half_open_max_calls"]
                }
            },
        ]
    },
    "data_format": {
        "description": "Data object definition",
        "specs": [
            {
                "task": "Define a user profile object",
                "ground_truth": {
                    "fields": ["userId", "name", "email", "createdAt"]
                }
            },
            {
                "task": "Define a shopping cart item object",
                "ground_truth": {
                    "fields": ["productId", "quantity", "unitPrice", "discountCode"]
                }
            },
            {
                "task": "Define an address object",
                "ground_truth": {
                    "fields": ["streetLine1", "streetLine2", "city", "state", "postalCode", "country"]
                }
            },
            {
                "task": "Define a payment method object",
                "ground_truth": {
                    "fields": ["methodId", "cardLast4", "expiryMonth", "expiryYear", "billingAddressId"]
                }
            },
            {
                "task": "Define an invoice line item object",
                "ground_truth": {
                    "fields": ["lineId", "description", "quantity", "unitPrice", "taxRate", "subtotal"]
                }
            },
            {
                "task": "Define a notification preference object",
                "ground_truth": {
                    "fields": ["userId", "channel", "frequency", "enabled", "lastSentAt"]
                }
            },
        ]
    },
    "graphql": {
        "description": "GraphQL schema design",
        "specs": [
            {
                "task": "Define a User GraphQL type",
                "ground_truth": {
                    "type_name": "User",
                    "fields": ["id", "email", "displayName", "avatarUrl", "createdAt"]
                }
            },
            {
                "task": "Define a Product GraphQL type",
                "ground_truth": {
                    "type_name": "Product",
                    "fields": ["id", "title", "description", "price", "inStock", "categoryId"]
                }
            },
            {
                "task": "Define a CreateOrder GraphQL mutation",
                "ground_truth": {
                    "type_name": "CreateOrder",
                    "fields": ["userId", "lineItems", "shippingAddressId", "paymentMethodId"]
                }
            },
            {
                "task": "Define a Comment GraphQL type",
                "ground_truth": {
                    "type_name": "Comment",
                    "fields": ["id", "authorId", "postId", "body", "createdAt", "editedAt"]
                }
            },
        ]
    },
    "event": {
        "description": "Event / message schema",
        "specs": [
            {
                "task": "Define a UserSignedUp event",
                "ground_truth": {
                    "event_name": "UserSignedUp",
                    "fields": ["userId", "email", "signupSource", "occurredAt"]
                }
            },
            {
                "task": "Define an OrderShipped event",
                "ground_truth": {
                    "event_name": "OrderShipped",
                    "fields": ["orderId", "trackingNumber", "carrier", "shippedAt", "estimatedArrival"]
                }
            },
            {
                "task": "Define a PaymentFailed event",
                "ground_truth": {
                    "event_name": "PaymentFailed",
                    "fields": ["paymentId", "orderId", "errorCode", "errorMessage", "failedAt"]
                }
            },
            {
                "task": "Define a CartAbandoned event",
                "ground_truth": {
                    "event_name": "CartAbandoned",
                    "fields": ["cartId", "userId", "totalValue", "itemCount", "abandonedAt"]
                }
            },
        ]
    },
    "cli": {
        "description": "Command-line interface specification",
        "specs": [
            {
                "task": "Specify a database backup CLI",
                "ground_truth": {
                    "command": "backup",
                    "fields": ["--source", "--destination", "--compress", "--verbose"]
                }
            },
            {
                "task": "Specify a deploy CLI",
                "ground_truth": {
                    "command": "deploy",
                    "fields": ["--environment", "--version", "--dry-run", "--rollback-on-failure"]
                }
            },
            {
                "task": "Specify a log query CLI",
                "ground_truth": {
                    "command": "logs",
                    "fields": ["--service", "--since", "--until", "--level", "--follow"]
                }
            },
        ]
    },
    "error_response": {
        "description": "Error response schema",
        "specs": [
            {
                "task": "Define a validation error response",
                "ground_truth": {
                    "error_code": "VALIDATION_ERROR",
                    "fields": ["errorCode", "message", "fieldErrors", "requestId", "timestamp"]
                }
            },
            {
                "task": "Define an authentication error response",
                "ground_truth": {
                    "error_code": "AUTH_FAILED",
                    "fields": ["errorCode", "message", "reason", "retryAfter", "timestamp"]
                }
            },
            {
                "task": "Define a rate-limit error response",
                "ground_truth": {
                    "error_code": "RATE_LIMITED",
                    "fields": ["errorCode", "message", "limit", "remaining", "resetAt"]
                }
            },
        ]
    },
}


def _flatten_templates():
    """Return a flat list of (domain, template) pairs for template-uniform sampling."""
    flat = []
    for domain_name, domain_data in DOMAINS.items():
        for template in domain_data["specs"]:
            flat.append((domain_name, template))
    return flat


_FLAT_TEMPLATES = _flatten_templates()


def generate_spec(domain: str = None) -> dict:
    """
    Returns:
    {
        "task_description": str,   # What agents A and B receive
        "ground_truth": dict,      # What correct output looks like (hidden from agents)
        "domain": str,
        "spec_id": str             # Unique ID for logging
    }

    Sampling: when domain is None, uses TEMPLATE-UNIFORM sampling across the
    flat list of (domain, template) pairs — every template has equal probability,
    not every domain. This avoids over-representing single-template domains.
    """
    if domain is None:
        chosen_domain, spec_template = random.choice(_FLAT_TEMPLATES)
    else:
        chosen_domain = domain
        spec_template = random.choice(DOMAINS[domain]["specs"])
    return {
        "task_description": spec_template["task"],
        "ground_truth": spec_template["ground_truth"],
        "domain": chosen_domain,
        "spec_id": str(uuid.uuid4())
    }


def list_domains() -> list:
    return list(DOMAINS.keys())


def template_count() -> dict:
    return {d: len(DOMAINS[d]["specs"]) for d in DOMAINS}
