#include "driver_dht11.h"
#include "main.h"
#include "cmsis_os.h"
#include "semphr.h"
#include "driver_key.h"

static TIM_HandleTypeDef        htim;
static int g_dht11_read_fail_cnt = 0;

#define DHT11_READ_RETRY_CNT 5

static void DHT11_TIM_Init(void);

/* 二进制信号量句柄 */
static SemaphoreHandle_t xBinarySemaphore;

void DHT11_Notify_Task(void)
{
	BaseType_t xHigherPriorityTaskWoken = pdFALSE;
	xSemaphoreGiveFromISR(xBinarySemaphore, &xHigherPriorityTaskWoken);
	portYIELD_FROM_ISR( xHigherPriorityTaskWoken );
}

static void DHT11_GPIO_Init_As_Output(void)
{
	GPIO_InitTypeDef GPIO_InitStruct = {0};

    HAL_GPIO_DeInit(DHT11_PORT, DHT11_PIN);
	
    GPIO_InitStruct.Pin = DHT11_PIN;           
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD;         
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;   
    HAL_GPIO_Init(DHT11_PORT, &GPIO_InitStruct);
}

void DHT11_Init(void)
{
	
    DHT11_TIM_Init();
    
	DHT11_CLK_EN();
    
	DHT11_GPIO_Init_As_Output();

	/* 创建二进制信号量 */
	xBinarySemaphore = xSemaphoreCreateBinary( );
	if( xBinarySemaphore == NULL )
	{
		printf("can not create Semaphore\r\n");
	}
}

static void DHT11_TIM_Init(void)
{
    TIM_ClockConfigTypeDef sClockSourceConfig = {0};
    TIM_MasterConfigTypeDef sMasterConfig = {0};
    
    __HAL_RCC_TIM3_CLK_ENABLE();
    
    htim.Instance              = TIM3;
    htim.Init.Period           = 0;
    htim.Init.Prescaler        = 72-1;  /* 72M/72 = 1Mhz, T=1us  */
    htim.Init.ClockDivision    = 0;
    htim.Init.CounterMode      = TIM_COUNTERMODE_UP;
    htim.Init.RepetitionCounter = 0;
    htim.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;

    if(HAL_TIM_Base_Init(&htim) != HAL_OK)
    {
        Error_Handler();
    }
    sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
    if (HAL_TIM_ConfigClockSource(&htim, &sClockSourceConfig) != HAL_OK)
    {
        Error_Handler();
    }
    sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
    sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
    if (HAL_TIMEx_MasterConfigSynchronization(&htim, &sMasterConfig) != HAL_OK)
    {
        Error_Handler();
    }
}

static void DHT11_usDelay(uint32_t us)
{
    uint16_t counter = 0;
	__HAL_TIM_SET_AUTORELOAD(&htim, us);		
	__HAL_TIM_SET_COUNTER(&htim, counter);
	HAL_TIM_Base_Start(&htim);
	while(counter != us)
	{
		counter = __HAL_TIM_GET_COUNTER(&htim);
	}
	HAL_TIM_Base_Stop(&htim);
}

static void DHT11_StartTimer(void)
{
    uint16_t counter = 0;
	uint32_t us = 10000; /* 10ms */
	__HAL_TIM_SET_AUTORELOAD(&htim, us);		
	__HAL_TIM_SET_COUNTER(&htim, counter);
	HAL_TIM_Base_Start(&htim);
}

int DHT11_ReadTimer_us(void)
{
	return __HAL_TIM_GET_COUNTER(&htim);
}

static void DHT11_StopTimer(void)
{
	HAL_TIM_Base_Stop(&htim);
}


static void DHT11_Start(void)
{
	DHT11_L;
	DHT11_usDelay(20000);
}

static int DHT11_WaitForVal(uint8_t val, uint16_t timeout)
{
	while(timeout--)
	{
		if(DHT11_IN==val)
			return 0;
		DHT11_usDelay(1);
	}
	
	return -1;
}

static int DHT11_RecvByte(void)
{
	uint8_t i = 0;
	uint8_t data = 0;

	for(i=0; i<8; i++)
	{
		if(DHT11_WaitForVal(1, 1000))
			return -1;
		DHT11_usDelay(40);
		data <<= 1;
		if(DHT11_IN)
		{
			data |= 1;
		}
		if(DHT11_WaitForVal(0, 1000))
			return -1;
	}

	return data;
}


static int DHT11_ParseData(unsigned int *temperature, unsigned int *humidity)
{
	int *p = Get_DHT11_Edge_Times();
	int i, j, m = 0;
	unsigned char data[5];

	int offset;

	for (offset = 0; offset <= 6; offset++)
	{
		m = offset;
		for (i = 0; i < 5; i++)
		{
			data[i] = 0;
			for (j = 0; j < 8; j++)
			{
				data[i] <<= 1;

				if ((p[m+1] - p[m]) > 40)
					data[i] |= 1;

				m += 2;
			}		
		}

		/* 检查检验码 + 合理范围过滤 */
		if ((data[0] + data[1] + data[2] + data[3] == data[4]) &&
			(data[0] <= 100) && (data[2] <= 80))
		{
			*humidity = data[0];
			*temperature = data[2];
			return 0; 
		}
	}

	return -1;
}

static int DHT11_ReadOnce(unsigned int *temperature, unsigned int *humidity)
{
	/* 1. 发出Start */
	DHT11_Start();	// 开始信号
	DHT11_H; 

	/* 启动定时器/使能中断 */
	DHT11_StartTimer();
	DHT11_GPIO_Init_As_IRQ();  /* 配置为中断引脚 */
	DHT11_IRQ_Enable();


	/* 在中断里记录ACK、数据脉冲 */
	
	/* 4. 阻塞 */
	if (xSemaphoreTake(xBinarySemaphore, pdMS_TO_TICKS(10)) != pdTRUE)
	{
		DHT11_StopTimer();
		DHT11_IRQ_Disable();
		DHT11_GPIO_Init_As_Output();
		DHT11_H; 
		return -1;
	}

	/* 接收到80个中断时就把任务唤醒了
	 * 可能还没接收完全部的数据
	 * 所以再等等
	 */
	vTaskDelay(1);
	DHT11_StopTimer();
	DHT11_IRQ_Disable();	
	DHT11_GPIO_Init_As_Output();
	DHT11_H; 

	/* 5. 被唤醒后解析数据 */
	return DHT11_ParseData(temperature, humidity);
}

int DHT11_Read(unsigned int *temperature, unsigned int *humidity)
{
	int i;
	int ret = -1;

	for (i = 0; i < DHT11_READ_RETRY_CNT; i++)
	{
		ret = DHT11_ReadOnce(temperature, humidity);
		if (ret == 0)
		{
			g_dht11_read_fail_cnt = 0;
			return 0;
		}
		vTaskDelay(pdMS_TO_TICKS(2));
	}

	g_dht11_read_fail_cnt++;
	if ((g_dht11_read_fail_cnt % 10) == 0)
	{
		printf("DHT11 read fail x%d\r\n", g_dht11_read_fail_cnt);
	}
	return -1;
}


