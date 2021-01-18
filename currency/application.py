# VIDEO 2: IMPORT LIBRARIES & DEFINE CONSTANTS

import pandas as pd
import math
import matplotlib.pyplot as plt
from flask import Flask

currencies = ["USD", "JPN", "CAN", "SWE", "GBR", "EUR"]
start_year, start_month = 2001, 1
end_year, end_month = 2020, 11
summary, all_cp, all_dt = [], [], []
xr = dict()

for current_year in range(start_year, end_year + 1):
    for current_month in range(1, 13):
        if current_year == start_year and current_month < start_month:
            continue
        month_str = str(current_month) if len(str(current_month)) == 2 else "0" + str(current_month)
        all_dt.append(str(current_year) + month_str)
        if current_year == end_year and current_month == end_month:
            break

# VIDEO 3: PREPARE THE DATA & READ CSVs

lr = pd.read_csv("data/lending_rates.csv")
for currency in currencies:
    if currency == "USD": continue
    xr[currency] = pd.read_csv("data/" + currency + "_monthly.csv")


# VIDEO 4: DEFINE FUNCTIONS I


# Get the lending rate of a given currency in a given time
def getLendingRate(currency, year, month):
    lr2 = lr.loc[lr["Year"] == year]
    return math.pow(lr2.loc[lr2["Month"] == month][currency].item() / 100 + 1, 1 / 12) - 1


# Get the exchange rate of two given currencies in a given time
def getExchangeRate(currency_1, currency_2, year, month):
    if currency_1 == currency_2: return 1
    if currency_1 == "USD":
        xr2 = xr[currency_2].loc[xr[currency_2]["YEAR"] == year]
        return xr2.loc[xr2["MONTH"] == month][currency_2].item()
    xr1 = xr[currency_1].loc[xr[currency_1]["YEAR"] == year]
    if currency_2 == "USD":
        return 1 / xr1.loc[xr1["MONTH"] == month][currency_1].item()
    else:
        xr2 = xr[currency_2].loc[xr[currency_2]["YEAR"] == year]
        return xr2.loc[xr2["MONTH"] == month].item() / xr1.loc[xr1["MONTH"] == month].item()


# VIDEO 5: DEFINE FUNCTIONS II


# Add one month to a given year and month
def addMonth(year, month):
    return [year, month + 1] if month != 12 else [year + 1, 1]


# Calculate the growth rate of a given currency in a given time
def growth(currency, year, month):
    return getLendingRate(currency, year, month) - getLendingRate(currency, year - 1, month)


# Get the currency that go short in a given time
def getGoShortCurrency(year, month):
    short_currency, short_growth = "USD", growth("USD", year, month)
    for currency in currencies:
        if growth(currency, year, month) < short_growth:
            short_currency, short_growth = currency, growth(currency, year, month)
    return [short_currency, short_growth]


# Get the currency that go long in a given time
def getGoLongCurrency(year, month):
    long_currency, long_growth = "USD", growth("USD", year, month)
    for currency in currencies:
        if growth(currency, year, month) > long_growth:
            long_currency, long_growth = currency, growth(currency, year, month)
    return [long_currency, long_growth]


# VIDEO 6: THE MONTHLY REBALANCE FUNCTION


def monthlyRebalance(year, month, cumulative_profit):
    short, long = getGoShortCurrency(year, month), getGoLongCurrency(year, month)
    short_lr, long_lr = getLendingRate(short[0], year, month), getLendingRate(long[0], year, month)
    borrow_xr0 = getExchangeRate("USD", short[0], year, month)
    lend_xr0 = getExchangeRate("USD", long[0], year, month)
    borrow_xr1 = getExchangeRate(short[0], "USD", addMonth(year, month)[0], addMonth(year, month)[1])
    lend_xr1 = getExchangeRate(long[0], "USD", addMonth(year, month)[0], addMonth(year, month)[1])
    borrow_amount, lend_amount = 1000000 * borrow_xr0, (1000000 + cumulative_profit) * lend_xr0
    short_future, long_future = borrow_amount * (1 + short_lr) * borrow_xr1, lend_amount * (1 + long_lr) * lend_xr1
    new_cumulative_profit = long_future - short_future
    all_cp.append(new_cumulative_profit)
    ncp_rounded = round(new_cumulative_profit, 4)
    change_str = str(ncp_rounded) if ncp_rounded < 0 else "+" + str(ncp_rounded)
    summary.append([year, month, [short[0], round(short[1], 6)], round(100 * short_lr, 2), round(borrow_xr0, 6),
                    round(1 / borrow_xr1, 6), round(short_future, 2), [long[0], round(long[1], 6)],
                    round(lend_amount, 2),
                    round(100 * long_lr, 2), round(lend_xr0, 6), round(1 / lend_xr1, 6), round(long_future, 6),
                    change_str])
    if year == end_year and month == end_month:
        return
    new_year = addMonth(year, month)[0]
    new_month = addMonth(year, month)[1]
    monthlyRebalance(new_year, new_month, new_cumulative_profit)


monthlyRebalance(start_year, start_month, 0)

# VIDEO 7: DEMONSTRATE THE RESULTS IN A FLASK WEB APP

plot_df = pd.DataFrame({"Date": all_dt, "Cumulative Profit": all_cp})
plot_df["Date"] = pd.to_datetime(plot_df["Date"], format="%Y%m")
plot_df = plot_df.set_index("Date")
plot_df.index = pd.to_datetime(plot_df.index, format="%Y-%m-%c")
plot_df.plot(figsize=(10, 5))
plt.title('Cumulative Profit (USD) (' + str(start_year) + ' to ' + str(end_year) + ')')
plt.savefig('static/line_cp.png')


def summary_str():
    ret_str = '''<table border=1 align=center><tr><th>Year</th><th>Month</th><th>Lend Amt (Lend Cur)</th>
    <th>Borrow</th><th>Borrow IR</th><th>Borrow XR0</th><th>Borrow XR1</th><th>Borrow FV (USD)</th>
    <th>Lend</th><th>Lend IR</th><th>Lend XR0</th><th>Lend XR1</th><th>Lend FV (USD)</th>
    <th>Cum. Profit (USD)</th></tr>'''
    for row in summary:
        ret_str += "<tr>"
        for element in row:
            ret_str += "<td>" + str(element) + "</td>"
        ret_str += "</tr>"
    ret_str += "</table>"
    return ret_str


html_content_str = "<html>\n<head> <title>Currency Momentum </title>" + \
                   "</head>\n<body><center><font size=6><b>Currency Momentum" + \
                   "</b></font></center><br><img src='static/line_cp.png' class='center'" \
                   " style=' display: block; margin-left: auto; margin-right: auto; width: 70%;'>\n" \
                   + summary_str() + "</body>\n</html>"

application = Flask(__name__)
application.add_url_rule('/', 'index', (lambda: html_content_str))
if __name__ == "__main__": application.run()
