import marimo

__generated_with = "0.24.2"
app = marimo.App(app_title="The Binary Entropy Function")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import altair as alt
    import numpy as np
    import pandas as pd

    return alt, np, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # The Binary Entropy Function

    A coin comes up heads with probability $x$. Before the flip, how much do you
    not know? The binary entropy function answers that in one number:

    $$H_2(x) = x \cdot \log_b \frac{1}{x} + (1-x) \cdot \log_b \frac{1}{1-x}
            = -x \log_b x - (1-x)\log_b(1-x)$$

    Each term is a surprise $\log_b \frac{1}{p}$ weighted by how often you are
    surprised that way, so $H_2$ is the *expected* surprise of one draw. With
    $b = 2$ it is measured in bits, with $b = e$ in nats. The convention
    $0 \log 0 = 0$ closes the function at both ends, which is what makes it
    continuous on the whole interval $[0, 1]$.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    unit = mo.ui.radio(
        options={"bits (log₂)": 2.0, "nats (ln)": "e"},
        value="bits (log₂)",
        label="Unit",
        inline=True,
    )
    show_terms = mo.ui.switch(label="Show the two terms separately", value=False)

    mo.hstack([unit, show_terms], justify="start", gap=2)
    return show_terms, unit


@app.cell
def _(np):
    def binary_entropy(x, base=2.0):
        """H₂ over an array of probabilities, with 0·log0 = 0 at both ends.

        `np.where` alone would still evaluate log(0) and warn, so the zeros are
        substituted before the logarithm rather than after it.
        """
        x = np.asarray(x, dtype=float)
        safe = np.where((x > 0.0) & (x < 1.0), x, 0.5)
        log = np.log if base == "e" else (lambda v: np.log(v) / np.log(base))
        h = -safe * log(safe) - (1.0 - safe) * log(1.0 - safe)
        return np.where((x > 0.0) & (x < 1.0), h, 0.0)

    def surprise_term(p, base=2.0):
        """One half of the sum, -p·log p, so the two can be plotted apart."""
        p = np.asarray(p, dtype=float)
        safe = np.where(p > 0.0, p, 1.0)
        log = np.log if base == "e" else (lambda v: np.log(v) / np.log(base))
        return np.where(p > 0.0, -safe * log(safe), 0.0)

    return binary_entropy, surprise_term


@app.cell
def _(binary_entropy, np, pd, surprise_term, unit):
    # 501 points: dense enough that the near-vertical shoulders at 0 and 1 read as
    # curves rather than as corners.
    x_grid = np.linspace(0.0, 1.0, 501)
    base = unit.value

    entropy = pd.DataFrame(
        {
            "x": x_grid,
            "H": binary_entropy(x_grid, base),
            # The two halves of the sum, for the decomposition view.
            "heads": surprise_term(x_grid, base),
            "tails": surprise_term(1.0 - x_grid, base),
        }
    )

    unit_label = "nats" if base == "e" else "bits"
    return base, entropy, unit_label


