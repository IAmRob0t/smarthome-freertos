#include "kal_dht11.h"
#include "cal_dht11.h"

int KAL_DHT11DeviceInit(struct DHT11Dev *ptDHT11Dev)
{
    return CAL_DHT11DeviceInit(ptDHT11Dev);
}

int KAL_DHT11Device_GetValue(struct DHT11Dev *ptDHT11Dev)
{
    return CAL_DHT11Device_GetValue(ptDHT11Dev);
}
