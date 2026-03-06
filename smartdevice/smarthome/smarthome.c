#include <stdio.h>
#include <string.h>
#include <input_buffer.h>
#include <input_system.h>
#include <led_device.h>
#include <dht11_device.h>
#include <fan_device.h>
#include <display_system.h>
#include <font_system.h>
#include <show_text.h>
#include <net_system.h>
#include <kal_time.h>
#include <message.h>
#include "main.h"
#include "smarthome.h"

/**********************************************************************
 * 函数名称： SystemInit
 * 功能描述： 系统初始化:初始化各类子系统
 * 输入参数： 无
 * 输出参数： 无
 * 返 回 值： 无
 * 修改日期       版本号     修改人	      修改内容
 * -----------------------------------------------
 * 2021/10/16	     V1.0	  韦东山	      创建
 ***********************************************************************/
static void SubSystemInit(void)
{
	PNetDevice pNetDev;

	KAL_Delay(2000);
	
	/* 1.初始化LED */
	PLEDDevice p1 = GetLEDDevice(LED_WHITE);
	PLEDDevice p2 = GetLEDDevice(LED_BLUE);
	PLEDDevice p3 = GetLEDDevice(LED_GREEN);

	p1->Init(p1);
	p2->Init(p2);
	p3->Init(p3);

	/* 2. 初始化FAN */
	PFANDevice p4 = GetFANDevice();
	p4->Init(p4);

	/* 3. 初始化显示设备 */
	PDisplayDevice ptDevice;
	char *name = "OLED";

	/* 3.1 添加所有显示设备 */
	AddDisplayDevices();

	/* 3.2 取出OLED显示设备 */
	ptDevice = GetDisplayDevice(name);

	if (!ptDevice)
	{
		printf("Can not get DisplayDevice %s\r\n", name);
		return;
	}

	/* 3.3 初始化显示设备 */
	ptDevice->Init(ptDevice);

	/* 3.4 清除屏幕 */
	memset(ptDevice->FBBase, 0, ptDevice->iSize);

	/* 3.5 Flush屏幕 */
	ptDevice->Flush(ptDevice);

	/* 4. 初始化字库 */

	/* 4.1 添加字库 */
	AddFontLibs();

	/* 4.2 选择默认字库 */
	SetDefaultFontLib("ascii");

	/* 4.3 初始化默认字库 */
	InitDefaultFontLib();

	/* 5. 初始化输入系统 */

	/* 5.1 添加所以输入设备 */
	AddInputDevices();

	/* 5.2 初始化所有输入设备 */
	InitInputQueue();
	InitInputDevices();

	/* 6. 初始化网络系统 */

	/* 6.1 添加网卡 */
	AddNetDevices();

	/* 6.2 获得ESP8266网卡 */
	pNetDev = GetNetDevice("esp8266");

	/* 6.3 初始化网卡 */
	pNetDev->Init(pNetDev);	
}

/**********************************************************************
 * 函数名称： WifiConnect
 * 功能描述： 连接WIFI热点
 * 输入参数： 无
 * 输出参数： 无
 * 返 回 值： 无
 * 修改日期       版本号     修改人	      修改内容
 * -----------------------------------------------
 * 2021/10/16	     V1.0	  韦东山	      创建
 ***********************************************************************/
void WifiConnect(void)
{
	PNetDevice pNetDev;
	
	/* 获得ESP8266网卡 */
	pNetDev = GetNetDevice("esp8266");
	while (1)
	{
		/* 连接WIFI热点: 你做实验时需要修改这里: wifi热点名,密码 */
		if (pNetDev->Connect(pNetDev, SSID, PASSWORD) == 0)
		{
			printf("Connect WIFI ok\r\n");
			break;
		}
		else
		{
			printf("Connect WIFI err\r\n");
			KAL_Delay(1000);
		}
	}
	
}

/**********************************************************************
 * 函数名称： DisplayNetInfoAndCreateTransfer
 * 功能描述： 显示网卡信息(IP和端口), 并创建传输
 * 输入参数： 无
 * 输出参数： 无
 * 返 回 值： 无
 * 修改日期       版本号     修改人	      修改内容
 * -----------------------------------------------
 * 2021/10/16	     V1.0	  韦东山	      创建
 ***********************************************************************/
