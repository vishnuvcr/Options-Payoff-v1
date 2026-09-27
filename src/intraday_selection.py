from __future__ import annotations

from typing import Iterable, Mapping, Sequence


def first_positive_intraday_surface(
    surfaces: Iterable[tuple[object, Sequence[Mapping[str, object]]]]
) -> tuple[object, Mapping[str, object], Sequence[Mapping[str, object]]] | None:
    """
    Return the first intraday timestamp having any positive flatline.

    There is deliberately no 09:20 rejection rule and no percentage threshold.
    At the first timestamp with one or more positive candidates, the candidate
    with the largest positive flatline is selected; ties resolve to the smaller
    shift_points.
    """
    for timestamp, candidates in sorted(surfaces, key=lambda x: x[0]):
        positive = [c for c in candidates if float(c["flatline_inr"]) > 0.0]
        if not positive:
            continue
        positive.sort(key=lambda c: (-float(c["flatline_inr"]), int(c["shift_points"])))
        return timestamp, positive[0], candidates
    return None
