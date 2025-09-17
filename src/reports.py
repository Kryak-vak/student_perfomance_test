from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Mapping
from datetime import datetime
from typing import Generic, TypeVar

from tabulate import tabulate

from src.common_types import ReportT
from src.dto import DTOType, StudentDTO
from src.files import FileReader

FilterT = Mapping[str, str | datetime]


class ReportAggregator:
    def __init__(
        self,
        file_reader: FileReader,
        reporter_classes: tuple[type["ReporterType"], ...],
        filters: FilterT | None
    ) -> None:
        self.file_reader = file_reader
        self.reporter_classes = reporter_classes
        self.reports: list[ReportT] = []

        self.reporters = self._init_reporters(reporter_classes, filters)
    
    def _init_reporters(
            self,
            reporter_classes: tuple[type["ReporterType"], ...],
            filters: FilterT | None,
            ) -> tuple["ReporterType", ...]:
        
        return tuple(rep(filters) for rep in reporter_classes)

    def run_reporters(self, del_prev_reports=True) -> None:
        if del_prev_reports:
            self.reports = []

        for dto in self.file_reader.read_one():
            for reporter in self.reporters:
                reporter.add_to_report(dto)
        
        for reporter in self.reporters:
            self.reports.append(reporter.report)


class AbstractReporter(ABC, Generic[DTOType]):
    group_key_name: str
    report_keys: tuple[str, ...]
    headers_map: dict[str, str]

    def __init__(self, filters: FilterT | None = None) -> None:
        self.filters: FilterT

        if filters is None:
            self.filters = {}
            self.add_to_report = self._add_to_report
        else:
            self.filters = filters
        
        self.report: ReportT = defaultdict(dict)

    def add_to_report(self, dto: DTOType) -> None:
        if not self._apply_filters(dto):
            return None
        
        self._add_to_report(dto)
    
    def _apply_filters(self, dto: DTOType) -> bool:
        return True

    def _add_to_report(self, dto: DTOType) -> None:
        group_key = getattr(dto, self.group_key_name)
        self.update_report(group_key, dto)
    
    @abstractmethod
    def update_report(self, group_key, dto: DTOType) -> None:
        pass

    def get_formatted_report(self) -> str:
        table_data = [
            [url, *(data[key] for key in self.report_keys)]
            for url, data in self.report.items()
        ]
        headers = [
            self.headers_map[self.group_key_name], *self.report_keys
        ]

        return tabulate(table_data, headers=headers, floatfmt=".1f")


ReporterType = TypeVar("ReporterType", bound=AbstractReporter)


class StudentPerformanceReporter(AbstractReporter[StudentDTO]):
    group_key_name = "fullname"
    report_keys = ("average_grade",)
    headers_map = {
        "fullname": "student_name"
    }
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.report = defaultdict(lambda: defaultdict(int))
        self.row_count = 0
    
    def _apply_filters(self, dto: StudentDTO) -> bool:
        date_f = self.filters.get("date")
        if not date_f:
            return True
        
        return dto.date == date_f

    def update_report(self, group_key: str, dto: StudentDTO) -> None:
        rec = self.report[group_key]
        rec["sum"] += dto.grade
        rec["count"] += 1
        rec["average_grade"] = rec["sum"] / rec["count"]
