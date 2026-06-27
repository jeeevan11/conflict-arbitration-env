import random

CONFLICT_TYPES = {
    "naming":        "same concept, different names",
    "format":        "same data, different structure",
    "assumption":    "different beliefs about shared interface",
    "logic":         "same operation, opposite behavior",
    "missing_field": "one agent omits a required field",
    "spelling":      "typo in a field name",
    "casing":        "same name, different casing convention",
    "value_drift":   "same key, materially different value",
}

NAMING_VARIANTS = {
    "userId":             ["user_id", "uid", "userID", "user_identifier", "UserId"],
    "user_id":            ["userId", "uid", "userID", "userIdentifier", "USER_ID"],
    "email":              ["emailAddress", "email_addr", "user_email", "mailAddress"],
    "createdAt":          ["created_at", "creation_time", "dateCreated", "createdOn", "CreatedAt"],
    "created_at":         ["createdAt", "creation_time", "dateCreated", "created_on"],
    "updatedAt":          ["updated_at", "modified_at", "lastModified", "lastUpdated"],
    "token":              ["auth_token", "access_token", "jwt", "session_token", "bearerToken"],
    "accessToken":        ["access_token", "auth_token", "jwt", "bearerToken"],
    "refreshToken":       ["refresh_token", "renewal_token", "rotateToken"],
    "productId":          ["product_id", "pid", "item_id", "productID", "ProductId"],
    "product_id":         ["productId", "pid", "item_id", "ProductId"],
    "orderId":            ["order_id", "oid", "orderID", "order_identifier", "OrderId"],
    "order_id":           ["orderId", "oid", "orderID", "order_identifier"],
    "sessionId":          ["session_id", "sid", "sessionID", "SessionId"],
    "session_id":         ["sessionId", "sid", "sessionID"],
    "paymentId":          ["payment_id", "pmt_id", "paymentID"],
    "payment_id":         ["paymentId", "pmt_id", "paymentID"],
    "fileId":             ["file_id", "fid", "fileID", "FileId"],
    "fileName":           ["file_name", "filename", "fname", "FileName"],
    "expiresAt":          ["expires_at", "expiryDate", "expirationTime", "expiresOn"],
    "expiresIn":          ["expires_in", "expiryDuration", "ttlSeconds"],
    "totalAmount":        ["total_amount", "totalCost", "totalPrice", "amount_total"],
    "totalPrice":         ["total_price", "totalAmount", "totalCost"],
    "total_price":        ["totalPrice", "total_amount", "totalCost"],
    "shippingAddress":    ["shipping_address", "shipAddr", "deliveryAddress"],
    "paymentMethod":      ["payment_method", "pmtMethod", "paymentType"],
    "password":           ["passwd", "pwd", "user_password", "Password"],
    "password_hash":      ["passwordHash", "pwd_hash", "hashedPassword"],
    "ipAddress":          ["ip_address", "ipAddr", "clientIp", "remote_ip"],
    "ip_address":         ["ipAddress", "ipAddr", "clientIp"],
    "trackingNumber":     ["tracking_number", "trackingId", "shipmentId"],
    "errorCode":          ["error_code", "errCode", "code", "ErrorCode"],
    "errorMessage":       ["error_message", "errMsg", "message", "ErrorMessage"],
    "errorMessage":       ["error_message", "errMsg", "message"],
    "requestId":          ["request_id", "reqId", "correlationId", "RequestId"],
    "timestamp":          ["ts", "time", "occurredAt", "eventTime"],
    "occurredAt":         ["occurred_at", "timestamp", "eventTime"],
    "name":               ["title", "displayName", "label"],
    "displayName":        ["display_name", "name", "title"],
    "title":              ["name", "label", "heading"],
    "description":        ["desc", "details", "summary"],
    "price":              ["unit_price", "cost", "amount"],
    "unitPrice":          ["unit_price", "price", "rate"],
    "quantity":           ["qty", "count", "amount"],
    "inventory":          ["stock", "stock_count", "qty_available"],
    "stock_count":        ["stockCount", "inventory", "qty_available"],
    "category_id":        ["categoryId", "cat_id", "category"],
    "categoryId":         ["category_id", "cat_id", "categoryID"],
    "sku":                ["SKU", "stock_keeping_unit", "productCode"],
    "host":               ["hostname", "server", "address"],
    "port":               ["port_number", "tcp_port"],
    "database":           ["db", "db_name", "schema"],
    "max_retries":        ["maxRetries", "retry_count", "max_attempts"],
    "timeout_ms":         ["timeoutMs", "timeout", "request_timeout"],
    "retry_delay_ms":     ["retryDelayMs", "retry_delay", "backoff_ms"],
    "carrier":            ["shippingCarrier", "courier", "deliveryProvider"],
    "shippedAt":          ["shipped_at", "shipDate", "dispatchedAt"],
    "estimatedArrival":   ["estimated_arrival", "etaDate", "expectedDelivery"],
    "estimatedDelivery":  ["estimated_delivery", "etaDate", "expectedDelivery"],
    "totalValue":         ["total_value", "totalAmount", "value"],
    "itemCount":          ["item_count", "count", "totalItems"],
    "channel":            ["medium", "deliveryChannel", "notificationChannel"],
    "frequency":          ["cadence", "interval", "rate"],
    "enabled":            ["isEnabled", "active", "is_active"],
    "lineItems":          ["line_items", "items", "orderLines"],
    "items":              ["lineItems", "products", "orderItems"],
    "shippingAddressId":  ["shipping_address_id", "shipAddrId", "deliveryAddressId"],
    "paymentMethodId":    ["payment_method_id", "pmtMethodId"],
    "billingAddressId":   ["billing_address_id", "billAddrId"],
    "cardLast4":          ["card_last4", "lastFour", "cardSuffix"],
    "expiryMonth":        ["expiry_month", "expMonth", "expirationMonth"],
    "expiryYear":         ["expiry_year", "expYear", "expirationYear"],
    "lineId":             ["line_id", "itemId", "rowId"],
    "taxRate":            ["tax_rate", "vatRate", "taxPercent"],
    "subtotal":           ["sub_total", "lineTotal", "amount"],
    "lastSentAt":         ["last_sent_at", "sentAt", "lastDelivery"],
    "issued_at":          ["issuedAt", "issue_time", "createdAt"],
    "expires_at":         ["expiresAt", "expiry", "ttl"],
    "log_id":             ["logId", "id", "entry_id"],
    "action":             ["operation", "verb", "actionType"],
    "resource_type":      ["resourceType", "entity_type", "resType"],
    "resource_id":        ["resourceId", "entity_id", "objectId"],
    "amount":             ["value", "sum", "total"],
    "currency":           ["currencyCode", "ccy", "currency_code"],
    "status":             ["state", "currentStatus", "phase"],
    "processed_at":       ["processedAt", "completedAt", "finalizedAt"],
    "type":               ["kind", "category", "variant"],
    "message":            ["msg", "text", "body"],
    "read_at":            ["readAt", "viewed_at", "seenAt"],
    "avatarUrl":          ["avatar_url", "profileImage", "photoUrl"],
    "authorId":           ["author_id", "createdBy", "userId"],
    "postId":             ["post_id", "parent_id", "threadId"],
    "body":               ["content", "text", "message"],
    "editedAt":           ["edited_at", "modifiedAt", "updatedAt"],
    "signupSource":       ["signup_source", "source", "registrationSource"],
    "trackingNumber":     ["tracking_number", "trackingId", "shipmentNo"],
    "cartId":             ["cart_id", "shoppingCartId", "basketId"],
    "abandonedAt":        ["abandoned_at", "leftAt", "exitedAt"],
    "fieldErrors":        ["field_errors", "validationErrors", "errors"],
    "retryAfter":         ["retry_after", "retryDelaySec", "cooldown"],
    "limit":              ["max", "rateLimit", "ceiling"],
    "remaining":          ["left", "available", "remainingQuota"],
    "resetAt":            ["reset_at", "resetTime", "windowResetAt"],
}

