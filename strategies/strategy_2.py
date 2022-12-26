

import pandas as pd
import matplotlib.pyplot as plt
import math
from matplotlib import style
from src.event import SignalEvent
from strategies.strategy import Strategy

class MovingAveragesLongShortStrategy(Strategy):
    def __init__(self, data, events, portfolio, short_period, long_period, verbose=False, version=1):
        self.data = data
        self.symbol_list = self.data.symbol_list
        self.events = events
        self.portfolio = portfolio
        self.short_period = short_period
        self.long_period = long_period
        self.name = 'Moving Averages Long'
        self.verbose = verbose
        self.version = version

        self.signals = self._setup_signals()
        self.strategy = self._setup_strategy()
        self.bought = self._setup_initial_bought()

    def _setup_signals(self):
        signals = {}
        for symbol in self.symbol_list:
            signals[symbol] = pd.DataFrame(columns=['Date', 'Signal'])

        return signals

    def _setup_strategy(self):
        strategy = {}
        for symbol in self.symbol_list:
            strategy[symbol] = pd.DataFrame(columns=['Date', 'Short EMA', 'Long EMA'])

        return strategy

    def _setup_initial_bought(self):
        bought = {}
        for symbol in self.symbol_list:
            bought[symbol] = False

        return bought

    def calculate_long_short(self, df):
        price_short = None
        price_long = None
        if self.version == 1:
            price_short = df['High'].ewm(span=self.short_period, min_periods=self.short_period, adjust=False).mean()[-1]
            price_long = df['Low'].ewm(span=self.long_period, min_periods=self.long_period, adjust=False).mean()[-1]
        else:
            price_short = df['Close'].tail(self.long_period).ewm(span=self.short_period, adjust=False).mean()[-1]
            price_long = df['Close'].tail(self.long_period).ewm(span=self.long_period, adjust=False).mean()[-1]

        return price_short, price_long

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for symbol in self.symbol_list:
                data = self.data.get_latest_data(symbol, N=-1)
                df = pd.DataFrame(data, columns=['Symbol','Date','Open', 'High', 'Low', 'Close'])
                df = df.drop(['Symbol'], axis=1)
                df.set_index('Date', inplace=True)
                # if data is not None and len(data) >= self.long_period:
                #     price_short, price_long = self.calculate_long_short(df)
                #     date = df.index.values[-1]
                #     price = df['Close'][-1]

                if data is not None and len(data) >= self.long_period:
                    price_short, price_long = self.calculate_long_short(df)
                    date = data[-1][self.data.time_col]
                    price = data[-1][self.data.price_col]
                    to_append = pd.DataFrame({'Date': [date], 'Short EMA': [price_short], 'Long EMA': [price_long]})
                    self.strategy[symbol] = pd.concat([self.strategy[symbol],to_append])
                    if self.bought[symbol] == False and price_short > price_long:
                        current_positions = self.portfolio.current_positions[symbol]
                        quantity = math.floor(self.portfolio.current_holdings['cash'] / price + current_positions)
                        if current_positions !=0:
                            signal = SignalEvent(symbol, date, 'EXIT', math.fabs(current_positions))
                            self.events.put(signal)
                            if self.verbose: print("Short Exit", date, price,math.fabs(current_positions) )


                        signal = SignalEvent(symbol, date, 'LONG', quantity)
                        self.events.put(signal)
                        if self.verbose: print("Long", date, price, quantity)

                        self.bought[symbol] = True
                        to_append = pd.DataFrame({'Signal': [quantity], 'Date': [date]})
                        self.signals[symbol] = pd.concat([self.signals[symbol], to_append])

                    elif self.bought[symbol] == True and price_short < price_long:
                        quantity = self.portfolio.current_positions[symbol]
                        signal = SignalEvent(symbol, date, 'EXIT', quantity)
                        self.events.put(signal)
                        if self.verbose: print("Long Exit", date, price, quantity)
                        signal = SignalEvent(symbol, date, 'SHORT', quantity)
                        self.events.put(signal)
                        if self.verbose: print("Short", date, price, quantity)
                        self.bought[symbol] = False
                        to_append = pd.DataFrame({'Signal': [-quantity], 'Date': [date]})
                        self.signals[symbol] = pd.concat([self.signals[symbol], to_append])




    def plot(self):
        style.use('ggplot')

        for symbol in self.symbol_list:
            self.strategy[symbol].set_index('Date', inplace=True)
            self.signals[symbol].set_index('Date', inplace=True)
            signals = self.signals[symbol]
            strategy_fig, strategy_ax = plt.subplots()
            df = self.data.all_data[symbol].copy()
            df = df['Close']
            df.columns = ['EUR']
            # df['Short'] = df['OMXS30'].ewm(span=self.short_period, min_periods=self.short_period, adjust=False).mean()
            # df['Long'] = df['OMXS30'].ewm(span=self.long_period, min_periods=self.long_period, adjust=False).mean()

            df.plot(ax=strategy_ax, color='dodgerblue', linewidth=1.0)

            short_index = signals[signals['Signal'] < 0].index
            long_index = signals[signals['Signal'] > 0].index

            strategy_ax.plot(self.strategy[symbol]['Short EMA'], label='Short EMA', color='grey')
            strategy_ax.plot(self.strategy[symbol]['Long EMA'], label='Long EMA', color='k')
            # strategy_ax.plot(short_index, df['EUR'].loc[short_index], 'v', markersize=10, color='r', label='Exit')
            # strategy_ax.plot(long_index, df['EUR'].loc[long_index], '^', markersize=10, color='g', label='Long')

            strategy_ax.set_title(self.name)
            strategy_ax.set_xlabel('Time')
            strategy_ax.set_ylabel('Value')
            strategy_ax.legend()

        plt.show()

