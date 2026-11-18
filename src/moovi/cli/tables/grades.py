"""Tabla dinámica del libro de calificaciones."""

from __future__ import annotations

from collections.abc import Sequence

from moovi.cli.tables.base import Column, RichValue, Table
from moovi.cli.tables.groups import groups_value
from moovi.cli.text import flatten_text, html_to_text
from moovi.domain.models import Grade, GradeItem, Gradebook


class GradesTable(Table):
    def __init__(self, gradebook: Gradebook) -> None:
        self._gradebook = gradebook
        self._names = _unique_names(gradebook.items)

    @property
    def columns(self) -> Sequence[Column]:
        return [
            Column("id", "ID"),
            Column("id_number", "ID NUMBER"),
            Column("last_name", "APELLIDOS"),
            Column("first_name", "NOMBRE"),
            Column("groups", "GRUPOS"),
            Column("full_name", "NOMBRE COMPLETO", table=False, csv=False),
            *[Column(name, name) for name in self._names],
        ]

    @property
    def rows(self) -> Sequence[Sequence[object]]:
        return [
            (
                student.user_id,
                student.id_number,
                student.last_name,
                student.first_name,
                groups_value(student.groups),
                student.full_name,
                *[_grade_value(grade) for grade in student.grades],
            )
            for student in self._gradebook.students
        ]

    @property
    def single_row(self) -> bool:
        return False


def _unique_names(items: Sequence[GradeItem]) -> list[str]:
    used = {"id", "id_number", "last_name", "first_name", "groups", "full_name"}
    names: list[str] = []
    for item in items:
        base = _item_base_name(item)
        name = base
        suffix = 2
        while name in used:
            name = f"{base} ({suffix})"
            suffix += 1
        used.add(name)
        names.append(name)
    return names


def _item_base_name(item: GradeItem) -> str:
    name = item.name.strip()
    if name:
        return name
    if item.type == "course":
        return "Total del curso"
    if item.type == "category":
        return f"Categoría {item.instance}"
    return f"item_{item.id}"


def _grade_value(grade: Grade | None) -> RichValue:
    if grade is None or not grade.has_value:
        return RichValue(raw=None, text="—", csv_text="")
    formatted = html_to_text(grade.formatted) if grade.formatted else ""
    text = formatted or _format_raw(grade.raw)
    csv_text = _format_raw(grade.raw) or flatten_text(formatted)
    return RichValue(raw=grade, text=text, csv_text=csv_text)


def _format_raw(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:g}"