void DisplayNetInfoAndCreateTransfer(void)
{
	PNetDevice pNetDev;
	char ip[20];
	int port = LOCAL_PORT;

	PDisplayDevice ptDevice;
	char str[100];
	
	/* 获得ESP8266网卡 */
	pNetDev = GetNetDevice("esp8266");
	
	/* 获得单板IP */
	if (pNetDev->GetInfo(pNetDev, ip) == 0)
	{
		printf("Board IP = %s, port = %d\r\n", ip, port);
	}
	else
	{
		printf("GetInfo err\r\n");
		return;
	}

	/* 创建网络传输
	 * 先关闭, 因为我们的开发板可能多次创建传输, 先关闭上次传输
	 */
	pNetDev->CloseTransfer(pNetDev);
	if (pNetDev->CreateTransfer(pNetDev, "udp", port) == 0)
	{
		printf("Create Transfer ok\r\n");
	}
	else
	{
		printf("Create Transfer err\r\n");
	}

	/* 在LCD上显示出来 */
	/* 获得指定的显示设备 */
	ptDevice = GetDisplayDevice("OLED");
	
	/* 在屏幕上显示文字 */
	/* 清除屏幕 */
	memset(ptDevice->FBBase, 0, ptDevice->iSize);
	
	/* 显示ip */
	ShowTextInDisplayDevice(ptDevice, 0, 15, "IP:");
	ShowTextInDisplayDevice(ptDevice, 0, 31, ip);

	/* 显示port */
	sprintf(str, "Port:%d", port);
	ShowTextInDisplayDevice(ptDevice, 0, 47, str);

	/* 显示厂家 */
	ShowTextInDisplayDevice(ptDevice, 0, 63, "www.100ask.net");

	
}

/**********************************************************************
 * 函数名称： SmartHomeControlDevices
 * 功能描述： 智能家居控制逻辑
 * 输入参数： strJson-Json格式的参数,比如: {"dev":"lamp1","status":"1"}
 * 输出参数： 无
 * 返 回 值： 无
 * 修改日期       版本号     修改人	      修改内容
 * -----------------------------------------------
 * 2021/10/16	     V1.0	  韦东山	      创建
 ***********************************************************************/
static void SmartHomeControlDevices(char *strJson)
{
	char dev[10];
	int status;
	char *pTmp;
	int i;
	int which;

	PLEDDevice ptLED;
	PFANDevice ptFAN;

	/* 取出dev的值 */
	pTmp = strstr(strJson, "\"dev\":\"");
	if (!pTmp)
		return;
	pTmp += strlen("\"dev\":\"");
	for (i = 0; pTmp[i] != '\"'; i++)
		dev[i] = pTmp[i];
	dev[i] = '\0';

	/* 取出status的值 */
	pTmp = strstr(strJson, "\"status\":\"");
	if (!pTmp)
		return;
	pTmp += strlen("\"status\":\"");
	status = (pTmp[0] == '-') ? (0 - (pTmp[1] - '0')) : (pTmp[0] - '0');

	if (strncmp(dev, "lamp", 4) == 0)
	{
		/* 控制LED */
		which = dev[4] - '0' - 1;
		ptLED = GetLEDDevice(which);
		if (ptLED)
			ptLED->Control(ptLED, status);
	}
	else if (strncmp(dev, "fan", 3) == 0)
	{
		/* 控制FAN */
		ptFAN = GetFANDevice();
		if (ptFAN)
			ptFAN->SetSpeed(ptFAN, status);
	}
	else if (strncmp(dev, "home", 4) == 0)
	{
		/* home */
		if (!status)
		{
			/* 回家: 打开所有LED、风扇 */
			for (i = 0; i < 3; i++)
			{
				ptLED = GetLEDDevice(i);
				if (ptLED)
					ptLED->Control(ptLED, 1);
			}

			ptFAN = GetFANDevice();
			if (ptFAN)
				ptFAN->SetSpeed(ptFAN, 1);
		}
		else
		{
			/* 离家: 关闭所有LED、风扇 */
			for (i = 0; i < 3; i++)
			{
				ptLED = GetLEDDevice(i);
				if (ptLED)
					ptLED->Control(ptLED, 0);
			}
			ptFAN = GetFANDevice();
			if (ptFAN)
				ptFAN->SetSpeed(ptFAN, 0);
		}
	}
	
}

/**********************************************************************
 * 函数名称： DisplayStartingInfo
 * 功能描述： 显示启动信息
 * 输入参数： 无
 * 输出参数： 无
 * 返 回 值： 无
 * 修改日期       版本号     修改人	      修改内容
 * -----------------------------------------------
 * 2021/10/18	     V1.0	  韦东山	      创建
 ***********************************************************************/
static void DisplayStartingInfo(void)
{	
	PDisplayDevice ptDevice;
	char *name = "OLED";

	/* 取出OLED显示设备 */
	ptDevice = GetDisplayDevice(name);

	/* 清除屏幕 */
	memset(ptDevice->FBBase, 0, ptDevice->iSize);
	
	/* 在屏幕上显示: Starting */
	ShowTextInDisplayDevice(ptDevice, 0, 16, VERSION);
	ShowTextInDisplayDevice(ptDevice, 0, 34, "Starting...");
}

/**********************************************************************
 * 函数名称： DisplayWifiStatus
 * 功能描述： 显示WIF状态
 * 输入参数： 无
 * 输出参数： 无
 * 返 回 值： 无
 * 修改日期       版本号     修改人	      修改内容
 * -----------------------------------------------
 * 2021/10/18	     V1.0	  韦东山	      创建
 ***********************************************************************/
