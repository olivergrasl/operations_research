import marimo

__generated_with = "0.24.2"
app = marimo.App(app_title="Beergame Policy Experiments")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import os

    import altair as alt
    import pandas as pd
    from BPTK_Py import bptk as BPTK

    return BPTK, alt, os, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Beergame Policy Experiments

    The Beer Distribution Game is a four-stage supply chain — retailer, wholesaler,
    distributor and brewery — in which each stage sees only the orders of its own
    customer and the deliveries of its own supplier. Orders and deliveries take
    time to move along the chain, and that delay is enough to turn a single step
    in consumer demand into wild swings further upstream: the *bullwhip effect*.

    This notebook runs the System Dynamics model of the game (built with
    [BPTK-Py](https://bptk.transentis.com), source in `src/beergame/`) through a
    series of ordering policies defined in `scenarios/beergame.json`, and compares
    their order behaviour, surplus (inventory minus backorder) and cost.
    """
    )
    return


@app.cell
def _(BPTK, mo, os):
    # BPTK resolves the model named in scenarios/beergame.json ("src.beergame...")
    # relative to the working directory, and only when the scenario storage is given
    # as a relative path - an absolute path turns into an unimportable module name.
    # So run from the repository root, wherever marimo was started.
    os.chdir(mo.notebook_dir().parent)

    bptk = BPTK(
        # WARN would print a line for every scenario that overrides a graphical
        # function's points - expected here, not worth reading.
        loglevel="ERROR",
        configuration={
            "scenario_storage": "scenarios/",
            # Print errors into the cell output instead of writing bptk_py.log.
            "log_modes": ["print"],
            # The file monitors watch for model edits in a long-running Jupyter
            # session; here they only leave threads behind that keep an export alive.
            "set_scenario_monitor": False,
            "set_model_monitor": False,
        },
    )
    return (bptk,)


@app.cell
def _(alt, bptk, mo, pd):
    # Categorical slots of the house palette, in fixed order. Colour follows the
    # entity, so a stage keeps its colour in every chart it appears in.
    PALETTE = [
        "#2a78d6",
        "#eb6834",
        "#1baf7a",
        "#eda100",
        "#e87ba4",
        "#008300",
        "#4a3aa7",
        "#e34948",
    ]

    STAGES = ["brewery", "distributor", "wholesaler", "retailer"]

    def simulate(scenarios, equations):
        """Run scenarios and return a wide frame indexed by week.

        With one scenario the columns are the equation names; with several, BPTK
        prefixes them as "beergame_<scenario>_<equation>".
        """
        df = bptk.run_scenarios(
            scenario_managers=["beergame"], scenarios=scenarios, equations=equations
        )
        if df is None:
            raise RuntimeError(f"BPTK returned no results for {scenarios} - see the log above")
        return df.rename_axis("Week")

    def area_chart(wide, title, y_title, dashed=()):
        """Overlapping (not stacked) areas, as in the BPTK plots this replaces.

        Each series is a 2px line over a light wash; `dashed` names series that are
        targets rather than results. A hover rule shows every value for a week.
        """
        series = list(wide.columns)
        colors = PALETTE[: len(series)]
        data = wide.reset_index()
        long = data.melt("Week", var_name="Series", value_name="Value")

        x = alt.X("Week:Q", title="Week", scale=alt.Scale(nice=False, padding=0))
        y = alt.Y("Value:Q", title=y_title, stack=None)
        color = alt.Color(
            "Series:N",
            title=None,
            scale=alt.Scale(domain=series, range=colors),
            sort=series,
            # Legend swatches drawn as solid strokes: by default they take the area's wash.
            legend=alt.Legend(
                orient="top", offset=4, symbolType="stroke", symbolOpacity=1, symbolStrokeWidth=2
            )
            if len(series) > 1
            else None,
        )
        base = alt.Chart(long).encode(x=x, y=y, color=color)

        areas = base.mark_area(opacity=0.1, interpolate="linear")
        lines = base.mark_line(strokeWidth=2).encode(
            strokeDash=alt.StrokeDash(
                "Series:N",
                scale=alt.Scale(
                    domain=series, range=[[5, 3] if s in dashed else [1, 0] for s in series]
                ),
                legend=None,
            )
        )

        hover = alt.selection_point(
            fields=["Week"], nearest=True, on="pointerover", empty=False, clear="pointerout"
        )
        rule = (
            alt.Chart(data)
            .mark_rule(color="#8a8a85", strokeWidth=1)
            .encode(
                x=x,
                opacity=alt.condition(hover, alt.value(0.6), alt.value(0.0)),
                tooltip=[alt.Tooltip("Week:Q", format=".0f")]
                + [alt.Tooltip(f"{s}:Q", title=s, format=",.0f") for s in series],
            )
            .add_params(hover)
        )

        chart = (
            alt.layer(areas, lines, rule)
            .properties(width="container", height=300, title=title)
            .configure_axis(grid=True, gridOpacity=0.15, domainOpacity=0.3, tickOpacity=0.3)
            .configure_view(stroke=None)
        )
        return mo.ui.altair_chart(chart, chart_selection=False, legend_selection=False)

    def order_behavior(scenario, title, consumer="retailer.incomingOrder"):
        """Orders each stage sends upstream, against what the consumer orders."""
        equations = [f"{s}.sendingOrders" for s in STAGES] + [consumer]
        wide = simulate([scenario], equations)
        wide.columns = [s.capitalize() for s in STAGES] + ["Consumer"]
        return area_chart(wide, title, "Beer ordered")

    def surplus(scenario, title):
        """Inventory minus backorder at every stage."""
        wide = simulate([scenario], [f"{s}.surplus" for s in STAGES])
        wide.columns = [s.capitalize() for s in STAGES]
        return area_chart(wide, title, "Surplus (units of beer)")

    def retailer_cost(scenario, title):
        wide = simulate(
            [scenario],
            ["performanceControlling.retailerCostAcc", "policySettings.targetRetailerCost"],
        )
        wide.columns = ["Retailer Cost", "Target Retailer Cost"]
        return area_chart(wide, title, "Accumulated cost", dashed={"Target Retailer Cost"})

    def supply_chain_cost(scenario, title):
        wide = simulate(
            [scenario],
            ["performanceControlling.supplyChainCostAcc", "policySettings.targetSupplyChainCost"],
        )
        wide.columns = ["Supply Chain Cost", "Target Supply Chain Cost"]
        return area_chart(wide, title, "Accumulated cost", dashed={"Target Supply Chain Cost"})

    RETAILER_DETAILS = {
        "sendingOrders": "Order",
        "openOrders": "Open Orders",
        "incomingDelivery": "Incoming Delivery",
        "inventory": "Inventory",
        "outgoingDelivery": "Outgoing Delivery",
        "incomingOrder": "Incoming Order",
        "backorder": "Backorder",
        "sophisticatedOrderDecision": "Target Order",
    }

    def retailer_details(scenario, title, incoming_order="incomingOrder"):
        """Every flow and stock at the retailer, as a chart and as the numbers."""
        # The steady-state scenario reads the consumer's orders from customerOrder.
        names = {
            (incoming_order if k == "incomingOrder" else k): v for k, v in RETAILER_DETAILS.items()
        }
        wide = simulate([scenario], [f"retailer.{e}" for e in names])
        wide.columns = list(names.values())
        return mo.ui.tabs(
            {
                "Chart": area_chart(wide, title, "Units of beer"),
                "Table": mo.ui.table(
                    wide.reset_index().astype({"Week": int}), selection=None, pagination=False
                ),
            }
        )

    def policy_charts(scenario, name):
        """The four standard views of a policy, stacked."""
        return mo.vstack(
            [
                order_behavior(scenario, f"{name} - Order Behavior"),
                surplus(scenario, f"{name} - Surplus"),
                retailer_cost(scenario, f"{name} - Retailer Cost"),
                supply_chain_cost(scenario, f"{name} - Supply Chain Cost"),
            ]
        )

    return (
        area_chart,
        order_behavior,
        policy_charts,
        retailer_cost,
        retailer_details,
        simulate,
        supply_chain_cost,
        surplus,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Steady State""")
    return


@app.cell
def _(retailer_details):
    retailer_details("steady_state", "Steady State", incoming_order="customerOrder")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 'Worst Case' Scenario""")
    return


@app.cell
def _(mo, order_behavior, retailer_cost, simulate, area_chart, supply_chain_cost, surplus):
    _consumer = simulate(["typical"], ["retailer.customerOrder"])
    _consumer.columns = ["Consumer Orders"]

    mo.vstack(
        [
            order_behavior(
                "typical", "'Worst Case' Order Behavior", consumer="retailer.customerOrder"
            ),
            area_chart(_consumer, "Consumer Order Behaviour Only Changes Once", "Beer ordered"),
            surplus("typical", "'Worst Case' Surplus"),
            retailer_cost("typical", "'Worst Case' Retailer Cost"),
            supply_chain_cost("typical", "'Worst Case' Supply Chain Cost"),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Ignore Backorders""")
    return


