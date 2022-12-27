import queue
import time
import datetime as dt
import logging
from src.data import HistoricCSVDataHandler, DataSource
from strategies.strategy_2 import MovingAveragesLongShortStrategy
from src.portfolio import NaivePortfolio
from src.execution import SimulateExecutionHandler
from src.settings import EQUITY


class TradingSession(object):

    def __init__(self, title, session_type="backtest", heartbeat = 0.0, end_session_time = None,  data=None,
                 portfolio=None, strategy=None, broker=None):
        self.session_type = session_type
        self.data = data
        self.portfolio = portfolio
        self.strategy = strategy
        self.broker = broker
        self.events_queue = queue.Queue()
        self.title = title
        self.heartbeat = heartbeat
        self._config_session()
        self.end_session_time = end_session_time


        if self.session_type == "live":
            if self.end_session_time is None:
                raise Exception("Must specify an end_session_time when live trading")


    def _config_session(self):
        """
        Initialises the necessary classes used
        within the session.
        """
        if self.data == None:
            self.data = HistoricCSVDataHandler(self.events_queue, './data/', ['EUR'], DataSource.IB)

        if self.portfolio == None:
            self.portfolio = NaivePortfolio(self.data, self.events_queue, '', initial_capital=EQUITY)

        if self.strategy == None:
            self.strategy = MovingAveragesLongShortStrategy(self.data, self.events_queue, self.portfolio,
                                                            5, 15, verbose=True, version=1)

            self.portfolio.strategy_name = self.strategy.name

        if self.broker == None:
            self.broker = SimulateExecutionHandler(self.events_queue)

    def _run_session(self):
        """
        Carries out an infinite while loop that polls the
        events queue and directs each event to either the
        strategy component of the execution handler. The
        loop continue until the event queue has been
        emptied.
        """
        if self.session_type == "backtest":
            logging.info(f'Started Backtest for strategy_1 at {dt.datetime.now()}')
        else:
            logging.info(f"Running Realtime Session until {self.end_session_time}")

        while True:
            # Update the bars (specific backtest code, as opposed to live trading)
            self.data.update_latest_data()
            if self.data.continue_backtest == False:
                break

            while True:
                try:
                    event = self.events_queue.get(block=False)
                except queue.Empty:
                    break

                if event is not None:
                    if event.type == 'MARKET':
                        self.strategy.calculate_signals(event)
                        self.portfolio.update_timeindex(event)
                    elif event.type == 'SIGNAL':
                        self.portfolio.update_signal(event)
                    elif event.type == 'ORDER':
                        self.broker.execute_order(event)
                    elif event.type == 'FILL':
                        self.portfolio.update_fill(event)

            if self.heartbeat !=0:
                time.sleep(self.heartbeat)

    def _output_performance(self):
        stats = self.portfolio.summary_stats()

        for stat in stats:
            logging.info(stat[0] + ": " + stat[1])

        self.strategy.plot()
        self.portfolio.plot_all()


    def start_trading(self):
        """
        Runs either a backtest or live session, and outputs performance when complete.
        """
        self._run_session()
        self._output_performance()
        logging.info("------------------------------TRADING SESSION COMPLETE------------------------------------")










