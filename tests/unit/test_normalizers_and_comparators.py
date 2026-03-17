from trustagents.comparators.core import compare_claims
from trustagents.normalizers.core import normalize_date, normalize_id


def test_normalizer_id_punctuation_cleanup():
    assert normalize_id("ID-12 34") == "id1234"


def test_date_format_equivalent_match():
    assert normalize_date("01/05/1990") == "1990-01-05"


def test_transposed_numeric_id_flagged_near_match():
    results = compare_claims(
        {"fullName": "Alex Carter", "dateOfBirth": "1990-01-05", "identifier": "12345"},
        {"fullName": "Alex Carter", "dateOfBirth": "1990-01-05", "identifier": "12354"},
    )
    id_result = [r for r in results if r.field == "identifier"][0]
    assert id_result.result == "NEAR_MATCH"
