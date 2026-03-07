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


class Palette:
    BG = "#0F172A"
    PANEL = "#111827"
    CARD = "#1E293B"
    CARD_SOFT = "#23324A"
    TEXT = "#E5E7EB"
    MUTED = "#94A3B8"
    ACCENT = "#22D3EE"
    GOOD = "#34D399"
    WARN = "#F59E0B"
    BAD = "#F87171"
    TX = "#93C5FD"
    RX = "#86EFAC"


class UdpGuiApp:
    HISTORY_MAX = 80
    OFFLINE_TIMEOUT_S = 5

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("SmartHome 控制中心 - 答辩版")
        self.root.geometry("1180x760")
        self.root.minsize(1024, 680)
        self.root.configure(bg=Palette.BG)

        self.recv_queue = queue.Queue()
        self.sock = None
        self.recv_thread = None
        self.running = False
        self.last_sender = None
        self.last_rx_time = 0.0
        self.rx_packets = 0
        self.tx_packets = 0

        self.listen_ip_var = tk.StringVar(value="0.0.0.0")
        self.listen_port_var = tk.StringVar(value="18080")
        self.board_ip_var = tk.StringVar(value="")
        self.board_port_var = tk.StringVar(value="1234")
        self.status_var = tk.StringVar(value="未启动")
        self.network_badge_var = tk.StringVar(value="IDLE")
        self.custom_var = tk.StringVar(value='{"dev":"lamp1","status":"1"}')

        self.metrics = {"T": "--", "H": "--", "L": "--", "AQ": "--"}
        self.history = {"T": [], "H": [], "AQ": []}
        self.metric_value_labels = {}
        self.metric_hint_labels = {}

        self.device_states = {"lamp1": 0, "lamp2": 0, "fan": 0, "home": 0}
        self.device_badges = {}

        self._setup_styles()
        self._build_ui()
        self._poll_queue()
        self._heartbeat_tick()

    def _setup_styles(self):
        style = ttk.Style(self.root)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Header.TLabel", background=Palette.BG, foreground=Palette.TEXT, font=("Microsoft YaHei UI", 20, "bold"))
        style.configure("SubHeader.TLabel", background=Palette.BG, foreground=Palette.MUTED, font=("Microsoft YaHei UI", 10))
        style.configure("PanelTitle.TLabel", background=Palette.PANEL, foreground=Palette.TEXT, font=("Microsoft YaHei UI", 11, "bold"))
        style.configure("Accent.TButton", font=("Microsoft YaHei UI", 10, "bold"), padding=6)

    def _build_ui(self):
        header = tk.Frame(self.root, bg=Palette.BG, padx=16, pady=10)
        header.pack(fill="x")
        ttk.Label(header, text="SmartHome UDP 控制中心", style="Header.TLabel").pack(anchor="w")
        ttk.Label(header, text="实时监控 · 设备控制 · 趋势可视化", style="SubHeader.TLabel").pack(anchor="w")

        top = tk.Frame(self.root, bg=Palette.BG, padx=12, pady=6)
        top.pack(fill="x")

        config_panel = tk.Frame(top, bg=Palette.PANEL, padx=12, pady=10, highlightthickness=1, highlightbackground="#263548")
        config_panel.pack(side="left", fill="x", expand=True)
        tk.Label(config_panel, text="连接配置", bg=Palette.PANEL, fg=Palette.TEXT, font=("Microsoft YaHei UI", 11, "bold")).grid(
            row=0, column=0, columnspan=10, sticky="w", pady=(0, 8)
        )

        self._dark_label(config_panel, "监听IP").grid(row=1, column=0, padx=(0, 4), pady=4, sticky="w")
        self._entry(config_panel, self.listen_ip_var, 12).grid(row=1, column=1, padx=4, pady=4)
        self._dark_label(config_panel, "监听端口").grid(row=1, column=2, padx=(8, 4), pady=4, sticky="w")
        self._entry(config_panel, self.listen_port_var, 8).grid(row=1, column=3, padx=4, pady=4)
        self._dark_label(config_panel, "设备IP").grid(row=1, column=4, padx=(8, 4), pady=4, sticky="w")
        self._entry(config_panel, self.board_ip_var, 15).grid(row=1, column=5, padx=4, pady=4)
        self._dark_label(config_panel, "设备端口").grid(row=1, column=6, padx=(8, 4), pady=4, sticky="w")
        self._entry(config_panel, self.board_port_var, 8).grid(row=1, column=7, padx=4, pady=4)

        self.btn_start = ttk.Button(config_panel, text="启动监听", style="Accent.TButton", command=self.start_udp)
        self.btn_start.grid(row=1, column=8, padx=(10, 4), pady=4)
        self.btn_stop = ttk.Button(config_panel, text="停止", command=self.stop_udp, state="disabled")
        self.btn_stop.grid(row=1, column=9, padx=(4, 0), pady=4)

        self._dark_label(config_panel, "运行状态").grid(row=2, column=0, padx=0, pady=(8, 0), sticky="w")
        self.status_label = tk.Label(
            config_panel,
            textvariable=self.status_var,
            bg=Palette.PANEL,
            fg=Palette.ACCENT,
            font=("Consolas", 10, "bold"),
            anchor="w",
        )
        self.status_label.grid(row=2, column=1, columnspan=7, sticky="we", padx=4, pady=(8, 0))

        self.network_badge = tk.Label(
            config_panel,
            textvariable=self.network_badge_var,
            bg="#1D4ED8",
            fg="white",
            width=10,
            font=("Microsoft YaHei UI", 9, "bold"),
            padx=8,
            pady=3,
        )
        self.network_badge.grid(row=2, column=8, columnspan=2, sticky="e", padx=(8, 0), pady=(8, 0))

        middle = tk.Frame(self.root, bg=Palette.BG, padx=12, pady=6)
        middle.pack(fill="both", expand=True)
        middle.columnconfigure(0, weight=7)
        middle.columnconfigure(1, weight=4)
        middle.rowconfigure(0, weight=1)
        middle.rowconfigure(1, weight=1)

        self._build_metrics_panel(middle)
        self._build_controls_panel(middle)
        self._build_log_panel(middle)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _dark_label(self, parent, text):
        return tk.Label(parent, text=text, bg=Palette.PANEL, fg=Palette.MUTED, font=("Microsoft YaHei UI", 9))

    def _entry(self, parent, text_var, width):
        return tk.Entry(
            parent,
            textvariable=text_var,
            width=width,
            bg=Palette.CARD,
            fg=Palette.TEXT,
            insertbackground=Palette.TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#334155",
            highlightcolor=Palette.ACCENT,
            font=("Consolas", 10),
        )

    def _build_metrics_panel(self, parent):
        panel = tk.Frame(parent, bg=Palette.PANEL, padx=12, pady=10, highlightthickness=1, highlightbackground="#263548")
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
        tk.Label(panel, text="实时环境数据", bg=Palette.PANEL, fg=Palette.TEXT, font=("Microsoft YaHei UI", 11, "bold")).pack(anchor="w")

        cards = tk.Frame(panel, bg=Palette.PANEL)
        cards.pack(fill="x", pady=(10, 8))

        card_defs = [("T", "温度", "°C"), ("H", "湿度", "%RH"), ("L", "光照", "0/1"), ("AQ", "空气质量", "ADC")]
        for idx, (key, title, unit) in enumerate(card_defs):
            card = tk.Frame(cards, bg=Palette.CARD, padx=10, pady=10, highlightthickness=1, highlightbackground="#304357")
            card.grid(row=0, column=idx, sticky="nsew", padx=(0, 8 if idx < 3 else 0))
            cards.columnconfigure(idx, weight=1)
            tk.Label(card, text=title, bg=Palette.CARD, fg=Palette.MUTED, font=("Microsoft YaHei UI", 9)).pack(anchor="w")
            val = tk.Label(card, text=self.metrics[key], bg=Palette.CARD, fg=Palette.TEXT, font=("Consolas", 24, "bold"))
            val.pack(anchor="w")
            hint = tk.Label(card, text=unit, bg=Palette.CARD, fg=Palette.ACCENT, font=("Microsoft YaHei UI", 9))
            hint.pack(anchor="w")
            self.metric_value_labels[key] = val
            self.metric_hint_labels[key] = hint

        trend_wrap = tk.Frame(panel, bg=Palette.CARD_SOFT, padx=8, pady=8, highlightthickness=1, highlightbackground="#3A4E66")
        trend_wrap.pack(fill="both", expand=True)
        tk.Label(trend_wrap, text="最近 80 个采样趋势 (T/H/AQ)", bg=Palette.CARD_SOFT, fg=Palette.TEXT, font=("Microsoft YaHei UI", 9, "bold")).pack(
            anchor="w"
        )
        self.trend_canvas = tk.Canvas(
            trend_wrap,
            bg="#0B1220",
            highlightthickness=0,
            height=220,
        )
        self.trend_canvas.pack(fill="both", expand=True, pady=(6, 0))
        self.trend_canvas.bind("<Configure>", lambda _e: self._draw_trend())

        stats = tk.Frame(panel, bg=Palette.PANEL)
        stats.pack(fill="x", pady=(8, 0))
        self.packet_label = tk.Label(
            stats, text="RX: 0   TX: 0", bg=Palette.PANEL, fg=Palette.MUTED, font=("Consolas", 10, "bold")
        )
        self.packet_label.pack(anchor="w")

    def _build_controls_panel(self, parent):
        panel = tk.Frame(parent, bg=Palette.PANEL, padx=12, pady=10, highlightthickness=1, highlightbackground="#263548")
        panel.grid(row=0, column=1, sticky="nsew", pady=(0, 8))
        tk.Label(panel, text="设备控制", bg=Palette.PANEL, fg=Palette.TEXT, font=("Microsoft YaHei UI", 11, "bold")).pack(anchor="w")

        badge_row = tk.Frame(panel, bg=Palette.PANEL)
        badge_row.pack(fill="x", pady=(8, 6))
        for idx, dev in enumerate(("lamp1", "lamp2", "fan", "home")):
            block = tk.Frame(badge_row, bg=Palette.CARD, padx=8, pady=6, highlightthickness=1, highlightbackground="#304357")
            block.grid(row=0, column=idx, sticky="nsew", padx=(0, 6 if idx < 3 else 0))
            badge_row.columnconfigure(idx, weight=1)
            tk.Label(block, text=dev.upper(), bg=Palette.CARD, fg=Palette.MUTED, font=("Consolas", 9, "bold")).pack()
            badge = tk.Label(block, text="OFF", bg=Palette.BAD, fg="white", width=8, font=("Consolas", 9, "bold"))
            badge.pack(pady=(4, 0))
            self.device_badges[dev] = badge

        btn_grid = tk.Frame(panel, bg=Palette.PANEL)
        btn_grid.pack(fill="x", pady=(4, 8))
        buttons = [
            ("灯1 开", "lamp1", 1), ("灯1 关", "lamp1", 0), ("灯1 切换", "lamp1", 2),
            ("灯2 开", "lamp2", 1), ("灯2 关", "lamp2", 0), ("灯2 切换", "lamp2", 2),
            ("风扇 开", "fan", 1), ("风扇 关", "fan", 0), ("回家", "home", 0), ("离家", "home", 1),
        ]
        for i, (txt, dev, st) in enumerate(buttons):
            r, c = divmod(i, 3)
            b = tk.Button(
                btn_grid,
                text=txt,
                bg=Palette.CARD,
                fg=Palette.TEXT,
                activebackground=Palette.ACCENT,
                activeforeground="#0B1020",
                relief="flat",
                padx=10,
                pady=8,
                font=("Microsoft YaHei UI", 9),
                command=lambda d=dev, s=st: self.send_json_cmd(d, s),
            )
            b.grid(row=r, column=c, sticky="we", padx=4, pady=4)
            btn_grid.columnconfigure(c, weight=1)

        send_wrap = tk.Frame(panel, bg=Palette.PANEL)
        send_wrap.pack(fill="both", expand=True)
        tk.Label(send_wrap, text="自定义发送", bg=Palette.PANEL, fg=Palette.MUTED, font=("Microsoft YaHei UI", 9)).pack(anchor="w")
        self.custom_entry = tk.Entry(
            send_wrap,
            textvariable=self.custom_var,
            bg="#0B1220",
            fg=Palette.TEXT,
            insertbackground=Palette.TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#334155",
            highlightcolor=Palette.ACCENT,
            font=("Consolas", 10),
        )
        self.custom_entry.pack(fill="x", pady=(4, 6))
        actions = tk.Frame(send_wrap, bg=Palette.PANEL)
        actions.pack(fill="x")
        ttk.Button(actions, text="发送 JSON", style="Accent.TButton", command=self.send_custom).pack(side="left")
        ttk.Button(actions, text="清空日志", command=lambda: self.log.delete("1.0", "end")).pack(side="right")

    def _build_log_panel(self, parent):
        panel = tk.Frame(parent, bg=Palette.PANEL, padx=12, pady=10, highlightthickness=1, highlightbackground="#263548")
        panel.grid(row=1, column=0, columnspan=2, sticky="nsew")
        tk.Label(panel, text="收发日志", bg=Palette.PANEL, fg=Palette.TEXT, font=("Microsoft YaHei UI", 11, "bold")).pack(anchor="w")

        log_wrap = tk.Frame(panel, bg=Palette.PANEL)
        log_wrap.pack(fill="both", expand=True, pady=(8, 0))
        self.log = tk.Text(
            log_wrap,
            height=16,
            wrap="word",
            bg="#0B1220",
            fg=Palette.TEXT,
            insertbackground=Palette.TEXT,
            relief="flat",
            font=("Consolas", 10),
            padx=8,
            pady=8,
        )
        self.log.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(log_wrap, orient="vertical", command=self.log.yview)
        sb.pack(side="right", fill="y")
        self.log.configure(yscrollcommand=sb.set)
        self.log.tag_config("tx", foreground=Palette.TX)
        self.log.tag_config("rx", foreground=Palette.RX)
        self.log.tag_config("warn", foreground=Palette.WARN)
        self.log.tag_config("err", foreground=Palette.BAD)
        self.log.tag_config("sys", foreground=Palette.MUTED)

    def _set_network_badge(self, text, color):
        self.network_badge_var.set(text)
        self.network_badge.configure(bg=color)

    def _log(self, msg, tag="sys"):
        self.log.insert("end", msg + "\n", tag)
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

    def _update_metric_card(self, key, value):
        self.metrics[key] = str(value)
        self.metric_value_labels[key].configure(text=self.metrics[key])
        if key == "AQ":
            try:
                num = float(value)
            except (TypeError, ValueError):
                num = None
            if num is not None:
                if num < 1300:
                    txt, color = "空气良好", Palette.GOOD
                elif num < 2200:
                    txt, color = "空气一般", Palette.WARN
                else:
                    txt, color = "空气较差", Palette.BAD
                self.metric_hint_labels[key].configure(text=f"ADC · {txt}", fg=color)

    def _push_history(self, key, val):
        series = self.history[key]
        series.append(val)
        if len(series) > self.HISTORY_MAX:
            del series[0]

    def _draw_trend(self):
        c = self.trend_canvas
        c.delete("all")
        w = max(c.winfo_width(), 100)
        h = max(c.winfo_height(), 120)
        pad = 24
        x0, y0, x1, y1 = pad, pad, w - pad, h - pad

        c.create_rectangle(x0, y0, x1, y1, outline="#2D3D52")
        for i in range(1, 4):
            y = y0 + (y1 - y0) * i / 4
            c.create_line(x0, y, x1, y, fill="#1F2A3C")

        combined = []
        for key in ("T", "H", "AQ"):
            combined.extend(self.history[key])
        if not combined:
            c.create_text(w / 2, h / 2, text="等待数据...", fill=Palette.MUTED, font=("Microsoft YaHei UI", 10))
            return

        mn = min(combined)
        mx = max(combined)
        if mx - mn < 1e-6:
            mx = mn + 1

        colors = {"T": "#60A5FA", "H": "#34D399", "AQ": "#F59E0B"}
        for key in ("T", "H", "AQ"):
            arr = self.history[key]
            if len(arr) < 2:
                continue
            pts = []
            span = max(len(arr) - 1, 1)
            for i, v in enumerate(arr):
                x = x0 + (x1 - x0) * i / span
                y = y1 - (y1 - y0) * ((v - mn) / (mx - mn))
                pts.extend((x, y))
            c.create_line(*pts, fill=colors[key], width=2, smooth=True)

        c.create_text(x0 + 6, y0 + 6, anchor="nw", text=f"min={mn:.1f}", fill=Palette.MUTED, font=("Consolas", 8))
        c.create_text(x0 + 6, y0 + 20, anchor="nw", text=f"max={mx:.1f}", fill=Palette.MUTED, font=("Consolas", 8))
        c.create_text(x1 - 120, y0 + 6, anchor="nw", text="T", fill="#60A5FA", font=("Consolas", 9, "bold"))
        c.create_text(x1 - 90, y0 + 6, anchor="nw", text="H", fill="#34D399", font=("Consolas", 9, "bold"))
        c.create_text(x1 - 60, y0 + 6, anchor="nw", text="AQ", fill="#F59E0B", font=("Consolas", 9, "bold"))

    def _update_device_badges(self):
        for dev, value in self.device_states.items():
            badge = self.device_badges[dev]
            if dev == "home":
                txt = "HOME" if value == 0 else "AWAY"
                color = "#1D4ED8" if value == 0 else "#7C3AED"
            else:
                txt = "ON" if int(value) == 1 else "OFF"
                color = Palette.GOOD if int(value) == 1 else Palette.BAD
            badge.configure(text=txt, bg=color)

    def _sync_device_state(self, dev, status):
        if dev not in self.device_states:
            return
        try:
            status = int(status)
        except (TypeError, ValueError):
            return
        if dev == "home":
            self.device_states[dev] = 0 if status == 0 else 1
        elif status == 2:
            self.device_states[dev] = 0 if self.device_states[dev] else 1
        else:
            self.device_states[dev] = 1 if status == 1 else 0
        self._update_device_badges()

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
        self.last_rx_time = 0
        self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self.recv_thread.start()
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.status_var.set(f"监听中 {listen_ip}:{listen_port}")
        self._set_network_badge("LISTEN", "#2563EB")
        self._log(f"[{ts()}] UDP启动: {listen_ip}:{listen_port}", "sys")

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
        self._set_network_badge("STOP", "#6B7280")
        self._log(f"[{ts()}] UDP已停止", "sys")

    def _recv_loop(self):
        while self.running and self.sock:
            try:
                data, addr = self.sock.recvfrom(2048)
            except socket.timeout:
                continue
            except Exception:
                break
            text = data.decode("utf-8", errors="replace")
            self.recv_queue.put((addr, text))

    def _handle_rx_payload(self, text):
        payload = None
        try:
            payload = json.loads(text)
        except Exception:
            return
        if not isinstance(payload, dict):
            return

        for key in ("T", "H", "L", "AQ", "A"):
            if key in payload:
                view_key = "AQ" if key == "A" else key
                self._update_metric_card(view_key, payload[key])
                if view_key in self.history:
                    try:
                        self._push_history(view_key, float(payload[key]))
                    except (TypeError, ValueError):
                        pass
        if "dev" in payload and "status" in payload:
            self._sync_device_state(str(payload["dev"]), payload["status"])

    def _poll_queue(self):
        refresh_chart = False
        while True:
            try:
                addr, text = self.recv_queue.get_nowait()
            except queue.Empty:
                break
            self.last_sender = addr
            self.last_rx_time = time.time()
            self.rx_packets += 1
            self.packet_label.configure(text=f"RX: {self.rx_packets}   TX: {self.tx_packets}")
            self._set_network_badge("ONLINE", Palette.GOOD)
            self._log(f"[{ts()}] RX {addr[0]}:{addr[1]} -> {text}", "rx")
            self._handle_rx_payload(text)
            refresh_chart = True
        if refresh_chart:
            self._draw_trend()
        self.root.after(120, self._poll_queue)

    def _heartbeat_tick(self):
        if self.running:
            if self.last_rx_time and (time.time() - self.last_rx_time) <= self.OFFLINE_TIMEOUT_S:
                self._set_network_badge("ONLINE", Palette.GOOD)
            elif self.last_rx_time:
                self._set_network_badge("OFFLINE", Palette.BAD)
            else:
                self._set_network_badge("LISTEN", "#2563EB")
        self.root.after(1000, self._heartbeat_tick)

    def send_text(self, text):
        if not self.running or not self.sock:
            messagebox.showwarning("未启动", "请先点击“启动监听”")
            return False
        addr = self._target_addr()
        if not addr:
            messagebox.showwarning("目标无效", "请填写正确的设备IP和端口，或先接收一帧数据")
            return False
        try:
            self.sock.sendto(text.encode("utf-8"), addr)
            self.tx_packets += 1
            self.packet_label.configure(text=f"RX: {self.rx_packets}   TX: {self.tx_packets}")
            self._log(f"[{ts()}] TX {addr[0]}:{addr[1]} <- {text}", "tx")
            return True
        except Exception as e:
            self._log(f"[{ts()}] 发送失败: {e}", "err")
            messagebox.showerror("发送失败", str(e))
            return False

    def send_json_cmd(self, dev, status):
        payload = json.dumps({"dev": dev, "status": str(status)}, ensure_ascii=False, separators=(",", ":"))
        if self.send_text(payload):
            self._sync_device_state(dev, status)

    def send_custom(self):
        text = self.custom_var.get().strip()
        if not text:
            messagebox.showwarning("内容为空", "请输入要发送的内容")
            return
        if text.startswith("{"):
            try:
                json.loads(text)
            except Exception as e:
                self._log(f"[{ts()}] JSON格式错误: {e}", "warn")
                messagebox.showwarning("JSON格式错误", str(e))
                return
        self.send_text(text)

    def on_close(self):
        self.stop_udp()
        self.root.destroy()


def main():
    root = tk.Tk()
    UdpGuiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
