"""設定管理模組"""

import json
import os
from typing import Dict, Any


class ConfigManager:
    """設定檔管理器"""
    
    def __init__(self, config_file: str = "input_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """載入設定檔"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_config(self, config: Dict[str, Any] = None) -> None:
        """儲存設定檔"""
        if config is None:
            config = self.config
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """取得設定值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """設定值"""
        self.config[key] = value
        self.save_config()