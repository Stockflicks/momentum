# Part 1: Libraries & Initialization

import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask

currencies, t_start, t_end = ["CAN", "JPN", "SWE", "USD", "GBR", "EUR"], 1999, 2019
best_trade, all_scores = pd.DataFrame(), pd.DataFrame()
lr, xr = pd.read_csv("lending_rates.csv"), pd.read_csv("all_exchange_rates.csv")


# Part 2: Useful Functions

def getScore(lr1, lr2, xr0, xr1): return ((1 + lr2) * xr0 / xr1) - (1 + lr1)
def getLR(currency, time): return lr[currency][time] / 100
def getXR(cur1, cur2, time):
    if cur1 == "USD": return xr[cur2][time]
    else: return 1 / xr[cur1][time] if cur2 == "USD" else xr[cur2][time] / xr[cur1][time]


# Part 3: Find the Best Trade

def getBestTrade(time, local_bt):
    max_i, max_j, max_score, pct_return, scores = "", "", 0, 0, []
    for i in currencies:
        for j in currencies:
            if i == j: continue
            score = getScore(getLR(i, time - t_start), getLR(j, time - t_start), 1, 1)
            scores.append([i, j, round(score * 100, 2)])
            if score > max_score:
                max_i, max_j, max_score = i, j, score
                pct_return = getScore(getLR(i, time - t_start), getLR(j, time - t_start),
                                      getXR(i, j, time - t_start), getXR(i, j, time - t_start + 1))
    all_scores[time] = scores
    return local_bt.append(pd.DataFrame([[time, max_i, max_j, pct_return * 100]],
                                        columns=["Year", "Short", "Long", "Return"]), ignore_index=True)


# Part 4: Results Summarization

def genDataStr():
    data_str = "<table border=1><tr><th>Year</th><th>Short</th><th>Long</th><th>% Return</th></tr>"
    for time in range(t_start, t_end):
        data_str += "<tr>"
        this_row = best_trade.loc[best_trade["Year"] == time]
        for attr in ["Year", "Short", "Long", "Return"]:
            data_str += "<td>" + str(round(this_row[attr].item(), 2)) + "%</td>" \
                if attr == "Return" else "<td>" + str(this_row[attr].item()) + "</td>"
        data_str += "</tr>"
    return data_str + "</table><br>"


def genAllScoreStr():
    all_str = ""
    for time in range(t_start, t_end):
        all_str += str(time) + " Information Set<table border=1>"
        for element in all_scores[time]:
            all_str += "<tr>"
            count = 0
            for element_2 in element:
                all_str += "<td>" + str(element_2) + "</td>" \
                    if count != 2 else "<td>" + str(element_2) + "%</td>"
                count += 1
            all_str += "</tr>"
        all_str += "</table><br>"
    return all_str


year_list = []
for t in range(t_start, t_end):
    best_trade = getBestTrade(t, best_trade)
    if not t % 3: year_list.append(t)
web_content = "<html>\n<head><title>Foreign Exchange Carry Trade" \
              "</title></head>\n<body><center><font size=6>" \
              "<b>Foreign Exchange Carry Trade</b></font>" \
              "<img src='static/ypr.png' class='center' " \
              "style='display: block; width: 40%;'>\n" + genDataStr()\
              + genAllScoreStr() + "</center></body>\n</html>"
plt.plot(best_trade["Year"], best_trade["Return"])
plt.axhline(y=0, color='grey', linestyle='-')
plt.xticks(year_list)
plt.title("Yearly Percentage Returns")
plt.savefig("static/ypr.png")
application = Flask(__name__)
application.add_url_rule('/', 'index', (lambda: web_content))
if __name__ == "__main__": application.run(debug=True)
