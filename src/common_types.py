from typing import TypeAlias

DataValueT: TypeAlias = str
ReportT: TypeAlias = dict[DataValueT, dict]
RowDTO: TypeAlias = dict[str, DataValueT]

