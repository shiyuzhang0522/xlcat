# xlcat

**Read Excel files directly from your HPC terminal.**

Print a worksheet, preview its first rows, inspect column headers, or export TSV/CSV.
Works with **`.xlsx` and `.xlsm`** on Linux and macOS. No Excel, pandas, or administrator access needed.

```bash
xlcat results.xlsx -n 6       # Header + first 5 data rows
xlcat results.xlsx --header   # Header only
```

## Install

Requires **Python 3.9+** with `venv` support, and Git. If your HPC provides Python
through modules, load its Python module first.

```bash
git clone https://github.com/shiyuzhang0522/xlcat.git
cd xlcat
bash install.sh
export PATH="$HOME/.local/bin:$PATH"
xlcat --help
```

The installer puts the command in `~/.local/bin` and creates a dedicated Python
environment in `~/.local/share/xlcat-venv`. It installs `openpyxl` there. No `sudo`
or environment activation is needed afterward.

To make the command available in future Bash sessions, add this line **once** to
`~/.bashrc` (use `~/.zshrc` for Zsh):

```bash
export PATH="$HOME/.local/bin:$PATH"
```

**Already using Conda or another Python environment?** You can skip the installer:

```bash
python3 -m pip install -r requirements.txt
python3 xlcat results.xlsx -n 6
```

## Usage

| Task | Command |
| --- | --- |
| Print the first worksheet | `xlcat results.xlsx` |
| Preview the first 10 rows | `xlcat results.xlsx -n 10` |
| Show just the header | `xlcat results.xlsx --header` |
| List column numbers, Excel letters, and names | `xlcat results.xlsx --columns` |
| List worksheets | `xlcat results.xlsx --sheets` |
| Select a sheet by name | `xlcat results.xlsx --sheet "Per locus" -n 6` |
| Select the second sheet | `xlcat results.xlsx --sheet-index 2 -n 6` |
| Start at a header on row 3 | `xlcat results.xlsx --header-row 3 -n 6` |
| Scroll through wide output | `xlcat results.xlsx \| less -S` |
| Export standard TSV | `xlcat results.xlsx --tsv > results.tsv` |
| Export CSV | `xlcat results.xlsx --csv > results.csv` |
| Display formula expressions | `xlcat results.xlsx --formulas -n 6` |

**`-n N` includes the header**, like `head -n N`. Use `-n 6` for one header plus
five data rows. All commands select the first worksheet unless a sheet is specified.

## Offline HPC installation

On an internet-connected machine with Python 3.9+, download this repository and the dependencies:

```bash
git clone https://github.com/shiyuzhang0522/xlcat.git
python3 -m pip download --only-binary=:all: -d xlcat-wheels -r xlcat/requirements.txt
```

Transfer both folders to the HPC. From the `xlcat` folder, run:

```bash
bash install.sh --no-index --find-links ../xlcat-wheels
export PATH="$HOME/.local/bin:$PATH"
```

## Things to know

- The tool only reads your workbook. It does not modify it or run macros.
- Default output is tab-separated text with embedded tabs/newlines escaped, so
  each worksheet row occupies one terminal line. `--tsv` and `--csv` preserve
  embedded characters using standard quoting.
- Formula cells show **saved results**, which may be stale or blank. The tool
  does not calculate formulas; use `--formulas` to see expressions.
- Blank cells stay blank. Excel styling and display formats are not reproduced.
- Legacy `.xls`, binary `.xlsb`, and password-encrypted files are not supported.

See [the reference guide](docs/reference.md) for detailed behavior and troubleshooting.

## Update and test

```bash
git pull --ff-only
bash install.sh
"$HOME/.local/share/xlcat-venv/bin/python" test_xlcat.py
```

Tests use synthetic workbooks and cover previews, headers, sheet selection,
exports, formulas, errors, and closed pipes.
