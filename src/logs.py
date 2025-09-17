import csv
from collections.abc import Iterable, Iterator
from pathlib import Path

from src.dto import BaseModel, StudentDTO


class LogReader:
    accepted_file_types = ('.csv', )

    def __init__(
            self,
            file_paths: Iterable[Path] | None = None,
            dir_paths: Iterable[Path] | None = None
        ) -> None:
        file_paths = file_paths if file_paths is not None else ()
        dir_paths = dir_paths if dir_paths is not None else ()

        self.file_paths: list[Path] = []
        if file_paths or dir_paths:
            self.file_paths: list[Path] = self._get_file_paths(file_paths, dir_paths)
    
    def _get_file_paths(
            self,
            file_paths: Iterable[Path],
            dir_paths: Iterable[Path]
        ) -> list[Path]:
        def _validate_dir_path(dir_path: Path) -> None:
            if not dir_path.is_dir():
                raise RuntimeError(f"Incorrect path in dir_paths: {dir_path}")
        
        def _validate_file_path(file_path: Path) -> None:
            if not file_path.is_file():
                raise RuntimeError(f"Incorrect path in file_paths: {file_path}")
            
            if file_path.suffix not in self.accepted_file_types:
                raise RuntimeError(f"Unsupported file type in file_paths: {file_path}")

        all_file_paths: list[Path] = []

        dir_file_paths: list[Path] = []
        for dir_path in dir_paths:
            _validate_dir_path(dir_path)
            for dir_file_path in dir_path.iterdir():
                if dir_file_path.is_dir():
                    continue

                dir_file_paths.append(dir_file_path)
        
        for file_path in (*file_paths, *dir_file_paths):
            _validate_file_path(file_path)
            all_file_paths.append(file_path)
        
        return all_file_paths

    def read_one(self) -> Iterator[BaseModel]:
        for file_path in self.file_paths:
            with open(file_path, "r", encoding="utf-8") as file:
                csv_reader = csv.reader(file)
                header = next(csv_reader)

                for row in csv_reader:
                    student_dto = StudentDTO.from_row(row)
                    yield student_dto


