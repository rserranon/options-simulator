# ▒▒▒  Covered–call vs naked–call vs long–stock payoff chart  ▒▒▒

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# ─────────── 1. INPUT PARAMETERS ───────────
strike_price = 420  # $ / share
premium = 10  # $ / share received
basis = 420  # cost basis of the stock

contract_size = 100  # shares per standard option
per_share = True  # True → $/share, False → $/contract
show_profit = True  # True → P/L,   False → mark-to-market value

# ─────────── 2. ABSOLUTE STOCK-PRICE GRID ───────────
stock_prices = np.arange(
    strike_price * 0.75,  # 315 …
    strike_price * 1.25 + 0.01,
    1.0,
)  # … 525

print(f"Stock price grid: {stock_prices}")
# ─────────── 3. PAY-OFFS  (always start PER SHARE) ───────────
long_stock = stock_prices.copy()  # Create explicit copy
naked_short_call = np.where(
    stock_prices <= strike_price,
    premium,  # OTM → keep premium
    premium - (stock_prices - strike_price),  # ITM → premium – intrinsic
)
covered_call = long_stock + naked_short_call

naked_short_put = np.where(
    stock_prices >= strike_price,
    premium,  # OTM → keep premium
    # ITM → premium - (strike - stock_price)
    premium - (strike_price - stock_prices),
)
# ─────────── 4. CONVERT “VALUE” → “PROFIT” IF NEEDED ───────────
if show_profit:
    long_stock -= basis
    covered_call -= basis  # covered-call owns the same shares
    # naked_short_call and naked_short_put already show profit (premium received minus intrinsic loss)
# ─────────── 5. SCALE UP TO CONTRACT IF NEEDED ───────────
scale = 1 if per_share else contract_size
long_stock *= scale
naked_short_call *= scale
naked_short_put *= scale
covered_call *= scale

# ─────────── 6. PLOT ───────────
plt.rcParams["figure.figsize"] = (12, 8)
plt.rcParams.update({"font.size": 16})
plt.plot(stock_prices, long_stock, label="Long Stock", lw=3)
plt.plot(stock_prices, naked_short_call, label="Naked Short Call", lw=3)
plt.plot(stock_prices, covered_call, label="Covered Call", lw=3)
plt.plot(stock_prices, naked_short_put, label="Naked Short Put", lw=3)

plt.axhline(0, color="gray", lw=1, ls="--")

ylabel = "Profit / Loss" if show_profit else "Position Value"
ylabel += " ($ per share)" if per_share else " ($ per 100-share contract)"
plt.ylabel(ylabel)
plt.xlabel("Stock Price at Expiration ($)")  # ← real prices, 315 – 525

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
