#!/usr/bin/env bash
set -euo pipefail

# Resolve repository root even if executed via symlink.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$ROOT_DIR/.venv"

# Create the virtual environment if it does not exist yet.
if [[ ! -d "$VENV_PATH" ]]; then
  python3 -m venv "$VENV_PATH"
fi

# Activate the environment for dependency installs and runtime.
# shellcheck disable=SC1090
source "$VENV_PATH/bin/activate"

# Ensure the editable install is present so module resolution works.
if ! python -c "import pdftools.gui.main" >/dev/null 2>&1; then
  pip install -e "$ROOT_DIR".[dev]
fi

# Launch the Qt application.
exec python -m pdftools.gui.main "$@"
