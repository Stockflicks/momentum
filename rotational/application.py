
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, render_template

def Rotationalmomentum_12_month(file_xlsx, capital):
    close_price_etf_df = pd.read_excel(file_xlsx)
    close_price_etf_df.columns = close_price_etf_df.iloc[0]
    close_price_etf_df = close_price_etf_df.loc[423:]
    close_price_etf_df = close_price_etf_df.set_index('Date')
    daily_return_etf_df = close_price_etf_df.pct_change(1) # calculate daily return
    daily_return_etf_df = daily_return_etf_df.fillna(method='bfill') # make sure no empty data
    daily_return_etf_df = daily_return_etf_df + 1
    monthly_total_return_df = daily_return_etf_df.resample('M').sum() # calculate monthly total return
    rolling_total_return_month_12_df = monthly_total_return_df.rolling(12).sum() # calculate rolling total return for 12 months
    rolling_total_return_month_12_df = rolling_total_return_month_12_df[11:]
    
    ans_list = [capital] # create a list and put monthly return inside
    time_list = [rolling_total_return_month_12_df.index[0]] # create a time list to record the time
    # Main Algorithm
    for i in range(len(rolling_total_return_month_12_df)-1):
        updated_capital = 0
        for j in range(3):
            top_etf = rolling_total_return_month_12_df.iloc[i].sort_values(ascending=False).index[j]
            str_year = str(rolling_total_return_month_12_df.iloc[i+1].name.year)
            int_month = rolling_total_return_month_12_df.iloc[i+1].name.month
            temp_df = daily_return_etf_df[str_year][(daily_return_etf_df[str_year].index.month == int_month)][top_etf]
            money_per_etf = (capital/3)
            for k in range(len(temp_df)):
                money_per_etf = money_per_etf * temp_df.iloc[k]
            updated_capital = money_per_etf + updated_capital
        
        time_list.append(temp_df.index[-1])
        ans_list.append(updated_capital)
        capital = updated_capital
    cum_df = pd.DataFrame({'monthly_return':ans_list},time_list)

    return cum_df
monthly_return_df = Rotationalmomentum_12_month("Rotational_system.xls", 10000)
monthly_return_df.plot(figsize=(20,10))
plt.savefig('static/return.png')

def table_str():
    ret_str = "<table border=1>"
    for i in range(len(monthly_return_df)):
        ret_str +=  "<tr><td>" + str(monthly_return_df.index[i]) + "</td><td>" + \
                    str(monthly_return_df['monthly_return'][i]) + "</td>"
    ret_str += "</tr></table>"
    return ret_str

html_content_str = "<html>\n<head> <title> Momentum </title>" +\
                   "</head>\n<body><center><font size=6><b> Momentum " + \
                   "</b></font></center><br>\n<font size=4><b>" +\
                   "</b></font><br><br><b></b><img src='static/return.png' class='center' style=' display: " \
                   "block; margin-left: auto; margin-right: auto; width: 45%;'><center>" + table_str() + \
                   "</center></body>\n</html>"

application = Flask(__name__)
application.add_url_rule('/', 'index', (lambda: html_content_str))
if __name__ == "__main__": application.run(debug = True)

