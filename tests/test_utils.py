from mini_framework.utils import prepare_kwargs


def test_prepare_kwargs_no_parameters() -> None:
    kwargs = {"a": 1, "b": 2}

    def callback() -> None:
        pass

    prepared_kwargs = prepare_kwargs(callback, kwargs)

    assert prepared_kwargs == {}


def test_prepare_kwargs_with_one_parameter() -> None:
    kwargs = {"a": 1, "b": 2}

    def callback(a: int) -> None:
        pass

    prepared_kwargs = prepare_kwargs(callback, kwargs)

    assert prepared_kwargs == {"a": 1}


def test_prepare_kwargs_with_unknown_parameter() -> None:
    kwargs = {"a": 1, "b": 2}

    def callback(c: int) -> None:
        pass

    prepared_kwargs = prepare_kwargs(callback, kwargs)

    assert prepared_kwargs == {}


def test_prepare_kwargs_with_kwargs_parameter() -> None:
    kwargs = {"a": 1, "b": 2}

    def callback(**kwargs) -> None:
        pass

    prepared_kwargs = prepare_kwargs(callback, kwargs)

    assert prepared_kwargs == kwargs
