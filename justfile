# Justfile for the operations research notebooks

# Default recipe: list what is available
default:
    @just --list

# Install the environment from uv.lock
sync:
    uv sync

# Open marimo's notebook browser on notebooks/ - the usual entry point
edit:
    uv run marimo edit notebooks

# Edit one notebook, e.g. `just edit-one binary_entropy`
edit-one NAME:
    uv run marimo edit notebooks/{{NAME}}.py

# Run a notebook as a read-only app (no code shown, cells still reactive)
run NAME:
    uv run marimo run notebooks/{{NAME}}.py

# Scaffold a new notebook and open it
new NAME:
    uv run marimo edit notebooks/{{NAME}}.py

# Export one notebook to a self-contained HTML page in build/
export NAME:
    mkdir -p build
    uv run marimo export html notebooks/{{NAME}}.py --output build/{{NAME}}.html

# Export every notebook. Doubles as the smoke test: an export runs all cells, so a
# notebook that raises cannot be exported.
export-all:
    mkdir -p build
    for nb in notebooks/*.py; do \
        name=$(basename "$nb" .py); \
        echo "-> $name"; \
        uv run marimo export html "$nb" --output "build/$name.html" || exit 1; \
    done

# Export to WASM, so the notebooks stay reactive on a static web host
export-wasm NAME:
    mkdir -p build
    uv run marimo export html-wasm notebooks/{{NAME}}.py --output build/wasm/{{NAME}} --mode edit

# Check formatting and lints
lint:
    uv run ruff format --check notebooks
    uv run ruff check notebooks

# Format the notebooks
format:
    uv run ruff format notebooks
    uv run ruff check --fix notebooks

# Raise the pinned dependency versions and relock
upgrade:
    uv lock --upgrade
    uv sync

# Remove exported output
clean:
    rm -rf build