KEYBOARD_NEIGHBORS = {
    'a': 'sqwz', 'b': 'vghn', 'c': 'xdfv', 'd': 'srfce',
    'e': 'wrsdf', 'f': 'drtgc', 'g': 'ftyhb', 'h': 'gyujn',
    'i': 'ujklo', 'j': 'huikm', 'k': 'jilo', 'l': 'kop',
    'm': 'njk',  'n': 'bhjm',  'o': 'iklp', 'p': 'ol',
    'q': 'wa',   'r': 'edft',  's': 'awedxz', 't': 'rfgy',
    'u': 'yhij', 'v': 'cfgb',  'w': 'qase', 'x': 'zsdc',
    'y': 'tghu', 'z': 'asx',
}


def _extract_expected_fields(ground_truth: dict) -> list:
    """Pull all expected field names from ground truth regardless of domain."""
    fields = []
    for key in ["request_fields", "response_fields", "fields"]:
        val = ground_truth.get(key, [])
        if isinstance(val, dict):
            fields.extend(val.keys())
        elif isinstance(val, list):
            fields.extend(val)
    return fields


def _make_typo(word: str, obviousness: str) -> str:
    if len(word) < 3:
        return word

    if obviousness == "high":
        idx = random.randint(1, len(word) - 2)
        return word[:idx] + word[idx+1:]

    elif obviousness == "medium":
        idx = random.randint(1, len(word) - 2)
        chars = list(word)
        chars[idx], chars[idx+1] = chars[idx+1], chars[idx]
        return ''.join(chars)

    else:
        lower = word.lower()
        candidates = [
            i for i, ch in enumerate(lower)
            if ch in KEYBOARD_NEIGHBORS and i > 0
        ]
        if not candidates:
            return word
        idx = random.choice(candidates)
        replacement = random.choice(KEYBOARD_NEIGHBORS[lower[idx]])
        if word[idx].isupper():
            replacement = replacement.upper()
        return word[:idx] + replacement + word[idx+1:]


