from __future__ import annotations

import functools
import string
from dataclasses import dataclass
from types import EllipsisType
from typing import *

from ..utils import parse_file_id, to_base
from .misc import DEFAULT_SHEET_NAME, ValueInputOption, ValueRenderOption
from .sheets import Sheets

if TYPE_CHECKING:
    from googleapiclient._apis.sheets.v4.resources import (
        UpdateValuesResponse,
        ValueRange,
    )


def to_slice(*slices: slice | int) -> tuple[slice, ...]:
    func = lambda slc: slc if isinstance(slc, slice) else slice(slc, slc)
    return tuple(map(func, slices))


def ix_to_str(ix: int | str | EllipsisType) -> str:
    return str(ix) if ix is not ... else ""


def format_range_name(range_name: str, sheet_name: str | None = None) -> str:
    if sheet_name is not None:
        return f"'{sheet_name}'!{range_name}"
    else:
        return range_name


def number_to_A1(row: int, col: int, sheet_name: str | None = None) -> str:
    t_col = (
        "".join(
            map(
                lambda x: string.ascii_letters[x - 1].upper(),
                to_base(col, base=26),
            )
        )
        if col is not ...
        else ""
    )
    t_row = ix_to_str(row)
    key = f"{t_col}{t_row}"
    return format_range_name(key, sheet_name)


slice_or_int = (slice, int)


def is_valid_ix(ix: slice | int | EllipsisType) -> bool:
    return isinstance(ix, slice_or_int) or ix is ...


def is_valid_sheet_name(sheet_name: str | None) -> bool:
    return isinstance(sheet_name, str) or sheet_name is None


def slices_to_a1(slices: tuple[slice, slice] | slice | int) -> tuple[str, str | None]:
    match slices:
        case row_ix, col_ix:
            r1 = number_to_A1(row_ix.start, col_ix.start)
            r2 = number_to_A1(row_ix.stop, col_ix.stop)
            return r1, r2
        case row_ix if isinstance(row_ix, slice):
            return ix_to_str(row_ix.start), ix_to_str(row_ix.stop)
        case row_ix:
            return ix_to_str(row_ix)


def parse_sheets_ixs(ixs: tuple[str, slice, slice] | slice | int) -> str:
    sheet_name = None
    r1, r2 = "", None

    match ixs:
        case t_sheet_name if is_valid_sheet_name(t_sheet_name):
            sheet_name = t_sheet_name
        case t_sheet_name, *slices if isinstance(t_sheet_name, str):
            sheet_name = t_sheet_name
            r1, r2 = slices_to_a1(to_slice(*slices))
        case t_sheet_name, t_range_name if is_valid_sheet_name(
            t_sheet_name
        ) and is_valid_sheet_name(t_range_name):
            return t_sheet_name, t_range_name
        case row_ix, col_ix if is_valid_ix(row_ix) and is_valid_ix(col_ix):
            r1, r2 = slices_to_a1(to_slice(row_ix, col_ix))
        case row_ix if is_valid_ix(row_ix):
            r1 = slices_to_a1(row_ix)
        case _:
            raise ValueError(f"Invalid ixs: {ixs}")

    range_name = f"{r1}:{r2}" if r2 is not None else str(r1)

    return sheet_name, range_name


@dataclass(frozen=True)
class _SheetSlice:
    sheet_name: str | None = None
    range_name: str | None = None

    def __str__(self) -> str:
        sheet_name = (
            self.sheet_name if self.sheet_name is not None else DEFAULT_SHEET_NAME
        )
        range_name = self.range_name if self.range_name is not None else ""
        return format_range_name(range_name, sheet_name)

    def __getitem__(self, ixs: tuple[slice, slice] | slice | int) -> _SheetSlice:
        if isinstance(ixs, _SheetSlice):
            return ixs
        else:
            return _SheetSlice(*parse_sheets_ixs(ixs))


SheetSlice = _SheetSlice()


class SheetsValueRange:
    def __init__(
        self,
        sheets: Sheets,
        spreadsheet_id: str,
        value_render_option: ValueRenderOption = ValueRenderOption.unformatted,
        value_input_option: ValueInputOption = ValueInputOption.user_entered,
        sheet_name: str | None = None,
        range_name: str | None = None,
        **kwargs: Any,
    ):
        self.sheets = sheets
        self.spreadsheet_id = parse_file_id(spreadsheet_id)
        self.value_render_option = value_render_option
        self.value_input_option = value_input_option

        self._sheet_name = sheet_name
        self._range_name = range_name

        self.kwargs = kwargs

    @property
    def range_name(self) -> str:
        return str(_SheetSlice(self._sheet_name, self._range_name))

    @functools.cached_property
    def values(self) -> ValueRange:
        return self.sheets.values(
            spreadsheet_id=self.spreadsheet_id,
            range_name=self.range_name,
            value_render_option=self.value_render_option,
            **self.kwargs,
        )

    def update(self, values: list[list[Any]], **kwargs: Any) -> UpdateValuesResponse:
        return self.sheets.update(
            spreadsheet_id=self.spreadsheet_id,
            range_name=self.range_name,
            values=values,
            value_input_option=self.value_input_option,
            **kwargs,
        )

    def __getitem__(
        self,
        ixs: tuple[str, slice, slice]
        | tuple[str, slice]
        | tuple[slice, slice]
        | tuple[str, str],
    ) -> "SheetsValueRange":
        slc = SheetSlice[ixs]

        sheet_name = slc.sheet_name if slc.sheet_name is not None else self._sheet_name
        range_name = slc.range_name if slc.range_name is not None else self._range_name

        return self.__class__(
            self.sheets,
            self.spreadsheet_id,
            self.value_render_option,
            self.value_input_option,
            sheet_name,
            range_name,
            **self.kwargs,
        )
