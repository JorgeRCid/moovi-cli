"""Comando de descarga del libro de calificaciones."""

from __future__ import annotations

import argparse
from dataclasses import replace

from moovi.cli.context import Services
from moovi.cli.formats.base import Formatter
from moovi.cli.tables import GradesTable


def register(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    common: argparse.ArgumentParser,
) -> None:
    grades = subparsers.add_parser(
        "grades",
        parents=[common],
        help="Descargar las calificaciones de un curso",
    )
    grades.add_argument("course_id", type=int, metavar="COURSE_ID")
    grades.add_argument(
        "--all-items",
        action="store_true",
        help="Incluir calificaciones sin ninguna nota",
    )
    grades.set_defaults(handler=_grades)


def _grades(
    args: argparse.Namespace, services: Services, formatter: Formatter
) -> int:
    gradebook = services.grades.gradebook(
        args.course_id, all_items=args.all_items
    )
    limit = getattr(args, "limit", None)
    if limit:
        gradebook = replace(gradebook, students=gradebook.students[:limit])
    formatter.render(GradesTable(gradebook))
    return 0
