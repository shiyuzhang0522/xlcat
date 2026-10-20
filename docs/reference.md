# xlcat — Excel from the HPC terminal

A small read-only Python command for `.xlsx` and `.xlsm`. No Excel, GUI, pandas,
administrator access, or running service is needed. Requires Python 3.9+ and
openpyxl 3.1.x. The source workbook is never saved or modified. Macros are not run.

For installation and offline setup, see the [README](../README.md).

## Daily commands

```bash
xlcat results.xlsx                       # Entire first worksheet
xlcat results.xlsx -n 6                  # Header + first 5 data rows
xlcat results.xlsx --header              # Header only
xlcat results.xlsx --columns             # Column number, Excel letter, header
xlcat results.xlsx --sheets              # List worksheets
xlcat results.xlsx -s 'Per locus' -n 10   # Sheet by exact name
xlcat results.xlsx --sheet-index 2 -n 10  # Sheet by 1-based position
xlcat results.xlsx --header-row 3 -n 6    # Start at row 3; print 6 rows total
xlcat results.xlsx --formulas -n 5        # Formula expressions
xlcat results.xlsx | less -S             # Scroll wide output
xlcat results.xlsx | head -n 6           # Also works with shell pipes
xlcat results.xlsx --tsv > results.tsv   # Standard quoted TSV export
xlcat results.xlsx --csv > results.csv   # Standard quoted CSV export
```

`-n N` means N worksheet rows **including the header**, like `head -n N`.
`--header-row R` selects the starting row; it never guesses which row is the header.
Numeric sheet names are unambiguous: `--sheet 2` selects the sheet named `2`;
`--sheet-index 2` selects the second worksheet.

## Text and Excel details

- Default output is terminal-friendly escaped TSV. Backslashes, embedded tabs,
  newlines, carriage returns, and other terminal control characters are escaped.
  One Excel row becomes one terminal line. Unicode is emitted as UTF-8.
- `--tsv` and `--csv` preserve text fields using standard CSV quoting. Embedded
  newlines may occupy multiple physical lines: use the built-in `-n` for previews,
  and a CSV-aware reader for parsing these exports. These modes do not sanitize
  terminal controls or spreadsheet formula-like text.
- Blank cells become empty fields, not `NA`. Booleans become TRUE/FALSE. Dates and
  times use ISO notation. Values are shown without Excel display formatting:
  percentages, custom decimal formats, and leading zeros from number formats
  are not reproduced. Text-stored leading zeros are preserved. No deliberate
  numeric rounding is applied; precision already lost in Excel cannot be restored.
- Formula mode defaults to **cached results saved by Excel**, which may be stale
  or absent (blank). This tool does not calculate formulas. Use `--formulas` to
  inspect expressions, or recalculate/save in Excel before exporting values.
- Merged cells have a value only in the top-left cell. Hidden rows, columns and
  sheets are included; filters do not suppress rows. Styles, bold text, pictures,
  and comments are not represented.
- The reader streams worksheet rows instead of building a pandas table. Workbook
  metadata and shared strings can still consume memory. `-n` stops worksheet
  reading early, but opening a large workbook can still take time.
- Formatting may enlarge the reported used range, causing trailing blanks. For
  files with incorrect declared ranges, try `--reset-dimensions`; this may produce
  rows with different field counts. `--columns` omits trailing blank headers.
- Legacy `.xls`, binary `.xlsb`, encrypted workbooks, and stdin input are not
  supported. Convert those Excel formats to `.xlsx` first.
- Errors go to stderr with a nonzero exit code; normal output stays pipe-friendly.
  Closing a pipe with `head` exits quietly. Never redirect output to the input
  filename, because the shell truncates it before this tool starts.

## Validation

Run `python3 test_xlcat.py` in this directory with openpyxl installed. Tests use
temporary minimal OOXML fixtures and cover row limits, sheet selection, headers,
blank/text/numeric/formula cells, quoting, malformed inputs, and early pipe closure.

Implementation references:
- https://openpyxl.readthedocs.io/en/stable/optimized.html
- https://openpyxl.readthedocs.io/en/stable/api/openpyxl.reader.excel.html
