from datetime import datetime

import pytest

from order_matching.simulation.news_feed import NewsEvent, NewsFeed


def test_news_event_creation() -> None:
    timestamp = datetime(2023, 1, 1, 10, 0)
    event = NewsEvent(timestamp=timestamp, headline="Federal Reserve hikes rates", impact=-0.05)
    assert event.timestamp == timestamp
    assert event.headline == "Federal Reserve hikes rates"
    assert event.impact == -0.05

    with pytest.raises(AttributeError):
        # Ensure it is frozen
        setattr(event, "headline", "New Headline")  # noqa


def test_news_feed_sorting_and_retrieval() -> None:
    event_1 = NewsEvent(timestamp=datetime(2023, 1, 1, 10, 0), headline="News 1", impact=0.1)
    event_2 = NewsEvent(timestamp=datetime(2023, 1, 1, 9, 0), headline="News 2", impact=0.2)
    event_3 = NewsEvent(timestamp=datetime(2023, 1, 1, 11, 0), headline="News 3", impact=-0.1)

    feed = NewsFeed([event_1, event_2, event_3])

    # Sorting verification
    assert feed._events == [event_2, event_1, event_3]

    # Query before any news
    assert feed.get_news(datetime(2023, 1, 1, 8, 0)) == []

    # Query exactly on first news
    assert feed.get_news(datetime(2023, 1, 1, 9, 0)) == [event_2]

    # Query between first and second
    assert feed.get_news(datetime(2023, 1, 1, 9, 30)) == [event_2]

    # Query at third news
    assert feed.get_news(datetime(2023, 1, 1, 11, 0)) == [event_2, event_1, event_3]

    # Query way after
    assert feed.get_news(datetime(2023, 1, 1, 12, 0)) == [event_2, event_1, event_3]
