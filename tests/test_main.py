from datetime import datetime

import pytest

from src.dto import StudentDTO
from src.files import FileReader
from src.reports import ReportAggregator, StudentPerformanceReporter


@pytest.fixture(params=[None, datetime(2023, 9, 1)])
def date_filter(request):
    return request.param


def test_file_reader(tmp_csv):
    reader = FileReader(file_paths=[tmp_csv])
    rows = list(reader.read_one())
    
    assert len(rows) == 3
    assert all(isinstance(r, StudentDTO) for r in rows)
    assert rows[0].fullname == "Семенова Елена"
    assert rows[0].grade == 5
    assert rows[0].date == datetime(2023, 9, 1)


def test_student_performance_report(tmp_csv, date_filter):
    reader = FileReader(file_paths=[tmp_csv])
    filters = {"date": date_filter} if date_filter else None
    reporter = StudentPerformanceReporter(filters=filters)

    for dto in reader.read_one():
        reporter.add_to_report(dto)

    report = reporter.report
    
    assert all("average_grade" in rec for rec in report.values())
    
    if date_filter is None:
        assert report["Семенова Елена"]["average_grade"] == (5 + 4) / 2
        assert report["Титов Владислав"]["average_grade"] == 3
    else:
        assert report["Семенова Елена"]["average_grade"] == 5
        assert report["Титов Владислав"]["average_grade"] == 3


def test_report_aggregator(tmp_csv, date_filter):
    file_reader = FileReader(file_paths=[tmp_csv])
    filters = {"date": date_filter} if date_filter else None
    aggregator = ReportAggregator(
        file_reader=file_reader,
        reporter_classes=(StudentPerformanceReporter,),
        filters=filters
    )
    aggregator.run_reporters()
    
    assert len(aggregator.reporters) == 1
    reporter = aggregator.reporters[0]
    
    if date_filter is None:
        assert reporter.report["Семенова Елена"]["average_grade"] == (5 + 4) / 2
        assert reporter.report["Титов Владислав"]["average_grade"] == 3
    else:
        for rec in reporter.report.values():
            assert rec["average_grade"] >= 3
