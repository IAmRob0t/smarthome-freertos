#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import queue
import socket
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox


def ts():
    return time.strftime("%H:%M:%S")


class UdpGuiApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("SmartHome UDP 控制台")
        self.root.geometry("860x620")

        self.recv_queue = queue.Queue()
        self.sock = None
        self.recv_thread = None
        self.running = False
        self.last_sender = None

        self.listen_ip_var = tk.StringVar(value="0.0.0.0")
        self.listen_port_var = tk.StringVar(value="18080")
        self.board_ip_var = tk.StringVar(value="")
        self.board_port_var = tk.StringVar(value="1234")
        self.status_var = tk.StringVar(value="未启动")

        self._build_ui()
        self._poll_queue()

    def _build_ui(self):
        frame_top = ttk.LabelFrame(self.root, text="连接配置")
        frame_top.pack(fill="x", padx=10, pady=8)

        ttk.Label(frame_top, text="监听IP").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        ttk.Entry(frame_top, textvariable=self.listen_ip_var, width=12).grid(row=0, column=1, padx=6, pady=6)
        ttk.Label(frame_top, text="监听端口").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        ttk.Entry(frame_top, textvariable=self.listen_port_var, width=8).grid(row=0, column=3, padx=6, pady=6)
        ttk.Label(frame_top, text="设备IP").grid(row=0, column=4, padx=6, pady=6, sticky="w")
        ttk.Entry(frame_top, textvariable=self.board_ip_var, width=15).grid(row=0, column=5, padx=6, pady=6)
        ttk.Label(frame_top, text="设备端口").grid(row=0, column=6, padx=6, pady=6, sticky="w")
        ttk.Entry(frame_top, textvariable=self.board_port_var, width=8).grid(row=0, column=7, padx=6, pady=6)

        self.btn_start = ttk.Button(frame_top, text="启动", command=self.start_udp)
        self.btn_start.grid(row=0, column=8, padx=8, pady=6)
        self.btn_stop = ttk.Button(frame_top, text="停止", command=self.stop_udp, state="disabled")
        self.btn_stop.grid(row=0, column=9, padx=8, pady=6)

        ttk.Label(frame_top, text="状态:").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        ttk.Label(frame_top, textvariable=self.status_var, foreground="#005a9e").grid(row=1, column=1, columnspan=9, padx=6, pady=6, sticky="w")

        frame_ctrl = ttk.LabelFrame(self.root, text="控制按钮")
        frame_ctrl.pack(fill="x", padx=10, pady=8)

        buttons = [
            ("灯1 开", "lamp1", 1), ("灯1 关", "lamp1", 0), ("灯1 切换", "lamp1", 2),
            ("灯2 开", "lamp2", 1), ("灯2 关", "lamp2", 0), ("灯2 切换", "lamp2", 2),
            ("风扇 开", "fan", 1), ("风扇 关", "fan", 0),
            ("回家", "home", 0), ("离家", "home", 1),
        ]
        for i, (txt, dev, st) in enumerate(buttons):
            r, c = divmod(i, 5)
            ttk.Button(frame_ctrl, text=txt, command=lambda d=dev, s=st: self.send_json_cmd(d, s), width=14).grid(
                row=r, column=c, padx=6, pady=6
            )

        frame_send = ttk.LabelFrame(self.root, text="自定义发送")
        frame_send.pack(fill="x", padx=10, pady=8)
        self.custom_var = tk.StringVar(value='{"dev":"lamp1","status":"1"}')
        ttk.Entry(frame_send, textvariable=self.custom_var).pack(side="left", fill="x", expand=True, padx=6, pady=6)
        ttk.Button(frame_send, text="发送", command=self.send_custom).pack(side="left", padx=6, pady=6)

        frame_log = ttk.LabelFrame(self.root, text="收发日志")
        frame_log.pack(fill="both", expand=True, padx=10, pady=8)
        self.log = tk.Text(frame_log, height=20, wrap="word")
        self.log.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        sb = ttk.Scrollbar(frame_log, orient="vertical", command=self.log.yview)
        sb.pack(side="right", fill="y")
        self.log.configure(yscrollcommand=sb.set)
        ttk.Button(self.root, text="清空日志", command=lambda: self.log.delete("1.0", "end")).pack(anchor="e", padx=12, pady=(0, 10))

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _log(self, msg: str):
        self.log.insert("end", msg + "\n")
        self.log.see("end")

    def _target_addr(self):
        ip = self.board_ip_var.get().strip()
        if not ip:
            return self.last_sender
        try:
            port = int(self.board_port_var.get().strip())
        except ValueError:
            return None
        return (ip, port)

    def start_udp(self):
        if self.running:
            return
        try:
            listen_ip = self.listen_ip_var.get().strip() or "0.0.0.0"
            listen_port = int(self.listen_port_var.get().strip())
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((listen_ip, listen_port))
            self.sock.settimeout(0.5)
        except Exception as e:
            messagebox.showerror("启动失败", str(e))
            return

        self.running = True
        self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self.recv_thread.start()
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.status_var.set(f"监听中 {listen_ip}:{listen_port}")
        self._log(f"[{ts()}] UDP启动: {listen_ip}:{listen_port}")

    def stop_udp(self):
        if not self.running:
            return
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
        self.sock = None
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.status_var.set("已停止")
        self._log(f"[{ts()}] UDP已停止")

    def _recv_loop(self):
        while self.running and self.sock:
            try:
                data, addr = self.sock.recvfrom(2048)
            except socket.timeout:
                continue
            except Exception:
                break
            self.last_sender = addr
            text = data.decode("utf-8", errors="replace")
            self.recv_queue.put(f"[{ts()}] RX {addr[0]}:{addr[1]} -> {text}")

    def _poll_queue(self):
        while True:
            try:
                msg = self.recv_queue.get_nowait()
            except queue.Empty:
                break
            self._log(msg)
        self.root.after(120, self._poll_queue)

    def send_text(self, text: str):
        if not self.running or not self.sock:
            messagebox.showwarning("未启动", "请先点击“启动”")
            return
        addr = self._target_addr()
        if not addr:
            messagebox.showwarning("目标无效", "请填写正确的设备IP和端口")
            return
        try:
            self.sock.sendto(text.encode("utf-8"), addr)
            self._log(f"[{ts()}] TX {addr[0]}:{addr[1]} <- {text}")
        except Exception as e:
            messagebox.showerror("发送失败", str(e))

    def send_json_cmd(self, dev: str, status: int):
        payload = json.dumps({"dev": dev, "status": str(status)}, ensure_ascii=False, separators=(",", ":"))
        self.send_text(payload)

    def send_custom(self):
        self.send_text(self.custom_var.get().strip())

    def on_close(self):
        self.stop_udp()
        self.root.destroy()


def main():
    root = tk.Tk()
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    app = UdpGuiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

