from order_matching.enums import Execution, Side, Status


def test_side() -> None:
    assert Side.SELL > Side.BUY
    assert str(Side.SELL) == Side.SELL.name


def test_status() -> None:
    assert Status.CANCEL > Status.OPEN
    assert str(Status.CANCEL) == Status.CANCEL.name


def test_execution() -> None:
    assert Execution.LIMIT > Execution.MARKET
    assert str(Execution.LIMIT) == Execution.LIMIT.name
