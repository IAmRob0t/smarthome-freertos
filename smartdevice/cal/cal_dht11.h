#ifndef __CAL_DHT11_H
#define __CAL_DHT11_H

#include "dht11_device.h"

int CAL_DHT11DeviceInit(struct DHT11Dev *ptDHT11Dev);

int CAL_DHT11Device_GetValue(struct DHT11Dev *ptDHT11Dev);

#endif /* __CAL_DHT11_H */
