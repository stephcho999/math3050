import pandas as pd
import yfinance as yf

xlv_df = yf.Ticker('XLV').history(period='max')

def getprice(df, date):
    if date in df.index:
        return df.loc[date, 'Close']
    else:
        pass

def getmacd(df, date):
    if date in df.index:
        return df.loc[date, 'MACD']
    else:
        return False

def macd_target(df_list, date):
    target_list = []
    for df in df_list:
        val = getmacd(df, date)
        if val == True:
            target_list.append(df)
    return target_list

def get_next_date(curr_date, days, df):
    for i in range(len(df.index)):
        if df.index[i] == curr_date:
            break
    return df.index[i+days]

def one_cycle_buy_sell(funds, fund_df, df_list, date, days):
    stock_purchased = []
    if len(df_list) != 0:
        fund_per_stock = funds/len(df_list)
    else:
        fund_series = pd.Series({'date': date, 'curr_fund': funds, 'num_stocks': len(df_list)})
        fund_df = fund_df.append(fund_series, ignore_index=True)
        return fund_df, funds

    #buy
    for df in df_list:
        stock_price = getprice(df, date)
        num_purchased = fund_per_stock / stock_price
        stock_purchased.append(num_purchased)
        funds -= num_purchased * stock_price

    #sell
    date = get_next_date(date, days, df=xlv_df)
    for i in range(len(df_list)):
        stock_price = getprice(df_list[i], date)
        funds += stock_price * stock_purchased[i]

    fund_series = pd.Series({'date': date, 'curr_fund': funds, 'num_stocks': len(df_list)})
    fund_df = fund_df.append(fund_series, ignore_index=True)

    return fund_df, funds

def simulate(funds, df_list, start, days, cycle):
    date = start
    fund_df = pd.DataFrame(columns=['date', 'curr_fund', 'num_stocks'])
    fund_series = pd.Series({'date': date, 'curr_fund': funds, 'num_stocks': 0})
    fund_df = fund_df.append(fund_series, ignore_index=True)
    for i in range(cycle):
        target_list = macd_target(df_list, date)
        fund_df, funds = one_cycle_buy_sell(funds, fund_df, target_list, date, days)
        date = get_next_date(date, days, df=xlv_df)
    return fund_df, funds

def simulate_xlv(funds, start, days, cycle):
    xlv_df = yf.Ticker('XLV').history(period='max')[['Close']]
    date = start
    fund_df = pd.DataFrame(columns=['date', 'curr_fund', 'num_stocks'])
    for i in range(cycle):
        fund_df, funds = one_cycle_buy_sell(funds, fund_df, [xlv_df], date, days)
        date = get_next_date(date, days, xlv_df)
    return fund_df, funds

