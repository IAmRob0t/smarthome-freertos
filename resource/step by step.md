# PC端替代小程序：UDP联调与图形界面交付（Step by Step）

本方案用于替代已停运的小程序，完成“采集展示 + 远程控制”闭环演示。
说明：老师要求不能让用户手动敲命令，所以命令行脚本用于联调，最终交付请使用图形界面版工具。

## 1. 你将用到的文件

- 脚本：`resource/udp_console.py`

## 2. 准备工作

1. 开发板正常运行，串口可看到 `T/H/L` 输出。
2. 电脑与 ESP8266 在同一局域网（同一热点/同一路由器）。
3. 电脑已安装 Python 3（命令行执行 `python --version` 能看到版本号）。

## 3. 先确认网络信息

1. 记录电脑 IP（Windows 命令行执行 `ipconfig`，找当前网卡 IPv4）。
2. 记录开发板 IP（你串口里已有 `Board IP = xxx.xxx.xxx.xxx`）。

## 4. 运行 UDP 控制台脚本（联调阶段）

在项目根目录打开 PowerShell，执行：

```powershell
python .\resource\udp_console.py --listen-port 8080 --board-ip <开发板IP> --board-port 1234
```

示例：

```powershell
python .\resource\udp_console.py --listen-port 8080 --board-ip 172.20.10.13 --board-port 1234
```

如果提示 `WinError 10048`（端口占用），改用：

```powershell
python .\resource\udp_console.py --listen-port 18080
```

运行后会看到：

- `UDP监听中: 0.0.0.0:8080`
- 若带了 `--board-ip`：会显示 `默认目标: <开发板IP>:1234`
- 若未带 `--board-ip`：需手动执行第 5 步中的 `target` 命令

## 5. 下发控制命令（联调阶段）

先设置目标（未使用 `--board-ip` 时必须先做）：

```text
target <开发板IP> 1234
```

例如：

```text
target 172.20.10.13 1234
```

然后在脚本交互界面输入以下任一命令：

- `lamp1 on`
- `lamp1 off`
- `lamp1 toggle`
- `lamp2 on`
- `lamp2 off`
- `fan on`
- `fan off`
- `home in`
- `home out`

脚本会自动发送 JSON 给开发板，例如：

```json
{"dev":"lamp1","status":"1"}
```

## 6. 查看接收数据（联调阶段）

当板端上传数据到你的电脑时，脚本窗口会自动显示：

```text
[18:30:00] RX from <board_ip>:<port> -> <payload>
```

你可用此窗口作为“PC端实时监控界面”演示。

## 7. 如果发送失败或收不到数据，按此排查

1. 检查电脑防火墙是否拦截 UDP `8080`（先临时放行 Python）。
2. 如果报 `WinError 10048`，说明监听端口被占用，改用 `--listen-port 18080`。
3. 检查 `--board-ip` 是否与串口打印的 `Board IP` 一致。
4. 检查开发板程序里 `LOCAL_PORT` 是否为 `1234`（与脚本 `--board-port` 对齐）。
5. 若提示“未设置目标地址”，先执行 `target <开发板IP> 1234`。
6. 如果串口有 `Create Transfer err`：
   - 你当前代码在 `smartdevice/net/esp8266.c` 里把远端写死成 `192.168.1.1:8080`。
   - 请改成你的电脑 IP 和监听端口（即第 3 步查到的 IP + `8080`）。
7. 本项目板端 JSON 解析要求紧凑格式：`{"dev":"lamp1","status":"1"}`（脚本已自动处理）。

## 8. 图形界面版交付（老师要求）

最简单方案：用 Python `tkinter` 做一个本地 GUI（按钮+状态文本），再打包成 exe。

界面最小功能建议：

1. 连接配置区：开发板 IP、端口、连接按钮。
2. 控制区：`lamp1 on/off`、`lamp2 on/off`、`fan on/off`、`home in/out` 按钮。
3. 监控区：实时显示接收数据（`T/H/L/A`）。
4. 日志区：显示发送和接收时间戳记录。

打包方式（Windows）：

```powershell
pip install pyinstaller
pyinstaller -F -w .\resource\udp_gui.py
```

打包后把 `dist\udp_gui.exe` 给老师演示即可，用户无需敲命令。

## 9. 答辩演示建议（最短流程）

1. 串口窗口展示 `T/H/L` 实时变化。
2. 脚本窗口展示实时接收数据（如果板端已实现发送）。
3. 在脚本中输入 `lamp1 on`、`fan on`，现场展示板端执行效果。
4. 输入 `home out`，展示一键联动。
