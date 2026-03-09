# ???????

> ??????????????????????Mermaid???????

## ??? 1?2.1.4 功能流程（可流程图化）

```mermaid
flowchart LR
    A[传感器采样 T/H/L/AQ] --> B[STM32 任务处理]
    B --> C[UDP 上报]
    C --> D[PC GUI 显示 RX]
    D --> E[用户下发控制 TX]
    E --> F[STM32 解析 JSON]
    F --> G[执行器动作]
    G --> H[状态回显与日志]
```

## ??? 2?2.2.1 实时性

```mermaid
flowchart TD
    T1[周期采集任务] --> Q[数据缓冲/发送]
    T2[事件控制任务] --> C[命令解析]
    C --> ACT[执行器控制]
    Q --> NET[网络上报]
```

## ??? 3?2.3.1 四层方案与数据闭环

```mermaid
flowchart LR
    S[传感器层] --> M[STM32F103ZET6]
    M --> E[ESP8266]
    E --> P[PC UDP 控制台]
    P --> E
    E --> M
    M --> A[执行器层]
```

## ??? 4?4.2.1 分层职责

```mermaid
flowchart TD
    DRV[驱动层] --> DEV[设备抽象层]
    DEV --> IN[输入层]
    DEV --> NET[网络层]
    IN --> APP[业务层]
    NET --> APP
```

## ??? 5?4.3.1 任务划分

```mermaid
sequenceDiagram
    participant D as DHT11_UpdateValue
    participant S as SmartHomeTask
    participant N as ESP8266/UDP
    D->>S: 更新 T/H/L/AQ
    S->>N: 周期上报 JSON
    N-->>S: 接收控制命令
    S->>S: 解析并驱动执行器
```

## ??? 6?4.4.1 中轴机制

```mermaid
flowchart LR
    K[按键输入] --> E[InputEvent]
    W[网络输入] --> E
    E --> Q[事件队列]
    Q --> J[JSON 语义转换]
    J --> C[控制执行]
```

## ??? 7?4.9.3 替换扩展

```mermaid
flowchart TD
    A[当前 UDP 适配层] --> B[接口保持不变]
    B --> C[替换为 MQTT/HTTP 适配层]
    C --> D[业务层零或小改动]
```

## ??? 8?5.1.1 实现闭环

```mermaid
flowchart LR
    S1[采集链路] --> S2[上报链路]
    S2 --> S3[控制链路]
    S3 --> S1
```

