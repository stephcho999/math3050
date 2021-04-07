import pandas as pd
import yfinance as yf

xlv_df = yf.Ticker('XLV').history(period='max')


def getprice(df_dict, ticker, date):
    if date in df_dict[ticker].index:
        return df_dict[ticker].loc[date, 'Close']
    else:
        pass


def getsma(df_dict, ticker, date):
    if date in df_dict[ticker].index:
        return df_dict[ticker].loc[date, 'SMA']
    else:
        return False


def sma_target(df_dict, date):
    buy_dict = {}
    sell_dict = {}
    for key, value in df_dict.items():
        val = getsma(df_dict, key, date)
        if val == True:
            buy_dict[key] = value
        else:
            sell_dict[key] = value
    return buy_dict, sell_dict


def get_next_date(curr_date, df):
    for i in range(len(df.index)):
        if df.index[i] == curr_date:
            break
    return df.index[i + 1]


def one_cycle_buy_sell(funds, fund_df, portfolio_dict, fund_per_stock, df_dict, buy_dict, sell_dict, date):
    # buy
    for key, val in buy_dict.items():
        if key not in portfolio_dict.keys():
            stock_price = getprice(buy_dict, key, date)
            num_purchased = fund_per_stock / stock_price
            portfolio_dict[key] = num_purchased
            funds -= num_purchased * stock_price

    # sell
    for key, val in sell_dict.items():
        if key in portfolio_dict.keys():
            stock_price = getprice(sell_dict, key, date)
            funds += stock_price * portfolio_dict[key]
            del portfolio_dict[key]

    current_val = portfolio_value(df_dict, portfolio_dict, funds, date)

    fund_series = pd.Series({'date': date, 'curr_fund': current_val, 'num_stocks': len(portfolio_dict)})
    fund_df = fund_df.append(fund_series, ignore_index=True)

    return funds, current_val, fund_df, portfolio_dict


def portfolio_value(df_dict, portfolio_dict, cash, date):
    current_val = cash
    for key, val in portfolio_dict.items():
        stock_price = getprice(df_dict, key, date)
        current_val += stock_price * val

    return current_val


def simulate(funds, df_dict, start, end):
    date = start
    fund_df = pd.DataFrame(columns=['date', 'curr_fund', 'num_stocks'])
    portfolio_dict = {}
    dict_length = len(df_dict)
    current_val = funds
    while date != end:
        buy_dict, sell_dict = sma_target(df_dict, date)
        fund_ps = current_val / dict_length
        funds, current_val, fund_df, portfolio_dict = one_cycle_buy_sell(
            funds, fund_df, portfolio_dict, fund_ps, df_dict, buy_dict, sell_dict, date)
        date = get_next_date(date, df=xlv_df)
    final_length = len(portfolio_dict)
    for key, val in portfolio_dict.items():
        stock_price = getprice(df_dict, key, date)
        funds += stock_price * portfolio_dict[key]



    return funds, current_val, fund_df


def sim_buy_hold_eq(funds, df_dict, start, end):
    date = start
    fund_df = pd.DataFrame(columns=['date', 'curr_fund', 'num_stocks'])
    portfolio_dict = {}
    dict_length = len(df_dict)
    current_val = funds
    fund_per_stock = funds/dict_length
    while date != end:
        for key,val in df_dict.items():
            if key not in portfolio_dict.keys():
                stock_price = getprice(df_dict, key, date)
                if stock_price:
                    num_purchased = fund_per_stock / stock_price
                    portfolio_dict[key] = num_purchased
                    funds -= num_purchased * stock_price

        current_val = portfolio_value(df_dict, portfolio_dict, funds, date)

        fund_series = pd.Series(
            {'date': date, 'curr_fund': current_val, 'num_stocks': len(portfolio_dict)})
        fund_df = fund_df.append(fund_series, ignore_index=True)

        date = get_next_date(date, xlv_df)

    for key, val in portfolio_dict.items():
        stock_price = getprice(df_dict, key, date)
        funds += stock_price * portfolio_dict[key]


    return funds, current_val, fund_df


'''
def simulate_xlv(funds, start, end):
    xlv_df = yf.Ticker('XLV').history(period='max')[['Close']]
    xlv_dict = {'XLV': xlv_df}
    date = start
    fund_df = pd.DataFrame(columns=['date', 'curr_fund', 'num_stocks'])
    while (date != end):
        fund_df, funds = one_cycle_buy_sell(funds, fund_df, [xlv_df], date, days)
        date = get_next_date(date, days, xlv_df)
    return fund_df, funds
'''
