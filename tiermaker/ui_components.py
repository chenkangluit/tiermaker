#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TierMaker - 排行榜制作工具
UI组件模块 - 包含各种UI组件和对话框
"""

import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk


class TierFrame(ttk.Frame):
    """等级区域框架"""
    def __init__(self, parent, app, tiers, images_dir, tkdnd_available, dnd_files):
        super().__init__(parent)
        self.app = app
        self.tiers = tiers
        self.images_dir = images_dir
        self.tkdnd_available = tkdnd_available
        self.dnd_files = dnd_files
        
        self.setup_tiers_area()
    
    def setup_tiers_area(self):
        """设置等级区域"""
        # 创建一个画布和滚动条
        self.tiers_canvas = tk.Canvas(self, bg="white")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tiers_canvas.yview)
        self.tiers_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.tiers_canvas.pack(side="left", fill="both", expand=True)
        
        # 创建一个框架来容纳所有等级行
        self.tiers_container = ttk.Frame(self.tiers_canvas)
        self.tiers_canvas_window = self.tiers_canvas.create_window((0, 0), window=self.tiers_container, anchor="nw")
        
        # 绑定事件以调整画布大小
        self.tiers_container.bind("<Configure>", self.on_tiers_container_configure)
        self.tiers_canvas.bind("<Configure>", self.on_tiers_canvas_configure)
        
        # 加载等级
        self.refresh_tiers(self.tiers)
    
    def on_tiers_container_configure(self, event):
        """当等级容器大小改变时调整画布滚动区域"""
        self.tiers_canvas.configure(scrollregion=self.tiers_canvas.bbox("all"))
    
    def on_tiers_canvas_configure(self, event):
        """当画布大小改变时调整内部窗口大小"""
        self.tiers_canvas.itemconfig(self.tiers_canvas_window, width=event.width)
    
    def refresh_tiers(self, tiers):
        """刷新等级区域"""
        self.tiers = tiers
        
        # 清除现有内容
        for widget in self.tiers_container.winfo_children():
            widget.destroy()
        
        # 为每个等级创建一行
        for i, tier in enumerate(self.tiers):
            tier_frame = ttk.Frame(self.tiers_container)
            tier_frame.pack(fill="x", pady=1)  # 减小行间距
            
            # 等级标签（左侧彩色部分）
            label_frame = tk.Frame(tier_frame, width=50, bg=tier["color"])  # 减小宽度
            label_frame.pack(side="left", fill="y")
            
            label = tk.Label(label_frame, text=tier["name"], bg=tier["color"], font=("Arial", 12, "bold"))  # 减小字体
            label.pack(expand=True, fill="both")
            
            # 图片区域（右侧）
            images_frame = ttk.Frame(tier_frame, height=80)  # 减小高度
            images_frame.pack(side="left", fill="both", expand=True)
            
            # 使用Canvas来实现水平滚动
            canvas = tk.Canvas(images_frame, height=80, bg="#f0f0f0")  # 减小高度
            scrollbar = ttk.Scrollbar(images_frame, orient="horizontal", command=canvas.xview)
            canvas.configure(xscrollcommand=scrollbar.set)
            
            scrollbar.pack(side="bottom", fill="x")
            canvas.pack(side="top", fill="both", expand=True)
            
            # 创建一个框架来容纳图片
            images_container = ttk.Frame(canvas)
            canvas_window = canvas.create_window((0, 0), window=images_container, anchor="nw")
            
            # 加载该等级的图片
            self.load_tier_images(images_container, tier)
            
            # 绑定事件以调整画布大小
            images_container.bind("<Configure>", lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))
            canvas.bind("<Configure>", lambda e, c=canvas, w=canvas_window: c.itemconfig(w, width=e.width))
            
            # 设置为可放置区域
            if self.tkdnd_available:
                canvas.drop_target_register(self.dnd_files)
                canvas.dnd_bind("<<Drop>>", lambda e, t=i: self.on_drop_to_tier(e, t))
    
    def load_tier_images(self, container, tier):
        """加载等级中的图片"""
        for img_info in tier.get("images", []):
            try:
                img_path = os.path.join(self.images_dir, img_info["filename"])
                if os.path.exists(img_path):
                    # 加载并调整图片大小
                    img = Image.open(img_path)
                    img = img.resize((70, 70), Image.LANCZOS)  # 减小图片大小
                    photo = ImageTk.PhotoImage(img)
                    
                    # 创建图片框架
                    img_frame = ttk.Frame(container)
                    img_frame.pack(side="left", padx=2, pady=2)
                    
                    # 显示图片
                    lbl = tk.Label(img_frame, image=photo)
                    lbl.image = photo  # 保持引用
                    lbl.pack()
                    
                    # 设置拖放功能
                    lbl.bind("<ButtonPress-1>", lambda e, f=img_frame, i=img_info: self.app.start_drag(e, f, i))
            except Exception as e:
                print(f"加载图片错误: {str(e)}")
    
    def on_drop_to_tier(self, event, tier_index):
        """处理拖放到等级的事件（支持外部文件拖放）"""
        try:
            # 获取拖放的文件路径
            if isinstance(event.data, str):
                files = event.data.split('} {')
                # 修复路径格式
                files = [f.replace('{', '').replace('}', '') for f in files]
            else:
                files = event.data
            
            # 处理每个文件
            for file_path in files:
                # 检查是否为图片文件
                if self.app.image_processor.is_valid_image(file_path):
                    # 添加到应用并移动到指定等级
                    img_info = self.app.image_processor.add_image_from_path(file_path)
                    if img_info:
                        self.app.move_image_to_tier(img_info, tier_index)
            
            # 刷新界面
            self.refresh_tiers(self.app.tiers)
        except Exception as e:
            print(f"处理拖放文件错误: {str(e)}")
            import traceback
            traceback.print_exc()


class RepositoryFrame(ttk.LabelFrame):
    """图片仓库框架"""
    def __init__(self, parent, app, repository_images, images_dir, tkdnd_available, dnd_files):
        super().__init__(parent, text="图片仓库")
        self.app = app
        self.repository_images = repository_images
        self.images_dir = images_dir
        self.tkdnd_available = tkdnd_available
        self.dnd_files = dnd_files
        
        self.setup_repository_area()
    
    def setup_repository_area(self):
        """设置图片仓库区域"""
        # 创建一个画布和滚动条
        self.repo_canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.repo_canvas.yview)
        self.repo_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.repo_canvas.pack(side="left", fill="both", expand=True)
        
        # 创建一个框架来容纳所有图片
        self.repo_container = ttk.Frame(self.repo_canvas)
        self.repo_canvas_window = self.repo_canvas.create_window((0, 0), window=self.repo_container, anchor="nw")
        
        # 绑定事件以调整画布大小
        self.repo_container.bind("<Configure>", self.on_repo_container_configure)
        self.repo_canvas.bind("<Configure>", self.on_repo_canvas_configure)
        
        # 添加按钮 - 使用更紧凑的样式
        add_btn_frame = ttk.Frame(self)
        add_btn_frame.pack(side="bottom", fill="x", padx=5, pady=3)
        
        add_btn = tk.Button(add_btn_frame, text="添加图片", command=self.app.add_images,
                          bg="#4CAF50", fg="white", font=("Arial", 10),
                          relief=tk.RAISED, padx=10, pady=3)
        add_btn.pack(side="right", padx=5)
        
        # 加载仓库图片
        self.refresh_repository(self.repository_images)
        
        # 设置为可放置区域，支持外部文件拖放
        if self.tkdnd_available:
            self.repo_canvas.drop_target_register(self.dnd_files)
            self.repo_canvas.dnd_bind('<<Drop>>', self.on_drop_to_repository)
    
    def on_repo_container_configure(self, event):
        """当仓库容器大小改变时调整画布滚动区域"""
        self.repo_canvas.configure(scrollregion=self.repo_canvas.bbox("all"))
    
    def on_repo_canvas_configure(self, event):
        """当画布大小改变时调整内部窗口大小"""
        self.repo_canvas.itemconfig(self.repo_canvas_window, width=event.width)
    
    def refresh_repository(self, repository_images):
        """刷新图片仓库"""
        self.repository_images = repository_images
        
        # 清除现有内容
        for widget in self.repo_container.winfo_children():
            widget.destroy()
        
        # 创建网格布局
        row, col = 0, 0
        max_cols = 3  # 每行最多显示的图片数
        
        for img_info in self.repository_images:
            try:
                img_path = os.path.join(self.images_dir, img_info["filename"])
                if os.path.exists(img_path):
                    # 加载并调整图片大小
                    img = Image.open(img_path)
                    img = img.resize((70, 70), Image.LANCZOS)  # 减小图片大小
                    photo = ImageTk.PhotoImage(img)
                    
                    # 创建图片框架
                    img_frame = ttk.Frame(self.repo_container)
                    img_frame.grid(row=row, column=col, padx=5, pady=5)
                    
                    # 显示图片
                    lbl = tk.Label(img_frame, image=photo)
                    lbl.image = photo  # 保持引用
                    lbl.pack()
                    
                    # 设置拖放功能
                    lbl.bind("<ButtonPress-1>", lambda e, f=img_frame, i=img_info: self.app.start_drag(e, f, i))
                    
                    # 更新行列位置
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
            except Exception as e:
                print(f"加载仓库图片错误: {str(e)}")
    
    def on_drop_to_repository(self, event):
        """处理拖放到仓库的事件（支持外部文件拖放）"""
        try:
            # 获取拖放的文件路径
            if isinstance(event.data, str):
                files = event.data.split('} {')
                # 修复路径格式
                files = [f.replace('{', '').replace('}', '') for f in files]
            else:
                files = event.data
            
            # 处理每个文件
            for file_path in files:
                # 检查是否为图片文件
                if self.app.image_processor.is_valid_image(file_path):
                    # 添加到仓库
                    img_info = self.app.image_processor.add_image_from_path(file_path)
                    if img_info and img_info not in self.app.repository_images:
                        self.app.repository_images.append(img_info)
            
            # 刷新仓库显示
            self.refresh_repository(self.app.repository_images)
            
            # 保存配置
            self.app.save_config()
        except Exception as e:
            print(f"处理拖放文件错误: {str(e)}")