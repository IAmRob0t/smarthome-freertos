#include "kal_dht11.h"
#include "dht11_device.h"
#include "main.h"

static int DHT11DeviceInit(struct DHT11Dev *ptDHT11Dev)
{
    return KAL_DHT11DeviceInit(ptDHT11Dev);
}

static int DHT11Device_GetValue(struct DHT11Dev *ptDHT11Dev)
{
    return KAL_DHT11Device_GetValue(ptDHT11Dev);
}

static DHT11Dev g_tDHT11Devices = {1, {0}, DHT11DeviceInit, DHT11Device_GetValue};

PDHT11Dev GetDHT11Device(int which)
{
    if(which <= 1)
        return &g_tDHT11Devices;
    
    return NULL;
}
