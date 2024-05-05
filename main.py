import ntplib
from datetime import datetime
import sys
import subprocess
import time
import pytz
import os
import argparse

# 定义NTP服务器列表
ntp_servers = ['cn.ntp.org.cn','ntp.tencent.com','ntp.ntsc.ac.cn', 'ntp.tuna.tsinghua.edu.cn','time.nist.gov']

# 获取NTP服务器时间和延迟的函数
def get_ntp_time_and_delay(server):
    client = ntplib.NTPClient()
    start = time.time()
    try:
        response = client.request(server, version=3)
        end = time.time()
        delay = (end - start) * 1000 / 2  # 延迟转换为毫秒
        print(f'正在测试{server}延迟...')
        print(f'延迟为{delay:.2f} ms')
        return response.tx_time, delay
    except Exception as e:
        print(f'测试{server}失败：{e}')
        return None, None

# 测试所有NTP服务器并选择延迟最低的服务器
def choose_best_ntp_server():
    min_delay = float('inf')
    best_time = None
    best_server = None
    for server in ntp_servers:
        ntp_time, delay = get_ntp_time_and_delay(server)
        if ntp_time is not None and delay < min_delay:
            min_delay = delay
            best_time = ntp_time
            best_server = server
    if best_server:
        print(f'当前使用{best_server}服务器。')
    return best_server, best_time

# 设置系统时间的函数
def set_system_time(ntp_time):
    if ntp_time is not None:
        # 将NTP时间戳转换为Asia/Shanghai时区
        shanghai_tz = pytz.timezone('Asia/Shanghai')
        localized_time = datetime.fromtimestamp(ntp_time, shanghai_tz)
        formatted_time = localized_time.strftime('%Y-%m-%d %H:%M:%S')
        
        if sys.platform.startswith('win'):
            # Windows系统的时间设置命令
            subprocess.run(f'date {formatted_time[:10]} && time {formatted_time[11:]}', shell=True)
        elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            # Linux和macOS系统的时间设置命令
            subprocess.run(f'sudo date -s "{formatted_time}"', shell=True)
    else:
        print('未获取到有效的NTP时间戳。')

# 主程序
if __name__ == '__main__':
    print('SCB校时程序 V1.0.0 by 云港网络(www.sunzishaokao.com)')
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='SCB校时程序 V1.0.0 by 云港网络(www.sunzishaokao.com)')
    parser.add_argument('-s', '--server', help='指定NTP服务器', default=None)
    args = parser.parse_args()

    # 如果指定了服务器，则直接使用该服务器
    if args.server:
        print(f'正在使用指定的服务器: {args.server}')
        ntp_time, delay = get_ntp_time_and_delay(args.server)
        if ntp_time:
            set_system_time(ntp_time)
            print('系统时间已校准')
        else:
            print('无法从指定的服务器获取时间。')
    else:
        # 如果没有指定服务器，则选择延迟最低的服务器
        best_server, best_time = choose_best_ntp_server()
        if best_time:
            set_system_time(best_time)
            print('系统时间已校准')
        else:
            print('无法获取NTP服务器时间，请检查网络连接。')

    # 暂停，等待用户按键继续
    print(os.system('pause'))