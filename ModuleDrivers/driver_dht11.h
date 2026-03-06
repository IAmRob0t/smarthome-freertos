#ifndef __DRIVER_DHT11_H
#define __DRIVER_DHT11_H

#include "stm32f1xx_hal.h"

#define DHT11_PIN           GPIO_PIN_6
#define DHT11_PORT          GPIOF
#define DHT11_CLK_EN()      __HAL_RCC_GPIOF_CLK_ENABLE()
#define DHT11_CLK_DIS()     __HAL_RCC_GPIOF_CLK_DISABLE()
    
#define DHT11_H      HAL_GPIO_WritePin(DHT11_PORT, DHT11_PIN, GPIO_PIN_SET)
#define DHT11_L      HAL_GPIO_WritePin(DHT11_PORT, DHT11_PIN, GPIO_PIN_RESET)
#define DHT11_IN     HAL_GPIO_ReadPin(DHT11_PORT, DHT11_PIN)

void DHT11_Init(void);
int DHT11_Read(unsigned int *temperature, unsigned int *humidity);


#endif /* __DRIVER_DHT11_H */
