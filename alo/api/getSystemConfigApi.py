import platform
import psutil
import socket
import subprocess
from . import api
import os
from flask_restful import Resource
from flask import jsonify

class GetSystemConfigApi(Resource):
    def get(self):
        try:
            # 1. 获取操作系统信息
            os_info = self.get_os_info()

            # 2. 获取 CPU 信息
            cpu_info = self.get_cpu_info()

            # 3. 获取 内存 信息
            memory_info = self.get_memory_info()

            # 4. 获取 GPU 信息 (重点：支持 Nvidia 显卡)
            gpu_info = self.get_gpu_info()

            # 5. 获取网络连通性
            network_status = self.get_network_status()

            data = {
                "os_version": os_info,
                "cpu_config": cpu_info,
                "memory_config": memory_info,
                "gpu_config": gpu_info,
                "network_status": network_status
            }

            return {"code": 200, "msg": "获取配置成功", "data": data}

        except Exception as e:
            print(f"获取系统配置失败: {e}")
            return {"code": 500, "msg": f"服务器内部错误: {str(e)}", "data": None}

    def get_os_info(self):
        """获取操作系统版本"""
        system = platform.system()
        if system == "Windows":
            return f"Windows {platform.release()} ({platform.version()})"
        elif system == "Linux":
            try:
                # 尝试获取具体的 Linux 发行版 (如 Ubuntu 20.04)
                # Python 3.8+ 推荐使用 distro 库，这里用读取文件的方式做通用兼容
                with open("/etc/os-release") as f:
                    lines = f.readlines()
                    name = next((line.split("=")[1].strip().strip('"') for line in lines if line.startswith("PRETTY_NAME=")), "Linux")
                    return name
            except:
                return f"Linux {platform.release()}"
        else:
            return f"{system} {platform.release()}"

    def get_cpu_info(self):
        """获取CPU核心数和型号"""
        physical_cores = psutil.cpu_count(logical=False)
        total_cores = psutil.cpu_count(logical=True)
        # 获取CPU名称 (Windows和Linux方法不同)
        cpu_name = platform.processor()
        return f"{cpu_name} | 物理核: {physical_cores}, 逻辑核: {total_cores}"

    def get_memory_info(self):
        """获取内存总量和使用率"""
        mem = psutil.virtual_memory()
        total_gb = round(mem.total / (1024 ** 3), 2)
        available_gb = round(mem.available / (1024 ** 3), 2)
        return f"{available_gb} GB | {total_gb} GB ({mem.percent}%)"

    def get_gpu_info(self):
        """通过 nvidia-smi 获取 GPU 信息"""
        try:
            # 执行 nvidia-smi 命令查询显卡名称和显存
            # csv格式: index, name, total_memory
            result = subprocess.check_output(
                ['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'],
                encoding='utf-8'
            )
            # 处理多张显卡的情况
            gpus = [line.strip() for line in result.strip().split('\n')]
            return " / ".join(gpus) # 返回如: "RTX 3090, 24576 MiB / RTX 3090, 24576 MiB"
        except FileNotFoundError:
            return "未检测到 NVIDIA 驱动或 nvidia-smi 命令"
        except Exception:
            return "无独立显卡 / 集成显卡"

    def get_network_status(self):
        """检测网络是否畅通 (Ping 百度或谷歌DNS)"""
        try:
            socket.create_connection(("172.20.110.176", 80), timeout=3)
            return "畅通 (已连接互联网)"
        except OSError:
            return "网络异常 / 离线"

# 记得在你的 Flask app 中注册这个资源
api.add_resource(GetSystemConfigApi, '/v1.0/prediction/systemconfig')