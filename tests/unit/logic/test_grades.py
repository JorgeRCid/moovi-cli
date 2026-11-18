from __future__ import annotations

from moovi.domain.models import (
    Grade,
    Gradebook,
    GradeItem,
    Group,
    Participant,
    StudentGrades,
)
from moovi.logic.services.grades import GradeService

ITEMS = (
    GradeItem(601, "Práctica 1", "mod", module="assign"),
    GradeItem(602, "Examen", "manual"),
    GradeItem(603, "Práctica 3", "mod", module="assign"),
)


class FakeSession:
    def __init__(self, gradebook: Gradebook | None = None) -> None:
        self._gradebook = gradebook or Gradebook(
            101,
            ITEMS,
            (
                StudentGrades(9, "Sin Grupo", grades=(None, Grade(7), None)),
                StudentGrades(7, "Ana Alumna", grades=(Grade(8.5), Grade(0), None)),
            ),
        )
        self.gradebook_calls = 0
        self.participant_calls = 0

    def grade_items(self, course_id: int) -> Gradebook:
        assert course_id == 101
        self.gradebook_calls += 1
        return self._gradebook

    def participants(self, course_id: int) -> list[Participant]:
        assert course_id == 101
        self.participant_calls += 1
        return [
            Participant(
                7,
                "Ana",
                "Alumna",
                groups=(Group(146, "DAGSS_2"),),
                id_number="297275",
            ),
            Participant(9, "Sin", "Grupo", id_number="654321"),
        ]


def test_gradebook_joins_participants_and_sorts_by_last_name() -> None:
    session = FakeSession()
    service = GradeService(session)

    gradebook = service.gradebook(101)

    assert session.gradebook_calls == 1
    assert session.participant_calls == 1
    assert [student.user_id for student in gradebook.students] == [7, 9]
    ana, sin_grupo = gradebook.students
    assert (ana.first_name, ana.last_name) == ("Ana", "Alumna")
    assert ana.id_number == "297275"
    assert ana.groups == (Group(146, "DAGSS_2"),)
    assert (sin_grupo.first_name, sin_grupo.last_name) == ("Sin", "Grupo")
    assert sin_grupo.id_number == "654321"
    assert sin_grupo.groups == ()


def test_gradebook_removes_items_without_any_grade_by_default() -> None:
    service = GradeService(FakeSession())

    gradebook = service.gradebook(101)

    assert [item.name for item in gradebook.items] == ["Práctica 1", "Examen"]
    assert [grade.raw if grade else None for grade in gradebook.students[0].grades] == [
        8.5,
        0,
    ]


def test_gradebook_all_items_keeps_empty_columns() -> None:
    service = GradeService(FakeSession())

    gradebook = service.gradebook(101, all_items=True)

    assert [item.name for item in gradebook.items] == [
        "Práctica 1",
        "Examen",
        "Práctica 3",
    ]
    assert gradebook.students[0].grades[2] is None


def test_gradebook_without_students_does_not_fetch_participants() -> None:
    session = FakeSession(Gradebook(101, (), ()))
    service = GradeService(session)

    gradebook = service.gradebook(101)

    assert gradebook.course_id == 101
    assert gradebook.students == ()
    assert session.participant_calls == 0


def test_gradebook_keeps_gradebook_id_number_when_participant_is_missing() -> None:
    gradebook = Gradebook(
        101,
        ITEMS[:1],
        (
            StudentGrades(
                99,
                "Alguien Sin Matrícula",
                id_number="999999",
                grades=(Grade(5),),
            ),
        ),
    )
    service = GradeService(FakeSession(gradebook))

    [student] = service.gradebook(101).students

    assert student.full_name == "Alguien Sin Matrícula"
    assert student.first_name == ""
    assert student.last_name == ""
    assert student.id_number == "999999"
