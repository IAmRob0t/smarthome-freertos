#ifndef __KAL_DHT11_H
#define __KAL_DHT11_H

#include "dht11_device.h"

int KAL_DHT11DeviceInit(struct DHT11Dev *ptDHT11Dev);

int KAL_DHT11Device_GetValue(struct DHT11Dev *ptDHT11Dev);

#endif /* __KAL_DHT11_H */
