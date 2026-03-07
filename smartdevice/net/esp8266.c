#include <stdio.h>
#include <string.h>
#include "net_device.h"
#include "at_command\at_command.h"
#include "smarthome.h"

#define ESP8266_DEFAULT_TIMEROUT 10  /* ms */
#define ESP8266_CTRL_TIMEOUT_MS 3000

static int ESP8266Init(struct NetDevice *ptDev)
{
    (void)ptDev;
    ATInterfaceInit();
    ATCommandSend("AT+CWMODE=3", ESP8266_CTRL_TIMEOUT_MS);
    ATCommandSend("AT+CIPMUX=0", ESP8266_CTRL_TIMEOUT_MS);
    return 0;
}

static int ESP8266Connect(struct NetDevice *ptDev, char *pSSID, char *pPassword)
{
    char cmd[100];
    (void)ptDev;
    sprintf(cmd, "AT+CWJAP=\"%s\",\"%s\"", pSSID, pPassword);
    return ATCommandSend(cmd, ESP8266_DEFAULT_TIMEROUT * 1000);
}

static void ESP8266CloseTransfer(struct NetDevice *ptDev)
{
    (void)ptDev;
    ATCommandSend("AT+CIPCLOSE", ESP8266_CTRL_TIMEOUT_MS);
}

static int ESP8266Send(struct NetDevice *ptDev, char *Type, char *pDestIP, int iDestPort, unsigned char *Data, int iLen)
{
    (void)ptDev;
    (void)Type;
    (void)pDestIP;
    (void)iDestPort;
    return ATDataSend(Data, iLen, ESP8266_DEFAULT_TIMEROUT * 100);
}

static int ESP8266Recv(struct NetDevice *ptDev, unsigned char *Data, int *piLen, int iTimeoutMS)
{
    (void)ptDev;
    return ATDataRecv(Data, piLen, iTimeoutMS);
}

static int ESP8266GetInfo(struct NetDevice *ptDev, char *ip_buf)
{
    char buf[200];
    int ret;
    char *ip;
    int i;

    ret = ATCommandSendAndRecv("AT+CIFSR", buf, ESP8266_DEFAULT_TIMEROUT * 1000);
    if (!ret)
    {
        ip = strstr(buf, "+CIFSR:STAIP,\"");
        if (ip)
        {
            ip += strlen("+CIFSR:STAIP,\"");
            for (i = 0; ip[i] != '\"'; i++)
            {
                ptDev->ip[i] = ip[i];
            }
            ptDev->ip[i] = '\0';
            strcpy(ip_buf, ptDev->ip);
            return 0;
        }
    }

    return -1;
}

static int ESP8266CreateTransfer(struct NetDevice *ptDev, char *Type, int iLocalPort)
{
    char cmd[100];
    (void)ptDev;
    (void)Type;
    sprintf(cmd, "AT+CIPSTART=\"UDP\",\"%s\",%d,%d,2", REMOTE_IP, REMOTE_PORT, iLocalPort);
    return ATCommandSend(cmd, ESP8266_CTRL_TIMEOUT_MS);
}

static NetDevice g_tESP8266NetDevice = {
    "esp8266",
    "0.0.0.0",
    {0, 0, 0, 0, 0, 0},
    ESP8266Init,
    ESP8266Connect,
    ESP8266GetInfo,
    ESP8266CreateTransfer,
    ESP8266CloseTransfer,
    ESP8266Send,
    ESP8266Recv
};

void AddNetDeviceESP8266(void)
{
    NetDeviceRegister(&g_tESP8266NetDevice);
}
