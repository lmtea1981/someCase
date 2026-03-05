import os
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from matplotlib.ticker import FuncFormatter

# 设置matplotlib中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Micro Hei', 'Heiti TC']  # 中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

class FundVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("基金净值可视化")
        self.root.geometry("1000x700")
        
        # 设置主题
        style = ttk.Style()
        style.theme_use('clam')
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建图表框架（放在上方）
        self.chart_frame = ttk.LabelFrame(self.main_frame, text="净值走势", padding="10")
        self.chart_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建控制框架
        self.control_frame = ttk.Frame(self.main_frame, padding="10")
        self.control_frame.pack(fill=tk.X, pady=5)
        
        # 刷新按钮
        self.refresh_button = ttk.Button(self.control_frame, text="刷新数据", command=self.refresh_data)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        # 全选按钮
        self.select_all_button = ttk.Button(self.control_frame, text="全选", command=self.select_all)
        self.select_all_button.pack(side=tk.LEFT, padx=5)
        
        # 取消全选按钮
        self.deselect_all_button = ttk.Button(self.control_frame, text="取消全选", command=self.deselect_all)
        self.deselect_all_button.pack(side=tk.LEFT, padx=5)
        
        # 时间区间设置
        ttk.Label(self.control_frame, text="开始日期:").pack(side=tk.LEFT, padx=5)
        self.start_date_var = tk.StringVar()
        self.start_date_entry = ttk.Entry(self.control_frame, textvariable=self.start_date_var, width=10)
        self.start_date_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.control_frame, text="结束日期:").pack(side=tk.LEFT, padx=5)
        self.end_date_var = tk.StringVar()
        self.end_date_entry = ttk.Entry(self.control_frame, textvariable=self.end_date_var, width=10)
        self.end_date_entry.pack(side=tk.LEFT, padx=5)
        
        self.apply_date_button = ttk.Button(self.control_frame, text="应用日期范围", command=self.apply_date_range)
        self.apply_date_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_date_button = ttk.Button(self.control_frame, text="重置日期范围", command=self.reset_date_range)
        self.reset_date_button.pack(side=tk.LEFT, padx=5)
        
        # 创建matplotlib图表
        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        self.canvas_chart = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas_chart.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 存储基金状态
        self.fund_status = {}  # 存储基金的显示状态
        self.fund_data = {}
        
        # 存储日期范围
        self.date_range = None
        
        # 添加十字线和数据提示
        self.vline = self.ax.axvline(color='gray', linestyle='--', alpha=0.5)
        self.hline = self.ax.axhline(color='gray', linestyle='--', alpha=0.5)
        self.tooltip = self.ax.text(0.02, 0.95, '', transform=self.ax.transAxes, bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7))
        self.tooltip.set_visible(False)
        
        # 绑定鼠标移动事件
        self.canvas_chart.mpl_connect('motion_notify_event', self.on_mouse_move)
        
        # 绑定鼠标点击事件（用于点击折线）
        self.canvas_chart.mpl_connect('button_press_event', self.on_click)
        
        # 绑定拾取事件（用于图例点击）
        self.canvas_chart.mpl_connect('pick_event', self.on_legend_clicked)
        
        # 加载数据
        self.load_data()
    
    def on_mouse_move(self, event):
        """处理鼠标移动事件，显示十字线和数据提示，以及折线加粗"""
        print(f"鼠标移动事件: x={event.xdata}, y={event.ydata}")
        
        # 检查事件是否有效
        if event is None or event.xdata is None or event.ydata is None:
            print("事件无效")
            return
        
        if not event.inaxes:
            # 鼠标不在图表区域内
            print("鼠标不在图表区域内")
            if hasattr(self, 'vline'):
                self.vline.set_visible(False)
            if hasattr(self, 'hline'):
                self.hline.set_visible(False)
            if hasattr(self, 'tooltip'):
                try:
                    self.tooltip.set_visible(False)
                except:
                    pass
            # 重新绘制所有数据点
            self.update_chart()
            try:
                self.canvas_chart.draw()
            except Exception as e:
                print(f"绘制图表出错: {e}")
            return
        
        # 确保十字线存在
        if not hasattr(self, 'vline') or not hasattr(self, 'hline'):
            print("十字线不存在")
            return
        
        # 更新十字线位置
        try:
            # 重新创建十字线，确保它们正确显示
            self.vline.remove()
            self.hline.remove()
            
            self.vline = self.ax.axvline(x=event.xdata, color='gray', linestyle='--', alpha=0.5)
            self.hline = self.ax.axhline(y=event.ydata, color='gray', linestyle='--', alpha=0.5)
            
            self.vline.set_visible(True)
            self.hline.set_visible(True)
            print("十字线更新成功")
        except Exception as e:
            print(f"更新十字线位置出错: {e}")
        
        # 查找最近的数据点
        tooltip_text = []
        closest_fund = None
        min_distance = float('inf')
        try:
            print(f"基金数量: {len(self.fund_status)}")
            # 找到距离鼠标最近的基金
            for fund_name, status in self.fund_status.items():
                if status and fund_name in self.fund_data:
                    print(f"处理基金: {fund_name}")
                    data = self.fund_data[fund_name]
                    dates = data['dates']
                    values = data['values']
                    
                    if dates:
                        # 找到最接近的日期
                        from matplotlib.dates import date2num
                        event_date = event.xdata
                        date_nums = date2num(dates)
                        closest_idx = min(range(len(date_nums)), key=lambda i: abs(date_nums[i] - event_date))
                        closest_date = dates[closest_idx]
                        closest_value = values[closest_idx]
                        
                        # 计算距离
                        distance = abs(date_nums[closest_idx] - event_date) + abs(closest_value - event.ydata)
                        
                        # 检查是否在合理范围内（3天）
                        if abs(date_nums[closest_idx] - event_date) < 3:
                            if distance < min_distance:
                                min_distance = distance
                                closest_fund = fund_name
                                tooltip_text = [f"{fund_name}: {closest_value:.4f} ({closest_date.strftime('%Y-%m-%d')})"]
                            print(f"找到数据点: {fund_name}, {closest_value}, {closest_date}")
            
            # 重新绘制图表，只显示最近的数据点
            self.ax.clear()
            
            # 重新创建十字线和数据提示
            self.vline = self.ax.axvline(x=event.xdata, color='gray', linestyle='--', alpha=0.5)
            self.hline = self.ax.axhline(y=event.ydata, color='gray', linestyle='--', alpha=0.5)
            
            # 收集所有数据点，用于设置轴范围
            all_dates = []
            all_values = []
            
            # 收集所有基金的标签，用于图例显示
            fund_labels = []
            # 绘制折线但不显示数据点
            for fund_name, status in self.fund_status.items():
                if fund_name in self.fund_data:
                    data = self.fund_data[fund_name]
                    if data['dates'] and data['values']:
                        if status:
                            # 过滤日期范围内的数据
                            filtered_dates = []
                            filtered_values = []
                            for date, value in zip(data['dates'], data['values']):
                                if self.date_range:
                                    start_date, end_date = self.date_range
                                    if start_date <= date <= end_date:
                                        filtered_dates.append(date)
                                        filtered_values.append(value)
                                else:
                                    filtered_dates.append(date)
                                    filtered_values.append(value)
                            
                            # 如果是距离鼠标最近的基金，加粗显示
                            if filtered_dates and filtered_values:
                                if fund_name == closest_fund:
                                    self.ax.plot(filtered_dates, filtered_values, label=fund_name, linewidth=3)
                                else:
                                    self.ax.plot(filtered_dates, filtered_values, label=fund_name, linewidth=1)
                                all_dates.extend(filtered_dates)
                                all_values.extend(filtered_values)
                        else:
                            # 基金禁用时，只添加标签到图例
                            fund_labels.append(fund_name)
            
            # 添加禁用基金的标签到图例
            for fund_name in fund_labels:
                # 使用空数据绘制一个不可见的线条，只为了在图例中显示
                self.ax.plot([], [], label=fund_name, alpha=0)
            
            # 只显示最近的数据点
            # 创建一个字典来存储每个基金的最近数据点
            fund_points = {}
            for fund_name, status in self.fund_status.items():
                if status and fund_name in self.fund_data:
                    data = self.fund_data[fund_name]
                    dates = data['dates']
                    values = data['values']
                    
                    if dates:
                        # 找到最接近的日期
                        from matplotlib.dates import date2num
                        event_date = event.xdata
                        date_nums = date2num(dates)
                        closest_idx = min(range(len(date_nums)), key=lambda i: abs(date_nums[i] - event_date))
                        closest_date = dates[closest_idx]
                        closest_value = values[closest_idx]
                        
                        # 检查是否在合理范围内（3天）
                        if abs(date_nums[closest_idx] - event_date) < 3:
                            fund_points[fund_name] = (closest_date, closest_value)
            
            # 绘制每个基金的最近数据点
            for fund_name, (date, value) in fund_points.items():
                if self.fund_status.get(fund_name, False):
                    self.ax.scatter(date, value, s=50, alpha=1.0, color='red')
            
            # 设置x轴范围为所有数据的实际范围
            if all_dates:
                min_date = min(all_dates)
                max_date = max(all_dates)
                self.ax.set_xlim(min_date, max_date)
            
            # 设置y轴范围，增加一些边距以更好地呈现折线变化幅度
            if all_values:
                min_value = min(all_values)
                max_value = max(all_values)
                # 计算边距，确保折线不会紧贴图表边缘
                margin = (max_value - min_value) * 0.1
                if margin == 0:  # 防止所有值相同的情况
                    margin = 0.1
                self.ax.set_ylim(min_value - margin, max_value + margin)
            
            # 设置图表属性
            self.ax.set_title('基金净值走势')
            self.ax.set_xlabel('日期')
            self.ax.set_ylabel('单位净值')
            self.ax.grid(True, linestyle='--', alpha=0.7)
            
            # 自动调整日期标签
            self.fig.autofmt_xdate()
            
            # 添加图例
            if self.fund_status:
                legend = self.ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')
                # 为图例添加点击事件并设置颜色
                for i, text in enumerate(legend.get_texts()):
                    fund_name = text.get_text()
                    text.set_picker(True)
                    # 根据基金状态设置颜色
                    if fund_name in self.fund_status and not self.fund_status[fund_name]:
                        text.set_color('gray')
                    else:
                        # 如果是距离鼠标最近的基金，突出显示图例
                        if fund_name == closest_fund:
                            text.set_color('red')
                            text.set_fontweight('bold')
                        else:
                            text.set_color('black')
                            text.set_fontweight('normal')
            
            # 调整布局
            self.fig.tight_layout()
            
            # 无论是否找到数据点，都更新数据提示
            if tooltip_text:
                print(f"创建数据提示: {tooltip_text}")
                # 移除旧的数据提示
                if hasattr(self, 'tooltip'):
                    try:
                        self.tooltip.remove()
                        print("移除旧数据提示成功")
                    except Exception as e:
                        print(f"移除旧数据提示出错: {e}")
                
                # 提取净值和日期信息
                # 精简点位信息，只显示净值和日期
                for i, text in enumerate(tooltip_text):
                    # 提取基金名称、净值和日期
                    parts = text.split(': ')
                    if len(parts) == 2:
                        fund_name = parts[0]
                        value_date = parts[1]
                        # 只保留净值和日期，移除基金名称
                        tooltip_text[i] = value_date
                
                # 计算数据提示的位置，确保不超出图表范围
                x_pos = event.xdata
                y_pos = event.ydata
                
                # 获取图表边界
                xlim = self.ax.get_xlim()
                ylim = self.ax.get_ylim()
                
                # 调整数据提示位置，确保不超出图表范围
                # 计算文本宽度和高度的近似值（以数据坐标为单位）
                text_width = 0.05 * (xlim[1] - xlim[0])
                text_height = 0.05 * (ylim[1] - ylim[0])
                
                # 如果数据提示会超出右边界，调整到左侧
                if x_pos + text_width > xlim[1]:
                    x_pos = xlim[1] - text_width
                # 如果数据提示会超出左边界，调整到右侧
                if x_pos - text_width < xlim[0]:
                    x_pos = xlim[0] + text_width
                # 如果数据提示会超出上边界，调整到下方
                if y_pos + text_height > ylim[1]:
                    y_pos = ylim[1] - text_height
                # 如果数据提示会超出下边界，调整到上方
                if y_pos - text_height < ylim[0]:
                    y_pos = ylim[0] + text_height
                
                # 创建新的数据提示
                self.tooltip = self.ax.text(
                    x_pos, 
                    y_pos, 
                    '\n'.join(tooltip_text), 
                    bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7)
                )
                self.tooltip.set_visible(True)
                print("数据提示创建成功")
            else:
                print("未找到数据点")
                if hasattr(self, 'tooltip'):
                    try:
                        self.tooltip.set_visible(False)
                        print("数据提示隐藏成功")
                    except Exception as e:
                        print(f"隐藏数据提示出错: {e}")
        except Exception as e:
            print(f"处理数据提示出错: {e}")
        
        try:
            self.canvas_chart.draw()
            print("图表绘制成功")
        except Exception as e:
            print(f"绘制图表出错: {e}")
    
    def get_history_dir(self):
        """获取history目录路径"""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'history')
    
    def load_data(self):
        """加载所有CSV文件数据"""
        history_dir = self.get_history_dir()
        
        # 清空现有数据
        self.fund_status.clear()
        self.fund_data.clear()
        
        # 加载CSV文件
        try:
            csv_files = [f for f in os.listdir(history_dir) if f.endswith('.csv')]
            
            if not csv_files:
                messagebox.showinfo("提示", "history目录下没有CSV文件")
                return
            
            print(f"找到 {len(csv_files)} 个CSV文件")
            
            for i, csv_file in enumerate(csv_files):
                fund_name = csv_file.replace('.csv', '')
                file_path = os.path.join(history_dir, csv_file)
                
                # 读取CSV数据
                dates = []
                values = []
                
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        date_str = row.get('发布日期')
                        value_str = row.get('单位净值')
                        if date_str and value_str:
                            try:
                                date = datetime.strptime(date_str, '%Y-%m-%d')
                                value = float(value_str)
                                dates.append(date)
                                values.append(value)
                            except Exception as e:
                                print(f"解析数据出错: {e}")
                                pass
                
                if dates and values:
                    # 按日期排序
                    sorted_data = sorted(zip(dates, values), key=lambda x: x[0])
                    sorted_dates, sorted_values = zip(*sorted_data)
                    
                    self.fund_data[fund_name] = {
                        'dates': sorted_dates,
                        'values': sorted_values
                    }
                    
                    # 默认显示所有基金
                    self.fund_status[fund_name] = True
                    
                    print(f"加载基金: {fund_name}, 数据点数量: {len(sorted_dates)}")
                else:
                    print(f"基金 {fund_name} 没有有效数据")
        except Exception as e:
            messagebox.showerror("错误", f"加载数据失败: {e}")
            print(f"加载数据失败: {e}")
        
        # 设置时间区间的开始时间为数据集中最早的时间
        if self.fund_data:
            all_dates = []
            for fund_name, data in self.fund_data.items():
                if data['dates']:
                    all_dates.extend(data['dates'])
            if all_dates:
                earliest_date = min(all_dates)
                latest_date = max(all_dates)
                self.start_date_var.set(earliest_date.strftime('%Y-%m-%d'))
                self.end_date_var.set(latest_date.strftime('%Y-%m-%d'))
                print(f"设置默认日期范围: {earliest_date} 到 {latest_date}")
        
        # 更新图表
        self.update_chart()
    
    def update_chart(self):
        """更新图表"""
        self.ax.clear()
        
        # 重新创建十字线和数据提示
        self.vline = self.ax.axvline(color='gray', linestyle='--', alpha=0.5)
        self.hline = self.ax.axhline(color='gray', linestyle='--', alpha=0.5)
        self.tooltip = self.ax.text(0.02, 0.95, '', transform=self.ax.transAxes, bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7))
        self.tooltip.set_visible(False)
        
        # 绘制选中的基金
        plotted_funds = 0
        all_dates = []
        all_values = []
        for fund_name, status in self.fund_status.items():
            if fund_name in self.fund_data:
                data = self.fund_data[fund_name]
                try:
                    # 确保数据不为空
                    if data['dates'] and data['values']:
                        # 只有当基金启用时才绘制曲线
                        if status:
                            # 过滤日期范围内的数据
                            filtered_dates = []
                            filtered_values = []
                            for date, value in zip(data['dates'], data['values']):
                                if self.date_range:
                                    start_date, end_date = self.date_range
                                    if start_date <= date <= end_date:
                                        filtered_dates.append(date)
                                        filtered_values.append(value)
                                else:
                                    filtered_dates.append(date)
                                    filtered_values.append(value)
                            
                            # 只绘制折线，不显示数据点
                            if filtered_dates and filtered_values:
                                self.ax.plot(filtered_dates, filtered_values, label=fund_name)
                                plotted_funds += 1
                                all_dates.extend(filtered_dates)
                                all_values.extend(filtered_values)
                                print(f"绘制基金: {fund_name}, 数据点数量: {len(filtered_dates)}")
                except Exception as e:
                    print(f"处理基金 {fund_name} 出错: {e}")
        
        # 为所有基金添加图例项，包括禁用的基金
        for fund_name, status in self.fund_status.items():
            if fund_name in self.fund_data and not status:
                # 为禁用的基金添加图例项
                self.ax.plot([], [], label=fund_name, alpha=0)
        
        print(f"共绘制 {plotted_funds} 个基金")
        
        # 设置x轴范围为所有数据的实际范围
        if all_dates:
            min_date = min(all_dates)
            max_date = max(all_dates)
            self.ax.set_xlim(min_date, max_date)
            print(f"设置x轴范围: {min_date} 到 {max_date}")
        
        # 设置y轴范围，增加一些边距以更好地呈现折线变化幅度
        if all_values:
            min_value = min(all_values)
            max_value = max(all_values)
            # 计算边距，确保折线不会紧贴图表边缘
            margin = (max_value - min_value) * 0.1
            if margin == 0:  # 防止所有值相同的情况
                margin = 0.1
            self.ax.set_ylim(min_value - margin, max_value + margin)
            print(f"设置y轴范围: {min_value - margin:.4f} 到 {max_value + margin:.4f}")
        
        # 设置图表属性
        self.ax.set_title('基金净值走势')
        self.ax.set_xlabel('日期')
        self.ax.set_ylabel('单位净值')
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        # 自动调整日期标签
        self.fig.autofmt_xdate()
        
        # 添加图例
        if self.fund_status:
            legend = self.ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')
            # 为图例添加点击事件并设置颜色
            for i, text in enumerate(legend.get_texts()):
                fund_name = text.get_text()
                text.set_picker(True)
                # 根据基金状态设置颜色
                if fund_name in self.fund_status and not self.fund_status[fund_name]:
                    text.set_color('gray')
                else:
                    text.set_color('black')
        
        # 调整布局
        self.fig.tight_layout()
        
        # 刷新图表
        self.canvas_chart.draw()
    
    def refresh_data(self):
        """刷新数据"""
        self.load_data()
    
    def select_all(self):
        """全选所有基金"""
        for fund_name in self.fund_status:
            self.fund_status[fund_name] = True
        self.update_chart()
    
    def deselect_all(self):
        """取消全选所有基金"""
        for fund_name in self.fund_status:
            self.fund_status[fund_name] = False
        self.update_chart()
    
    def on_click(self, event):
        """处理鼠标点击事件，点击折线后只显示该折线"""
        print(f"鼠标点击事件: x={event.xdata}, y={event.ydata}")
        
        # 检查事件是否有效
        if event is None or event.xdata is None or event.ydata is None:
            print("事件无效")
            return
        
        if not event.inaxes:
            # 鼠标不在图表区域内
            print("鼠标不在图表区域内")
            return
        
        # 找到距离点击位置最近的基金
        closest_fund = None
        min_distance = float('inf')
        
        for fund_name, status in self.fund_status.items():
            if status and fund_name in self.fund_data:
                data = self.fund_data[fund_name]
                dates = data['dates']
                values = data['values']
                
                if dates:
                    # 找到最接近的日期
                    from matplotlib.dates import date2num
                    event_date = event.xdata
                    date_nums = date2num(dates)
                    closest_idx = min(range(len(date_nums)), key=lambda i: abs(date_nums[i] - event_date))
                    closest_date = dates[closest_idx]
                    closest_value = values[closest_idx]
                    
                    # 计算距离
                    distance = abs(date_nums[closest_idx] - event_date) + abs(closest_value - event.ydata)
                    
                    # 检查是否在合理范围内（3天）
                    if abs(date_nums[closest_idx] - event_date) < 3 and distance < min_distance:
                        min_distance = distance
                        closest_fund = fund_name
        
        if closest_fund:
            print(f"点击了基金: {closest_fund}")
            # 只显示点击的基金，隐藏其他基金
            for fund_name in self.fund_status:
                self.fund_status[fund_name] = (fund_name == closest_fund)
            self.update_chart()
        
    def apply_date_range(self):
        """应用日期范围"""
        start_date_str = self.start_date_var.get()
        end_date_str = self.end_date_var.get()
        
        try:
            from datetime import datetime
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            
            if start_date > end_date:
                messagebox.showerror("错误", "开始日期不能晚于结束日期")
                return
            
            self.date_range = (start_date, end_date)
            self.update_chart()
            print(f"应用日期范围: {start_date} 到 {end_date}")
        except ValueError:
            messagebox.showerror("错误", "日期格式错误，请使用YYYY-MM-DD格式")
    
    def reset_date_range(self):
        """重置日期范围"""
        self.start_date_var.set("")
        self.end_date_var.set("")
        self.date_range = None
        self.update_chart()
        print("重置日期范围")
    
    def on_legend_clicked(self, event):
        """处理图例点击事件"""
        # 切换基金的显示状态
        fund_name = event.artist.get_text()
        if fund_name in self.fund_status:
            self.fund_status[fund_name] = not self.fund_status[fund_name]
            # 强制清除图表并重新绘制
            self.ax.clear()
            self.update_chart()

def main():
    """主函数"""
    root = tk.Tk()
    app = FundVisualizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()