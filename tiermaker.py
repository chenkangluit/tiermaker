#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TierMaker - 排行榜制作工具
启动脚本 - 应用程序入口点
"""

from tiermaker.main import TierMaker


def main():
    """启动TierMaker应用程序"""
    app = TierMaker()
    app.mainloop()


if __name__ == "__main__":
    main()