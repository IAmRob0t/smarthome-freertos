#include <input_system.h>
#include <kal_time.h>
#include <gpio_key.h>
#include <input_buffer.h>
#include "driver_key.h"
#include "driver_dht11.h"


static volatile uint8_t key1_val = KEY_RELEASED;
static volatile uint8_t key2_val = KEY_RELEASED;

int dht11_edge_times[100];
static int dht11_edge_cnt;

int *Get_DHT11_Edge_Times(void)
{
	return dht11_edge_times;
}


void KEY_GPIO_ReInit(void)
{
	GPIO_InitTypeDef GPIO_InitStruct = {0};
	
	KEY1_GPIO_CLK_EN();
	KEY2_GPIO_CLK_EN();

	GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING_FALLING;
	GPIO_InitStruct.Pull = GPIO_PULLUP;
	
	GPIO_InitStruct.Pin = KEY1_PIN;
	HAL_GPIO_Init(KEY1_PORT, &GPIO_InitStruct);
	
	GPIO_InitStruct.Pin = KEY2_PIN;
	HAL_GPIO_Init(KEY1_PORT, &GPIO_InitStruct);
	
	
	HAL_NVIC_SetPriority(EXTI15_10_IRQn, 0, 2);
	HAL_NVIC_EnableIRQ(EXTI15_10_IRQn);
}


void DHT11_GPIO_Init_As_IRQ(void)
{
	GPIO_InitTypeDef GPIO_InitStruct = {0};

    HAL_GPIO_DeInit(DHT11_PORT, DHT11_PIN);
	
	GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING_FALLING;
	GPIO_InitStruct.Pull = GPIO_PULLUP;
	
	GPIO_InitStruct.Pin = DHT11_PIN;
	HAL_GPIO_Init(DHT11_PORT, &GPIO_InitStruct);		
	
	/* DHT11采样脉宽对中断响应敏感: 提升到可调用FreeRTOS API的最高优先级边界 */
	HAL_NVIC_SetPriority(EXTI9_5_IRQn, 5, 0);
}

void DHT11_IRQ_Enable(void)
{
	dht11_edge_cnt = 0;
	HAL_NVIC_EnableIRQ(EXTI9_5_IRQn);
}

void DHT11_IRQ_Disable(void)
{
	HAL_NVIC_DisableIRQ(EXTI9_5_IRQn);
}


void EXTI15_10_IRQHandler(void)
{
	//printf("%s %s %d\r\n", __FILE__, __FUNCTION__, __LINE__);
	HAL_GPIO_EXTI_IRQHandler(KEY1_PIN);
	HAL_GPIO_EXTI_IRQHandler(KEY2_PIN);
}

void EXTI9_5_IRQHandler()
{
	HAL_GPIO_EXTI_IRQHandler(DHT11_PIN);
}


#if 0
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
	volatile int i = 0;
	InputEvent event;

	/* 消除抖动 */
	// HAL_Delay(5);
	// for (i = 0; i < 10000000; i++);
	
	if(KEY1_PIN == GPIO_Pin)
	{
		/* 构造InputEvent */
		event.time  = KAL_GetTime();  /* kal */
		event.eType = INPUT_EVENT_TYPE_KEY;
		event.iKey  = K1_CODE;

		/* 读取GPIO电平, GPIO为0表示按下, 此时压力是1,松开后压力是0 */
		event.iPressure = !K1_STATUS;  

		/* 放入环形缓冲区 */
		PutInputEvent(&event);
	}
	else if(KEY2_PIN == GPIO_Pin)
	{
		/* 构造InputEvent */
		event.time	= KAL_GetTime();  /* kal */
		event.eType = INPUT_EVENT_TYPE_KEY;
		event.iKey	= K2_CODE;

		/* 读取GPIO电平, GPIO为0表示按下, 此时压力是1,松开后压力是0 */
		event.iPressure = !K2_STATUS;

		/* 放入环形缓冲区 */
		PutInputEvent(&event);
	}
}

#else
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
	extern void DHT11_Notify_Task();
	if(KEY1_PIN == GPIO_Pin)
	{
		/* 启动定时器, 修改超时时间 */
		SetGPIOKeyTimer(0, HAL_GetTick()+20);
	}
	else if(KEY2_PIN == GPIO_Pin)
	{
		/* 启动定时器, 修改超时时间 */
		SetGPIOKeyTimer(1, HAL_GetTick()+20);
	}
	else if (DHT11_PIN == GPIO_Pin)
	{
		/* 记录中断发生的时间 */
		/* 如果收集到了80个数据: 唤醒任务 */
		if (dht11_edge_cnt == 83)
			return;
		dht11_edge_times[dht11_edge_cnt++] = DHT11_ReadTimer_us();
		if (dht11_edge_cnt == 80)
		{
			DHT11_Notify_Task();
		}
		
	}
}

#endif

uint8_t KEY1_Value(void)
{
	return key1_val;
}

uint8_t KEY2_Value(void)
{
	return key2_val;
}
