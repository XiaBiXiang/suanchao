"""
数据库初始化脚本
在 PostgreSQL 中创建 suanchao 数据库
"""

import subprocess
import sys


def create_database():
    """创建 suanchao 数据库"""
    try:
        # 尝试使用 createdb 命令
        result = subprocess.run(
            ["createdb", "suanchao", "-U", "postgres"], capture_output=True, text=True
        )
        if result.returncode == 0:
            print("数据库 suanchao 创建成功!")
            return True
        else:
            print(f"创建数据库失败: {result.stderr}")
            return False
    except FileNotFoundError:
        print("错误: 未找到 PostgreSQL 命令行工具 (createdb)")
        print("请确保 PostgreSQL 已安装并配置在 PATH 中")
        print("\n可选方案:")
        print(
            "1. 使用 Docker: docker run -d -e POSTGRES_PASSWORD=postgres -p 5432:5432 --name postgres postgres"
        )
        print(
            "2. 使用 Homebrew: brew install postgresql && brew services start postgresql"
        )
        return False


if __name__ == "__main__":
    create_database()
