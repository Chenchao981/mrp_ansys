"""
交期分析模块: 参数估计和到货预测
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional
from scipy.optimize import nnls


def estimate_leadtime_params(df: pd.DataFrame, robust: bool = True) -> pd.DataFrame:
    """
    估计交期参数 p1, p2
    
    Args:
        df: DataFrame包含订单和到货数据
        robust: 是否使用鲁棒估计
    
    Returns:
        DataFrame: 包含p1, p2参数的DataFrame
    """
    pass


def calculate_leadtime_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    计算交期指标 LT = 1*p1 + 2*p2, H = 1 + LT
    
    Args:
        df: 包含p1, p2的DataFrame
    
    Returns:
        DataFrame: 添加了LT, H列的DataFrame
    """
    pass


def calculate_expected_arrivals(df: pd.DataFrame) -> pd.DataFrame:
    """
    计算预期到货 EARR = p2*O_{t-2} + (p1+p2)*O_{t-1}
    
    Args:
        df: DataFrame
    
    Returns:
        DataFrame: 添加了EARR列的DataFrame
    """
    pass
