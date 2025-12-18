"""日誌管理模組"""

import logging
import os
from datetime import datetime


def setup_logger(name: str = "cmd_tool", log_file: str = None) -> logging.Logger:
    """設定日誌記錄器
    
    Args:
        name: 日誌記錄器名稱
        log_file: 日誌檔案路徑，None 則只輸出到控制台
    
    Returns:
        配置好的日誌記錄器
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 避免重複添加 handler
    if logger.handlers:
        return logger
    
    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 檔案 handler（如果指定了檔案路徑）
    if log_file:
        # 確保日誌目錄存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger