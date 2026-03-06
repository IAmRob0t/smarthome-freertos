#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import socket
import threading
import time


def now():
    return time.strftime("%H:%M:%S")


class UdpConsole:
    def __init__(self, listen_ip, listen_port, board_ip=None, board_port=1234):
        self.listen_addr = (listen_ip, listen_port)
        self.target_addr = (board_ip, board_port) if board_ip else None
        self.last_sender = None
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.listen_addr)
        self.sock.settimeout(0.5)

    def recv_loop(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(2048)
            except socket.timeout:
                continue
            except OSError:
                break
            self.last_sender = addr
            text = data.decode("utf-8", errors="replace")
            print(f"\n[{now()}] RX from {addr[0]}:{addr[1]} -> {text}")

    def send_text(self, text):
        addr = self.target_addr or self.last_sender
        if not addr:
            print("未设置目标地址。请先使用: target <board_ip> <board_port>")
            return
        self.sock.sendto(text.encode("utf-8"), addr)
        print(f"[{now()}] TX to {addr[0]}:{addr[1]} <- {text}")

    @staticmethod
    def build_cmd(dev, status):
        return json.dumps(
            {"dev": dev, "status": str(status)},
            ensure_ascii=False,
            separators=(",", ":"),
        )

    def run(self):
        th = threading.Thread(target=self.recv_loop, daemon=True)
        th.start()

        print(f"UDP监听中: {self.listen_addr[0]}:{self.listen_addr[1]}")
        if self.target_addr:
            print(f"默认目标: {self.target_addr[0]}:{self.target_addr[1]}")
        print("输入 help 查看命令。")

        while self.running:
            try:
                line = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                line = "quit"

            if not line:
                continue
            if line in ("q", "quit", "exit"):
                self.running = False
                break
            if line == "help":
                self.print_help()
                continue
            if line.startswith("target "):
                self.cmd_target(line)
                continue
            if line.startswith("send "):
                self.send_text(line[5:])
                continue

            # 快捷命令
            quick = {
                "lamp1 on": self.build_cmd("lamp1", 1),
                "lamp1 off": self.build_cmd("lamp1", 0),
                "lamp1 toggle": self.build_cmd("lamp1", 2),
                "lamp2 on": self.build_cmd("lamp2", 1),
                "lamp2 off": self.build_cmd("lamp2", 0),
                "lamp2 toggle": self.build_cmd("lamp2", 2),
                "fan on": self.build_cmd("fan", 1),
                "fan off": self.build_cmd("fan", 0),
                "home in": self.build_cmd("home", 0),
                "home out": self.build_cmd("home", 1),
            }
            if line in quick:
                self.send_text(quick[line])
            else:
                print("未知命令，输入 help 查看可用命令。")

        self.sock.close()
        print("已退出。")

    def cmd_target(self, line):
        parts = line.split()
        if len(parts) != 3:
            print("用法: target <board_ip> <board_port>")
            return
        ip = parts[1]
        try:
            port = int(parts[2])
        except ValueError:
            print("端口必须是数字")
            return
        self.target_addr = (ip, port)
        print(f"目标已设置: {ip}:{port}")

    @staticmethod
    def print_help():
        print(
            "\n可用命令:\n"
            "  help\n"
            "  quit | exit\n"
            "  target <board_ip> <board_port>\n"
            "  send <任意字符串>\n"
            "  lamp1 on|off|toggle\n"
            "  lamp2 on|off|toggle\n"
            "  fan on|off\n"
            "  home in|out\n"
            "\n说明:\n"
            "  1) 板端 JSON 示例: {\"dev\":\"lamp1\",\"status\":\"1\"}\n"
            "  2) 如果未设置 target，会尝试发给最近一次收到数据的来源地址。\n"
        )


def main():
    parser = argparse.ArgumentParser(description="Simple UDP console for STM32/ESP8266 demo")
    parser.add_argument("--listen-ip", default="0.0.0.0", help="本机监听IP，默认0.0.0.0")
    parser.add_argument("--listen-port", type=int, default=8080, help="本机监听端口，默认8080")
    parser.add_argument("--board-ip", default=None, help="开发板IP（可选）")
    parser.add_argument("--board-port", type=int, default=1234, help="开发板UDP端口，默认1234")
    args = parser.parse_args()

    app = UdpConsole(
        listen_ip=args.listen_ip,
        listen_port=args.listen_port,
        board_ip=args.board_ip,
        board_port=args.board_port,
    )
    app.run()


if __name__ == "__main__":
    main()
