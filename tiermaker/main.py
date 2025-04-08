#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TierMaker - 排行榜制作工具
主模块 - 包含主应用类和程序入口点
"""

import tkinter as tk
from tkinter import messagebox
import os

# 导入自定义模块
from tiermaker.config_manager import ConfigManager
from tiermaker.ui_components import TierFrame, RepositoryFrame
from tiermaker.tier_manager import TierManagerDialog
from tiermaker.image_utils import ImageProcessor

# 尝试导入tkinterdnd2库，如果不可用则使用基本的tk功能
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    TkinterDnDClass = TkinterDnD.Tk
    TKDND_AVAILABLE = True
except ImportError:
    messagebox.showwarning("功能受限", "未安装tkinterdnd2库，拖放功能将不可用。\n请使用pip install tkinterdnd2安装。")
    DND_FILES = "DND_Files"  # 仅用作占位符
    TkinterDnDClass = tk.Tk
    TKDND_AVAILABLE = False


class TierMaker(TkinterDnDClass):
    """TierMaker主应用类"""
    def __init__(self):
        super().__init__()
        self.title("TierMaker - 排行榜制作工具")
        self.geometry("1200x800")
        self.minsize(800, 600)
        
        # 设置应用图标
        self.iconbitmap(default="")
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 初始化图片处理器
        self.image_processor = ImageProcessor(self.config_manager.images_dir)
        
        # 初始化数据
        self.tiers = []
        self.repository_images = []
        self.load_config()
        
        # 创建UI
        self.create_menu()
        self.create_main_layout()
        
        # 绑定事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 初始化拖放数据
        self._drag_data = None
        self._drag_icon = None
    
    def load_config(self):
        """加载配置"""
        config = self.config_manager.load_config()
        if config:
            self.tiers = config.get('tiers', [])
            self.repository_images = config.get('repository_images', [])
        
        # 如果没有等级，添加默认等级
        if not self.tiers:
            self.tiers = [
                {"name": "S", "color": "#FF7F7F", "images": []},
                {"name": "A", "color": "#FFBF7F", "images": []},
                {"name": "B", "color": "#FFFF7F", "images": []},
                {"name": "C", "color": "#7FFF7F", "images": []},
                {"name": "D", "color": "#7FBFFF", "images": []},
                {"name": "E", "color": "#7F7FFF", "images": []},
                {"name": "F", "color": "#FF7FFF", "images": []}
            ]
    
    def save_config(self):
        """保存配置"""
        config = {
            'tiers': self.tiers,
            'repository_images': self.repository_images
        }
        self.config_manager.save_config(config)
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新建排行榜", command=self.new_tierlist)
        file_menu.add_command(label="保存排行榜", command=self.save_config)
        file_menu.add_command(label="导出为图片", command=self.export_as_image)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="添加图片到仓库", command=self.add_images)
        edit_menu.add_command(label="管理等级", command=self.manage_tiers)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="使用帮助", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)
        
        self.config(menu=menubar)
    
    def create_main_layout(self):
        """创建主界面布局"""
        from tkinter import ttk
        
        # 主分割窗口
        self.main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧：等级区域
        self.tier_frame = TierFrame(self.main_paned, self, self.tiers, 
                                   self.config_manager.images_dir, TKDND_AVAILABLE, DND_FILES)
        self.main_paned.add(self.tier_frame, weight=3)
        
        # 右侧：图片仓库
        self.repository_frame = RepositoryFrame(self.main_paned, self, 
                                               self.repository_images, 
                                               self.config_manager.images_dir,
                                               TKDND_AVAILABLE, DND_FILES)
        self.main_paned.add(self.repository_frame, weight=1)
    
    def refresh_ui(self):
        """刷新界面"""
        self.tier_frame.refresh_tiers(self.tiers)
        self.repository_frame.refresh_repository(self.repository_images)
    
    def move_image_to_tier(self, img_info, tier_index):
        """将图片移动到指定等级"""
        # 首先从原位置移除
        # 检查是否在仓库中
        if img_info in self.repository_images:
            self.repository_images.remove(img_info)
        else:
            # 检查是否在某个等级中
            for tier in self.tiers:
                if img_info in tier.get("images", []):
                    tier["images"].remove(img_info)
                    break
        
        # 添加到新等级
        if "images" not in self.tiers[tier_index]:
            self.tiers[tier_index]["images"] = []
        
        self.tiers[tier_index]["images"].append(img_info)
        
        # 刷新界面
        self.refresh_ui()
        
        # 保存配置
        self.save_config()
    
    def add_images(self):
        """添加图片到仓库"""
        from tkinter import filedialog
        
        filetypes = [
            ("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp")
        ]
        
        filenames = filedialog.askopenfilenames(
            title="选择图片",
            filetypes=filetypes
        )
        
        if not filenames:
            return
        
        for filename in filenames:
            img_info = self.image_processor.add_image_from_path(filename)
            if img_info and img_info not in self.repository_images:
                self.repository_images.append(img_info)
        
        # 刷新仓库显示
        self.repository_frame.refresh_repository(self.repository_images)
        
        # 保存配置
        self.save_config()
    
    def manage_tiers(self):
        """管理等级"""
        # 保存原始等级列表的副本，用于比较变化
        original_tiers = [tier.copy() for tier in self.tiers]
        original_tier_names = [tier['name'] for tier in original_tiers]
        
        # 打开等级管理对话框
        tier_manager = TierManagerDialog(self, self.tiers)
        self.wait_window(tier_manager)
        
        # 检查是否有等级被删除，将删除等级中的图片移回仓库
        current_tier_names = [tier['name'] for tier in self.tiers]
        for tier in original_tiers:
            if tier['name'] not in current_tier_names:
                # 将删除等级中的图片移回仓库
                for img_info in tier.get('images', []):
                    if img_info not in self.repository_images:
                        self.repository_images.append(img_info)
        
        # 刷新界面
        self.refresh_ui()
        
        # 保存配置
        self.save_config()
    
    def new_tierlist(self):
        """创建新的排行榜"""
        if messagebox.askyesno("新建排行榜", "确定要创建新的排行榜吗？这将清除当前的所有等级和图片。"):
            # 清除所有等级中的图片（但保留等级）
            for tier in self.tiers:
                tier["images"] = []
            
            # 刷新界面
            self.refresh_ui()
            
            # 保存配置
            self.save_config()
    
    def export_as_image(self):
        """导出为图片"""
        self.image_processor.export_tierlist_as_image(self.tiers, self.tier_frame.tiers_canvas)
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
        TierMaker 使用帮助：
        
        1. 添加图片：点击"编辑"菜单中的"添加图片到仓库"，或直接拖放图片到仓库区域。
        2. 排序图片：将仓库中的图片拖放到相应的等级行中。
        3. 管理等级：点击"编辑"菜单中的"管理等级"，可以添加、删除或修改等级。
        4. 保存排行榜：点击"文件"菜单中的"保存排行榜"。
        5. 导出为图片：点击"文件"菜单中的"导出为图片"，将排行榜保存为PNG图片。
        """
        messagebox.showinfo("使用帮助", help_text)
    
    def show_about(self):
        """显示关于信息"""
        about_text = """
        TierMaker - 排行榜制作工具
        
        版本: 1.1
        
        一个简单的工具，用于创建和分享你的排行榜。
        """
        messagebox.showinfo("关于", about_text)
    
    def start_drag(self, event, frame, img_info):
        """开始拖动图片"""
        # 保存被拖动的图片信息
        self._drag_data = {"frame": frame, "img_info": img_info, "start_x": event.x, "start_y": event.y}
        
        # 创建拖动时的视觉反馈
        self._drag_icon = tk.Toplevel(self)
        self._drag_icon.overrideredirect(True)  # 无边框窗口
        self._drag_icon.attributes("-topmost", True)  # 置顶
        self._drag_icon.attributes("-alpha", 0.7)  # 半透明
        
        # 在新窗口中显示图片
        try:
            from PIL import Image, ImageTk
            img_path = os.path.join(self.config_manager.images_dir, img_info["filename"])
            img = Image.open(img_path)
            img = img.resize((50, 50), Image.LANCZOS)  # 减小拖动图标大小
            photo = ImageTk.PhotoImage(img)
            
            lbl = tk.Label(self._drag_icon, image=photo)
            lbl.image = photo  # 保持引用
            lbl.pack()
            
            # 设置初始位置
            x, y = self.winfo_pointerxy()
            self._drag_icon.geometry(f"+{x-30}+{y-30}")
            
            # 绑定鼠标移动和释放事件
            self.bind("<B1-Motion>", self.on_drag_motion)
            self.bind("<ButtonRelease-1>", self.on_drag_release)
        except Exception as e:
            print(f"创建拖动图标错误: {str(e)}")
            if hasattr(self, '_drag_icon') and self._drag_icon:
                self._drag_icon.destroy()
    
    def on_drag_motion(self, event):
        """拖动过程中更新图标位置"""
        if hasattr(self, '_drag_icon') and self._drag_icon:
            # 更新拖动图标位置
            x, y = self.winfo_pointerxy()
            self._drag_icon.geometry(f"+{x-30}+{y-30}")
    
    def on_drag_release(self, event):
        """释放拖动，确定放置位置"""
        if hasattr(self, '_drag_icon') and self._drag_icon:
            self._drag_icon.destroy()
            
            # 确定鼠标位置
            x, y = event.x_root, event.y_root
            
            # 获取等级区域的位置
            tiers_canvas_x = self.tier_frame.tiers_canvas.winfo_rootx()
            tiers_canvas_y = self.tier_frame.tiers_canvas.winfo_rooty()
            tiers_canvas_width = self.tier_frame.tiers_canvas.winfo_width()
            tiers_canvas_height = self.tier_frame.tiers_canvas.winfo_height()
            
            # 检查是否在等级区域内
            if (tiers_canvas_x <= x < tiers_canvas_x + tiers_canvas_width and
                tiers_canvas_y <= y < tiers_canvas_y + tiers_canvas_height):
                
                # 获取所有等级行的子部件
                tier_widgets = self.tier_frame.tiers_container.winfo_children()
                
                # 计算相对于画布的位置
                canvas_y = y - tiers_canvas_y + self.tier_frame.tiers_canvas.yview()[0] * self.tier_frame.tiers_container.winfo_height()
                
                # 查找对应的等级
                for i, tier_widget in enumerate(tier_widgets):
                    if i < len(self.tiers):  # 确保索引不超出范围
                        tier_y = tier_widget.winfo_y()
                        tier_height = tier_widget.winfo_height()
                        
                        if tier_y <= canvas_y < tier_y + tier_height:
                            # 找到目标等级，移动图片
                            self.move_image_to_tier(self._drag_data["img_info"], i)
                            break
                else:
                    # 如果没有找到匹配的等级，尝试移动到最近的等级
                    if tier_widgets and self._drag_data and "img_info" in self._drag_data:
                        # 计算最近的等级
                        closest_tier = 0
                        min_distance = float('inf')
                        
                        for i, tier_widget in enumerate(tier_widgets):
                            if i < len(self.tiers):
                                tier_center = tier_widget.winfo_y() + tier_widget.winfo_height() / 2
                                distance = abs(canvas_y - tier_center)
                                
                                if distance < min_distance:
                                    min_distance = distance
                                    closest_tier = i
                        
                        # 移动到最近的等级
                        self.move_image_to_tier(self._drag_data["img_info"], closest_tier)
            
            # 解除绑定
            self.unbind("<B1-Motion>")
            self.unbind("<ButtonRelease-1>")
            
            # 清除拖动数据
            self._drag_data = None
    
    def on_closing(self):
        """关闭应用前的操作"""
        if messagebox.askyesno("退出", "确定要退出吗？未保存的更改将丢失。"):
            self.save_config()  # 自动保存当前状态
            self.destroy()


def main():
    """程序入口点"""
    app = TierMaker()
    app.mainloop()


if __name__ == "__main__":
    main()