static void DisplayWifiStatus(void)
{	
	PDisplayDevice ptDevice;
	char *name = "OLED";

	/* 取出OLED显示设备 */
	ptDevice = GetDisplayDevice(name);
	
	/* 在屏幕上显示: Starting */
	ShowTextInDisplayDevice(ptDevice, 0, 54, "WIFI Connecting ...");
}

/* LM393 DO口: 常见模块是低电平表示超过阈值(亮/暗取决于电位器方向) */
static int LM393_GetLightState(void)
{
	return (HAL_GPIO_ReadPin(LM393_DO_GPIO_Port, LM393_DO_Pin) == GPIO_PIN_RESET) ? 1 : 0;
}

static void LM393_ADC_Init(void)
{
	GPIO_InitTypeDef GPIO_InitStruct = {0};

	/* ADC时钟 <= 14MHz: PCLK2(72MHz)/6 = 12MHz */
	RCC->CFGR &= ~RCC_CFGR_ADCPRE;
	RCC->CFGR |= RCC_CFGR_ADCPRE_DIV6;

	__HAL_RCC_GPIOA_CLK_ENABLE();
	__HAL_RCC_ADC1_CLK_ENABLE();

	/* PA1 -> ADC1_IN1 */
	GPIO_InitStruct.Pin = LM393_AO_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
	HAL_GPIO_Init(LM393_AO_GPIO_Port, &GPIO_InitStruct);

	ADC1->CR1 = 0;
	ADC1->CR2 = 0;
	ADC1->SMPR2 &= ~(ADC_SMPR2_SMP1);
	ADC1->SMPR2 |= ADC_SMPR2_SMP1; /* 通道1采样时间239.5周期，抗噪更好 */
	ADC1->SQR1 = 0;
	ADC1->SQR3 = 1; /* rank1 = ch1 */
	ADC1->CR2 |= ADC_CR2_ADON;
	HAL_Delay(1);

	/* 复位校准并校准 */
	ADC1->CR2 |= ADC_CR2_RSTCAL;
	while (ADC1->CR2 & ADC_CR2_RSTCAL);
	ADC1->CR2 |= ADC_CR2_CAL;
	while (ADC1->CR2 & ADC_CR2_CAL);
}

static unsigned short LM393_ReadAO(void)
{
	ADC1->CR2 |= ADC_CR2_ADON;
	ADC1->CR2 |= ADC_CR2_EXTTRIG;
	ADC1->CR2 |= ADC_CR2_SWSTART;
	while (!(ADC1->SR & ADC_SR_EOC));
	return (unsigned short)(ADC1->DR & 0x0FFF);
}

void DHT11_UpdateValue(void)
{
    PDHT11Dev dht11 = GetDHT11Device(1);
	int err;
	int light_state;
	unsigned short light_adc;

    /* 初始化DHT11设备 */
    dht11->DevInit(dht11);
	LM393_ADC_Init();

	while (1)	
	{
		//vTaskSuspendAll();
	    err = dht11->GetValue(dht11);
		//xTaskResumeAll();

		if (!err)
		{	
			light_state = LM393_GetLightState();
			light_adc = LM393_ReadAO();
		    printf("T=%d,H=%d,L=%d,A=%u\r\n", dht11->value.temperature, dht11->value.humidity, light_state, light_adc);
		}
	    //KAL_Delay(5000);
	    vTaskDelay(5000);
	}
}

/**********************************************************************
 * 函数名称： SmartHomeTask
 * 功能描述： 智能家居任务函数
 * 输入参数： 无
 * 输出参数： 无
 * 返 回 值： 无
 * 修改日期       版本号     修改人	      修改内容
 * -----------------------------------------------
 * 2021/10/16	     V1.0	  韦东山	      创建
 ***********************************************************************/
void SmartHomeTask(void)
{
	char strJson[100];
	InputEvent event;
	
	/* 初始化各类设备/子系统 		*/
	SubSystemInit();

	/* 显示启动信息 */
	DisplayStartingInfo();

	/* 显示WIFI信息 */
	DisplayWifiStatus();

	vTaskSuspendAll();
	/* 连接WIFI			   */
	WifiConnect();
	
	/* 在OLED上显示IP、端口	*/
	DisplayNetInfoAndCreateTransfer();
	xTaskResumeAll();

	while (1)
	{
		/* 读取InputEvent 	   */
		if (0 == GetInputEvent(&event))
		{
			/* 转换为Json格式的参数  */
			if (0 == ConvertInputEventToJson(&event, strJson))
			{
				/* 控制设备 			 */
				SmartHomeControlDevices(strJson);
			}
		}
        //DHT11_UpdateValue();
	}
}