def inject_spelling_conflict(output: str, ground_truth: dict, obviousness: str):
    candidates = _extract_expected_fields(ground_truth)
    candidates = [f for f in candidates if len(f) >= 4]
    if not candidates:
        return output, "no suitable field found"
    target = random.choice(candidates)
    corrupted = _make_typo(target, obviousness)
    if corrupted == target:
        return output, "typo no-op"
    corrupted_output = output.replace(target, corrupted)
    return corrupted_output, f"Agent used '{corrupted}' instead of '{target}'"


def _inject_naming_conflict(output: str, ground_truth: dict, obviousness: str):
    fields = _extract_expected_fields(ground_truth)
    candidates = [f for f in fields if f in NAMING_VARIANTS]
    if not candidates:
        candidates = [f for f in fields if len(f) >= 3]
        if not candidates:
            return output, "no suitable field found"
        target = random.choice(candidates)
        if "_" in target:
            replacement = ''.join(p.capitalize() if i else p for i, p in enumerate(target.split('_')))
        else:
            import re
            replacement = re.sub(r'(?<!^)([A-Z])', r'_\1', target).lower()
        if replacement == target:
            return output, "naming no-op"
    else:
        target = random.choice(candidates)
        replacement = random.choice(NAMING_VARIANTS[target])
    corrupted = output.replace(target, replacement)
    return corrupted, f"Agent used '{replacement}' instead of '{target}'"


def _inject_casing_conflict(output: str, ground_truth: dict, obviousness: str):
    """Same name, different casing. e.g. userId vs UserId vs USERID."""
    fields = _extract_expected_fields(ground_truth)
    candidates = [f for f in fields if any(c.isalpha() for c in f) and len(f) >= 3]
    if not candidates:
        return output, "no suitable field found"
    target = random.choice(candidates)
    transforms = []
    if target != target.upper():
        transforms.append(target.upper())
    if target != target.lower():
        transforms.append(target.lower())
    cap = target[0].upper() + target[1:] if target[0].islower() else target[0].lower() + target[1:]
    if cap != target:
        transforms.append(cap)
    if not transforms:
        return output, "casing no-op"
    replacement = random.choice(transforms)
    corrupted = output.replace(target, replacement)
    return corrupted, f"Agent used '{replacement}' instead of '{target}'"


def _inject_format_conflict(output: str, ground_truth: dict, obviousness: str):
    options = []
    if "{" in output and "}" in output:
        options.append(("array", lambda s: s.replace("{", "[").replace("}", "]"),
                        "Agent used array format instead of object format"))
    if '": "' in output:
        options.append(("yaml-ish", lambda s: s.replace('": "', ': ').replace('",', ',').replace('"', ''),
                        "Agent used YAML-style instead of JSON"))
    if not options:
        return output + "\n# format altered", "Agent altered output format"
    _, fn, desc = random.choice(options)
    return fn(output), desc


