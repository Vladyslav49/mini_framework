import pytest

from mini_framework import Application


def test_workflow_data(app: Application) -> None:
    app["some"] = 1

    assert app["some"] == 1

    del app["some"]

    with pytest.raises(KeyError):
        app["some"]
