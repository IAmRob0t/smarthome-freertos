# 前言

​	本篇是介绍STM32CubeMX工具中关于RTOS的各项配置在工程中的所在位置以及体现方式。

# 1. Config parameters

## 1.1 API

| ![](03_STM32CubeMX RTOS参数示例\00_api.jpg) |
| :-----------------------------------------: |

​	主要体现在会用到`CMSIS_RTOS_V2`中的`cmsis_os2.c`和`cmsis_os2.h`。

## 1.2 Version

| ![](03_STM32CubeMX RTOS参数示例\01_kernel_verison_id.jpg) |
| :-------------------------------------------------------: |

​	在`cmsis_os2.c`中定义了内核信息。

## 1.3 Kernel Settings

| ![](03_STM32CubeMX RTOS参数示例\02_kernel_settings.jpg) |
| :-----------------------------------------------------: |

​	`Kernel Settings`的设置在生成的工程中的`FreeRTOSConfig.h`文件中体现，当cubemx工具中修改了后，这个文件的这些值也会跟随改变。

## 1.4 Memory management settings

| ![](03_STM32CubeMX RTOS参数示例\03_mem_manage_settings.jpg) |
| :---------------------------------------------------------: |

​	`Memory management settings`的配置值也是在`FreeRTOSConfig.h`文件中体现。

## 1.5 Hook function related definitions

| ![](03_STM32CubeMX RTOS参数示例\04_hook.jpg) |
| :------------------------------------------: |

​	`Hook function related definitions`的配置值也是在`FreeRTOSConfig.h`文件中体现。

## 1.6 Run time and task stats gathering related definitions

| ![](03_STM32CubeMX RTOS参数示例\5_.jpg) |
| :-------------------------------------: |

​	`Run time and task stats gathering related definitions`的配置值也是在`FreeRTOSConfig.h`文件中体现，有些没有使能的在`FreeRTOS.h`文件中会被预处理宏定义为0。

## 1.7 Co-routine related definitions

| ![](03_STM32CubeMX RTOS参数示例\6_co-runtine.jpg) |
| :-----------------------------------------------: |

​	`Co-routine related definitions`的配置值会在`FreeRTOSConfig.h`文件中体现，有些没有使能的在`FreeRTOS.h`文件中会被预处理宏定义为0。

## 1.8 Software timer definitions

| ![](03_STM32CubeMX RTOS参数示例\7_soft_timer.jpg) |
| :-----------------------------------------------: |

​	`Software timer definitions`的配置值会在`FreeRTOSConfig.h`文件中体现。

## 1.9 Interrupt nesting behavior configuration

| ![](03_STM32CubeMX RTOS参数示例\8_interrupt_nesting.jpg) |
| :------------------------------------------------------: |

​	`Interrupt nesting behavior configuration`的配置值会在`FreeRTOSConfig.h`文件中体现。

# 2. Include parameters

| ![](03_STM32CubeMX RTOS参数示例\9_include_param.jpg) |
| :--------------------------------------------------: |

​	`Include parameters`的配置值会在`FreeRTOSConfig.h`文件中体现。

# 3. Advanced settings

| ![](03_STM32CubeMX RTOS参数示例\10_advance.jpg) |
| :---------------------------------------------: |

​	`Advanced settings`的配置值会在`FreeRTOS.h`文件中体现。

# 4. User constants

| ![](03_STM32CubeMX RTOS参数示例\11_constant.jpg) |
| :----------------------------------------------: |

​	`User constants`的配置值会在`main.h`文件中体现。

# 5. Tasks and Queues

​	`Tasks and Queues`的配置会在`freertos.c`文件完成初始化和新建。

| ![](03_STM32CubeMX RTOS参数示例\12_task.jpg) |
| :------------------------------------------: |

| ![](03_STM32CubeMX RTOS参数示例\13_queue.jpg) |
| :-------------------------------------------: |

# 6. Timers and Semaphores

​	`Timers and Semaphores`的配置会在`freertos.c`文件完成初始化和新建，可以创建二进制信号和计数型信号。

| ![](03_STM32CubeMX RTOS参数示例\14_timer_semaphore.jpg) |
| :-----------------------------------------------------: |

# 7. Mutexes

​	`Mutexes`的配置会在`freertos.c`文件完成初始化和新建，可以创建一般的互斥量和递归型的互斥量。

| ![](03_STM32CubeMX RTOS参数示例\15_mutex.jpg) |
| :-------------------------------------------: |

# 8. Events

| ![](03_STM32CubeMX RTOS参数示例\16_events.jpg) |
| :--------------------------------------------: |

`Events`的配置会在`freertos.c`文件完成初始化和新建。

# 9. FreeRTOS Heap Usage

​	下图是最终的资源消耗总结：

| ![](03_STM32CubeMX RTOS参数示例\17_summary.jpg) |
| :---------------------------------------------: |

