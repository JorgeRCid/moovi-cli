"""Casos de uso del libro de calificaciones."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace

from moovi.domain.models import (
    GradeItem,
    Gradebook,
    Participant,
    StudentGrades,
)
from moovi.logic.session import MoodleSession


class GradeService:
    def __init__(self, session: MoodleSession) -> None:
        self._session = session

    def gradebook(self, course_id: int, *, all_items: bool = False) -> Gradebook:
        """Libro de calificaciones del curso.

        Por defecto elimina las columnas sin ninguna nota. Con ``all_items``
        conserva todas las calificaciones creadas en el libro.
        """
        gradebook = self._session.grade_items(course_id)
        if not gradebook.students:
            return replace(gradebook, course_id=course_id)

        participants = {
            participant.id: participant
            for participant in self._session.participants(course_id)
        }
        students = tuple(
            _with_participant(student, participants.get(student.user_id))
            for student in gradebook.students
        )
        students = tuple(
            sorted(
                students,
                key=lambda student: (
                    student.last_name.casefold(),
                    student.first_name.casefold(),
                    student.user_id,
                ),
            )
        )
        if all_items:
            return Gradebook(course_id, gradebook.items, students)

        items, students = _only_graded(gradebook.items, students)
        return Gradebook(course_id, items, students)


def _with_participant(
    student: StudentGrades, participant: Participant | None
) -> StudentGrades:
    if participant is None:
        return student
    return replace(
        student,
        first_name=participant.first_name,
        last_name=participant.last_name,
        id_number=participant.id_number or student.id_number,
        groups=participant.groups,
    )


def _only_graded(
    items: Sequence[GradeItem], students: Sequence[StudentGrades]
) -> tuple[tuple[GradeItem, ...], tuple[StudentGrades, ...]]:
    keep = [
        index
        for index, _ in enumerate(items)
        if any(
            student.grades[index] is not None
            and student.grades[index].has_value
            for student in students
        )
    ]
    if len(keep) == len(items):
        return tuple(items), tuple(students)

    compact_items = tuple(items[index] for index in keep)
    compact_students = tuple(
        replace(
            student,
            grades=tuple(student.grades[index] for index in keep),
        )
        for student in students
    )
    return compact_items, compact_students
