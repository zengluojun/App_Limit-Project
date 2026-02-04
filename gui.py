import tkinter as tk
from tkinter import ttk, messagebox
import os
import time
from mods.config_manager import ConfigManager
from mods.monitor import Monitor

class ACEProcessMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("ACE反作弊限制扫盘工具")
        self.root.geometry("600x600")
        self.root.resizable(True, True)
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 初始化监控器
        self.monitor = Monitor(self.config_manager, self.log)
        # 设置进程状态回调函数
        self.monitor.set_process_status_callback(self.process_status_handler)
        
        # 日志文件路径
        self.log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "monitor.log")
        
        self.create_widgets()
        
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="ACE反作弊限制扫盘工具", font=("SimHei", 16, "bold"))
        title_label.pack(pady=10)
        
        # 系统信息框架
        sys_frame = ttk.LabelFrame(main_frame, text="系统信息", padding="10")
        sys_frame.pack(fill=tk.X, pady=5)
        
        cpu_count = os.cpu_count()
        last_cpu = cpu_count - 1
        check_interval = self.config_manager.get_check_interval()
        
        ttk.Label(sys_frame, text=f"CPU数量: {cpu_count}").pack(anchor=tk.W, pady=2)
        ttk.Label(sys_frame, text=f"使用的CPU索引: {last_cpu}").pack(anchor=tk.W, pady=2)
        ttk.Label(sys_frame, text=f"检查间隔: {check_interval}秒").pack(anchor=tk.W, pady=2)
        ttk.Label(sys_frame, text=f"日志文件: {self.log_file}").pack(anchor=tk.W, pady=2)
        
        # 监控进程框架
        process_frame = ttk.LabelFrame(main_frame, text="监控进程", padding="10")
        process_frame.pack(fill=tk.X, pady=5)
        
        # 存储进程标签的字典
        self.process_labels = {}
        
        monitored_processes = self.config_manager.get_monitored_processes()
        if monitored_processes:
            for i, process in enumerate(monitored_processes):
                label = ttk.Label(process_frame, text=f"进程 {i+1}: {process}")
                label.pack(anchor=tk.W, pady=2)
                self.process_labels[process] = label
        else:
            ttk.Label(process_frame, text="暂无监控进程").pack(anchor=tk.W, pady=2)
        
        # 操作选项框架
        option_frame = ttk.LabelFrame(main_frame, text="操作选项", padding="10")
        option_frame.pack(fill=tk.X, pady=5)
        
        # 优先级选项（高）
        priority_label = ttk.Label(option_frame, text="优先级限制:")
        priority_label.pack(anchor=tk.W, pady=2)
        
        priority_frame = ttk.Frame(option_frame)
        priority_frame.pack(anchor=tk.W, pady=2)
        
        self.priority_var = tk.StringVar(value="最低")
        priority_options = ["最低", "低", "正常", "高", "最高"]
        priority_combo = ttk.Combobox(priority_frame, textvariable=self.priority_var, values=priority_options, state="readonly", width=20)
        priority_combo.pack(side=tk.LEFT, padx=5)
        
        # CPU选项（低）
        cpu_label = ttk.Label(option_frame, text="CPU限制:")
        cpu_label.pack(anchor=tk.W, pady=2)
        
        cpu_frame = ttk.Frame(option_frame)
        cpu_frame.pack(anchor=tk.W, pady=2)
        
        cpu_count = os.cpu_count()
        cpu_options = [f"CPU {i}" for i in range(cpu_count)] + ["所有CPU"]
        self.cpu_var = tk.StringVar(value=f"CPU {cpu_count - 1}")
        cpu_combo = ttk.Combobox(cpu_frame, textvariable=self.cpu_var, values=cpu_options, state="readonly", width=20)
        cpu_combo.pack(side=tk.LEFT, padx=5)
        
        # 操作按钮框架
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        self.toggle_btn = ttk.Button(btn_frame, text="开始监控", command=self.toggle_monitoring)
        self.toggle_btn.pack(side=tk.LEFT, padx=5)
        
        self.config_btn = ttk.Button(btn_frame, text="配置", command=self.open_config)
        self.config_btn.pack(side=tk.LEFT, padx=5)
        
    def log(self, message):
        """添加日志信息到文件"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        # 写入日志文件
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message)
        except Exception as e:
            pass
        
    def toggle_monitoring(self):
        """切换监控状态"""
        if not self.monitor.is_monitoring:
            # 启动监控
            # 设置优先级和CPU选项
            priority = self.priority_var.get()
            cpu_option = self.cpu_var.get()
            self.monitor.set_priority(priority)
            self.monitor.set_cpu_option(cpu_option)
            
            # 开始监控后，进程文字变灰
            for process, label in self.process_labels.items():
                label.config(foreground="gray")
            
            self.toggle_btn.config(text="停止监控")
            self.monitor.start_monitoring()
        else:
            # 停止监控
            self.toggle_btn.config(text="开始监控")
            self.monitor.stop_monitoring()
    
    def process_status_handler(self, process_name, status):
        """处理进程状态变化"""
        if process_name in self.process_labels:
            label = self.process_labels[process_name]
            if status == "found":
                # 查询到对应进程后变黑
                label.config(foreground="black")
            elif status == "priority_success" or status == "affinity_success":
                # 设置成功变绿
                label.config(foreground="green")
            elif status == "priority_failed" or status == "affinity_failed":
                # 设置未成功后变黄
                label.config(foreground="orange")
            elif status == "not_found":
                # 未找到进程变灰
                label.config(foreground="gray")
    
    def update_process_display(self):
        """更新界面上的进程显示"""
        # 重新加载配置
        self.config_manager.config = self.config_manager.load_config()
        
        # 获取主框架
        main_frame = self.root.winfo_children()[0]
        
        # 查找系统信息框架和监控进程框架
        sys_frame = None
        process_frame = None
        
        for child in main_frame.winfo_children():
            if isinstance(child, ttk.LabelFrame):
                if child.cget("text") == "系统信息":
                    sys_frame = child
                elif child.cget("text") == "监控进程":
                    process_frame = child
        
        # 更新系统信息中的检查间隔
        if sys_frame:
            # 清除系统信息中的检查间隔标签
            for child in sys_frame.winfo_children():
                if "检查间隔:" in child.cget("text"):
                    child.destroy()
            # 添加新的检查间隔标签
            check_interval = self.config_manager.get_check_interval()
            ttk.Label(sys_frame, text=f"检查间隔: {check_interval}秒").pack(anchor=tk.W, pady=2)
        
        # 更新监控进程显示
        if process_frame:
            # 清除所有进程标签
            for child in process_frame.winfo_children():
                child.destroy()
            # 清空进程标签字典
            self.process_labels.clear()
            # 添加新的进程标签
            monitored_processes = self.config_manager.get_monitored_processes()
            if monitored_processes:
                for i, process in enumerate(monitored_processes):
                    label = ttk.Label(process_frame, text=f"进程 {i+1}: {process}")
                    label.pack(anchor=tk.W, pady=2)
                    self.process_labels[process] = label
            else:
                ttk.Label(process_frame, text="暂无监控进程").pack(anchor=tk.W, pady=2)
    
    def open_config(self):
        """打开配置窗口"""
        config_window = tk.Toplevel(self.root)
        config_window.title("配置")
        config_window.geometry("400x300")
        config_window.resizable(True, True)
        
        config_frame = ttk.Frame(config_window, padding="10")
        config_frame.pack(fill=tk.BOTH, expand=True)
        
        # 进程列表配置
        process_label = ttk.Label(config_frame, text="监控进程列表:")
        process_label.pack(anchor=tk.W, pady=5)
        
        monitored_processes = self.config_manager.get_monitored_processes()
        process_text = tk.Text(config_frame, height=10, width=40)
        process_text.pack(fill=tk.X, pady=5)
        process_text.insert(tk.END, "\n".join(monitored_processes))
        
        # 检查间隔配置
        interval_label = ttk.Label(config_frame, text="检查间隔 (秒):")
        interval_label.pack(anchor=tk.W, pady=5)
        
        check_interval = self.config_manager.get_check_interval()
        interval_var = tk.StringVar(value=str(check_interval))
        interval_entry = ttk.Entry(config_frame, textvariable=interval_var, width=10)
        interval_entry.pack(anchor=tk.W, pady=5)
        
        # 保存按钮
        def save_config():
            try:
                # 获取进程列表
                processes = process_text.get(1.0, tk.END).strip().split("\n")
                processes = [p.strip() for p in processes if p.strip()]
                
                # 获取检查间隔
                interval = int(interval_var.get())
                if interval <= 0:
                    raise ValueError("检查间隔必须大于0")
                
                # 保存配置
                success = self.config_manager.update_config(processes, interval)
                if success:
                    # 重新加载配置
                    self.config_manager.config = self.config_manager.load_config()
                    
                    # 更新界面显示
                    self.update_process_display()
                    
                    messagebox.showinfo("成功", "配置已保存，已自动更新")
                    config_window.destroy()
                else:
                    messagebox.showerror("错误", "保存配置失败")
                
            except ValueError as e:
                messagebox.showerror("错误", f"配置错误: {e}")
            except Exception as e:
                messagebox.showerror("错误", f"保存配置失败: {e}")
        
        save_btn = ttk.Button(config_frame, text="保存", command=save_config)
        save_btn.pack(pady=10)

def main():
    root = tk.Tk()
    app = ACEProcessMonitor(root)
    root.mainloop()

if __name__ == "__main__":
    main()