def _inject_assumption_conflict(output: str, ground_truth: dict, obviousness: str):
    """
    Real assumption drift: change one declared identifier to a plausible alternative
    without leaving a giveaway comment.
    """
    if "endpoint" in ground_truth:
        original = ground_truth["endpoint"]
        method, _, path = original.partition(" ")
        alternatives = []
        if method == "POST" and "/login" in path:
            alternatives.append("POST /sessions")
        if method == "POST" and "/auth/refresh" in path:
            alternatives.append("PUT /auth/token")
        if method == "GET" and path.startswith("/users/"):
            alternatives.append(path.replace("{userId}", "{id}"))
        if method == "GET" and path == "/products":
            alternatives.append("GET /catalog/items")
        if not alternatives:
            new_method = "PUT" if method == "POST" else "POST" if method == "PUT" else method
            alternatives.append(f"{new_method} {path}")
        new_endpoint = random.choice(alternatives)
        if new_endpoint in output:
            return output, "assumption no-op"
        return output.replace(original, new_endpoint), f"Agent assumed '{new_endpoint}' instead of '{original}'"

    if "table" in ground_truth:
        original = ground_truth["table"]
        alt = original + "_v2" if not original.endswith("_v2") else original.rstrip("_v2")
        return output.replace(f'"{original}"', f'"{alt}"').replace(f"'{original}'", f"'{alt}'"), \
            f"Agent assumed table '{alt}' instead of '{original}'"

    if "type_name" in ground_truth:
        original = ground_truth["type_name"]
        alt = original + "Input" if not original.endswith("Input") else original.replace("Input", "")
        return output.replace(original, alt), f"Agent assumed type '{alt}' instead of '{original}'"

    if "event_name" in ground_truth:
        original = ground_truth["event_name"]
        parts = ''.join([' ' + c.lower() if c.isupper() else c for c in original]).strip().split()
        if len(parts) >= 2:
            alt = parts[1].capitalize() + parts[0].capitalize() + ''.join(p.capitalize() for p in parts[2:])
        else:
            alt = original + "V2"
        return output.replace(original, alt), f"Agent assumed event '{alt}' instead of '{original}'"

    if "command" in ground_truth:
        original = ground_truth["command"]
        alts = {"backup": "snapshot", "deploy": "release", "logs": "tail"}
        alt = alts.get(original, original + "-cli")
        return output.replace(original, alt), f"Agent assumed command '{alt}' instead of '{original}'"

    return output, "no assumption target available"


def _inject_logic_conflict(output: str, ground_truth: dict, obviousness: str):
    replacements = [
        ("true", "false"), ("True", "False"),
        ("yes", "no"), ("YES", "NO"),
        ("enabled", "disabled"),
        ("allow", "deny"), ("ALLOW", "DENY"),
        ("active", "inactive"),
        ("success", "failure"),
        ("required", "optional"),
        ("public", "private"),
        ("read", "write"),
    ]
    random.shuffle(replacements)
    for src, dst in replacements:
        if src in output:
            return output.replace(src, dst, 1), f"Agent inverted '{src}' to '{dst}'"
    return output, "no logic target found"


def _inject_value_drift(output: str, ground_truth: dict, obviousness: str):
    """Same key, different value — e.g. timeout 5000 → 30000."""
    import re
    numeric_keys = []
    for k, v in ground_truth.items():
        if isinstance(v, (int, float)) and k not in ("fields",):
            numeric_keys.append((k, v))
    if not numeric_keys:
        return output, "no numeric value to drift"
    key, val = random.choice(numeric_keys)
    if isinstance(val, int):
        new_val = val * (2 if val > 0 else 0) + (1 if val == 0 else 0)
    else:
        new_val = val * 2.5
    pattern = rf'(["\']?{re.escape(key)}["\']?\s*[:=]\s*){val}'
    if re.search(pattern, output):
        new_output = re.sub(pattern, rf'\g<1>{new_val}', output, count=1)
        return new_output, f"Agent set '{key}' to {new_val} instead of {val}"
    return output, f"value for '{key}' not present in output"


def _inject_missing_field_conflict(output: str, ground_truth: dict, obviousness: str):
    fields = _extract_expected_fields(ground_truth)
    candidates = [f for f in fields if f in output]
    if not candidates:
        return output, "no field present to remove"
    target = random.choice(candidates)
    corrupted = output.replace(target, "")
    return corrupted, f"Agent omitted required field '{target}'"


_INJECTORS = {
    "naming": _inject_naming_conflict,
    "format": _inject_format_conflict,
    "assumption": _inject_assumption_conflict,
    "logic": _inject_logic_conflict,
    "missing_field": _inject_missing_field_conflict,
    "spelling": inject_spelling_conflict,
    "casing": _inject_casing_conflict,
    "value_drift": _inject_value_drift,
}


def inject_conflict(spec, output_a, output_b, conflict_type, wrong_agent, obviousness):
    target_output = output_b if wrong_agent == 1 else output_a
    ground_truth = spec["ground_truth"]

    injector = _INJECTORS.get(conflict_type)
    if injector is None:
        return output_a, output_b, None
    corrupted, description = injector(target_output, ground_truth, obviousness)

    if corrupted == target_output:
        return output_a, output_b, None

    if wrong_agent == 1:
        return output_a, corrupted, {
            "conflict_type": conflict_type,
            "wrong_agent": 1,
            "description": description
        }
    else:
        return corrupted, output_b, {
            "conflict_type": conflict_type,
            "wrong_agent": 0,
            "description": description
        }


def get_random_conflict_type(curriculum_phase: int) -> str:
    """Phase 1: naming only. Phase 2: naming+format+spelling. Phase 3+: all."""
    if curriculum_phase == 1:
        return "naming"
    elif curriculum_phase == 2:
        return random.choice(["naming", "format", "spelling"])
    else:
        return random.choice(list(CONFLICT_TYPES.keys()))


inject = inject_conflict