@app.cell
def _(mo, order_behavior, retailer_cost, retailer_details, surplus):
    mo.vstack(
        [
            order_behavior("ignore_backorders", "Ignore Backorders - Order Behavior"),
            surplus("ignore_backorders", "Ignore Backorders - Surplus"),
            retailer_details("ignore_backorders", "Ignore Backorders - Details"),
            retailer_cost("ignore_backorders", "Ignore Backorders - Retailer Cost"),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Ignore Backorders, But Include Supply Line""")
    return


@app.cell
def _(
    area_chart,
    mo,
    order_behavior,
    retailer_cost,
    retailer_details,
    simulate,
    supply_chain_cost,
    surplus,
):
    _comparison = simulate(["ignore_backorders", "include_supply_line"], ["retailer.surplus"])
    _comparison = _comparison.rename(
        columns={
            "beergame_ignore_backorders_retailer.surplus": "Ignore Backorders",
            "beergame_include_supply_line_retailer.surplus": "Include Supply Line",
        }
    )[["Ignore Backorders", "Include Supply Line"]]

    mo.vstack(
        [
            order_behavior("include_supply_line", "Include Supply Line - Order Behavior"),
            area_chart(_comparison, "Comparison of Retailer Surplus", "Surplus (units of beer)"),
            surplus("include_supply_line", "Include Supply Line - Surplus"),
            retailer_details("include_supply_line", "Include Supply Line - 1 Week Adjustment Time"),
            retailer_cost("include_supply_line", "Include Supply Line - Retailer Cost"),
            supply_chain_cost("include_supply_line", "Include Supply Line - Supply Chain Cost"),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Remember Open Orders""")
    return


@app.cell
def _(policy_charts):
    policy_charts("remember_open_orders", "Remember Open Orders")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Eight Weeks Inventory Adjustment Time""")
    return


@app.cell
def _(mo, order_behavior, retailer_cost, retailer_details, supply_chain_cost, surplus):
    _name = "Inventory Adjustment Time 8 Weeks"
    mo.vstack(
        [
            order_behavior("inventory_adjustment_time_8", f"{_name} - Order Behavior"),
            surplus("inventory_adjustment_time_8", f"{_name} - Surplus"),
            retailer_details("inventory_adjustment_time_8", f"{_name} - Details"),
            retailer_cost("inventory_adjustment_time_8", f"{_name} - Retailer Cost"),
            supply_chain_cost("inventory_adjustment_time_8", f"{_name} - Supply Chain Cost"),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Zero Inventory Target - 8 Weeks Adjustment Time""")
    return


@app.cell
def _(policy_charts):
    policy_charts("zero_inventory_target_8w", "Zero Inventory Target")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Improve Communication""")
    return


@app.cell
def _(policy_charts):
    policy_charts("improve_communication", "Improve Communication")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Perfect Forecast""")
    return


@app.cell
def _(policy_charts):
    policy_charts("perfect_forecast", "Perfect Forecast")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Variable Demand""")
    return


@app.cell
def _(policy_charts):
    policy_charts("variable_demand", "Variable Demand")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Variable Demand: Perfect Forecast""")
    return


@app.cell
def _(policy_charts):
    policy_charts("variable_demand_perfect_forecast", "Variable Demand Perfect Forecast")
    return


if __name__ == "__main__":
    app.run()
