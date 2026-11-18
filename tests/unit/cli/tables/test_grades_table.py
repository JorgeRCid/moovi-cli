from __future__ import annotations

from moovi.cli.tables import GradesTable
from moovi.cli.tables.base import RichValue
from moovi.domain.models import Grade, Gradebook, GradeItem, Group, StudentGrades


def gradebook() -> Gradebook:
    return Gradebook(
        101,
        (
            GradeItem(601, "Práctica 1", "mod", module="assign"),
            GradeItem(602, "Examen", "manual"),
        ),
        (
            StudentGrades(
                7,
                "Ana Alumna",
                first_name="Ana",
                last_name="Alumna",
                id_number="297275",
                groups=(
                    Group(146, "PROII_1 (Laboratorio)"),
                    Group(147, "MODALIDAD_GLOBAL"),
                ),
                grades=(
                    Grade(raw=8.5, formatted="8.50"),
                    Grade(raw=None, formatted="-"),
                ),
            ),
        ),
    )


def test_columns_put_ids_first_and_hide_full_name() -> None:
    table = GradesTable(gradebook())

    assert [column.key for column in table.columns] == [
        "id",
        "id_number",
        "last_name",
        "first_name",
        "groups",
        "full_name",
        "Práctica 1",
        "Examen",
    ]
    columns = {column.key: column for column in table.columns}
    assert columns["id_number"].header == "ID NUMBER"
    assert columns["last_name"].header == "APELLIDOS"
    assert columns["groups"].header == "GRUPOS"
    assert columns["full_name"].table is False
    assert columns["full_name"].csv is False


def test_rows_align_student_data_and_grades() -> None:
    table = GradesTable(gradebook())
    row = table.rows[0]

    assert row[:4] == (7, "297275", "Alumna", "Ana")
    groups = row[4]
    assert isinstance(groups, RichValue)
    assert groups.text == "PROII_1 (Laboratorio); MODALIDAD_GLOBAL"
    assert groups.csv_text == "PROII_1 (Laboratorio);MODALIDAD_GLOBAL"
    assert row[5] == "Ana Alumna"
    practice = row[6]
    exam = row[7]
    assert isinstance(practice, RichValue)
    assert practice.raw == Grade(raw=8.5, formatted="8.50")
    assert practice.text == "8.50"
    assert practice.csv_text == "8.5"

    assert isinstance(exam, RichValue)
    assert exam.raw is None
    assert exam.text == "—"
    assert exam.csv_text == ""


def test_numeric_csv_uses_raw_value_with_dot_decimal() -> None:
    table = GradesTable(
        Gradebook(
            101,
            (GradeItem(601, "Práctica 1", "mod"),),
            (
                StudentGrades(
                    7,
                    "Ana Alumna",
                    grades=(Grade(raw=8.5, formatted="8,50"),),
                ),
            ),
        )
    )

    grade = table.rows[0][6]
    assert isinstance(grade, RichValue)
    assert grade.text == "8,50"
    assert grade.csv_text == "8.5"


def test_html_in_formatted_grade_is_cleaned_for_table_and_csv() -> None:
    table = GradesTable(
        Gradebook(
            101,
            (GradeItem(601, "Práctica 1", "mod"),),
            (
                StudentGrades(
                    7,
                    "Ana Alumna",
                    grades=(
                        Grade(
                            raw=8.5,
                            formatted='<img class="icon" alt="">8.50',
                        ),
                    ),
                ),
            ),
        )
    )

    grade = table.rows[0][6]
    assert isinstance(grade, RichValue)
    assert grade.text == "8.50"
    assert grade.csv_text == "8.5"


def test_non_numeric_grade_uses_formatted_text_in_csv() -> None:
    table = GradesTable(
        Gradebook(
            101,
            (GradeItem(601, "Práctica 1", "mod"),),
            (
                StudentGrades(
                    7,
                    "Ana Alumna",
                    grades=(Grade(raw=None, formatted="Apto"),),
                ),
            ),
        )
    )

    grade = table.rows[0][6]
    assert isinstance(grade, RichValue)
    assert grade.text == "Apto"
    assert grade.csv_text == "Apto"


def test_empty_course_and_category_names_get_labels() -> None:
    table = GradesTable(
        Gradebook(
            101,
            (
                GradeItem(1, "", "course", instance=1686),
                GradeItem(2, "", "category", instance=7649),
            ),
            (),
        )
    )

    assert [column.key for column in table.columns[6:]] == [
        "Total del curso",
        "Categoría 7649",
    ]


def test_duplicate_and_reserved_names_are_desambiguated() -> None:
    table = GradesTable(
        Gradebook(
            101,
            (
                GradeItem(601, "id", "manual"),
                GradeItem(602, "id", "manual"),
                GradeItem(603, "", "manual"),
            ),
            (),
        )
    )

    assert [column.key for column in table.columns] == [
        "id",
        "id_number",
        "last_name",
        "first_name",
        "groups",
        "full_name",
        "id (2)",
        "id (3)",
        "item_603",
    ]
