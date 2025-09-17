import argparse
import pathlib
from datetime import datetime
from enum import Enum

from src.logs import LogReader
from src.reports import AbstractReporter, ReportAggregator, StudentPerformanceReporter


class ReportTypeEnum(Enum):
    PERFORMANCE = ("student-performance", StudentPerformanceReporter)

    def __init__(self, cli_value: str, reporter: type["AbstractReporter"]):
        self.cli_value = cli_value
        self.reporter = reporter

    @classmethod
    def to_tuple(cls) -> tuple[str, ...]:
        return tuple(e.cli_value for e in cls)

    @classmethod
    def from_value(cls, value: str) -> "ReportTypeEnum":
        for member in cls:
            if member.cli_value == value:
                return member
        
        raise ValueError(f"Unsupported report type: {value}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="StudentPerformance",
        description="Create an in-console report of the provided log files",
        epilog="Text at the bottom of help",
    )

    parser.add_argument(
        "-f", "--file",
        action="extend",
        nargs="*",
        type=pathlib.Path,
        help="a relative or absolute file/folder path/paths",
    )
    parser.add_argument(
        "-d", "--dir",
        action="extend",
        nargs="*",
        type=pathlib.Path,
        help="a relative or absolute file/folder path/paths",
    )
    parser.add_argument(
        "-r", "--report",
        type=str,
        choices=ReportTypeEnum.to_tuple(),
        help="a string specifying the report type",
        default=ReportTypeEnum.PERFORMANCE.cli_value,
    )
    parser.add_argument(
        "--date",
        type=datetime.fromisoformat,
        help="a date string in ISO 8601 format (YYYY-MM-DD)",
    )

    return parser


class ArgHandler:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.report_enum = ReportTypeEnum.from_value(args.report)
        self.reporter = self.report_enum.reporter

    @property
    def file_paths(self) -> list[pathlib.Path] | None:
        return self.args.file

    @property
    def dir_paths(self) -> list[pathlib.Path] | None:
        return self.args.dir

    @property
    def date(self) -> datetime | None:
        return self.args.date


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    arg_handler = ArgHandler(args)

    log_reader = LogReader(arg_handler.file_paths, arg_handler.dir_paths)

    filters = {"date": arg_handler.date} if arg_handler.date else None
    report_aggregator = ReportAggregator(
        log_reader=log_reader,
        reporter_classes=(arg_handler.reporter,),
        filters=filters,
    )
    report_aggregator.run_reporters()

    for reporter in report_aggregator.reporters:
        print(reporter.get_formatted_report())
    


if __name__ == "__main__":
    main()