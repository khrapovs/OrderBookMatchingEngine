from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class NewsEvent:
    """Represents a structured news event in the market simulation.

    Parameters
    ----------
    timestamp : datetime
        The time at which the news event occurs.
    headline : str
        The text headline summarizing the news.
    impact : float
        The numerical indicator of the news impact (e.g. positive/negative shift).
    """

    timestamp: datetime
    headline: str
    impact: float


class NewsFeed:
    """Manages structured news events for the market simulation.

    Parameters
    ----------
    events : list[NewsEvent], optional
        The list of news events.
    """

    def __init__(self, events: list[NewsEvent] | None = None) -> None:
        self._events = sorted(events or [], key=lambda e: e.timestamp)

    def get_news(self, timestamp: datetime) -> list[NewsEvent]:
        """Retrieve all news events published up to the given timestamp.

        Parameters
        ----------
        timestamp : datetime
            The query timestamp.

        Returns
        -------
        list[NewsEvent]
            The list of matching news events.
        """
        return [e for e in self._events if e.timestamp <= timestamp]
