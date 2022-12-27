
import logging
from common.log import set_logger_name
from src.trading_session import TradingSession


set_logger_name('trading_session_1')

session = TradingSession(title="Sample Backtest")
stats = session.start_trading()


