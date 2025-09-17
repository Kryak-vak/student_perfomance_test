from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar


@dataclass
class BaseModel:
    pass


@dataclass
class StudentDTO(BaseModel):
    fullname: str
    subject: str
    teacher: str
    date: datetime
    grade: int

    @classmethod
    def from_row(cls, row: list[str]) -> "StudentDTO":
        fullname, subject, teacher, date_str, grade_str = row
        return cls(
            fullname=fullname,
            subject=subject,
            teacher=teacher,
            date=datetime.fromisoformat(date_str),
            grade=int(grade_str),
        )


DTOType = TypeVar("DTOType", bound=BaseModel)

