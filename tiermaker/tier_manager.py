#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TierMaker - 排行榜制作工具
等级管理模块 - 处理等级的管理和操作
"""

import tkinter as tk
from tkinter import ttk, messagebox, colorchooser


class TierManagerDialog(tk.Toplevel):
    """等级管理对话框"""
    def __init__(self, parent, tiers):
        super().__init__(parent)
        self.title("管理等级")
        self.geometry("400x700")
        self.resizable(False, True)  # 允许垂直方向调整大小
        self.transient(parent)  # 设置为父窗口的临时窗口
        self.grab_set()  # 模态对话框
        
        self.parent = parent
        self.tiers = tiers.copy()  # 复制一份，以便取消时不影响原数据
        self.result = None  # 对话框结果
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建对话框控件"""
        # 设置最小窗口大小，确保所有元素可见
        self.minsize(400, 550)
        
        # 主容器框架
        main_container = ttk.Frame(self)
        main_container.pack(fill="both", expand=True)
        
        # 等级列表框架
        list_frame = ttk.LabelFrame(main_container, text="等级列表")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 创建列表和滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.tier_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=15)
        self.tier_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tier_listbox.yview)
        
        # 填充列表
        self.refresh_tier_list()
        
        # 选择事件
        self.tier_listbox.bind("<<ListboxSelect>>", self.on_tier_select)
        
        # 等级编辑框架
        edit_frame = ttk.LabelFrame(main_container, text="等级编辑")
        edit_frame.pack(fill="x", padx=10, pady=10)
        
        # 名称输入
        name_frame = ttk.Frame(edit_frame)
        name_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(name_frame, text="名称:").pack(side="left")
        self.name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.name_var).pack(side="left", fill="x", expand=True, padx=5)
        
        # 颜色选择
        color_frame = ttk.Frame(edit_frame)
        color_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(color_frame, text="颜色:").pack(side="left")
        self.color_var = tk.StringVar()
        ttk.Entry(color_frame, textvariable=self.color_var).pack(side="left", fill="x", expand=True, padx=5)
        
        self.color_preview = tk.Frame(color_frame, width=30, height=20, bg="#FFFFFF")
        self.color_preview.pack(side="left", padx=5)
        
        # 使用更紧凑的按钮样式
        tk.Button(color_frame, text="选择颜色", command=self.choose_color,
                 bg="#607D8B", fg="white", font=("Arial", 10),
                 relief=tk.RAISED, padx=10, pady=3).pack(side="left", padx=5)
        
        # 按钮框架
        button_frame = ttk.Frame(edit_frame)
        button_frame.pack(fill="x", padx=5, pady=10)
        
        # 使用更紧凑的按钮样式
        tk.Button(button_frame, text="添加", command=self.add_tier, 
                 bg="#2196F3", fg="white", font=("Arial", 10),
                 relief=tk.RAISED, padx=10, pady=3).pack(side="left", padx=5)
        tk.Button(button_frame, text="更新", command=self.update_tier,
                 bg="#FF9800", fg="white", font=("Arial", 10),
                 relief=tk.RAISED, padx=10, pady=3).pack(side="left", padx=5)
        tk.Button(button_frame, text="删除", command=self.delete_tier,
                 bg="#f44336", fg="white", font=("Arial", 10),
                 relief=tk.RAISED, padx=10, pady=3).pack(side="left", padx=5)
        
        # 上移下移按钮
        move_frame = ttk.Frame(edit_frame)
        move_frame.pack(fill="x", padx=5, pady=5)
        
        # 使用更紧凑的按钮样式
        tk.Button(move_frame, text="上移", command=self.move_up,
                 bg="#9C27B0", fg="white", font=("Arial", 10),
                 relief=tk.RAISED, padx=10, pady=3).pack(side="left", padx=5)
        tk.Button(move_frame, text="下移", command=self.move_down,
                 bg="#9C27B0", fg="white", font=("Arial", 10),
                 relief=tk.RAISED, padx=10, pady=3).pack(side="left", padx=5)
        
        # 底部按钮 - 使用更紧凑的样式
        bottom_frame = tk.Frame(self, bg="#E0E0E0")
        bottom_frame.pack(side="bottom", fill="x", padx=10, pady=5)
        
        # 使用更小、更紧凑的按钮
        cancel_btn = tk.Button(bottom_frame, text="取消", command=self.on_cancel,
                          bg="#f44336", fg="white", font=("Arial", 11),
                          relief=tk.RAISED, padx=15, pady=5)
        cancel_btn.pack(side="right", padx=10, pady=8)
        
        ok_btn = tk.Button(bottom_frame, text="确定", command=self.on_ok,
                          bg="#4CAF50", fg="white", font=("Arial", 11),
                          relief=tk.RAISED, padx=15, pady=5)
        ok_btn.pack(side="right", padx=10, pady=8)
    
    def refresh_tier_list(self):
        """刷新等级列表"""
        self.tier_listbox.delete(0, tk.END)
        for tier in self.tiers:
            self.tier_listbox.insert(tk.END, f"{tier['name']} ({tier['color']})")
    
    def on_tier_select(self, event):
        """当选择等级时更新编辑区域"""
        selection = self.tier_listbox.curselection()
        if selection:
            index = selection[0]
            tier = self.tiers[index]
            self.name_var.set(tier["name"])
            self.color_var.set(tier["color"])
            self.color_preview.config(bg=tier["color"])
    
    def choose_color(self):
        """选择颜色"""
        color = self.color_var.get()
        if not color.startswith("#"):
            color = "#FFFFFF"
        
        # 使用颜色选择器
        color_code = colorchooser.askcolor(color)
        
        if color_code[1]:  # 如果用户选择了颜色
            self.color_var.set(color_code[1])
            self.color_preview.config(bg=color_code[1])
    
    def add_tier(self):
        """添加新等级"""
        name = self.name_var.get().strip()
        color = self.color_var.get().strip()
        
        if not name:
            messagebox.showerror("错误", "请输入等级名称")
            return
        
        if not color.startswith("#") or len(color) != 7:
            messagebox.showerror("错误", "颜色格式无效，请使用十六进制格式，如 #FF0000")
            return
        
        # 添加新等级
        self.tiers.append({"name": name, "color": color, "images": []})
        
        # 刷新列表
        self.refresh_tier_list()
        
        # 清空输入
        self.name_var.set("")
        self.color_var.set("#FFFFFF")
        self.color_preview.config(bg="#FFFFFF")
    
    def update_tier(self):
        """更新选中的等级"""
        selection = self.tier_listbox.curselection()
        if not selection:
            messagebox.showerror("错误", "请先选择一个等级")
            return
        
        index = selection[0]
        name = self.name_var.get().strip()
        color = self.color_var.get().strip()
        
        if not name:
            messagebox.showerror("错误", "请输入等级名称")
            return
        
        if not color.startswith("#") or len(color) != 7:
            messagebox.showerror("错误", "颜色格式无效，请使用十六进制格式，如 #FF0000")
            return
        
        # 更新等级
        self.tiers[index]["name"] = name
        self.tiers[index]["color"] = color
        
        # 刷新列表
        self.refresh_tier_list()
    
    def delete_tier(self):
        """删除选中的等级"""
        selection = self.tier_listbox.curselection()
        if not selection:
            messagebox.showerror("错误", "请先选择一个等级")
            return
        
        index = selection[0]
        
        # 确认删除
        if messagebox.askyesno("确认删除", f"确定要删除等级 '{self.tiers[index]['name']}' 吗？这将移除该等级中的所有图片。"):
            # 删除等级
            del self.tiers[index]
            
            # 刷新列表
            self.refresh_tier_list()
            
            # 清空输入
            self.name_var.set("")
            self.color_var.set("#FFFFFF")
            self.color_preview.config(bg="#FFFFFF")
    
    def move_up(self):
        """上移选中的等级"""
        selection = self.tier_listbox.curselection()
        if not selection:
            messagebox.showerror("错误", "请先选择一个等级")
            return
        
        index = selection[0]
        if index > 0:
            # 交换位置
            self.tiers[index], self.tiers[index-1] = self.tiers[index-1], self.tiers[index]
            
            # 刷新列表
            self.refresh_tier_list()
            
            # 更新选择
            self.tier_listbox.selection_clear(0, tk.END)
            self.tier_listbox.selection_set(index-1)
            self.tier_listbox.see(index-1)
            self.on_tier_select(None)
    
    def move_down(self):
        """下移选中的等级"""
        selection = self.tier_listbox.curselection()
        if not selection:
            messagebox.showerror("错误", "请先选择一个等级")
            return
        
        index = selection[0]
        if index < len(self.tiers) - 1:
            # 交换位置
            self.tiers[index], self.tiers[index+1] = self.tiers[index+1], self.tiers[index]
            
            # 刷新列表
            self.refresh_tier_list()
            
            # 更新选择
            self.tier_listbox.selection_clear(0, tk.END)
            self.tier_listbox.selection_set(index+1)
            self.tier_listbox.see(index+1)
            self.on_tier_select(None)
    
    def on_ok(self):
        """确定按钮事件"""
        # 将修改后的等级列表应用到父窗口
        self.parent.tiers = self.tiers.copy()
        
        # 关闭对话框
        self.destroy()
    
    def on_cancel(self):
        """取消按钮事件"""
        self.destroy()