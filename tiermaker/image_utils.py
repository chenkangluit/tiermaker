#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TierMaker - 排行榜制作工具
图片处理模块 - 处理图片的加载、保存和操作
"""

import os
import shutil
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont


class ImageProcessor:
    """图片处理类，负责处理图片的加载、保存和操作"""
    
    def __init__(self, images_dir):
        """初始化图片处理器
        
        Args:
            images_dir: 图片存储目录
        """
        self.images_dir = images_dir
    
    def is_valid_image(self, file_path):
        """检查文件是否为有效的图片文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否为有效的图片文件
        """
        valid_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp")
        return file_path.lower().endswith(valid_extensions)
    
    def add_image_from_path(self, file_path):
        """从文件路径添加图片到仓库
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            dict: 图片信息，如果添加失败则返回None
        """
        try:
            # 检查文件是否为有效的图片文件
            if not self.is_valid_image(file_path):
                messagebox.showerror("添加图片错误", f"不支持的图片格式: {file_path}")
                return None
                
            # 生成唯一文件名
            base_name = os.path.basename(file_path)
            # 获取当前图片数量作为前缀
            existing_images = [f for f in os.listdir(self.images_dir) if os.path.isfile(os.path.join(self.images_dir, f))]
            new_filename = f"{len(existing_images)}_{base_name}"
            dest_path = os.path.join(self.images_dir, new_filename)
            
            # 复制文件到应用目录
            shutil.copy2(file_path, dest_path)
            
            # 返回图片信息
            return {"filename": new_filename, "original_name": base_name}
        except Exception as e:
            messagebox.showerror("添加图片错误", f"无法添加图片 {file_path}: {str(e)}")
            return None
    
    def load_image(self, img_info, size=(70, 70)):
        """加载图片并调整大小
        
        Args:
            img_info: 图片信息字典
            size: 图片大小，默认为(70, 70)
            
        Returns:
            PhotoImage: 加载的图片，如果加载失败则返回None
        """
        try:
            img_path = os.path.join(self.images_dir, img_info["filename"])
            if os.path.exists(img_path):
                img = Image.open(img_path)
                img = img.resize(size, Image.LANCZOS)
                return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"加载图片错误: {str(e)}")
        return None
    
    def hex_to_rgb(self, hex_color):
        """将十六进制颜色转换为RGB
        
        Args:
            hex_color: 十六进制颜色字符串
            
        Returns:
            tuple: RGB颜色元组
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def export_tierlist_as_image(self, tiers, tiers_canvas):
        """导出排行榜为图片
        
        Args:
            tiers: 等级列表
            tiers_canvas: 等级区域画布
        """
        # 获取保存路径
        filetypes = [("PNG图片", "*.png")]
        filename = filedialog.asksaveasfilename(
            title="保存排行榜图片",
            defaultextension=".png",
            filetypes=filetypes
        )
        
        if not filename:
            return
        
        try:
            # 计算实际需要的高度
            tier_height = 80  # 每个等级的高度
            total_height = tier_height * len(tiers)  # 精确计算总高度，不添加额外空间
            
            # 创建一个新的图像
            width = tiers_canvas.winfo_width()
            
            # 确保有最小尺寸
            width = max(width, 800)
            
            img = Image.new("RGB", (width, total_height), color="white")
            
            # 在图像上绘制每个等级
            draw_y = 0
            for tier in tiers:
                # 绘制等级标签背景
                for y in range(draw_y, draw_y + tier_height):
                    for x in range(0, 50):  # 减小宽度与界面一致
                        r, g, b = self.hex_to_rgb(tier["color"])
                        img.putpixel((x, y), (r, g, b))
                
                # 绘制等级名称
                draw = ImageDraw.Draw(img)
                try:
                    # 尝试加载字体
                    font = ImageFont.truetype("arial.ttf", 20)
                except:
                    # 如果无法加载，使用默认字体
                    font = ImageFont.load_default()
                
                # 计算文本位置，使其居中
                text_width = font.getsize(tier["name"])[0] if hasattr(font, 'getsize') else 20
                text_x = (50 - text_width) // 2  # 调整为新的宽度
                text_y = draw_y + (tier_height - 20) // 2  # 垂直居中
                draw.text((text_x, text_y), tier["name"], fill="black", font=font)
                
                # 加载并绘制该等级的图片
                draw_x = 70
                for img_info in tier.get("images", []):
                    try:
                        img_path = os.path.join(self.images_dir, img_info["filename"])
                        if os.path.exists(img_path):
                            tier_img = Image.open(img_path)
                            tier_img = tier_img.resize((70, 70), Image.LANCZOS)  # 调整为新的图片大小
                            img.paste(tier_img, (draw_x, draw_y + (tier_height - 70) // 2))  # 垂直居中
                            draw_x += 80  # 减小间距
                    except Exception as e:
                        print(f"导出图片错误: {str(e)}")
                
                # 移动到下一个等级位置，不添加额外间距
                draw_y += tier_height
            
            # 保存图像
            img.save(filename)
            messagebox.showinfo("导出成功", f"排行榜已成功导出为图片: {filename}")
        except Exception as e:
            messagebox.showerror("导出错误", f"导出图片时出错: {str(e)}")