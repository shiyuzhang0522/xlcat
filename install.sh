#!/usr/bin/env bash
# Install xlcat for the current user. Extra arguments are passed to pip.
# Example offline install: bash install.sh --no-index --find-links ../xlcat-wheels
set -euo pipefail

xlcat_source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
xlcat_python="${XLCAT_PYTHON:-python3}"
xlcat_env_dir="${XLCAT_ENV_DIR:-$HOME/.local/share/xlcat-venv}"
xlcat_bin_dir="${XLCAT_BIN_DIR:-$HOME/.local/bin}"

"$xlcat_python" -c 'import sys; sys.exit("xlcat requires Python 3.9 or newer") if sys.version_info < (3, 9) else None'
printf '[1/3] Preparing Python environment: %s\n' "$xlcat_env_dir"
"$xlcat_python" -m venv "$xlcat_env_dir"
printf '[2/3] Installing dependencies\n'
"$xlcat_env_dir/bin/python" -m pip install -r "$xlcat_source_dir/requirements.txt" "$@"
printf '[3/3] Installing xlcat\n'
mkdir -p "$xlcat_bin_dir"
install -m 755 "$xlcat_source_dir/xlcat" "$xlcat_env_dir/bin/xlcat"
# Quote paths safely, including spaces and shell metacharacters.
"$xlcat_env_dir/bin/python" - "$xlcat_env_dir" "$xlcat_bin_dir/xlcat" <<'PY'
import os
from pathlib import Path
import shlex
import sys

env_dir = Path(sys.argv[1]).resolve()
target = Path(sys.argv[2])
text = '#!/bin/sh\nexec {} {} "$@"\n'.format(
    shlex.quote(str(env_dir / 'bin/python')),
    shlex.quote(str(env_dir / 'bin/xlcat')),
)
target.write_text(text, encoding='utf-8')
os.chmod(target, 0o755)
PY
"$xlcat_bin_dir/xlcat" --version
printf '\nInstalled. Add the following line to your shell configuration if needed:\n'
printf 'export PATH=%q:"$PATH"\n' "$xlcat_bin_dir"
