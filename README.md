# Operations Research & Analytics

Marimo notebooks on operations research and analytics topics. Each notebook is a
standalone, reactive document: prose, a few controls, and charts that recompute
when the controls move.

## Notebooks

| Notebook | Topic |
|---|---|
| [`notebooks/binary_entropy.py`](notebooks/binary_entropy.py) | The binary entropy function `H₂(x)` — uncertainty in a single biased binary outcome, in bits or nats |

## Getting started

Requires [uv](https://docs.astral.sh/uv/) and [just](https://just.systems).

```sh
just sync      # install the environment from uv.lock
just edit      # open the notebook browser on notebooks/
```

`just` on its own lists every recipe. The ones you will use most:

| Recipe | What it does |
|---|---|
| `just edit` | marimo's notebook browser on `notebooks/` |
| `just edit-one binary_entropy` | open one notebook for editing |
| `just run binary_entropy` | run a notebook as a read-only app |
| `just new my_topic` | scaffold a new notebook and open it |
| `just export binary_entropy` | export to a self-contained HTML page in `build/` |
| `just export-all` | export everything — also the smoke test, since an export runs every cell |
| `just export-wasm binary_entropy` | export to WASM, reactive on a static host |
| `just lint` / `just format` | ruff |
| `just upgrade` | raise the pinned versions and relock |

## Conventions

* Notebooks live in `notebooks/`, one topic per file, named in `snake_case`.
* marimo stores notebooks as plain Python, so they diff and review like code.
* Dependencies are pinned exactly in `pyproject.toml`: a notebook is a document,
  and a document that renders differently next month is a bug.
* Charts use [Altair](https://altair-viz.github.io), which marimo renders as
  Vega-Lite — tooltips and selections keep working in exported HTML.
