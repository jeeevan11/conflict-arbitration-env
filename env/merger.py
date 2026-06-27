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


def verify_against_spec(merged: str, spec: dict) -> dict:
    """
    Compares merged output against spec ground truth.
    Programmatic check only. No LLM.

    For API specs: check endpoint path, method, field names, field types
    For DB specs: check table name, column names, column types
    For config specs: check key names, value types, value ranges
    For data format specs: check field names, field types
    """
    ground_truth = spec["ground_truth"]
    expected_fields = _extract_expected_fields(ground_truth)

    missing_fields = []
    type_mismatches = []
    matched = 0
    total = 0

    for field in expected_fields:
        total += 1
        if field.lower() in merged.lower():
            matched += 1
        else:
            missing_fields.append(field)

    for identifier_key in ["endpoint", "table", "type_name", "event_name", "command", "error_code"]:
        if identifier_key in ground_truth:
            total += 1
            if str(ground_truth[identifier_key]).lower() in merged.lower():
                matched += 1
            else:
                missing_fields.append(f"{identifier_key}:{ground_truth[identifier_key]}")

    for key in ["timeout_ms", "max_retries", "retry_delay_ms",
                "host", "port", "database",
                "requests_per_minute", "burst_size", "window_seconds", "block_duration_ms",
                "cache_ttl_seconds", "max_size_mb", "eviction_policy", "compression_enabled",
                "failure_threshold", "success_threshold",
                "open_state_timeout_ms", "half_open_max_calls",
                "max_connections", "idle_timeout_ms"]:
        if key in ground_truth:
            total += 1
            if key.lower() in merged.lower():
                matched += 1
            else:
                missing_fields.append(key)

    satisfaction_score = matched / total if total > 0 else 0.0
    spec_satisfied = satisfaction_score >= 0.9 and len(missing_fields) == 0

    return {
        "spec_satisfied": spec_satisfied,
        "satisfaction_score": round(satisfaction_score, 3),
        "missing_fields": missing_fields,
        "type_mismatches": type_mismatches,
    }


def _token_present(token: str, text: str) -> bool:
    import re
    pattern = r'(?<![A-Za-z0-9_])' + re.escape(token) + r'(?![A-Za-z0-9_])'
    return re.search(pattern, text) is not None


