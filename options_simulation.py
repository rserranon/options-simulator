# ▒▒▒ Covered–call vs naked–call vs long–stock payoff chart ▒▒▒

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# ─────────── 1. INPUT PARAMETERS ───────────
strike_price = 420  # $ / share
premium = 10  # $ / share received
basis = 420  # cost basis of the stock
contract_size = 100  # shares per standard option
per_share = True  # True → $/share, False → $/contract
show_profit = True  # True → P/L, False → mark-to-market value

# ─────────── 2. STRATEGY SELECTION ───────────
# Choose which strategies to plot by including them in this list
strategies_to_plot = [
    "Long Stock",
    # "Naked Short Call",
    "Covered Call",
    # "Naked Short Put",
    # "Cash Secured Put",
    # Modify this list to select strategies,
    # e.g., ["Long Stock", "Covered Call"]
]

# ─────────── 3. ABSOLUTE STOCK-PRICE GRID ───────────
stock_prices = np.arange(
    strike_price * 0.75,  # 315 …
    strike_price * 1.25 + 0.01,
    1.0,
)  # … 525

# ─────────── 4. PAY-OFF CALCULATIONS (Per Share) ───────────
# Dictionary to store strategy calculations
strategies = {}
if "Long Stock" in strategies_to_plot:
    strategies["Long Stock"] = stock_prices.copy()  # Explicit copy
if "Naked Short Call" in strategies_to_plot:
    strategies["Naked Short Call"] = np.where(
        stock_prices <= strike_price,
        premium,  # OTM → keep premium
        premium - (stock_prices - strike_price),  # ITM → premium – intrinsic
    )
if "Covered Call" in strategies_to_plot:
    # Requires Long Stock and Naked Short Call
    if "Long Stock" not in strategies:
        strategies["Long Stock"] = stock_prices.copy()
    if "Naked Short Call" not in strategies:
        strategies["Naked Short Call"] = np.where(
            stock_prices <= strike_price,
            premium,
            premium - (stock_prices - strike_price),
        )
    strategies["Covered Call"] = (
        strategies["Long Stock"] + strategies["Naked Short Call"]
    )
if "Naked Short Put" in strategies_to_plot:
    strategies["Naked Short Put"] = np.where(
        stock_prices >= strike_price,
        premium,  # OTM → keep premium
        premium - (strike_price - stock_prices),  # ITM → premium – intrinsic
    )
if "Cash Secured Put" in strategies_to_plot:
    strategies["Cash Secured Put"] = np.where(
        stock_prices >= strike_price,
        premium,  # OTM → keep premium
        premium - (strike_price - stock_prices),  # ITM → premium – intrinsic
    )

print(f"\nStrategies: {strategies.keys()}\n")

# ─────────── 5. CONVERT “VALUE” → “PROFIT” IF NEEDED ───────────
if show_profit:
    if "Long Stock" in strategies:
        strategies["Long Stock"] -= basis
    if "Covered Call" in strategies:
        # Covered-call owns the same shares
        strategies["Covered Call"] -= basis
    # Naked Short Call and Naked Short Put already show profit

# ─────────── 6. SCALE UP TO CONTRACT IF NEEDED ───────────
scale = 1 if per_share else contract_size
for strategy in strategies:
    strategies[strategy] *= scale

# ─────────── 7. PLOT ───────────
plt.rcParams["figure.figsize"] = (12, 8)
plt.rcParams.update({"font.size": 16})

# Plot only selected strategies
for strategy, payoff in strategies.items():
    plt.plot(stock_prices, payoff, label=strategy, lw=3)

plt.axhline(0, color="gray", lw=1, ls="--")

ylabel = "Profit / Loss" if show_profit else "Position Value"
ylabel += " ($ per share)" if per_share else " ($ per 100-share contract)"
plt.ylabel(ylabel)
plt.xlabel("Stock Price at Expiration ($)")
title_mode = "P/L" if show_profit else "Value"
title_scale = "Per Share" if per_share else "Per Contract"
plt.title(
    f"Pay-off at Expiration ({title_mode}, {title_scale})\n"
    f"Strike = ${strike_price}, Premium = ${premium}, Cost Basis = ${basis}"
)

plt.grid(True)
plt.legend()
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:,.0f}"))
plt.tight_layout()
plt.show()
