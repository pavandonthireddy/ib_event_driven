import datetime as dt
from ib_insync import *
from src.settings import ENVIRONMENTS, DATA_DIR
import pywt
from src.settings import OUTPUT_RESULTS_DIR
from scripts.helper import *
import matplotlib.pyplot as plt
from trend_scanning_label import getBinsFromTrend
import numpy as np
import pandas as pd
from modwtpy import modwt, imodwt
from scipy import stats
from scipy.signal import savgol_filter

df = pd.read_csv("../data/EUR.csv", header=0, parse_dates=True)


df = df[:500]

