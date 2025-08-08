"""
数据标准化模块: 构建主表和计算基础指标
"""

import pandas as pd
import numpy as np
from typing import Dict, List


def build_main_table(df_long: pd.DataFrame) -> pd.DataFrame:
    """
    构建产品×月份主表
    
    Args:
        df_long: 长格式数据表
    
    Returns:
        DataFrame: 主表，键为 (company, product, month)
    """
    pass


def calculate_total_demand(df_main: pd.DataFrame) -> pd.DataFrame:
    """
    计算总需求 D = S + S_other + OUT_other
    
    Args:
        df_main: 主表
    
    Returns:
        DataFrame: 添加了D列的主表
    """
    pass


def validate_data_completeness(df_main: pd.DataFrame) -> Dict:
    """
    验证数据完整性
    
    Args:
        df_main: 主表
    
    Returns:
        Dict: 验证结果报告
    """
    pass
