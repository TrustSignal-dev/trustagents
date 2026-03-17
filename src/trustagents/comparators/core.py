from __future__ import annotations

from trustagents.oracle.models import ComparisonResult
from trustagents.normalizers.core import normalize_date, normalize_id, normalize_name


def _one_char_typo(a: str, b: str) -> bool:
    if abs(len(a) - len(b)) > 1:
        return False
    mismatches = sum(1 for x, y in zip(a, b) if x != y) + abs(len(a) - len(b))
    return mismatches == 1


def _swapped_name(a: str, b: str) -> bool:
    pa = a.split()
    pb = b.split()
    return len(pa) >= 2 and len(pb) >= 2 and pa[0] == pb[-1] and pa[-1] == pb[0]


def _transposed_digits(a: str, b: str) -> bool:
    if len(a) != len(b):
        return False
    diffs = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    return len(diffs) == 2 and a[diffs[0]] == b[diffs[1]] and a[diffs[1]] == b[diffs[0]]


def compare_claims(claims: dict, source: dict) -> list[ComparisonResult]:
    results: list[ComparisonResult] = []

    c_name = claims.get("fullName")
    s_name = source.get("fullName")
    c_norm = normalize_name(c_name)
    s_norm = normalize_name(s_name)
    name_result = "MISMATCH"
    explanation = "Name mismatch"
    severity = "high"
    if c_name == s_name:
        name_result, explanation, severity = "EXACT_MATCH", "Exact name match", "info"
    elif c_norm and s_norm and c_norm == s_norm:
        name_result, explanation, severity = "NORMALIZED_MATCH", "Whitespace/case normalized match", "info"
    elif c_norm and s_norm and _one_char_typo(c_norm, s_norm):
        name_result, explanation, severity = "NEAR_MATCH", "One-character typo detected", "medium"
    elif c_norm and s_norm and _swapped_name(c_norm, s_norm):
        name_result, explanation, severity = "AMBIGUOUS", "Swapped first/last names", "medium"
    elif c_norm and s_norm and (c_norm.replace(".", "")[:1] == s_norm[:1]):
        name_result, explanation, severity = "AMBIGUOUS", "Initials vs full-name pattern", "medium"

    results.append(
        ComparisonResult(
            field="fullName",
            original_value=c_name,
            normalized_value=c_norm,
            source_value=s_name,
            normalized_source_value=s_norm,
            result=name_result,
            severity=severity,
            explanation=explanation,
        )
    )

    c_date = claims.get("dateOfBirth")
    s_date = source.get("dateOfBirth")
    cd_norm = normalize_date(c_date)
    sd_norm = normalize_date(s_date)
    date_result = "MISMATCH"
    if cd_norm == sd_norm:
        date_result = "MATCH"
        exp = "Equivalent date format matched"
        sev = "info"
    else:
        exp = "Date drift or timezone-sensitive mismatch"
        sev = "medium"
    results.append(
        ComparisonResult(
            field="dateOfBirth",
            original_value=c_date,
            normalized_value=cd_norm,
            source_value=s_date,
            normalized_source_value=sd_norm,
            result=date_result,
            severity=sev,
            explanation=exp,
        )
    )

    c_id, s_id = claims.get("identifier"), source.get("identifier")
    ci_norm, si_norm = normalize_id(c_id), normalize_id(s_id)
    id_result = "MISMATCH"
    exp = "Identifier mismatch"
    sev = "high"
    if ci_norm == si_norm:
        id_result, exp, sev = "MATCH", "Identifier normalized match", "info"
    elif ci_norm and si_norm and _transposed_digits(ci_norm, si_norm):
        id_result, exp, sev = "NEAR_MATCH", "Transposed digits detected", "medium"
    results.append(
        ComparisonResult(
            field="identifier",
            original_value=c_id,
            normalized_value=ci_norm,
            source_value=s_id,
            normalized_source_value=si_norm,
            result=id_result,
            severity=sev,
            explanation=exp,
        )
    )

    c_hash, s_hash = claims.get("artifactHash"), source.get("artifactHash")
    h_result = "MATCH" if c_hash and s_hash and c_hash == s_hash else "MISMATCH"
    results.append(
        ComparisonResult(
            field="artifactHash",
            original_value=c_hash,
            normalized_value=c_hash,
            source_value=s_hash,
            normalized_source_value=s_hash,
            result=h_result,
            severity="high" if h_result == "MISMATCH" else "info",
            explanation="Metadata hash mismatch" if h_result == "MISMATCH" else "Metadata hash match",
        )
    )

    return results
