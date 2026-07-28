import datetime


def on_dt_str(s: str | None) -> int | None:
    return None if s is None else int(
        datetime.datetime.fromisoformat(s).timestamp())