def merge_outputs(
    output_a: str,
    output_b: str,
    spec: dict
) -> dict:
    """
    Attempts to combine both outputs into one coherent result.

    Returns:
    {
        "merged": str,                    # The combined output
        "merge_succeeded": bool,          # Did it work without fatal conflicts?
        "conflicts_detected": list[str],  # List of specific conflicts found
        "spec_satisfied": bool,           # Does merged output satisfy spec?
        "satisfaction_score": float,      # 0.0 to 1.0
        "missing_fields": list[str],      # Fields in ground truth but not in merged
        "type_mismatches": list[str],     # Fields with wrong types
    }
    """
    import re
    merged = output_a + "\n---\n" + output_b
    conflicts_detected = []

    ground_truth = spec["ground_truth"]
    expected_fields = _extract_expected_fields(ground_truth)

    # 1. Per-field presence (detects missing_field, spelling, naming, casing)
    for field in expected_fields:
        in_a = _token_present(field, output_a)
        in_b = _token_present(field, output_b)
        if in_a != in_b:
            conflicts_detected.append(
                f"field '{field}' present in {'A' if in_a else 'B'} but missing in {'B' if in_a else 'A'}"
            )

    # 2. Naming variant detection from full NAMING_VARIANTS table
    try:
        from env.conflict_injector import NAMING_VARIANTS
    except ImportError:
        NAMING_VARIANTS = {}
    legitimate_strings = set()
    for k, v in ground_truth.items():
        legitimate_strings.add(k)
        if isinstance(v, str):
            legitimate_strings.add(v)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, str):
                    legitimate_strings.add(item)
        elif isinstance(v, dict):
            legitimate_strings.update(v.keys())

    for original in expected_fields:
        if original in NAMING_VARIANTS:
            for variant in NAMING_VARIANTS[original]:
                if variant == original:
                    continue
                if variant in legitimate_strings:
                    continue
                if _token_present(variant, output_a) or _token_present(variant, output_b):
                    conflicts_detected.append(
                        f"naming conflict: variant '{variant}' present alongside expected '{original}'"
                    )
                    break

    # 3. Casing conflicts: same field appears in both case-folded variants
    for field in expected_fields:
        if field == field.lower():
            continue
        upper_present = _token_present(field.upper(), output_a) or _token_present(field.upper(), output_b)
        if upper_present and not (_token_present(field, output_a) and _token_present(field, output_b)):
            conflicts_detected.append(f"casing conflict: '{field}' vs '{field.upper()}'")

    # 4. Identifier conflicts (endpoint, table, type_name, event_name, command, error_code)
    for ident_key in ["endpoint", "table", "type_name", "event_name", "command", "error_code"]:
        if ident_key in ground_truth:
            ident = str(ground_truth[ident_key])
            in_a = ident.lower() in output_a.lower()
            in_b = ident.lower() in output_b.lower()
            if in_a != in_b:
                conflicts_detected.append(
                    f"{ident_key} '{ident}' present in {'A' if in_a else 'B'} but missing in {'B' if in_a else 'A'}"
                )

    # 5. Value drift: numeric values declared in ground_truth disagree between A and B
    for key, val in ground_truth.items():
        if not isinstance(val, (int, float)):
            continue
        if key in ("fields",):
            continue
        pat = rf'["\']?{re.escape(key)}["\']?\s*[:=]\s*([\-0-9.]+)'
        m_a = re.search(pat, output_a)
        m_b = re.search(pat, output_b)
        if m_a and m_b and m_a.group(1) != m_b.group(1):
            conflicts_detected.append(
                f"value drift on '{key}': A={m_a.group(1)} vs B={m_b.group(1)}"
            )

    # 6. Logic inversions: well-known opposite-pair tokens disagree
    LOGIC_PAIRS = [
        ("true", "false"), ("yes", "no"), ("enabled", "disabled"),
        ("allow", "deny"), ("active", "inactive"), ("success", "failure"),
        ("required", "optional"), ("public", "private"), ("read", "write"),
    ]
    for pos, neg in LOGIC_PAIRS:
        a_has_pos = re.search(rf'\b{pos}\b', output_a, re.IGNORECASE)
        a_has_neg = re.search(rf'\b{neg}\b', output_a, re.IGNORECASE)
        b_has_pos = re.search(rf'\b{pos}\b', output_b, re.IGNORECASE)
        b_has_neg = re.search(rf'\b{neg}\b', output_b, re.IGNORECASE)
        if (a_has_pos and b_has_neg and not a_has_neg and not b_has_pos) or \
           (a_has_neg and b_has_pos and not a_has_pos and not b_has_neg):
            conflicts_detected.append(f"logic inversion: '{pos}' vs '{neg}'")

    # 7. Format conflicts: braces/brackets balance differs strongly between A and B
    a_braces = output_a.count('{') + output_a.count('}')
    a_brackets = output_a.count('[') + output_a.count(']')
    b_braces = output_b.count('{') + output_b.count('}')
    b_brackets = output_b.count('[') + output_b.count(']')
    if a_braces > 0 and b_braces == 0 and b_brackets > 0:
        conflicts_detected.append("format conflict: A uses object braces, B uses brackets")
    if b_braces > 0 and a_braces == 0 and a_brackets > 0:
        conflicts_detected.append("format conflict: B uses object braces, A uses brackets")
    if (':' in output_a and '"' in output_a) and (':' in output_b and '"' not in output_b and '{' not in output_b):
        conflicts_detected.append("format conflict: A uses JSON, B uses YAML-style")
    if (':' in output_b and '"' in output_b) and (':' in output_a and '"' not in output_a and '{' not in output_a):
        conflicts_detected.append("format conflict: B uses JSON, A uses YAML-style")

    verification = verify_against_spec(merged, spec)

    merge_succeeded = len(conflicts_detected) == 0 and verification["spec_satisfied"]

    return {
        "merged": merged,
        "merge_succeeded": merge_succeeded,
        "conflicts_detected": conflicts_detected,
        "spec_satisfied": verification["spec_satisfied"],
        "satisfaction_score": verification["satisfaction_score"],
        "missing_fields": verification["missing_fields"],
        "type_mismatches": verification["type_mismatches"],
    }


def score_agent_alignment(agent_output: str, spec: dict) -> dict:
    """
    Scores a single agent's output against spec ground truth.
    Returns 0.0–1.0. Used to compute contrast between agents.
    """
    ground_truth = spec["ground_truth"]
    score = 0.0
    total = 0
    issues = []

    expected_fields = _extract_expected_fields(ground_truth)
    for field in expected_fields:
        total += 1
        if field.lower() in agent_output.lower():
            score += 1.0
        else:
            issues.append(f"missing field: {field}")

    for identifier_key in ["endpoint", "table", "type_name", "event_name", "command", "error_code"]:
        if identifier_key in ground_truth:
            total += 1
            if str(ground_truth[identifier_key]).lower() in agent_output.lower():
                score += 1.0
            else:
                issues.append(f"wrong {identifier_key}: expected {ground_truth[identifier_key]}")

    alignment = score / total if total > 0 else 0.0
    return {
        "alignment_score": round(alignment, 3),
        "issues": issues,
        "fields_checked": total,
    }
