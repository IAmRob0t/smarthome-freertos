#include "cal_dht11.h"
#include "driver_dht11.h"

int CAL_DHT11DeviceInit(struct DHT11Dev *ptDHT11Dev)
{
    DHT11_Init();
    return 0;
}

int CAL_DHT11Device_GetValue(struct DHT11Dev *ptDHT11Dev)
{
    return DHT11_Read(&ptDHT11Dev->value.temperature, &ptDHT11Dev->value.humidity);
}
