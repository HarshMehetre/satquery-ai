from app.config.settings import settings


def test_default_planner_provider():
    assert settings.planner_provider == "gemini"


def test_gemini_configuration():
    assert settings.gemini_model == "gemini-3.5-flash-lite"