import queue
from src.data import HistoricCSVDataHandler, DataSource
from strategies.strategy_2 import MovingAveragesLongShortStrategy
from src.portfolio import NaivePortfolio
from src.execution import SimulateExecutionHandler
import logging
from common.log import set_logger_name
import datetime as dt

set_logger_name('strategy_2')

def backtest(events, data, portfolio, strategy, broker):
    logging.info(f'Started Backtest for strategy_1 at {dt.datetime.now()}')

    while True:
        # Update the bars (specific backtest code, as opposed to live trading)
        data.update_latest_data()
        if data.continue_backtest == False:
            break

        while True:
            try:
                event = events.get(block=False)
            except queue.Empty:
                break

            if event is not None:
                if event.type == 'MARKET':
                    strategy.calculate_signals(event)
                    portfolio.update_timeindex(event)
                elif event.type == 'SIGNAL':
                    portfolio.update_signal(event)
                elif event.type == 'ORDER':
                    broker.execute_order(event)
                elif event.type == 'FILL':
                    portfolio.update_fill(event)

        # time.sleep(10*60)
    stats = portfolio.summary_stats()

    for stat in stats:
            print(stat[0] + ": " + stat[1])

    strategy.plot()
    portfolio.plot_all()


# Declare the components with respective parameters
events = queue.Queue()

data = HistoricCSVDataHandler(events, './data/', ['EUR'], DataSource.IB)
portfolio = NaivePortfolio(data, events, '', initial_capital=100)
strategy = MovingAveragesLongShortStrategy(data, events, portfolio, 50, 200, verbose=True, version=1)
portfolio.strategy_name = strategy.name
broker = SimulateExecutionHandler(events)

backtest(events, data, portfolio, strategy, broker)