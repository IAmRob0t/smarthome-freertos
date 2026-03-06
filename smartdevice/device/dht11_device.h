#ifndef __DHT11_DEVICE_H
#define __DHT11_DEVICE_H

typedef struct
{
    unsigned int temperature;
    unsigned int humidity;
}DHT11_VAL;

typedef struct DHT11Dev
{
    int which;
    DHT11_VAL value;
    int (*DevInit)(struct DHT11Dev *ptDHT11Dev);
    int (*GetValue)(struct DHT11Dev *ptDHT11Dev);
}DHT11Dev, *PDHT11Dev;

PDHT11Dev GetDHT11Device(int which);

#endif /* __DHT11_DEVICE_H */
