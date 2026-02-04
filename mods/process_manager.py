import psutil
import os

class ProcessManager:
    def __init__(self):
        self.last_cpu = self.get_last_cpu()
        self.cpu_count = os.cpu_count()
    
    def get_last_cpu(self):
        """获取最后一个CPU的索引"""
        return os.cpu_count() - 1
    
    def detect_processes(self, process_name):
        """检测指定名称的进程"""
        found_processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] == process_name:
                    found_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return found_processes
    
    def get_priority_class(self, priority):
        """根据优先级名称获取优先级类"""
        priority_map = {
            "最低": psutil.IDLE_PRIORITY_CLASS,
            "低": psutil.BELOW_NORMAL_PRIORITY_CLASS,
            "正常": psutil.NORMAL_PRIORITY_CLASS,
            "高": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
            "最高": psutil.HIGH_PRIORITY_CLASS
        }
        return priority_map.get(priority, psutil.IDLE_PRIORITY_CLASS)
    
    def modify_process_priority(self, proc, priority="最低"):
        """修改进程优先级"""
        try:
            priority_class = self.get_priority_class(priority)
            proc.nice(priority_class)
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False
    
    def get_cpu_affinity(self, cpu_option):
        """根据CPU选项获取CPU亲和力"""
        if cpu_option == "所有CPU":
            return list(range(self.cpu_count))
        elif cpu_option.startswith("CPU "):
            cpu_index = int(cpu_option.split(" ")[1])
            if 0 <= cpu_index < self.cpu_count:
                return [cpu_index]
        return [self.last_cpu]
    
    def modify_process_affinity(self, proc, cpu_option=None):
        """设置进程处理器相关性"""
        try:
            if cpu_option:
                affinity = self.get_cpu_affinity(cpu_option)
            else:
                affinity = [self.last_cpu]
            proc.cpu_affinity(affinity)
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False
    
    def modify_process(self, proc, priority="最低", cpu_option=None):
        """修改进程的优先级和处理器相关性"""
        priority_result = self.modify_process_priority(proc, priority)
        affinity_result = self.modify_process_affinity(proc, cpu_option)
        return priority_result and affinity_result
    
    def process_exists(self, process_name):
        """检查进程是否存在"""
        return len(self.detect_processes(process_name)) > 0