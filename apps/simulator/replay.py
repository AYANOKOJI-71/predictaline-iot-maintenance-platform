"""A local fixture replay helper; it never connects to a remote broker or physical equipment."""

from predictaline.fixtures import SCENARIOS


def list_local_scenarios() -> list[str]:
    return sorted(SCENARIOS)
