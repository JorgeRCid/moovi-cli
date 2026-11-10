"""Formato común de los grupos de una persona."""

from __future__ import annotations

from collections.abc import Sequence

from moovi.cli.tables.base import RichValue
from moovi.domain.models import Group


def groups_value(groups: Sequence[Group]) -> RichValue:
    return RichValue(
        raw=groups,
        text="; ".join(group.name for group in groups if group.name),
        csv_text=";".join(
            group.name.replace(";", "#") for group in groups if group.name
        ),
    )
