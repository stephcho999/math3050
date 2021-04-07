import pandas as pd
import yfinance as yf

xlv_df = yf.Ticker('XLV').history(period='max')


def getprice(df_dict, ticker, date):
    if date in df_dict[ticker].index:
        return df_dict[ticker].loc[date, 'Close']
    else:
        pass


def getstoch(df_dict, ticker, date):
    if date in df_dict[ticker].index:
        return df_dict[ticker].loc[date, 'stoch']
    else:
        return False


def getk(df_dict, ticker, date):
    if date in df_dict[ticker].index:
        return df_dict[ticker].loc[date, 'K']
    else:
        return False


def stoch_target(df_dict, date, option=False):
    buy_dict = {}
    sell_dict = {}
    for key, value in df_dict.items():
        stoch_val = getstoch(df_dict, key, date)
        k_val = getk(df_dict, key, date)
        if stoch_val == True:
            if k_val <= 20:
                buy_dict[key] = value
        if option:
            if stoch_val == False:
                if k_val >= 80:
                    sell_dict[key] = value
        if not option:
            if k_val >= 80:
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

    fund_series = pd.Series({'date': date, 'cash': funds, 'curr_fund': current_val, 'num_stocks': len(portfolio_dict)})
    fund_df = fund_df.append(fund_series, ignore_index=True)

    return funds, current_val, fund_df, portfolio_dict


def portfolio_value(df_dict, portfolio_dict, cash, date):
    current_val = cash
    for key, val in portfolio_dict.items():
        stock_price = getprice(df_dict, key, date)
        current_val += stock_price * val

    return current_val


def simulate(funds, df_dict, start, end, option=False):
    date = start
    fund_df = pd.DataFrame(columns=['date', 'cash', 'curr_fund', 'num_stocks'])
    portfolio_dict = {}
    dict_length = len(df_dict)
    current_val = funds
    while date != end:
        buy_dict, sell_dict = stoch_target(df_dict, date, option)
        fund_ps = current_val / dict_length
        funds, current_val, fund_df, portfolio_dict = one_cycle_buy_sell(
            funds, fund_df, portfolio_dict, fund_ps, df_dict, buy_dict, sell_dict, date)
        date = get_next_date(date, df=xlv_df)
    final_length = len(portfolio_dict)
    for key, val in portfolio_dict.items():
        stock_price = getprice(df_dict, key, date)
        funds += stock_price * portfolio_dict[key]

    fund_series = pd.Series({'date': date, 'cash': funds, 'curr_fund': current_val, 'num_stocks': final_length})
    fund_df = fund_df.append(fund_series, ignore_index=True)

    return funds, current_val, fund_df

