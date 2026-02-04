import json
import os

class ConfigManager:
    def __init__(self):
        # 获取当前模块所在目录的父目录，即ACE反作弊限制扫盘目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(os.path.dirname(current_dir), 'config.json')
        self.config = self.load_config()
    
    def load_config(self):
        """从文件加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            # 如果配置文件不存在，返回默认配置
            return {
                "MONITORED_PROCESSES": ["SGuardSvc64.exe", "SGuard64.exe"],
                "CHECK_INTERVAL": 5
            }
    
    def save_config(self, config_data):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            return False
    
    def get_monitored_processes(self):
        """获取监控的进程列表"""
        return self.config.get("MONITORED_PROCESSES", [])
    
    def get_check_interval(self):
        """获取检查间隔"""
        return self.config.get("CHECK_INTERVAL", 5)
    
    def update_config(self, processes, interval):
        """更新配置"""
        self.config = {
            "MONITORED_PROCESSES": processes,
            "CHECK_INTERVAL": interval
        }
        return self.save_config(self.config)