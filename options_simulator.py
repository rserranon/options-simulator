import numpy as np
import plotly.graph_objects as go
import panel as pn
import pandas as pd

# Enable Panel extension
pn.extension()

# ─────────── 1. CREATE INPUT WIDGETS ───────────
strike_price_input = pn.widgets.FloatInput(name="Strike Price ($)", value=420.0, step=1.0, width=200)
premium_input = pn.widgets.FloatInput(name="Premium ($ per share)", value=10.0, step=0.1, width=200)
basis_input = pn.widgets.FloatInput(name="Cost Basis ($)", value=420.0, step=1.0, width=200)
contract_size_input = pn.widgets.IntInput(name="Contract Size (shares)", value=100, step=1, width=200)
per_share_input = pn.widgets.Checkbox(name="Per Share", value=True)
show_profit_input = pn.widgets.Checkbox(name="Show Profit/Loss", value=True)
strategies_input = pn.widgets.MultiChoice(
    name="Strategies to Plot",
    value=["Long Stock", "Covered Call", "Cash Secured Put"],
    options=["Long Stock", "Naked Short Call", "Covered Call", "Naked Short Put", "Cash Secured Put"],
    width=200
)

# ─────────── 2. FUNCTION TO GENERATE PLOT ───────────
def create_payoff_plot(strike_price, premium, basis, contract_size, per_share, show_profit, strategies_to_plot):
    # Stock price grid
    stock_prices = np.arange(strike_price * 0.75, strike_price * 1.25 + 0.01, 1.0)

    # Payoff calculations (Per Share)
    strategies = {}
    if "Long Stock" in strategies_to_plot:
        strategies["Long Stock"] = stock_prices.copy()
    if "Naked Short Call" in strategies_to_plot:
        strategies["Naked Short Call"] = np.where(
            stock_prices <= strike_price,
            premium,
            premium - (stock_prices - strike_price),
        )
    if "Covered Call" in strategies_to_plot:
        if "Long Stock" not in strategies:
            strategies["Long Stock"] = stock_prices.copy()
        if "Naked Short Call" not in strategies:
            strategies["Naked Short Call"] = np.where(
                stock_prices <= strike_price,
                premium,
                premium - (stock_prices - strike_price),
            )
        strategies["Covered Call"] = strategies["Long Stock"] + strategies["Naked Short Call"]
    if "Naked Short Put" in strategies_to_plot:
        strategies["Naked Short Put"] = np.where(
            stock_prices >= strike_price,
            premium,
            premium - (strike_price - stock_prices),
        )
    if "Cash Secured Put" in strategies_to_plot:
        strategies["Cash Secured Put"] = np.where(
            stock_prices >= strike_price,
            premium,
            premium - (strike_price - stock_prices),
        )

    # Convert to profit if needed
    if show_profit:
        if "Long Stock" in strategies:
            strategies["Long Stock"] -= basis
        if "Covered Call" in strategies:
            strategies["Covered Call"] -= basis

    # Scale up to contract if needed
    scale = 1 if per_share else contract_size
    for strategy in strategies:
        strategies[strategy] *= scale

    # Create Plotly figure
    fig = go.Figure()
    for strategy, payoff in strategies.items():
        fig.add_trace(go.Scatter(x=stock_prices, y=payoff, name=strategy, line=dict(width=2)))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    # Set labels and title
    ylabel = "Profit / Loss" if show_profit else "Position Value"
    ylabel += " ($ per share)" if per_share else " ($ per 100-share contract)"
    title_mode = "P/L" if show_profit else "Value"
    title_scale = "Per Share" if per_share else "Per Contract"
    fig.update_layout(
        title={
            'text': f"Pay-off at Expiration ({title_mode}, {title_scale})<br>Strike = ${strike_price:.2f}, Premium = ${premium:.2f}, Cost Basis = ${basis:.2f}",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title="Stock Price at Expiration ($)",
        yaxis_title=ylabel,
        showlegend=True,
        width=600,  # Constrain plot width
        height=400,  # Constrain plot height
        margin=dict(l=50, r=50, t=100, b=50),  # Adjust margins for better fit
        font=dict(size=10),  # Smaller font for better scaling
        xaxis=dict(tickformat=",.0f"),
        yaxis=dict(tickformat=",.0f")
    )
    
    return fig

# ─────────── 3. CREATE INTERACTIVE DASHBOARD ───────────
@pn.depends(
    strike_price_input.param.value,
    premium_input.param.value,
    basis_input.param.value,
    contract_size_input.param.value,
    per_share_input.param.value,
    show_profit_input.param.value,
    strategies_input.param.value
)
def update_plot(strike_price, premium, basis, contract_size, per_share, show_profit, strategies_to_plot):
    if not strategies_to_plot:
        return pn.pane.Markdown("Please select at least one strategy to plot.")
    try:
        if strike_price <= 0 or premium < 0 or basis < 0 or contract_size <= 0:
            return pn.pane.Markdown("All inputs must be positive.")
        fig = create_payoff_plot(strike_price, premium, basis, contract_size, per_share, show_profit, strategies_to_plot)
        return pn.pane.Plotly(fig, width=600, height=400)  # Constrain pane size
    except Exception as e:
        return pn.pane.Markdown(f"Error: {str(e)}")

input_pane = pn.Column(
    pn.pane.Markdown("## Options Payoff Simulator"),
    strike_price_input,
    premium_input,
    basis_input,
    contract_size_input,
    per_share_input,
    show_profit_input,
    strategies_input,
    width=250,  # Constrain input pane width
    height=400,  # Explicit height to resolve warnings
    sizing_mode="fixed"  # Prevent input pane from stretching
)

dashboard = pn.Row(
    input_pane,
    pn.Spacer(width=20),
    update_plot,
    sizing_mode="scale_both",  # Scale to fit available space
    max_width=1000,  # Limit total dashboard width
    max_height=600,  # Limit total dashboard height
    css_classes=["panel-responsive"]  # Optional: for custom styling
)

# ─────────── 5. RUN THE DASHBOARD ───────────
if __name__ == "__main__":
    dashboard.show()
