from order_matching.enums import Execution


def test_execution() -> None:
    assert Execution.LIMIT > Execution.MARKET
    assert str(Execution.LIMIT) == Execution.LIMIT.name
