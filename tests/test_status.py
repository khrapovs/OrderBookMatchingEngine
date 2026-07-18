from order_matching.enums import Status


def test_status() -> None:
    assert Status.CANCEL > Status.OPEN
    assert str(Status.CANCEL) == Status.CANCEL.name
