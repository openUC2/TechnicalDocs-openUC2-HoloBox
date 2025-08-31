#!/usr/bin/env bash
# setup_offline_pyscript_pandas.sh
# Create an *offline* PyScript + Pyodide setup with pandas and a working demo page.

set -euo pipefail

# --- versions / paths ---------------------------------------------------------
PYODIDE_VERSION="${PYODIDE_VERSION:-0.28.2}"   # change if you prefer another
ROOT_DIR="${PWD}/pyscript-offline"
PUBLIC_DIR="pyscript-offline/public"

# --- folders ------------------------------------------------------------------
mkdir -p "pyscript-offline/public"
cd "pyscript-offline"

# --- PyScript core via npm ----------------------------------------------------
if ! command -v npm >/dev/null 2>&1; then
  echo "npm not found. Please install Node.js/npm first." >&2
  exit 1
fi

[ -f package.json ] || echo '{}' > package.json
npm i @pyscript/core@latest

# copy pyscript dist into public
mkdir -p "pyscript-offline/public/pyscript"
cp -R "./node_modules/@pyscript/core/dist/." "pyscript-offline/public/pyscript/"

# --- Pyodide: full bundle (includes pandas & friends) -------------------------
# (~200–300 MB download)
cd "pyscript-offline"
TARBALL="pyodide-0.28.2.tar.bz2"
URL="https://github.com/pyodide/pyodide/releases/download/0.28.2/pyodide-0.28.2.tar.bz2"

echo "Downloading ${URL} ..."
curl -L -o "pyodide-0.28.2.tar.bz2" "${URL}"

echo "Extracting pyodide-0.28.2.tar.bz2 ..."
tar -xjf "pyodide-0.28.2.tar.bz2"  # creates ./pyodide-0.28.2/pyodide/*

# copy the entire pyodide folder (contains pyodide.mjs/wasm, stdlib, and all packages)
mkdir -p "public/pyodide"
cp -R "pyodide/." "pyscript-offline/public/pyodide/"

# --- Demo page (uses pandas offline) ------------------------------------------
cat > "pyscript-offline/public/index.html" <<'HTML'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>PyScript Offline — pandas</title>
  <script type="module" src="/pyscript/core.js"></script>
  <link rel="stylesheet" href="/pyscript/core.css">
  <style>
    body { font-family: system-ui, sans-serif; margin: 2rem; }
    #out { margin-top: 1rem; padding: 1rem; border: 1px solid #ccc; }
    table { border-collapse: collapse; }
    td, th { border: 1px solid #999; padding: 0.25rem 0.5rem; }
  </style>
</head>
<body>
  <h1>PyScript Offline + Pyodide + pandas</h1>

  <py-config>
    interpreter = "/pyodide/pyodide.mjs"
    packages = ["pandas"]
  </py-config>

  <div id="out"></div>

  <script type="py">
from pyscript import document
import pandas as pd

df = pd.DataFrame({
    "a": range(1, 6),
    "b": [x**2 for x in range(1, 6)],
    "c": ["odd" if x % 2 else "even" for x in range(1, 6)],
})

# Render as HTML table
html = df.to_html(index=False)
document.querySelector("#out").innerHTML = html
  </script>
</body>
</html>
HTML

# --- helpful message ----------------------------------------------------------
cat <<MSG

Done.

Run a local server (choose ONE):

  1) Python http.server
     python3 -m http.server -d "pyscript-offline/public" 8080
     → open http://localhost:8080

  2) With COOP/COEP (for worker features):
     npx static-handler --coi "pyscript-offline/public"

All files are in: pyscript-offline/public
- /pyscript/core.js, core.css
- /pyodide/* (runtime + stdlib + packages incl. pandas)
- index.html (offline pandas demo)
MSG
