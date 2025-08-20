import pytest

from pathlib import Path


@pytest.fixture(scope="session")
def player_html():
    folder = Path(__file__).parent / "data"
    return {
        file.stem: file.read_text(encoding="utf-8")
        for file in folder.glob("*.html")
    }