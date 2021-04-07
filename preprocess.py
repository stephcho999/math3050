import yfinance as yf
import pandas as pd
import datetime
import numpy as np

def prep_close(ticker):
    hist = yf.Ticker(ticker).history(period='max')
    close_df = hist['Close'].to_frame().rename(columns={'Close': ticker})
    if pd.to_datetime('12/22/98') in close_df.index:
        close_df = close_df.loc['1998-12-22':, :]
    return close_df.transpose()

def prep_close_all(tickers):
    df_list = []
    for ticker in tickers:
        df = prep_close(ticker)
        df_list.append(df)
    return pd.concat(df_list)

def prep_sma(ticker, short=50, long=200):
    hist = yf.Ticker(ticker).history(period='max')
    close_df = hist['Close'].to_frame()
    sma_df = close_df['Close'].rolling(short).mean().to_frame().rename(columns={'Close': str(short) + 'avg'})\
        .merge(close_df['Close'].rolling(long).mean().to_frame().rename(columns={'Close': str(long) + 'avg'}), 'left', left_index=True, right_index=True)
    sma_df = sma_df.dropna()
    if pd.to_datetime('12/22/98') in close_df.index:
        sma_df = sma_df.loc['1998-12-22':, :]
    sma_df['SMA'] = np.where(sma_df['50avg'] > sma_df['200avg'], True, False)
    sma_df = sma_df[['SMA']].rename(columns={'SMA':ticker})
    return sma_df.transpose()

def prep_sma_all(tickers):
    df_list = []
    for ticker in tickers:
        df = prep_sma(ticker)
        df_list.append(df)
    return pd.concat(df_list)



def prep_movavg(ticker, short=50, long=200):
    hist = yf.Ticker(ticker).history(period='max')
    close_df = hist['Close'].to_frame()
    movavg_df = close_df.merge(close_df['Close'].rolling(short).mean().to_frame().rename(columns={'Close': str(short)+'avg'}), 'left', left_index=True, right_index=True)\
        .merge(close_df['Close'].rolling(long).mean().to_frame().rename(columns={'Close': str(long)+'avg'}), 'left', left_index=True, right_index=True)
    movavg_df = movavg_df.dropna()
    if pd.to_datetime('12/22/98') in movavg_df.index:
        movavg_df = movavg_df.loc['1998-12-22':, :]
    movavg_df['SMA'] = np.where(movavg_df['50avg'] > movavg_df['200avg'], True, False)
    movavg_df = movavg_df[['Close','SMA']]
    return movavg_df

def prep_all_movavg(tickers):
    df_list = []
    for ticker in tickers:
        df = prep_movavg(ticker)
        df_list.append(df)
    return df_list

def prep_movavg_mod(tickers):
    df_dict = {}
    for ticker in tickers:
        df = prep_movavg(ticker)
        df_dict[ticker] = df
    return df_dict

def prep_macd(ticker):
    hist = yf.Ticker(ticker).history(period='max')
    close_df = hist['Close'].to_frame()
    macd_df = close_df.merge(
        close_df['Close'].ewm(span=12, adjust=False).mean().to_frame().rename(columns={'Close': 'ewm_12'}), 'left',
        left_index=True, right_index=True)
    macd_df = macd_df.merge(
        macd_df['Close'].ewm(span=26, adjust=False).mean().to_frame().rename(columns={'Close': 'ewm_26'}), 'left',
        left_index=True, right_index=True)
    macd_df['macd'] = macd_df['ewm_12'] - macd_df['ewm_26']
    macd_df = macd_df[26:]
    macd_df = macd_df.merge(
        macd_df['macd'].ewm(span=9, adjust=False).mean().to_frame().rename(columns={'macd': 'signal'}), 'left',
        left_index=True, right_index=True)
    macd_df['MACD'] = np.where(macd_df['macd'] > macd_df['signal'], True, False)
    if pd.to_datetime('12/22/98') in macd_df.index:
        macd_df = macd_df.loc['1998-12-22':, :]
    macd_df = macd_df[['Close','MACD']]
    return macd_df

def prep_all_macd(tickers):
    df_list = []
    for ticker in tickers:
        df = prep_macd(ticker)
        df_list.append(df)
    return df_list

def prep_macd_mod(tickers):
    df_dict = {}
    for ticker in tickers:
        df = prep_macd(ticker)
        df_dict[ticker] = df
    return df_dict

def prep_stoch(ticker):
    hist = yf.Ticker(ticker).history(period='max')
    stoch_df = hist['Close'].to_frame()
    stoch_df = stoch_df.merge(stoch_df['Close'].rolling(14).min().to_frame().rename(columns={'Close': 'L14'}), left_index=True, right_index=True).merge(
        stoch_df['Close'].rolling(14).max().to_frame().rename(columns={'Close': 'H14'}), left_index=True,
        right_index=True)
    stoch_df = stoch_df.dropna()
    stoch_df['K'] = (stoch_df['Close'] - stoch_df['L14']) / (stoch_df['H14'] - stoch_df['L14']) * 100
    stoch_df = stoch_df.merge(stoch_df['K'].rolling(3).mean().to_frame().rename(columns={'K': 'D'}), left_index=True,
                              right_index=True)
    stoch_df['stoch'] = np.where(stoch_df['K'] > stoch_df['D'], True, False)
    if pd.to_datetime('12/22/98') in stoch_df.index:
        stoch_df = stoch_df.loc['1998-12-22':, :]
    stoch_df = stoch_df[['Close','K', 'stoch']]
    return stoch_df


def prep_all_stoch(tickers):
    df_list = []
    for ticker in tickers:
        df = prep_stoch(ticker)
        df_list.append(df)
    return df_list


def prep_stoch_mod(tickers):
    df_dict = {}
    for ticker in tickers:
        df = prep_stoch(ticker)
        df_dict[ticker] = df
    return df_dict

