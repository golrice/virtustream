import socket
import time
import logging
import signal
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('TCP_Listener')

# 全局变量，用于控制程序运行
running = True

def signal_handler(sig, frame):
    """处理Ctrl+C信号"""
    global running
    print("Ctrl+C detected, shutting down gracefully...")
    running = False

def listen_for_moves():
    global running
    
    # 注册Ctrl+C信号处理
    signal.signal(signal.SIGINT, signal_handler)
    print("Listening for moves on port 12340... (Press Ctrl+C to stop)")
    
    try:
        
        # client_socket.connect(('localhost', 12340))
        while running:
            host = '127.0.0.1'  # 或 'localhost'
            port = 12340
            total_time = 5      # 总监听时间（5秒）
            poll_interval = 0.2 # 轮询间隔（0.2秒）
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((host, port))
                client_socket.settimeout(poll_interval)  # 每次 recv() 最多等 0.2 秒

                start_time = time.time()
                while time.time() - start_time < total_time:
                    try:
                        data = client_socket.recv(1024)
                        if data:
                            print(f"[{time.time():.3f}] Received: {data.decode()}")
                    except socket.timeout:
                        continue  # 0.2秒内没数据，继续循环
                    except Exception as e:
                        print(f"Error: {e}")
                        break

            except ConnectionRefusedError:
                print("Error: Server not available.")
            finally:
                client_socket.close()
                print("Connection closed.")
                
                
    except Exception as e:
        print(f"Failed to connect to client: {e}")
    finally:
        client_socket.close()
        print("Server socket closed")
        sys.exit(0)

if __name__ == "__main__":
    listen_for_moves()
# import socket
# import time

# def listen_for_moves():
#     host = '127.0.0.1'  # 或 'localhost'
#     port = 12340
#     total_time = 5      # 总监听时间（5秒）
#     poll_interval = 0.2 # 轮询间隔（0.2秒）

#     print(f"Listening for moves on {host}:{port} for {total_time} seconds...")

#     try:
#         client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         client_socket.connect((host, port))
#         client_socket.settimeout(poll_interval)  # 每次 recv() 最多等 0.2 秒

#         start_time = time.time()
#         while time.time() - start_time < total_time:
#             try:
#                 data = client_socket.recv(1024)
#                 if data:
#                     print(f"[{time.time():.3f}] Received: {data.decode()}")
#             except socket.timeout:
#                 continue  # 0.2秒内没数据，继续循环
#             except Exception as e:
#                 print(f"Error: {e}")
#                 break

#     except ConnectionRefusedError:
#         print("Error: Server not available.")
#     finally:
#         client_socket.close()
#         print("Connection closed.")

# if __name__ == "__main__":
#     listen_for_moves()