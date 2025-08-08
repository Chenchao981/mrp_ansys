#!/usr/bin/env python3
"""
MRP系统主程序
车规功率芯片动态安全库存与月度下单管理

使用方法:
    python scripts/run_mrp.py --config config.yaml
    python scripts/run_mrp.py --config config.yaml --output-dir custom_outputs
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, Any
import yaml

# 添加src路径到系统路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mrp import io, normalize, metrics, leadtime, policy, quality, report


def load_config(config_path: str) -> Dict[str, Any]:
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def setup_logging(config: Dict[str, Any]) -> None:
    """设置日志"""
    log_config = config.get('logging', {})
    level = getattr(logging, log_config.get('level', 'INFO'))
    format_str = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 确保输出目录存在
    log_file = log_config.get('file')
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(level=level, format=format_str, 
                          handlers=[
                              logging.FileHandler(log_file, encoding='utf-8'),
                              logging.StreamHandler(sys.stdout)
                          ])
    else:
        logging.basicConfig(level=level, format=format_str)


def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(description='MRP系统 - 车规功率芯片动态安全库存管理')
    parser.add_argument('--config', '-c', required=True, help='配置文件路径')
    parser.add_argument('--output-dir', '-o', help='输出目录覆盖')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 加载配置
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"错误：无法加载配置文件 {args.config}: {e}")
        sys.exit(1)
    
    # 覆盖输出目录
    if args.output_dir:
        config['output']['directory'] = args.output_dir
    
    # 设置日志级别
    if args.verbose:
        config['logging']['level'] = 'DEBUG'
    
    # 初始化日志
    setup_logging(config)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 50)
    logger.info("MRP系统启动")
    logger.info("=" * 50)
    
    try:
        # 确保输出目录存在
        output_dir = Path(config['output']['directory'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("第一阶段：数据读取和预处理")
        
        # Step 1: 读取原始数据
        logger.info("1. 读取原始Excel文件...")
        input_file = config['data']['input_file']
        raw_df = io.read_raw_excel(input_file)
        logger.info(f"读取完成，数据形状: {raw_df.shape}")
        
        # Step 2: 解析产品块
        logger.info("2. 解析产品数据块...")
        df_long = io.parse_product_blocks(raw_df)
        logger.info(f"解析完成，长格式数据形状: {df_long.shape}")
        
        # Step 3: 构建主表
        logger.info("3. 构建主数据表...")
        df_main = normalize.build_main_table(df_long)
        logger.info(f"主表构建完成，形状: {df_main.shape}")
        
        # Step 4: 计算总需求
        logger.info("4. 计算总需求...")
        df_main = normalize.calculate_total_demand(df_main)
        
        # Step 5: 质量检查
        logger.info("5. 执行质量检查...")
        if config['quality']['enable_balance_check']:
            quality_result = quality.check_inventory_balance(
                df_main, 
                config['parameters']['balance_tolerance']
            )
            # 导出质量报告
            quality_file = output_dir / config['output']['files']['quality_report']
            report.export_to_csv(quality_result, str(output_dir), quality_file.name)
            logger.info(f"质量报告已保存: {quality_file}")
        
        # 导出主表
        main_table_file = output_dir / config['output']['files']['main_table']
        report.export_to_csv(df_main, str(output_dir), main_table_file.name)
        logger.info(f"主数据表已保存: {main_table_file}")
        
        logger.info("第一阶段完成！")
        logger.info(f"输出文件保存在: {output_dir}")
        
    except Exception as e:
        logger.error(f"执行过程中发生错误: {e}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        sys.exit(1)
    
    logger.info("MRP系统执行完成")


if __name__ == "__main__":
    main()