@app.cell(hide_code=True)
def _(alt, entropy, mo, pd, show_terms, unit_label):
    # Categorical slots 1-3 of the house palette. Identity is never colour alone:
    # with the decomposition on there is a legend, and the total stays solid while
    # the two terms are dashed.
    _colors = {"H₂(x)": "#2a78d6", "−x·log x": "#eb6834", "−(1−x)·log(1−x)": "#1baf7a"}

    _series = ["H₂(x)"] + (["−x·log x", "−(1−x)·log(1−x)"] if show_terms.value else [])
    _long = pd.concat(
        [
            entropy[["x", column]].rename(columns={column: "value"}).assign(series=name)
            for name, column in zip(_colors, ["H", "heads", "tails"])
            if name in _series
        ]
    )

    _x = alt.X(
        "x:Q",
        title="x — probability of heads",
        scale=alt.Scale(domain=[0, 1], nice=False, padding=0),
        axis=alt.Axis(tickCount=6, format=".1f"),
    )
    _y = alt.Y("value:Q", title=f"H₂(x) — {unit_label}", axis=alt.Axis(tickCount=6))
    _color = alt.Color(
        "series:N",
        title=None,
        scale=alt.Scale(domain=_series, range=[_colors[s] for s in _series]),
        legend=alt.Legend(orient="top", offset=4) if show_terms.value else None,
    )

    _lines = (
        alt.Chart(_long)
        .mark_line(strokeWidth=2)
        .encode(
            x=_x,
            y=_y,
            color=_color,
            strokeDash=alt.StrokeDash(
                "series:N",
                scale=alt.Scale(domain=_series, range=[[1, 0], [5, 3], [5, 3]][: len(_series)]),
                legend=None,
            ),
            opacity=alt.condition(alt.datum.series == "H₂(x)", alt.value(1.0), alt.value(0.7)),
        )
    )

    # Hover layer: a vertical rule snapped to the nearest x, with every series in
    # one tooltip. `empty=False` keeps it hidden until the pointer is over the plot.
    _hover = alt.selection_point(
        fields=["x"], nearest=True, on="pointerover", empty=False, clear="pointerout"
    )
    _rule = (
        alt.Chart(entropy)
        .mark_rule(color="#8a8a85", strokeWidth=1)
        .encode(
            x=_x,
            opacity=alt.condition(_hover, alt.value(0.6), alt.value(0.0)),
            tooltip=[
                alt.Tooltip("x:Q", title="x", format=".3f"),
                alt.Tooltip("H:Q", title=f"H₂ ({unit_label})", format=".4f"),
                *(
                    [
                        alt.Tooltip("heads:Q", title="−x·log x", format=".4f"),
                        alt.Tooltip("tails:Q", title="−(1−x)·log(1−x)", format=".4f"),
                    ]
                    if show_terms.value
                    else []
                ),
            ],
        )
        .add_params(_hover)
    )

    # The one point worth labelling directly: the maximum at x = 1/2.
    _peak = entropy.loc[[entropy["H"].idxmax()]].assign(
        label=lambda d: d["H"].map(lambda v: f"{v:.3f} {unit_label}")
    )
    _peak_dot = (
        alt.Chart(_peak)
        .mark_point(size=80, filled=True, color=_colors["H₂(x)"], stroke="#fcfcfb", strokeWidth=2)
        .encode(x=_x, y=alt.Y("H:Q"))
    )
    _peak_label = (
        alt.Chart(_peak)
        .mark_text(dy=-14, fontSize=12, color="#52514e")
        .encode(x=_x, y=alt.Y("H:Q"), text="label:N")
    )

    _chart = (
        alt.layer(_lines, _rule, _peak_dot, _peak_label)
        .properties(
            width="container",
            height=380,
            title=f"Uncertainty in a single biased coin flip ({unit_label})",
        )
        .configure_axis(grid=True, gridOpacity=0.15, domainOpacity=0.3, tickOpacity=0.3)
        .configure_view(stroke=None)
    )

    mo.ui.altair_chart(_chart, chart_selection=False, legend_selection=False)
    return


@app.cell(hide_code=True)
def _(base, binary_entropy, mo, unit_label):
    _peak_value = float(binary_entropy([0.5], base)[0])

    mo.md(
        f"""
    The curve is **concave**, **symmetric about $x = 1/2$** and pinned to zero at
    both ends. A coin that always lands heads carries no uncertainty at all; a fair
    coin carries the most any single binary outcome can — **{_peak_value:.4f}
    {unit_label}**. Switching the unit only rescales the vertical axis by
    $\\ln 2 \\approx 0.6931$; the shape never changes.

    The shoulders matter more than the peak in practice. Going from $x = 0.5$ to
    $x = 0.6$ costs only about 3% of the entropy, while going from $x = 0.9$ to
    $x = 0.99$ removes roughly 83% of what was left. **Near-certainty is expensive
    to buy and cheap to lose.**
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## The numbers behind the curve""")
    return


@app.cell(hide_code=True)
def _(base, binary_entropy, mo, np, pd):
    _x = np.arange(0.0, 1.01, 0.05)
    _table = pd.DataFrame({"x": _x, "H₂(x)": binary_entropy(_x, base)}).round(4)

    mo.ui.table(_table, selection=None, pagination=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Where this turns up in operations research

    * **Decision trees and information gain.** Splitting a node on an attribute is
      worth doing exactly insofar as it lowers the entropy of the label — the
      curve above *is* the impurity measure, and its concavity is why a split can
      never increase expected entropy.
    * **Value of information.** The gap between $H_2(\text{prior})$ and the
      expected posterior entropy is the information a test or survey buys you.
      Read off the shoulders: a test that moves a belief from 0.5 to 0.6 has
      bought almost nothing.
    * **Coding and capacity.** $H_2(x)$ is the average number of bits per symbol
      needed to encode a biased binary source, and $1 - H_2(p)$ is the capacity of
      a binary symmetric channel with error rate $p$ — the sharpest reminder that
      a channel that errs half the time transmits nothing at all.
    * **Diversity and concentration.** As a two-category special case of Shannon
      entropy it measures the balance of a portfolio, a queue mix or a market
      share split, where it behaves like a smooth cousin of the
      Herfindahl index.
    """
    )
    return


if __name__ == "__main__":
    app.run()
