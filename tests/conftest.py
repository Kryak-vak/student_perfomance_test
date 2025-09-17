from pathlib import Path

import pytest


@pytest.fixture
def tmp_csv(tmp_path: Path) -> Path:
    file_path = tmp_path / "students.csv"
    file_path.write_text(
        "fullname,subject,teacher_name,date,grade\n"
        "Семенова Елена,Английский язык,Ковалева Анна,2023-09-01,5\n"
        "Семенова Елена,Математика,Петрова Ольга,2023-09-02,4\n"
        "Титов Владислав,Математика,Петрова Ольга,2023-09-01,3\n",
        encoding="utf-8"
    )
    return file_path
