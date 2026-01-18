import pytest


@pytest.fixture(autouse=True, scope="session")
def cleanup_qzemoji():
    yield
    import qzemoji

    qzemoji.close()
