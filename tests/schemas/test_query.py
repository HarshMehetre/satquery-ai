import pytest
from pydantic import ValidationError

from app.schemas.query import NaturalLanguageQuery


def test_natural_language_query_accepts_query() -> None:
    request = NaturalLanguageQuery(
        query="Find vegetation loss near major roads."
    )

    assert request.query == "Find vegetation loss near major roads."


def test_natural_language_query_rejects_empty_query() -> None:
    with pytest.raises(ValidationError):
        NaturalLanguageQuery(query="")