from order_matching.enums import Side


def test_side() -> None:
    assert Side.SELL > Side.BUY
    assert str(Side.SELL) == Side.SELL.name
