#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TierMaker - 排行榜制作工具
配置管理模块 - 处理配置的加载和保存
"""

import os
import json
from tkinter import messagebox


class ConfigManager:
    """配置管理类，负责处理配置文件的加载和保存"""
    
    def __init__(self):
        """初始化配置管理器"""
        # 创建数据存储目录
        self.app_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tiermaker_data")
        self.images_dir = os.path.join(self.app_dir, "images")
        self.config_file = os.path.join(self.app_dir, "config.json")
        
        self.ensure_directories()
    
    def ensure_directories(self):
        """确保应用所需的目录存在"""
        os.makedirs(self.app_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showerror("加载错误", f"无法加载配置文件: {str(e)}")
        return None
    
    def save_config(self, config):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("保存错误", f"无法保存配置文件: {str(e)}")
            return False