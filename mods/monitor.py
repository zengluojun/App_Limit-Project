import time
import threading
from mods.process_manager import ProcessManager

class Monitor:
    def __init__(self, config_manager, log_callback):
        self.config_manager = config_manager
        self.log_callback = log_callback
        self.process_manager = ProcessManager()
        self.is_monitoring = False
        self.monitor_thread = None
        self.priority = "最低"
        self.cpu_option = None
        self.process_status_callback = None
    
    def set_process_status_callback(self, callback):
        """设置进程状态回调函数"""
        self.process_status_callback = callback
    
    def set_priority(self, priority):
        """设置优先级"""
        self.priority = priority
    
    def set_cpu_option(self, cpu_option):
        """设置CPU选项"""
        self.cpu_option = cpu_option
    
    def start_monitoring(self):
        """开始监控进程"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
            self.monitor_thread.start()
            self.log_callback("监控已启动")
    
    def stop_monitoring(self):
        """停止监控进程"""
        if self.is_monitoring:
            self.is_monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=1)
            self.log_callback("监控已停止")
    
    def monitor_processes(self):
        """监控进程的主循环"""
        while self.is_monitoring:
            self.log_callback("开始检查进程...")
            
            monitored_processes = self.config_manager.get_monitored_processes()
            check_interval = self.config_manager.get_check_interval()
            
            for process_name in monitored_processes:
                self.check_process(process_name)
            
            self.log_callback("检查完成，等待下一次检查...")
            time.sleep(check_interval)
    
    def check_process(self, process_name):
        """检查并修改指定进程"""
        processes = self.process_manager.detect_processes(process_name)
        
        if not processes:
            self.log_callback(f"未找到进程: {process_name}")
            # 通知GUI进程未找到
            if self.process_status_callback:
                self.process_status_callback(process_name, "not_found")
            return
        
        for proc in processes:
            self.log_callback(f"找到进程: {process_name} (PID: {proc.info['pid']})")
            # 通知GUI进程已找到
            if self.process_status_callback:
                self.process_status_callback(process_name, "found")
            
            # 尝试修改进程优先级
            priority_success = self.process_manager.modify_process_priority(proc, self.priority)
            if priority_success:
                self.log_callback(f"已将进程优先级设置为{self.priority}")
                # 通知GUI优先级设置成功
                if self.process_status_callback:
                    self.process_status_callback(process_name, "priority_success")
            else:
                self.log_callback(f"无法修改进程优先级: {process_name}")
                # 通知GUI优先级设置失败
                if self.process_status_callback:
                    self.process_status_callback(process_name, "priority_failed")
            
            # 尝试修改处理器相关性
            affinity_success = self.process_manager.modify_process_affinity(proc, self.cpu_option)
            if affinity_success:
                cpu_info = self.cpu_option if self.cpu_option else f"CPU {self.process_manager.last_cpu}"
                self.log_callback(f"已将处理器相关性设置为{cpu_info}")
                # 通知GUI处理器相关性设置成功
                if self.process_status_callback:
                    self.process_status_callback(process_name, "affinity_success")
            else:
                self.log_callback(f"无法修改处理器相关性: {process_name}")
                # 通知GUI处理器相关性设置失败
                if self.process_status_callback:
                    self.process_status_callback(process_name, "affinity_failed")