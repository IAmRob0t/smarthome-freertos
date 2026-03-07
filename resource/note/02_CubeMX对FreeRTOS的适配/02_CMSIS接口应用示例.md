# 前言

​	本篇是对CMSIS中RTOS接口的一些简单应用，使用的工程是基于STM32CubeMX创建的一个MDK工程模板。

# 1. API总览

​	首先看一下API一览：

| ![](02_CMSIS接口应用示例\0_all_api.png) |
| :-------------------------------------: |

其中红色字体的是CMSIS没有对FreeRTOS内核实现封装的。

# 2. 应用

## 2.1 内核信息和控制函数

### 2.1.1 内核信息

* 例程：`01_0_osKernelGetInfo`

* 获取内核信息的接口原型：

```c

osStatus_t osKernelGetInfo (osVersion_t *version,
							char *id_buf,
							uint32_t id_size 
							);
```

这三个参数在**01_接口函数和参数介绍**中介绍过了，我们去工程中使用它来获取内核信息。

* 例程代码

| <img src="02_CMSIS接口应用示例\15_get_kernel_info_code.png" style="zoom:75%;" /> |
| :----------------------------------------------------------: |

* 测试结果：

| ![](02_CMSIS接口应用示例\16_get_kernel_info_result.png) |
| :-----------------------------------------------------: |

需要说明的是，获取内核信息并不需要初始化内核，也不需要让内核run起来。

### 2.1.2 内核状态

* 例程：`01_1_osKernelGetState`
* 获取内核状态的接口原型：

```c
osKernelState_t osKernelGetState (void);
```

* 内核状态枚举：

```c
typedef enum {
  osKernelInactive        =  0,         ///< Inactive.
  osKernelReady           =  1,         ///< Ready.
  osKernelRunning         =  2,         ///< Running.
  osKernelLocked          =  3,         ///< Locked.
  osKernelSuspended       =  4,         ///< Suspended.
  osKernelError           = -1,         ///< Error.
  osKernelReserved        = 0x7FFFFFFFU ///< Prevents enum down-size compiler optimization.
} osKernelState_t;
```

* 接口解析

  本次使用的实时系统是FreeRTOS，`osKernelGetState`中调用的FreeRTOS的函数是`xTaskGetSchedulerState`。

* 例程代码

  我们分别在内核初始化前、初始化后以及开始运行后去获取下内核状态，看一下获得的状态码。另外在这一段会利用到一个任务，对于任务或者说线程的接口我们在后面说，这里只是暂时利用下它。

```c
/* main.c */
    /* USER CODE BEGIN 2 */
    EnableDebugIRQ();
    printf("深圳百问网科技有限公司\r\nwww.100ask.net\r\n");
    printf("RTOS训练营一期 \r\n");
    printf(">>>CMSIS API Test Get Kernel State Project<<<\r\n");
    
    osKernelState_t state_before_init, state_after_init;
    state_before_init = osKernelGetState();
    /* USER CODE END 2 */

    /* Init scheduler */
    osKernelInitialize();  /* Call init function for freertos objects (in freertos.c) */
  
    state_after_init = osKernelGetState();
    printf("内核初始化前的状态码：%d\r\n", state_before_init);
    printf("内核初始化后的状态码：%d\r\n", state_after_init);
    
/* freertos.c */
void StartDefaultTask(void *argument)
{
    /* USER CODE BEGIN StartDefaultTask */
    osKernelState_t state_after_start;
    state_after_start = osKernelGetState();
    printf("内核开始运行后的状态码：%d\r\n", state_after_start);
    /* Infinite loop */
    for(;;)
    {
        osDelay(1);
    }
    /* USER CODE END StartDefaultTask */
}
```

* 测试结果

| ![](02_CMSIS接口应用示例\17_get_kernel_state_result.png) |
| :------------------------------------------------------: |

* Tips

  在实际设计中，我们可以在一个优先级低的任务中定时获取内核状态，来判断系统处于什么状态：

```c
  /* freertos.c */
  void StartDefaultTask(void *argument)
  {
      /* USER CODE BEGIN StartDefaultTask */
      osKernelState_t state;
      state = osKernelGetState();
      printf("内核开始运行后的状态码：%d\r\n", state);
      /* Infinite loop */
      for(;;)
      {
          osDelay(1000);
          state = osKernelGetState();
          switch(state)
          {
              case osKernelInactive:
              {
                  printf("内核未准备好！\r\n");
                  break;
              }
              case osKernelReady:
              {
                  printf("内核已准备好！\r\n");
                  break;
              }
              case osKernelRunning:
              {
                  printf("内核正在运行中！\r\n");
                  break;
              }
              case osKernelLocked:
              {
                  printf("内核锁定！\r\n");
                  break;
              }
              case osKernelSuspended:
              {
                  printf("内核暂停运行！\r\n");
                  break;
              }
              case osKernelError:
              {
                  printf("内核发生错误！\r\n");
                  break;
              }
              default:break;
          }
      }
      /* USER CODE END StartDefaultTask */
  }
```

### 2.1.3 内核初始化函数

* 接口原型

```c
osStatus_t osKernelInitialize (void);
```

* 解析

  只有在对内核初始化之后，才能继续后面的对RTOS的操作。通过STM32CubeMX生成的工程模板已经调用此函数初始化内核了。

### 2.1.4 内核开始运行函数

* 例程：`01_2_osKernelStart`
* 接口原型

```c
osStatus_t osKernelStart (void);
```

* 解析

  通过调用此函数开启内核对任务或者线程的调度，在调用此函数之后的操作都不会执行到。

* 例程代码

| <img src="02_CMSIS接口应用示例\18_after_start_kernel.png" style="zoom:67%;" /> |
| :----------------------------------------------------------: |

像这样写的话后面这句`"After Start Kernrl."`是执行不到的，也就无法打印出来，我们看下结果：

| <img src="02_CMSIS接口应用示例\19_after_kernelstart_result.png" style="zoom:67%;" /> |
| :----------------------------------------------------------: |

### 2.1.5 锁定内核和解锁函数

* 例程：`01_3_osKernelLock_Unlock`
* 接口原型

```c
int32_t osKernelLock (void);
int32_t osKernelUnlock (void);
```

* 接口解析

  此函数会锁定内核，让内核暂停运行，然后去执行此函数之后的语句，直到调用解锁内核的函数，内核才会继续运行。

* 例程代码

```c
void StartDefaultTask(void *argument)
{
    /* USER CODE BEGIN StartDefaultTask */
    uint32_t count = 0;
    int32_t state = 0;
    printf("StartDefaultTask\r\n");
    /* Infinite loop */
    for(;;)
    {
        osDelay(1000);
        count++;
        printf("Running count: %d\r\n", count);
        if(count==5)
        {
            state = osKernelLock();
            printf("Lock Kernel State: %d\r\n", state);
            while((count++)<10)
            {
                printf("Kernel Locked count: %d\r\n", count);
            }
            osKernelUnlock();
            printf("Unlock Kernel!\r\n");
        }
    }
    /* USER CODE END StartDefaultTask */
}
```

* 测试结果

| <img src="02_CMSIS接口应用示例\20_kernel_lock_unlock_result.png" style="zoom:67%;" /> |
| :----------------------------------------------------------: |

可以看到，程序计数5次之后将内核锁定了，执行了锁定后的程序后重新解锁内核，任务又继续运行了。

### 2.1.6 重载内核锁定状态函数

* 例程：`01_4_osKernelRestoreLock`
* 接口原型：

```c
int32_t osKernelRestoreLock (int32_t lock);
```

* 接口解析

  这个函数是配合**osKernelLock**和**osKernelUnlock**使用的，这两个函数返回的都是调用它们前的内核状态，当执行完**osKernelLock**或**osKernelUnlock**后可以将它们的返回值使用**osKernelRestoreLock**函数重载内核状态。

* 例程代码

  比如***2.1.5**节的代码，在执行完lock后的程序后，可以用**osKernelRestoreLock**替代**osKernelUnlock**，这样写：

```c
void StartDefaultTask(void *argument)
{
    /* USER CODE BEGIN StartDefaultTask */
    uint32_t count = 0;
    int32_t state = 0;
    printf("StartDefaultTask\r\n");
    /* Infinite loop */
    for(;;)
    {
        osDelay(1000);
        count++;
        printf("Running count: %d\r\n", count);
        if(count==5)
        {
            state = osKernelLock();
            printf("Lock Kernel State: %d\r\n", state);
            while((count++)<10)
            {
                printf("Kernel Locked count: %d\r\n", count);
            }
            
            /* 替代osKernelUnlock */
            osKernelRestoreLock(state);
            
            printf("RestoreLock Kernel!\r\n");
        }
    }
    /* USER CODE END StartDefaultTask */
}
```

* 测试结果

| <img src="02_CMSIS接口应用示例\21_kernel_restorelock_result.png" style="zoom:67%;" /> |
| :----------------------------------------------------------: |

### 2.1.7 内核的暂停和重启函数

* 例程：这两个函数在FreeRTOS内核下是没有具体实现的，所以没有例程。
* 接口原型

```c
uint32_t osKernelSuspend (void);
void osKernelResume	(uint32_t sleep_ticks);
```

### 2.1.8 获取内核滴答定时器的频率和计数值函数

* 例程：`01_5_osKernelGetTick`
* 接口原型

```c
uint32_t osKernelGetTickCount (void);
uint32_t osKernelGetTickFreq (void);
```

* 接口解析

  这两个函数分别是获取内核时钟的频率和计数值的，可以用来做某些定时或计数的应用。

* 例程代码

```c
void StartDefaultTask(void *argument)
{
    /* USER CODE BEGIN StartDefaultTask */
    uint32_t tick_freq = 0;
    uint32_t tick_cnt_0 = 0;
    uint32_t tick = 0;
    
    tick_freq = osKernelGetTickFreq();
    printf("Kernel Tick Frequency is %d Hz\r\n", tick_freq);
    
    tick_cnt_0 = osKernelGetTickCount();
    printf("Start Tick Cnt is %d\r\n", tick_cnt_0);
    
    /* Infinite loop */
    for(;;)
    {
        osDelay(1);
        tick = osKernelGetTickCount();
        if( (tick - tick_cnt_0) == 1000 )
        {
            printf("Tick count has been runned 1000 Times\r\n");
            printf(">>>Current Tick: %d\t Last Tick: %d<<<\r\n", tick, tick_cnt_0);
            tick_cnt_0 = tick;
        }
    }
    /* USER CODE END StartDefaultTask */
}
```

* 测试结果

| <img src="02_CMSIS接口应用示例\22_kernel_tick_result.png" style="zoom:67%;" /> |
| :----------------------------------------------------------: |

### 2.1.9 获取内核系统定时器的频率和计数值函数

* 例程：`01_6_osKernelGetSysTimer`
* 接口原型

```c
uint32_t osKernelGetSysTimerFreq (void);
uint32_t osKernelGetSysTimerCount (void);
```

* 接口解析

  这两个函数是获取内核系统频率和计数的，通常情况下内核的频率就是我们设置的芯片的工作频率。

* 例程代码

```C
void StartDefaultTask(void *argument)
{
    /* USER CODE BEGIN StartDefaultTask */
    uint32_t cur_count = 0, last_count = 0;
    uint32_t sys_timer_freq = 0;

    sys_timer_freq = osKernelGetSysTimerFreq();
    last_count = osKernelGetSysTimerCount();
    printf("Kernel System Timer Frequency is %d Hz.\r\n", sys_timer_freq);
    printf("Start Kernel System Timer Count is %d.\r\n", last_count);

    /* Infinite loop */
    for(;;)
    {
        osDelay(1);
        cur_count = osKernelGetSysTimerCount();
        if( (cur_count - last_count) > (sys_timer_freq) )
        {
            /* sys_timer_freq --> 系统频率作为计数上限值
             * 相当于每隔1Hz即1s进入一次这个判断
             */
            printf("Kernel System Timer Has Been Runned %d Times.\r\n", sys_timer_freq);
            printf("Current count: %d\t Last count: %d\r\n", cur_count, last_count);
            last_count = cur_count;
        }
    }
    /* USER CODE END StartDefaultTask */
}
```

* 测试结果

| <img src="02_CMSIS接口应用示例\23_kernel_sys_timer_result.png" style="zoom:67%;" /> |
| :----------------------------------------------------------: |

## 2.2 线程管理函数

​	从这一节开始我们会在工程中新建一个目录叫`api_test`，我们会在里面新建源文件来存放示例代码。

### 2.2.1 新建线程和线程退出

* 例程：`02_0_osThreadNew_Delete`
* 接口原型

```c
osThreadId_t osThreadNew (osThreadFunc_t func, 	// 线程入口函数
						  void *argument, 		// 传给线程任务的起始参数
						  const osThreadAttr_t *attr);	// 线程任务的属性
void osThreadExit(void);
```

* 接口解析

  当在线程中调用`osThreadExit`函数时，会退出当前线程。对于FreeRTOS内核而言，这个接口调用更多是FreeRTOS的`vTaskDelete`函数，所以一旦使用`osThreadExit`退出当前线程后，该线程就被释放掉了，无法再启动。
  
  `osThreadNew`这个接口需要3个参数，第一个是入口函数，也就是我们任务的主体函数，这个函数不能有返回值；第二个是传给入口函数的参数，一般是给的NULL；最后个参数是线程的属性，线程具有哪些属性呢？我们来看一看：

```c
typedef struct {
  				const char                   *name;   ///< name of the thread
  				uint32_t                 attr_bits;   ///< attribute bits
  				void                      *cb_mem;    ///< memory for control block
  				uint32_t                   cb_size;   ///< size of provided memory for control block
  				void                   *stack_mem;    ///< memory for stack
  				uint32_t                stack_size;   ///< size of stack
  				osPriority_t              priority;   ///< initial thread priority (default: osPriorityNormal)
  				TZ_ModuleId_t            tz_module;   ///< TrustZone module identifier
  				uint32_t                  reserved;   ///< reserved (must be 0)
} osThreadAttr_t;

```

从这个线程属性结构体中我们可以得出以下几个结论：	

​	① 我们可以给一个线程任务定义名称，程序中可以通过名称得到这个线程的ID，从而来控制这个线程；

​	② 属性位是用来使线程可结合或不可结合的，其可配置的有两个宏定义参数可选：

```c
#define osThreadJoinable   0x00000001U	// 使多个线程可以结合
#define osThreadDetached   0x00000000U	// 不可结合
```

这一个结构体成员的作用在后面介绍线程结合函数的时候说明。

​	③ cb就是control block的缩写，`cb_mem`和`cb_size`是用来给线程任务分配静态内存块的；

​	④ `stack_mem`和`stack_size`是用来分配静态内存堆空间的，可以用来改变我们使用STM32CubeMX配置的默认128*4bytes的堆空间大小；

​	⑤ `priority`用来设置线程任务的优先级，线程任务的优先级数值越高，优先级越高，在CMSIS封装的接口中的优先级枚举是这样的：

```c
typedef enum {
  osPriorityNone          =  0,         ///< No priority (not initialized).
  osPriorityIdle          =  1,         ///< Reserved for Idle thread.
  osPriorityLow           =  8,         ///< Priority: low
  osPriorityLow1          =  8+1,       ///< Priority: low + 1
  osPriorityLow2          =  8+2,       ///< Priority: low + 2
  osPriorityLow3          =  8+3,       ///< Priority: low + 3
  osPriorityLow4          =  8+4,       ///< Priority: low + 4
  osPriorityLow5          =  8+5,       ///< Priority: low + 5
  osPriorityLow6          =  8+6,       ///< Priority: low + 6
  osPriorityLow7          =  8+7,       ///< Priority: low + 7
  osPriorityBelowNormal   = 16,         ///< Priority: below normal
  osPriorityBelowNormal1  = 16+1,       ///< Priority: below normal + 1
  osPriorityBelowNormal2  = 16+2,       ///< Priority: below normal + 2
  osPriorityBelowNormal3  = 16+3,       ///< Priority: below normal + 3
  osPriorityBelowNormal4  = 16+4,       ///< Priority: below normal + 4
  osPriorityBelowNormal5  = 16+5,       ///< Priority: below normal + 5
  osPriorityBelowNormal6  = 16+6,       ///< Priority: below normal + 6
  osPriorityBelowNormal7  = 16+7,       ///< Priority: below normal + 7
  osPriorityNormal        = 24,         ///< Priority: normal
  osPriorityNormal1       = 24+1,       ///< Priority: normal + 1
  osPriorityNormal2       = 24+2,       ///< Priority: normal + 2
  osPriorityNormal3       = 24+3,       ///< Priority: normal + 3
  osPriorityNormal4       = 24+4,       ///< Priority: normal + 4
  osPriorityNormal5       = 24+5,       ///< Priority: normal + 5
  osPriorityNormal6       = 24+6,       ///< Priority: normal + 6
  osPriorityNormal7       = 24+7,       ///< Priority: normal + 7
  osPriorityAboveNormal   = 32,         ///< Priority: above normal
  osPriorityAboveNormal1  = 32+1,       ///< Priority: above normal + 1
  osPriorityAboveNormal2  = 32+2,       ///< Priority: above normal + 2
  osPriorityAboveNormal3  = 32+3,       ///< Priority: above normal + 3
  osPriorityAboveNormal4  = 32+4,       ///< Priority: above normal + 4
  osPriorityAboveNormal5  = 32+5,       ///< Priority: above normal + 5
  osPriorityAboveNormal6  = 32+6,       ///< Priority: above normal + 6
  osPriorityAboveNormal7  = 32+7,       ///< Priority: above normal + 7
  osPriorityHigh          = 40,         ///< Priority: high
  osPriorityHigh1         = 40+1,       ///< Priority: high + 1
  osPriorityHigh2         = 40+2,       ///< Priority: high + 2
  osPriorityHigh3         = 40+3,       ///< Priority: high + 3
  osPriorityHigh4         = 40+4,       ///< Priority: high + 4
  osPriorityHigh5         = 40+5,       ///< Priority: high + 5
  osPriorityHigh6         = 40+6,       ///< Priority: high + 6
  osPriorityHigh7         = 40+7,       ///< Priority: high + 7
  osPriorityRealtime      = 48,         ///< Priority: realtime
  osPriorityRealtime1     = 48+1,       ///< Priority: realtime + 1
  osPriorityRealtime2     = 48+2,       ///< Priority: realtime + 2
  osPriorityRealtime3     = 48+3,       ///< Priority: realtime + 3
  osPriorityRealtime4     = 48+4,       ///< Priority: realtime + 4
  osPriorityRealtime5     = 48+5,       ///< Priority: realtime + 5
  osPriorityRealtime6     = 48+6,       ///< Priority: realtime + 6
  osPriorityRealtime7     = 48+7,       ///< Priority: realtime + 7
  osPriorityISR           = 56,         ///< Reserved for ISR deferred thread.
  osPriorityError         = -1,         ///< System cannot determine priority or illegal priority.
  osPriorityReserved      = 0x7FFFFFFF  ///< Prevents enum down-size compiler optimization.
} osPriority_t;
```

​	⑥ 信任区模块标志，这个在CMSIS中只是一个宏定义，一般很少用：

```c
#define TZ_MODULEID_T

typedef uint32_t TZ_ModuleId_t
```

所以我们要新建一个任务，需要有一个已经定义好的入口函数，需要设置这个函数的属性（这不是必须的，可以直接让其为NULL）。

* 新建一个简单的线程任务

  一个简单的任务就是只有入口函数，既不设置参数也不设置属性：

```c
/* api_test.c */

/* 声明入口函数 */
static void thread1(void *argument);

/* 对外的任务初始化函数接口 */
void api_osThreadNew_init(void)
{
    /* 对于一个简单的任务，不需要输入参数，也不需要设置线程任务的属性 */
    osThreadId_t thread1_id = osThreadNew(thread1, NULL, NULL);
}

/* 新建的简单的线程任务入口函数 */
static void thread1(void *argument)
{
    printf("ThreadNew Simple Thread\r\n");
    for(;;)
    {
        osDelay(1);
    }
}
```

* 新建一个非默认堆大小的线程任务

  非默认堆大小就是要去改变线程任务属性中的堆大小那个结构体成员`stack_size`：

```c
/* api_test.c */
/* 线程任务的ID */
osThreadId_t thread2_id;
/* 线程任务2的属性初始化 */
const osThreadAttr_t thread2_attr = {
  .stack_size = 1024,                            // Create the thread stack with a size of 1024 bytes
};

static void thread2(void *argument);

/* 对外的任务初始化函数接口 */
void api_osThreadNew_init(void)
{
    /* 新建一个修改堆大小的线程 */
    thread2_id = osThreadNew(thread2, NULL, &thread2_attr);
}

/* 新建的修改堆大小的线程任务2的入口函数 */
static void thread2(void *argument)
{
    printf("Thread2 ID: %d\tStack size: %d\r\n", (int)thread2_id, thread2_attr.stack_size);
    
    for(;;)
    {
        osDelay(10);
    }
}
```

* 新建一个分配静态内存的线程任务

  分配静态内存给线程任务就是要设置线程任务属性中的控制块和堆空间：

```c
/* 线程任务的ID */
osThreadId_t thread3_id;

/* 指定线程的堆空间 */
static uint64_t thread3_stk[64];

/* 线程的控制块结构体 */
static uint8_t thread3_tcb[1024];

/* 线程任务的属性初始化 */
const osThreadAttr_t thread3_attr = {
    .cb_mem = &thread3_tcb[0],
    .cb_size = sizeof(thread3_tcb),
    .stack_mem = &thread3_stk[0],       // 指定线程3的堆空间地址
    .stack_size = sizeof(thread3_stk),  // 设置线程3的对空间大小
};

/* 声明入口函数 */
static void thread3(void *argument);

/* 新建一个指定堆空间和大小的线程 */
static void thread3(void *argument)
{
    printf("Thread3 ID: %d\tStack memory address: 0x%x\r\n", (int)thread3_id, (uint32_t)thread3_attr.stack_mem);
    printf("Thread3 ID: %d\tStack size: %d\r\n", (int)thread3_id,thread3_attr.stack_size);
    
    for(;;)
    {
        osDelay(5);
    }
}

/* 对外的任务初始化函数接口 */
void api_osThreadNew_init(void)
{    
    /* 新建一个指定堆空间和大小的线程 */
    thread3_id = osThreadNew(thread3, NULL, &thread3_attr);
}
```

* 新建一个不同优先等级的线程任务

  对于线程的优先级，如果是同意优先级，默认情况下是谁后创建谁的优先等级高，但是我们可以修改线程的属性中的优先等级那个结构体成员来设置不同任务的不同优先等级，比如我们前面建立的3个线程任务，我们就设置他们的优先级又低到高如下：thread2-->thread3-->thread1

```c
/* 线程任务的属性初始化 */
const osThreadAttr_t thread1_attr = {
  .priority = (osPriority_t)osPriorityLow2,   // 让线程1的优先等级是osPriorityLow2
};

const osThreadAttr_t thread2_attr = {
  .stack_size = 1024,   // 让线程2的堆大小变成1024bytes
    .priority = (osPriority_t)osPriorityLow,   // 让线程2的优先等级是osPriorityLow
};

const osThreadAttr_t thread3_attr = {
    .cb_mem = &thread3_tcb[0],
    .cb_size = sizeof(thread3_tcb),
    .stack_mem = &thread3_stk[0],       // 指定线程3的堆空间地址
    .stack_size = sizeof(thread3_stk),  // 设置线程3的对空间大小
    .priority = (osPriority_t)osPriorityLow1,   // 让线程3的优先等级是osPriorityLow1
};

/* 对外的任务初始化函数接口 */
void api_osThreadNew_init(void)
{
    /* 对于一个简单的任务，不需要输入参数，也不需要设置线程任务的属性 */
    thread1_id = osThreadNew(thread1, NULL, &thread1_attr);
    
    /* 新建一个修改堆大小的线程 */
    thread2_id = osThreadNew(thread2, NULL, &thread2_attr);
    
    /* 新建一个指定堆空间和大小的线程 */
    thread3_id = osThreadNew(thread3, NULL, &thread3_attr);
}
```

默认情况下是线程3的优先级最高最先执行，然后是线程2，最后是线程1，但是设置优先级后，就会最先执行线程1，然后是线程3，然后是线程2，之后，我们让新建的线程1运行3s后退出，线程2运行5s后退出，线程3运行8s后退出。

* 例程代码

```c
/* 新建的简单的线程任务入口函数 */
static void thread1(void *argument)
{
    uint32_t count = 0;
    printf("ThreadNew Simple Thread\r\n");
    for(;;)
    {
        if((count++)==3)
        {
            printf("线程1退出运行 \r\n");
            osThreadExit();
        }
        else
        {
            printf(">>>Thread_1 runs %d s\r\n", count);
        }
        osDelay(1000);
    }
}

/* 新建的修改堆大小的线程任务2的入口函数 */
static void thread2(void *argument)
{
    uint32_t count = 0;
    printf("Thread2 ID: %d\tStack size: %d\r\n", (int)thread2_id, thread2_attr.stack_size);
    
    for(;;)
    {
        if((count++)==5)
        {
            printf("线程2退出运行 \r\n");
            osThreadExit();
        }
        else
        {
            printf(">>>Thread_2 runs %d s\r\n", count);
        }
        osDelay(1000);
    }
}

/* 新建一个指定堆空间和大小的线程 */
static void thread3(void *argument)
{
    uint32_t count = 0;
    printf("Thread3 ID: %d\tStack memory address: %d\r\n", (int)thread3_id, (int)thread3_attr.stack_mem);
    printf("Thread3 ID: %d\tStack size: %d\r\n", (int)thread3_id,thread3_attr.stack_size);
    
    for(;;)
    {
        if((count++)==8)
        {
            printf("线程3退出运行 \r\n");
            osThreadExit();
        }
        else
        {
            printf(">>>Thread_3 runs %d s\r\n", count);
        }
        osDelay(1000);
    }
}
```

* 测试结果

| <img src="02_CMSIS接口应用示例\24_thread_prioty.png" style="zoom:67%;" /> |
| :----------------------------------------------------------: |



### 2.2.2 获取线程的名称、ID和状态

* 例程：`02_2_osThreadGetName_Id_State`
* 接口原型

```c
const char *osThreadGetName (osThreadId_t thread_id);
osThreadId_t osThreadGetId (void);
osThreadState_t osThreadGetState (osThreadId_t thread_id);
```

* 接口解析

​	获取线程的名称和状态是根据线程ID去查找获取的，而获取线程ID这个接口函数，它获取的是当前所在线程且是一个正在运行状态下的线程的ID。

* 例程代码

```c
/* 线程任务的属性初始化 */
const osThreadAttr_t thread1_attr = {
    .name = "Thread 1"    // 设置线程的名称
};

/* 新建的简单的线程任务入口函数 */
static void thread1(void *argument)
{
    osThreadId_t cur_id = osThreadGetId();
    const char *name = osThreadGetName(cur_id);
    osThreadState_t state = osThreadGetState(cur_id);
    
    printf("Current running thread's id: 0x%x\r\n", (uint32_t)cur_id);
    printf(">>> Name: %s\r\n", name);
    printf(">>> State: %d\r\n", state);
    for(;;)
    {
        osDelay(10);
    }
}
```

* 测试结果

| ![](02_CMSIS接口应用示例\25_get_thread_name_id.png) |
| :-------------------------------------------------: |

### 2.2.3 线程的优先级

* 例程：`02_3_osThreadSet_Get_Priority`
* 接口原型

```c
osStatus_t osThreadSetPriority (osThreadId_t thread_id, osPriority_t priority);
osPriority_t osThreadGetPriority (osThreadId_t thread_id);
```

* 接口解析

  这两个函数是设置指定线程ID对应线程的优先级，在应用中可以根据实时性或者数据重要性等来动态设置某个任务的优先级，让其先与某些任务执行或者后于某些任务执行。

* 代码例程

```c
/* 线程任务的属性初始化 */
const osThreadAttr_t thread1_attr = {
    .priority = (osPriority_t)osPriorityLow2,   // 让线程1的优先等级是osPriorityLow2
};

const osThreadAttr_t thread2_attr = {
    .priority = (osPriority_t)osPriorityLow1,   // 让线程2的优先等级是osPriorityLow
};

/* 线程任务1的入口函数 */
static void thread1(void *argument)
{   
    osStatus status;
    
    osPriority_t priority= osThreadGetPriority(thread1_id);
    for(;;)
    {
        printf("Thread_1 >>> 1\r\n");
        status = osThreadSetPriority(thread2_id, priority + 1);
        printf("Thread_1 >>> 2\r\n");
        osDelay(1000);
    }
}

/* 线程任务2的入口函数 */
static void thread2(void *argument)
{
    osStatus status;
    
    osPriority_t priority= osThreadGetPriority(thread1_id);
    for(;;)
    {
        printf("Thread_2 >>> 3\r\n");
        status = osThreadSetPriority(thread2_id, priority - 1);
        printf("Thread_2 >>> 4\r\n");
        osDelay(1000);
    }
}
```

* 测试结果

| <img src="02_CMSIS接口应用示例\26_thread_priority_result.png" style="zoom:67%;" /> |
| :----------------------------------------------------------: |

​	如果我们没有改变线程2的优先级，在默认情况下线程1的优先级是要优于线程2的，那么这种情况下打印出来的结果应该是`Thread_1 >>> 1 ——> Thread_1 >>> 2 ——> Thread_2 >>> 3 ——> Thread_2 >>> 4` ，但是我们在线程1中提高了线程2的优先等级，让线程2在下一个任务调度先执行，即打印了`Thread_1 >>> 1` 后提高了线程2的优先级高于线程1，所以会立即去执行线程2，即打印`Thread_2 >>> 3`，之后又将线程2的优先级降低于线程1，所以下一刻又会回到线程1去打印`Thread_1 >>> 2`，然后再调度到线程2打印`Thread_2 >>> 4`得到我们的结果。

### 2.2.4 线程让步

* 例程：`02_4_osThreadYield`
* 接口原型

```c
osStatus_t osThreadYield (void);
```

* 接口解析

  这个函数的作用是让正在运行的线程1处于就绪状态，然后和线程1相同优先级且处于准备状态的线程2、3、4……n立即执行。

* 例程代码

  例程设计了两个相同优先级的线程，线程1进入循环就立即让步，让线程2执行，线程2执行完之后退出线程，线程1等待线程2执行完之后再执行，最后同样退出线程。

```c
/* 线程任务的属性初始化 */
const osThreadAttr_t thread1_attr = {
    .priority = (osPriority_t)osPriorityLow1,   // 让线程1的优先等级是osPriorityLow1
};

const osThreadAttr_t thread2_attr = {
    .priority = (osPriority_t)osPriorityLow1,   // 让线程2的优先等级是osPriorityLow1
};

/* 线程任务1的入口函数 */
static void thread1(void *argument)
{       
    osStatus status;
    for(;;)
    {
        status = osThreadYield();
        printf("1\r\n");
        printf("2\r\n");
        osThreadExit();
    }
}

/* 线程任务2的入口函数 */
static void thread2(void *argument)
{
    osStatus status;
    for(;;)
    {
        printf("3\r\n");
        printf("4\r\n");
        osThreadExit();
    }
}
```

* 测试结果

| <img src="02_CMSIS接口应用示例\27_thread_yield.png" style="zoom:67%;" /> |
| :----------------------------------------------------------: |

### 2.2.5 线程的暂停和重启

* 例程：`02_5_osThreadSuspend_Resume`
* 接口原型

```c
osStatus_t osThreadSuspend (osThreadId_t thread_id);
osStatus_t osThreadResume (osThreadId_t thread_id);
```

* 接口解析

  `osThreadSuspend`会将指定id的线程从运行状态变为阻塞状态，`osThreadResume`会将指定id的线程从阻塞状态恢复为准备状态。如果resume的线程的优先级高于某个正在运行的线程，那么这个resume后的线程会在下一刻被立即执行。

* 例程代码

  例程中让线程1每隔5s暂停线程2的运行，然后等待5s恢复线程2的运行：

```c
/* 线程任务1的入口函数 */
static void thread1(void *argument)
{       
    uint32_t count = 0;
    osStatus status;
    for(;;)
    {
        count++;
        printf("Thread_1 is running: %d\r\n", count);
        if(count == 5)
        {
            status = osThreadSuspend(thread2_id);
            if(status == osOK)
            {
                printf("Suspend Thread_2\r\n");
            }
        }
        if(count==10)
        {
            status = osThreadResume(thread2_id);
            if(status == osOK)
            {
                printf("Resume Thread_2\r\n");
                count = 0;
            }
        }
        osDelay(1000);
    }
}

/* 线程任务2的入口函数 */
static void thread2(void *argument)
{
    uint32_t count = 0;
    osStatus status;
    for(;;)
    {
        count++;
        printf("Thread_2 >>> %d\r\n", count);
        osDelay(1000);
    }
}
```

* 测试结果

| <img src="02_CMSIS接口应用示例\28_thread_suspend_resume.png" style="zoom:67%;" /> |
| :----------------------------------------------------------: |

### 2.2.6 线程的结合和分离

* 例程：无
* 接口原型

```c
osStatus_t osThreadDetach(osThreadId_t thread_id);
osStatus_t osThreadJoin	(osThreadId_t thread_id);
```

* 接口解析

  `osThreadDetach`让指定id的slave线程从之前被结合进去的master线程中分离出来，而`osThreadJoin`则是让线程结合到另一个线程中去。被结合的master线程只有当结合进去的slave线程执行完且通过`osThreadExit`退出线程后才会执行自身的处理。

* 例程代码

  因为FreeRTOS中没有对任务的join和detach，所以CMSIS封装FreeRTOS接口的时候，没有实现这两个功能，下面展示的是对这两个接口的伪代码示例：

```C
__NO_RETURN void worker (void *argument) {
  ; // work a lot on data[] 
  osDelay(1000U);
  osThreadExit();
}
 
__NO_RETURN void thread1 (void *argument) {
  osThreadAttr_t worker_attr;
  osThreadId_t worker_ids[4];
  uint8_t data[4][10];
  memset(&worker_attr, 0, sizeof(worker_attr));
  worker_attr.attr_bits = osThreadJoinable;
 
  worker_ids[0] = osThreadNew(worker, &data[0][0], &worker_attr);
  worker_ids[1] = osThreadNew(worker, &data[1][0], &worker_attr);
  worker_ids[2] = osThreadNew(worker, &data[2][0], &worker_attr);
  worker_ids[3] = osThreadNew(worker, &data[3][0], &worker_attr);
 
  osThreadJoin(worker_ids[0]);
  osThreadJoin(worker_ids[1]);
  osThreadJoin(worker_ids[2]);
  osThreadJoin(worker_ids[3]);
 
  osThreadExit(); 
}
```

### 2.2.7 线程的终止

* 例程：`02_6_osThreadTerminate`
* 接口原型

```c
osStatus_t osThreadTerminate (osThreadId_t thread_id);
```

* 接口解析

  此函数会将指定id的线程终止，且从线程列表中删除，然后执行后面的处于活跃状态且是准备状态的线程，如果要删除的id对应的线程已经不在线程列表里面了则会返回一个错误代码。

* 例程代码

  例程中让线程1运行5s后终止正在运行的线程2，然后继续运行5s后终止自己：

```c
/* 线程任务1的入口函数 */
static void thread1(void *argument)
{       
    uint32_t count = 0;
    osStatus status;
    for(;;)
    {
        count++;
        printf("Thread_1 is running: %d\r\n", count);
        if(count == 5)
        {
            status = osThreadTerminate(thread2_id);
            if(status == osOK)
            {
                printf("Terminate Thread_2 OK\r\n");
            }
        }
        if(count==10)
        {
            status = osThreadTerminate(thread1_id);
            if(status == osOK)
            {
                printf("Terminate Thread_1 OK\r\n");
            }
            else
            {
                printf("Terminate Thread_1 Error!\r\n");
            }
        }
        osDelay(1000);
    }
}

/* 线程任务2的入口函数 */
static void thread2(void *argument)
{
    uint32_t count = 0;
    osStatus status;
    for(;;)
    {
        count++;
        printf("Thread_2 >>> %d\r\n", count);
        osDelay(1000);
    }
}
```

* 测试结果

| <img src="02_CMSIS接口应用示例\29_thread_terminate.png" style="zoom:67%;" /> |
| :----------------------------------------------------------: |

### 2.2.8 获取线程的堆空间信息

* 例程：`02_7_osThreadGetStack`
* 接口原型

```c
uint32_t osThreadGetStackSize (osThreadId_t thread_id);	// 获取线程的整个堆空间大小
uint32_t osThreadGetStackSpace (osThreadId_t thread_id);	// 获取线程的剩余的堆空间大小
```

* 接口解析

  `osThreadGetStackSize`的实现CMSIS官方备注是未能实现的，所以无法使用。`osThreadGetStackSpace`获取指定id对应线程的剩余的堆空间大小，单位是byte。

* 例程代码

  例程设计让线程1运行5s后去获取线程2的堆空间大小：

```c
static void thread1(void *argument)
{       
    uint32_t count = 0;
    uint32_t stack_size = 0, remain_size = 0;
    for(;;)
    {
        printf("Remain %d seconds\r\n", 5-count);
        count++;
        if(count == 5)
        {
            stack_size = osThreadGetStackSize(thread2_id);
            remain_size = osThreadGetStackSpace(thread2_id);
            
            if(stack_size == 0)
            {
                printf("Get Thread_2 Stack Size Error.\r\n");
            }
            else
            {
                printf("Thread_2 Total Stack Size is %d bytes.\r\n", stack_size);
            }
            if(remain_size == 0)
            {
                printf("Get Thread_2 Remain Stack Size Error.\r\n");
            }
            else
            {
                printf("Thread_2 Remain Stack Size is %d bytes.\r\n", remain_size);
            }
            osThreadExit();
        }
        osDelay(1000);
    }
}

/* 线程任务2的入口函数 */
static void thread2(void *argument)
{
    for(;;)
    {
        osDelay(1000);
    }
}
```

* 测试结果

| <img src="02_CMSIS接口应用示例\30_get_thread_stack.png" style="zoom:75%;" /> |
| :----------------------------------------------------------: |

### 2.2.9 获取线程列表中的线程

* 例程：`02_8_osThreadGetCount_Enum`
* 接口原型

```c
uint32_t osThreadGetCount (void);
uint32_t osThreadEnumerate (osThreadId_t *thread_array, uint32_t array_items);
```

* 接口解析

  `osThreadGetCount`获取当前内核中处于活跃状态的线程个数，`osThreadEnumerate`获取当前内核中的所有线程个数，并获取它们的ID。如果这两个函数的返回值是0，那就代表获取信息发生了错误。

* 例程代码

  例程中让线程1运行5s后去获取内核中的线程信息，然后退出线程，线程2则一直运行：

```c
/* 线程任务1的入口函数 */
static void thread1(void *argument)
{       
    int i = 0;
    uint32_t count = 0;
    uint32_t active_thread_cnt = 0;
    uint32_t thread_cnt = 0;
    osThreadId_t thread_ids[10];
    
    for(;;)
    {
        printf("%d\r\n", 5-count);
        count++;
        if(count == 5)
        {
            active_thread_cnt = osThreadGetCount();
            thread_cnt = osThreadEnumerate(thread_ids, 10);
            if(active_thread_cnt == 0)
            {
                printf("Get Active Thread Count Error!\r\n\r\n");
            }
            else
            {
                printf("Now there are %d active thread.\r\n", active_thread_cnt);
            }
            if(thread_cnt==0)
            {
                printf("Get Thread Count Error!\r\n");
            }
            else
            {
                printf("There are %d threads in enumerate.\r\n", thread_cnt);
                printf("Their IDS are \t");
                for(i=0; i<thread_cnt; i++)
                {
                    printf("0x%x\t", (uint32_t)thread_ids[i]);
                }
                printf("\r\n");
            }
            osThreadExit();
        }

        osDelay(1000);
    }
}

/* 线程任务2的入口函数 */
static void thread2(void *argument)
{
    for(;;)
    {
        osDelay(1000);
    }
}
```

* 测试结果

| <img src="02_CMSIS接口应用示例\31_get_kernel_thread.png" style="zoom:77%;" /> |
| :----------------------------------------------------------: |

## 2.3 线程标志函数

### 2.3.1 设置和获取线程的标志

* 例程：`03_0_osThreadFlagSet_Get`
* 接口原型

```C
uint32_t osThreadFlagsSet (osThreadId_t thread_id, uint32_t flags);
uint32_t osThreadFlagsGet (void);
```

* 接口解析

  函数`osThreadFlagsSet`实现的功能是让指定id的线程的标志和设置的这个`flags`相或，如果线程的标志在设置前是`t_flag = 0;`我们在某个地方调用此函数传入标志参数`flags=3`，那么最后`t_flag = 0|3 = 3;`如果我们接下来再调用此函数传入参数`flags=2`，那么`t_flag`等于多少？既然是相或，也就是原本的3和现在2相或，得到的结果还是3。

  函数`osThreadFlagsGet`它是获取当前线程的标志值，我们可以通过判断获取的这个值的某些位数，来做一些逻辑控制。

* 例程代码

  我们的例程写的很简单，就是让线程1每隔500ms设置一次线程2的标志，线程2则是每隔50ms去获取它本身的标志，并将其输出出来。

```c
/* 线程任务1的入口函数 */
static void thread1(void *argument)
{
    uint32_t count = 0;
    
    for(;;)
    {
        printf("%d\r\n", count);
        
        osThreadFlagsSet(thread2_id, 1<<count);
        if((count++) > 5)
        {
            osThreadExit();
        }
        osDelay(500);
    }
}

/* 线程任务2的入口函数 */
static void thread2(void *argument)
{
    uint32_t cur_flag = 0, last_flag = 0;
    for(;;)
    {
        cur_flag = osThreadFlagsGet();
        if(last_flag != cur_flag)
        {
            last_flag = cur_flag;
            printf("Thread_2 Flag: 0x%x OK!\r\n", cur_flag);
        }
        osDelay(50);
    }
}
```

* 测试结果

| <img src="02_CMSIS接口应用示例\32_set_get_thread_flag.png" style="zoom:80%;" /> |
| :----------------------------------------------------------: |

​	可以看到设置的标志值分别是：***0 | (1<<0)=0x1 ——> 1 | (1<<1)=0x3 ——> 3 | (1<<2)=0x7 ——>...——>0x3F | (1<<6) = 0x7F***

### 2.3.2 等待和清除线程的标志

* 例程：`03_1_osThreadFlagWait_Clear`
* 接口原型

```c
uint32_t osThreadFlagsWait (uint32_t flags, 	// 想要等待的标志
                            uint32_t options,	// 等待的操作字：osFlagsWaitAny、osFlagsWaitAll、osFlagsNoClear
                            uint32_t timeout);	// 延时时间：0~osWaitForever
uint32_t osThreadFlagsClear (uint32_t flags);	// 想要清除的标志
```

* 接口解析

  函数`osThreadFlagsWait`是等待当前线程的某一位或者某几位满足预期等待的标志`flags`，等待的时间单位是ms，但是如果等待时间输入的是`osWaitForever`那么如果当前线程的标志一直无法满足预期，那么该线程就会陷入阻塞状态，直到标志满足为止。比如预期等待的标志`flags=0x03`也就是第0位和第1位是1其它的是0，或者说有连续的2位是1，这关键是看操作字是如何设置的，如果设置的是`osFlagsWaitAll`那么就是bit[1:0]=[1,1]，bit[其它]=0，而如果设置的是`osFlagsWaitAny`那么只要有任意两个连着的bit[n+1:n]=[1,1]即可；还有一个关键字是`osFlagsNoClear`，它是用来控制函数`osThreadFlagsWait`在等到标志之后是否清除掉预期标志的那几个bit，缺省情况下是默认清除的，比如如果我预期等待的标志是`0x03`，设置的操作字是`osFlagsWaitAll | osFlagsNoClear`，当线程的标志被设置为`0x03`时，这个函数就会返回`0x03`，而如果操作字仅仅是写作`osFlagsWaitAll`，那么当线程的标志被设置为`0x03`满足需求后，就会将标志的bit[1:0]设置为0，返回值就是0。

  函数`osThreadFlagsClear`是清除当前线程标志的某几位，比如当前线程的标志是`0x0B(0b0000 1011)`，想要清除的标志是`flags=0xA`，那么当前线程的标志就会变成`0x1`，它的内部做法是：

```
t_flag &= ~flags;
0b0000 1011 &= ~0b0000 1010 ——> 0b0000 1011 &= 0b1111 0101 ——> t_flag = 0b0000 0001 = 0x01
```

* 例程代码

  例程是将不同的操作字组合、不同的等待时间都做了测试演示。

```c
/* 线程任务2的入口函数 */
static void thread2(void *argument)
{
    uint32_t last_flag = 0, cur_flag = 0;
    for(;;)
    {
        /* 等待函数有3中操作字：osFlagsWaitAny、osFlagsWaitAll、osFlagsNoClear
         * osFlagsWaitAny：任意位满足等待的标志即可
         * osFlagsWaitAll：需要整个标志所有位满足等待的标志
         * osFlagsNoClear：等到标志后不清除标志
         * 这几个操作字可以组合使用，通常前两个和osFlagsNoClear搭配使用
         * 等待函数还有个超时参数，此参数有个特殊宏定义：osWaitForever，即等到条件满足为止，否则一直等待
         * 等待函数的返回值有几个错误码：osFlagsErrorUnknown、osFlagsErrorTimeout、osFlagsErrorResource、osFlagsErrorParameter
         * 如果返回的是这几个值就需要对这些错误做处理
        */
        
        /* 1. 有超时的等待，等待任意位满足条件，且事后清除标志 */
        last_flag = osThreadFlagsWait(1<<1, osFlagsWaitAny, 100);
        cur_flag = osThreadFlagsGet();
        if(last_flag<osFlagsErrorParameter)
        {
            /* 如果等到了标志，那么该标志会被清除掉 */
            printf(">>osFlagsWaitAny<< for flag \"0x%x\" >>100ms<< OK\r\n", (1<<1));
            printf("Last Flag: 0x%x\tCurrent Flag: 0x%x\r\n", last_flag, cur_flag);
        }
        else
        {
            /* 如果没有等到标志，则不会有清除动作 */
            last_flag = osThreadFlagsClear(cur_flag);
            printf(">>osFlagsWaitAny<< for flag \"0x%x\" >>100ms<< Error, Current Flag: 0x%x\r\n", (1<<1), cur_flag);
        }
        
        /* 2. 一直等待，等到任意位满足标志为止，且事后清除标志 */
        last_flag = osThreadFlagsWait(1<<2, osFlagsWaitAny, osWaitForever);
        cur_flag = osThreadFlagsGet();
        if(last_flag<osFlagsErrorParameter)
        {
            printf(">>osFlagsWaitAny<< for flag \"0x%x\" >>osWaitForever<< OK\r\n", (1<<2));
            printf("Last Flag: 0x%x\tCurrent Flag: 0x%x\r\n", last_flag, cur_flag);
        }
        else
        {
            last_flag = osThreadFlagsClear(cur_flag);
            printf(">>osFlagsWaitAny<< for flag \"0x%x\" >>osWaitForever<< Error, Current Flag: 0x%x\r\n", (1<<2), cur_flag);
        }
        
        /* 3. 一直等待，等到任意位满足标志为止，且事后不清除标志 */
        last_flag = osThreadFlagsWait(1<<3, osFlagsWaitAny | osFlagsNoClear, osWaitForever);
        cur_flag = osThreadFlagsGet();
        if(last_flag<osFlagsErrorParameter)
        {
            /* 如果等到了标志，在这种操作字的情况下，该标志不会被清除掉 */
            printf(">>osFlagsWaitAny & osFlagsNoClear<< for flag \"0x%x\" >>osWaitForever<< OK\r\n", (1<<3));
            printf("Last Flag: 0x%x\tCurrent Flag: 0x%x\r\n", last_flag, cur_flag);
        }
        else
        {
            last_flag = osThreadFlagsClear(cur_flag);
            printf(">>osFlagsWaitAny & osFlagsNoClear<< for flag \"0x%x\" >>osWaitForever<< Error, Current Flag: 0x%x\r\n", (1<<3), cur_flag);
        }
        
        /* 4. 有时间限制的等待，等待整个标志指定位满足标志，且事后清除标志 */
        last_flag = osThreadFlagsWait(1<<4, osFlagsWaitAll, 100);
        cur_flag = osThreadFlagsGet();
        if(last_flag<osFlagsErrorParameter)
        {
            printf(">>osFlagsWaitAll<< for flag \"0x%x\" >>100ms<< OK\r\n", (1<<4));
            printf("Last Flag: 0x%x\tCurrent Flag: 0x%x\r\n", last_flag, cur_flag);
        }
        else
        {
            last_flag = osThreadFlagsClear(cur_flag);
            printf(">>osFlagsWaitAll<< for flag \"0x%x\" >>100ms<< Error, Current Flag: 0x%x\r\n", (1<<4), cur_flag);
        }
        
        /* 5. 一直等待，等待整个标志指定位满足标志为止，且事后清除标志 */
        last_flag = osThreadFlagsWait(1<<5, osFlagsWaitAll, osWaitForever);
        cur_flag = osThreadFlagsGet();
        if(last_flag<osFlagsErrorParameter)
        {
            printf(">>osFlagsWaitAll<< for flag \"0x%x\" >>osWaitForever<< OK\r\n", (1<<5));
            printf("Last Flag: 0x%x\tCurrent Flag: 0x%x\r\n", last_flag, cur_flag);
        }
        else
        {
            last_flag = osThreadFlagsClear(cur_flag);
            printf(">>osFlagsWaitAll<< for flag \"0x%x\" >>osWaitForever<< Error, Current Flag: 0x%x\r\n", (1<<5), cur_flag);
        }
        
        /* 6. 一直等待，等待整个标志指定位满足标志为止，且事后不清除标志 */
        last_flag = osThreadFlagsWait(1<<6, osFlagsWaitAll | osFlagsNoClear, osWaitForever);
        cur_flag = osThreadFlagsGet();
        if(last_flag<osFlagsErrorParameter)
        {
            printf(">>osFlagsWaitAll & osFlagsNoClear<< for flag \"0x%x\" >>osWaitForever<< OK\r\n", (1<<6));
            printf("Last Flag: 0x%x\tCurrent Flag: 0x%x\r\n", last_flag, cur_flag);
        }
        else
        {
            last_flag = osThreadFlagsClear(cur_flag);
            printf(">>osFlagsWaitAll & osFlagsNoClear<< for flag \"0x%x\" >>osWaitForever<< Error, Current Flag: 0x%x\r\n", (1<<6), cur_flag);
        }
        
        /* 7. 手动清除所有标志 */
        last_flag = osThreadFlagsClear(last_flag);
        cur_flag = osThreadFlagsGet();
        printf(">>osThreadFlagsClear<< flag \"0x%x\" OK\r\n", last_flag);
        printf("Last Flag: 0x%x\tCurrent Flag: 0x%x\r\n", last_flag, cur_flag);
        
        osThreadExit();
    }
}
```

* 测试结果

| ![](02_CMSIS接口应用示例\33_wait_clear_thread_flag.png) |
| :-----------------------------------------------------: |

## 2.4 事件标志函数

### 2.4.1 事件标志的新建、获取名称和删除

* 例程：`04_0_osEventFlagsNew_GetName_Delete`
* 接口原型

```c
osEventFlagsId_t osEventFlagsNew (const osEventFlagsAttr_t *attr);
osStatus_t osEventFlagsDelete (osEventFlagsId_t ef_id);
const char * osEventFlagsGetName(osEventFlagsId_t ef_id);//FreeRTOS未实现
```

* 接口解析

  函数`osEventFlagsNew`是新建一个事件标志，其参数是指定事件的属性，可以缺省写作NULL，也可以根据需求设置属性，其属性的成员：

```c
typedef struct {
  const char                   *name;   ///< name of the event flags
  uint32_t                 attr_bits;   ///< attribute bits
  void                      *cb_mem;    ///< memory for control block
  uint32_t                   cb_size;   ///< size of provided memory for control block
} osEventFlagsAttr_t;
```

可以看到和线程的属性很相似，确实差不多，它们的含义是一样的，这里就不多说了，这个函数返回的是事件的ID，其实就是一个分配给事件的地址。

​	函数`osEventFlagsDelete`的功能是删除一个指定id的事件，如果这个id对应的事件不存在，则会返回一个错误值；

​	函数`osEventFlagsGetName`的功能是获取一个指定id事件的名称，对于FreeRTOS内核，CMSIS是没有实现封装的。

* 例程代码

  例程很简单，就是完成一个事件的新建并且在线程运行5s后删除这个事件。

```c
/* 事件标志ID */
osEventFlagsId_t evt_id;

static void thread1(void *argument)
{
    osStatus status;
    uint32_t count = 0;
    const char *evt_name;
    osEventFlagsAttr_t evt_attr = {
        .name = "Event 1",  /* 设置事件的名称 */
    };

    evt_id = osEventFlagsNew(&evt_attr);
    
    /* 获取事件的名称，对于FreeRTOS内核没有实现 */
//    evt_name = osEventFlagsGetName(evt_id);
//    printf("Event Name: %s\r\n", evt_name);
    
    for(;;)
    {
        printf("%d\r\n", 5-count);
        if(count==5)
        {
            status = osEventFlagsDelete(evt_id);
            if(status == osOK)
            {
                printf("Event 0x%x is deleted.\r\n", (uint32_t)evt_id);
                osThreadExit();
            }
            else
            {
                printf("Delete Event 0x%x Error.\r\n", (uint32_t)evt_id);
                count = 0;
            }
        }
        count++;
        osDelay(1000);
    }
}
```

* 测试结果

| ![](02_CMSIS接口应用示例\34_evt_new_delete.png) |
| :---------------------------------------------: |

### 2.4.2 事件标志的设置、获取和清除

* 例程：`04_1_osEventFlagsSet_Get_Clear`
* 接口原型

```c
uint32_t osEventFlagsSet (osEventFlagsId_t ef_id, 
                          uint32_t flags);
uint32_t osEventFlagsClear (osEventFlagsId_t ef_id, 
                            uint32_t flags);
uint32_t osEventFlagsGet (osEventFlagsId_t ef_id);
```

* 接口解析

  事件和线程的标志其实很相似，其设置和清除都是对预期标志对应的位进行与或操作，不同的地方是线程的标志获取只能获取当前线程的标志，但是事件可以在不同的线程中获取同一个id的事件标志值。

* 例程代码

  例程是让线程1每隔1s去设置一次事件的标志，让事件标志逐位置位，循环6次之后结束；让线程2去获取事件标志，只有事件标志更新后才输出标志值。

```c
/* 事件标志ID */
osEventFlagsId_t evt_id;

/* 线程任务1的入口函数 */
static void thread1(void *argument)
{
    uint32_t count = 0;
    uint32_t cur_evt = 0, last_evt = 0;
    evt_id = osEventFlagsNew(NULL);
    
    for(;;)
    {
        printf("%d\r\n", count);
        
        last_evt = osEventFlagsGet(evt_id);
        cur_evt = osEventFlagsSet(evt_id, 1<<count);
        printf(">>> Setting Event Flag <<<\r\n");
        printf(">>> Last Event Flag: 0x%x\tCurrent Event Flag: 0x%x <<<\r\n", last_evt, cur_evt);
        if((count++) > 5)
        {
            last_evt = osEventFlagsClear(evt_id, cur_evt);
            cur_evt = osEventFlagsGet(evt_id);
            printf("@@@ Clear Event Flag @@@\r\n");
            printf("@@@ Last Event Flag: 0x%x\tCurrent Event Flag: 0x%x\r\n", last_evt, cur_evt);
            osThreadExit();
        }
        osDelay(1000);
    }
}

/* 线程任务2的入口函数 */
static void thread2(void *argument)
{
    uint32_t cur_evt = 0, last_evt = 0;
    for(;;)
    {
        cur_evt = osEventFlagsGet(evt_id);
        if(last_evt != cur_evt)
        {
            printf("$$$ Getting Event Flag $$$\r\n");
            printf("$$$ Last Event Flag: 0x%x\tCurrent Event Flag: 0x%x $$$\r\n", last_evt, cur_evt);
            last_evt = cur_evt;
        }

        osDelay(50);
    }
}
```

* 测试结果

| ![](02_CMSIS接口应用示例\35_evt_set_get_clear.png) |
| :------------------------------------------------: |

### 2.4.3 事件标志的等待

* 例程：`04_2_osEventFlagsWait`
* 接口原型

```c
uint32_t osEventFlagsWait (osEventFlagsId_t ef_id, 
                           uint32_t flags, 
                           uint32_t options, 
                           uint32_t timeout);
```

* 接口解析

  事件标志的等待和线程标志的等待也是十分相似的，其等待的标志在操作字下的结果和线程标志的等待是完全一样的流程，不同的地方还是第一个参数id值，一个线程可以获取多个不同id的事件标志值。

* 例程代码

  例程还是让线程1去设置事件的标志，设置5次；线程2等待一个标志。

```c
/* 事件标志ID */
osEventFlagsId_t evt_id;

/* 线程任务1的入口函数 */
static void thread1(void *argument)
{
    uint32_t count = 0;
    uint32_t evt_flag = 0;
    evt_id = osEventFlagsNew(NULL);
    
    for(;;)
    {
        printf("%d\r\n", count);
        
        evt_flag = osEventFlagsSet(evt_id, 1<<count);
        printf(">>> Setting Event Flag: 0x%x\r\n", evt_flag);
        if(count > 5)
        {
            osThreadExit();
        }
        else
        {
            count++;
        }
        osDelay(1000);
    }
}

/* 线程任务2的入口函数 */
static void thread2(void *argument)
{
    uint32_t last_flag = 0;
    for(;;)
    {
        last_flag = osEventFlagsWait(evt_id, (1<<4), osFlagsWaitAny, osWaitForever);
        if(last_flag > osFlagsError && last_flag < osFlagsErrorUnknown)
        {
            printf("$$$ Last Event Flag: 0x%x\r\n", last_flag);
            printf("$$$ Wait for Event Flag: 0x%x Error\r\n", (1<<4));
        }
        else
        {
            printf("$$$ Last Event Flag: 0x%x\r\n", last_flag);
            printf("$$$ Wait for Event Flag: 0x%x OK\r\n", (1<<4));
            osThreadExit();
        }
        osDelay(1);
    }
}
```

* 测试结果

| ![](02_CMSIS接口应用示例\36_evt_wait.png) |
| :---------------------------------------: |



## 2.5 通用延时函数

* 例程：`05_0_generic_wait_api`
* 接口原型

```c
osStatus_t osDelay (uint32_t ticks);
osStatus_t osDelayUntil (uint32_t ticks);
```

* 接口解析

  函数`osDelay`的功能是从调用的那个时刻t起延时相对时间ticks个单位，不管我调用此函数前做了多久时间的工作，反正我要等待ticks个单位的时间之后才能去做后面的事情；

  函数`osDelayUntil`的功能是延时绝对时间，也就是延时到一个确切的时间点，所以它的参数ticks不是一段相对时间单位，而是一个时间点。比如我从早上9点开始工作，要工作到中午12点才能去吃饭，我可能只花了1个小时就将工作做好了，也就是在早上10点我就没事干了，但是我还是需要等到中午12点才能去吃饭，而不能提前去吃饭；但是第二天上午的事情有一点多，我干到11点50才做好上午的工作，那我还是要等10分钟的时间才能去吃饭；第三天，来大活了，干到12点都还没有干完，但是任务紧急没办法只能埋头苦干，等终于将事情做完了，一看时间，早就过了12点了，那还等什么，不等了直接去吃饭了。这个例子就说明了`osDelayUntil`的两种状态。

* 例程代码

  本次的实验用的是MDK的模拟器，因为使用模拟器比较好观察现象。我们在线程1中让某个值固定周期的0和1翻转，在线程2中做一个随机个数的赋值操作，然后延时等待到一个绝对时间。

```c
#include <stdlib.h>

/* 测试变量 */
static volatile uint8_t val_1 = 0;
static volatile uint8_t val_2 = 0;

/* 线程任务1的入口函数 */
static void thread1(void *argument)
{
    for(;;)
    {
        val_1 = !val_1;
        osDelay(500);
    }
}

/* 线程任务2的入口函数 */
static void thread2(void *argument)
{
    uint16_t i = 0;
    uint16_t tmp_buf[128] = {0};
    uint32_t tick = osKernelGetTickCount();
    for(;;)
    {
        tick = osKernelGetTickCount();
        val_2 = 1;
        for(i=0; i<(rand()%128); i++)
        {
            tmp_buf[i] = i;
            osDelay(2);
        }
        val_2 = 0;
        osDelayUntil(tick + 500);
    }
}
```

* 测试结果

| ![](02_CMSIS接口应用示例\37_generic_delay_result.png) |
| :---------------------------------------------------: |

​	可以看到`val_1`的变化是周期性的，它的每次延时都是针对某个时刻相对延时了固定时间；而`val_2`的变化则不同，为1的持续时间表示工作的时长，因为每次做的都是随机个数的赋值和延时，所以为1的时长就不一样，但是尽管如此，我从这一时刻开始工作，到下一时刻重新开始工作的周期是一致的，因为在程序中记录了每次开始工作时的时间点，延时时间是从这个时间点开始的500个单位之后，即周期还是可以固定500个单位。

​	`osDelayUntil`比较适合那种需要固定周期处理数据但是数据长度不定的场景。

## 2.6 软件定时器管理函数

* 例程：`06_0_timer_manage_api`
* 接口原型

```c
osTimerId_t osTimerNew (osTimerFunc_t func, 	// 函数指针，指向定时器的回调函数
                        osTimerType_t type, 	// 软件定时器类型，支持osTimerOnce和osTimerPeriodic
                        void *argument, 		// 传参
                        const osTimerAttr_t *attr);	// 定时器的属性
const char *osTimerGetName (osTimerId_t timer_id);	// 获取定时器的名称
osStatus_t osTimerStart (osTimerId_t timer_id, uint32_t ticks);	// 启动定时器，周期是ticks，默认情况下单位是ms
osStatus_t osTimerStop (osTimerId_t timer_id);	// 停止定时器
uint32_t osTimerIsRunning (osTimerId_t timer_id);	// 获取定时器的状态：0-停止；1-正在运行
osStatus_t osTimerDelete (osTimerId_t timer_id);	// 删除定时器
```

* 接口解析

​	函数`osTimerNew`指定某个软件定时器的处理函数或者叫回调函数、定时器的类型、参数和属性。回调函数由用户自定义，其格式参照参数类型`osTimerFunc_t`：

```c
typedef void (*osTimerFunc_t) (void *argument);
```

所以我们可以将一个软件定时器的回调函数写成例程中的那个样子。第二个参数是定时器的类型，它是这样定义的：

```c
typedef enum {
  osTimerOnce               = 0,          ///< One-shot timer.
  osTimerPeriodic           = 1           ///< Repeating timer.
} osTimerType_t;
```

支持两种定时器：一次性的和周期性的，顾名思义，一次性的意思就是定时器在经过设置的计数时间后进入回调函数，处理任务，退出之后该定时器就停止运行了；而周期性的定时器则是在经过设置的计数时间进入回调函数处理任务再退出之后，计数会归位重新计数，重新进入回调函数处理任务。第三个参数是传给回调函数的参数；第四个参数是设置定时器的属性，其定义如下：

```c
typedef struct {
  const char                   *name;   ///< name of the timer
  uint32_t                 attr_bits;   ///< attribute bits
  void                      *cb_mem;    ///< memory for control block
  uint32_t                   cb_size;   ///< size of provided memory for control block
} osTimerAttr_t;
```

有了前面的经验，这里就不多做解释了。

* 例程代码

  例程中创建了两个定时器，一个一次性的定时器Timer1，计数时间是333个ms，在线程1中开启；一个周期性的定时器Timer2，周期是777ms，在线程2中开启。每进入一次Timer1的回调函数，全局变量exec1自增1，自增到5次的时候删除Timer1；每进入一次Timer2的回调函数，全局变量exec2会自增1，自增到3的时候终止线程1，那么这个时刻Timer1就最多再会进入回调函数1次就再也进不去了；自增到5的时候终止线程2；自增到8的时候停止Timer2的运行，而此刻没有线程去开启Timer2，所以Timer2也再也不会进入回调函数，让exec2自增了，所以程序最后永远也执行不到`case 10`那里。

```c
/* 测试变量 */
static volatile uint32_t exec1 = 0;
static volatile uint32_t exec2 = 0;

/* 软件定时器的ID */
osTimerId_t timer1_id;
osTimerId_t timer2_id;

/* 软件定时器的属性初始化 */
osTimerAttr_t timer1_attr = {
    .name = "Timer1"    // 设置软件定时器1的名称
};
osTimerAttr_t timer2_attr = {
    .name = "Timer2"    // 设置软件定时器2的名称
};

/* 软件定时器的回调函数 */
static void Timer1_CallBack(void *arg);
static void Timer2_CallBack(void *arg);

/* 对外的任务初始化函数接口 */
void api_osThreadNew_init(void)
{
    /* 新建线程 */
    thread1_id = osThreadNew(thread1, NULL, &thread1_attr);
    thread2_id = osThreadNew(thread2, NULL, &thread2_attr);
    
    /* 新建定时器 */
    // Create one-shoot timer
    timer1_id = osTimerNew(Timer1_CallBack, osTimerOnce, (uint32_t*)&exec1, &timer1_attr);
    if(timer1_id != NULL)
    {
        printf("One-shot timer created\r\n");
    }
    
    // Create periodic timer
    timer2_id = osTimerNew(Timer2_CallBack, osTimerPeriodic, (uint32_t*)&exec2, &timer2_attr);
    if(timer2_id != NULL)
    {
        printf("Periodic timer created\r\n");
    }
}

/* 线程任务1的入口函数 */
static void thread1(void *argument)
{
    const char *name = NULL;
    if(timer1_id != NULL)
    {
        name = osTimerGetName(timer1_id);
    }
    else
    {
        printf("Timer -1- is inexistent.\r\n");
        osThreadExit();
    }
    
    for(;;)
    {
        if(osTimerIsRunning(timer1_id) == 0)
        {
            printf("Start Timer -1-\r\n");
            osTimerStart(timer1_id, 333);
        }
        osDelay(50);
    }
}

/* 线程任务2的入口函数 */
static void thread2(void *argument)
{
    const char *name = NULL;
    if(timer2_id != NULL)
    {
        name = osTimerGetName(timer2_id);
        
        printf("Start Timer >2<\r\n");
        osTimerStart(timer2_id, 777);
    }
    else
    {
        printf("Timer >2< is inexistent.\r\n");
        osThreadExit();
    }
    
    for(;;)
    {
        osDelay(50);
    }
}

/* 软件定时器1的回调函数 */
static void Timer1_CallBack(void *arg)
{
    exec1++;
    printf("Timer -1- \tTest Paragram: %d\r\n", exec1);
    if(exec1==5)
    {
        printf("Delete Timer -1-\r\n");
        osTimerDelete(timer1_id);
    }
}

/* 软件定时器2的回调函数 */
static void Timer2_CallBack(void *arg)
{
    exec2++;
    printf("Timer >2< \tTest Paragram: %d\r\n", exec2);
    switch(exec2)
    {
        case 3:
        {
            printf("Terminate Thread *1*\r\n");
            osThreadTerminate(thread1_id);
            break;
        }
        case 5:
        {
            printf("Terminate Thread *2*\r\n");
            osThreadTerminate(thread2_id);
            break;
        }
        case 8:
        {
            if(osTimerIsRunning(timer2_id) == 1)
            {
                printf("Stop Timer >2<\r\n");
                osTimerStop(timer2_id);
            }
            break;
        }
        case 10:
        {
            printf("Timer >2< can not reach here!\r\n");
            break;
        }
        default:break;
    }
}
```

* 测试结果

| ![](02_CMSIS接口应用示例\38_timer_result.png) |
| :-------------------------------------------: |

* Tips

  我们还利用软件定时器做了一个实际的例子：处理按键。大家可以下载例程`23_timer_get_key`观察现象。

## 2.7 互斥量管理函数

* 例程：`07_0_mutex_manage_api`
* 接口原型

```c
osMutexId_t osMutexNew (const osMutexAttr_t *attr);	// 新建一个互斥量
osStatus_t osMutexAcquire (osMutexId_t mutex_id, uint32_t timeout);	// 获取某个互斥量的访问权限，允许的话返回osOK
osStatus_t osMutexRelease (osMutexId_t mutex_id);	// 释放某个互斥量；
osThreadId_t osMutexGetOwner (osMutexId_t mutex_id);	// 获知某个互斥量现在在哪个线程被访问
osStatus_t osMutexDelete (osMutexId_t mutex_id);	// 删除某个互斥量
```

* 接口解析

  函数`osMutexNew`是新建一个互斥量，其属性可以设置为NULL，也可以根据需求设计，其定义如下：

```c
typedef struct {
  const char                   *name;   ///< name of the mutex
  uint32_t                 attr_bits;   ///< attribute bits
  void                      *cb_mem;    ///< memory for control block
  uint32_t                   cb_size;   ///< size of provided memory for control block
} osMutexAttr_t;
```

​	函数`osMutexAcquire`是获取指定id互斥量的访问权限，由等待时间，范围0~osWaitForever，如果获取了权限则会返回osOK；

​	函数`osMutexRelease`是释放某个互斥量的访问权限，让其他地方可以获取权限，释放成功则会返回osOK;

​	函数`osMutexGetOwner`是获取正在访问某个互斥量的线程的id；

​	函数`osMutexDelete`是删除某个互斥量，使其再也无法被访问；

* 例程代码

  ce是代码让线程1和线程2都去获取同一个互斥量的访问权限，然后对一个全局变量做自增。线程1是一直请求权限，如果获取了权限，则对全局变量自增之后释放权限；线程2则是有限时的请求权限，获取权限之后对全局变量自增，然后删除此互斥量；最终全局变量的值经过两次自增之后变成2。

```c
/* 测试变量 */
static int g_num = 0;

/* 线程ID */
static osThreadId_t id1;
static osThreadId_t id2;

/* 互斥量ID */
static osMutexId_t mutex_id;  
 
/* 互斥量的属性 */
static const osMutexAttr_t Thread_Mutex_attr = {
  "myThreadMutex",                          // human readable mutex name
  osMutexRecursive | osMutexPrioInherit,    // attr_bits
  NULL,                                     // memory for control block   
  0U                                        // size for control block
};

/* 线程的属性 */
static const osThreadAttr_t attr1 = {
    .priority = osPriorityLow1,
};

static const osThreadAttr_t attr2 = {
    .priority = osPriorityLow1,
};

/* 线程1的入口函数 */
static void Thread1(void *arg)
{
    osThreadId_t id;
    osStatus sta;
    
    for(;;)
    {
        sta = osMutexAcquire(mutex_id, osWaitForever);
        if(sta == osOK)
        {
            printf("Thread >1< obtained mutex\r\n");
            g_num++;
            printf("Thread >1< get global varibale is %d\r\n", g_num);
            sta = osMutexRelease(mutex_id);
            if(sta == osOK)
            {
                osThreadExit();
            }
        }
        osDelay(10);
    }
}

/* 线程2的入口函数 */
static void Thread2(void *arg)
{
    osThreadId_t id;
    osStatus sta;
    for(;;)
    {
        sta = osMutexAcquire(mutex_id, 100);
        if(sta == osOK)
        {
            printf("Thread >2< obtained mutex\r\n");
            g_num++;
            printf("Thread >2< get global varibale is %d\r\n", g_num);
            
            sta = osMutexDelete(mutex_id);
            if(sta ==osOK)
            {
                printf("Thread >2< delete the mutex.\r\n");
                osThreadExit();
            }
        }
        osDelay(100);
    }    
}

/* 对外的任务初始化函数接口 */
void api_osThreadNew_init(void)
{
    /* 新建线程1 */
    id1 = osThreadNew(Thread1, NULL, &attr1);
    if(id1 != NULL)
    {
        printf("Thread1 created\r\n");
    }
    
    /* 新建线程2 */
    id2 = osThreadNew(Thread2, NULL, &attr2);
    if(id2 != NULL)
    {
        printf("Thread2 created\r\n");
    }
    
    /* 新建互斥量 */
    mutex_id = osMutexNew(&Thread_Mutex_attr);
    if (mutex_id != NULL)  
    {
        printf("Mutex object created\r\n");
    }
}
```

* 测试结果

| <img src="02_CMSIS接口应用示例\39_mutex_result.png" style="zoom:60%;" /> |
| :----------------------------------------------------------: |

## 2.8 信号量

### 2.8.1 二进制信号

* 例程：`08_1_semaphore_binary`
* 接口原型

```c
osSemaphoreId_t osSemaphoreNew (uint32_t max_count, 	// 信号的最大计数值
                                uint32_t initial_count, // 信号的初始计数值
                                const osSemaphoreAttr_t *attr);	// 信号的属性
osStatus_t osSemaphoreAcquire (osSemaphoreId_t semaphore_id, uint32_t timeout);	// 获取一个信号
osStatus_t osSemaphoreRelease (osSemaphoreId_t semaphore_id);	// 释放一个信号
```

* 接口解析

  函数`osSemaphoreNew`是新建一个信号量，设置其最大计数值和初始计数值，属性可以设置NULL也可以根据需求设置，属性的定义是：

```c
typedef struct {
  const char                   *name;   ///< name of the mutex
  uint32_t                 attr_bits;   ///< attribute bits
  void                      *cb_mem;    ///< memory for control block
  uint32_t                   cb_size;   ///< size of provided memory for control block
} osMutexAttr_t;
```

使用此函数新建的信号量只能从初始计数值到最大计数值之间增大或减小，在此范围内，请求一次信号量会使信号量的计数值自减1，释放一次信号量则会使计数值自增1。比如本小节用到的二进制信号，则是让最大计数值为1，使其在0和1之间变化。

​	函数`osSemaphoreAcquire`请求获取某个信号，如果成功获取到则会使信号计数值减1，且返回osOK;

​	函数`osSemaphoreRelease`释放某个信号，如果成功释放则会使信号计数值增1，且返回osOK;

* 例程代码

  例程让线程`deal_semaphore_thread`去有限时的请求获取信号，获取到了则调用一个数据输出函数；让线程`produce_semaphore_thread`先做一个随即个数的数据处理然后释放信号；由于我们将该信号的计数值范围设置为0~1成为了一个二进制信号，只有在释放一次过后，别的线程才能获取到这个信号；所以尽管这两个线程的优先级我们在程序中都设置为了同一等级，执行顺序是`produce_semaphore_thread`——>`deal_semaphore_thread`，

```c
/* 测试变量 */
#define TEST_SIZE   (16)
static uint16_t test_buf[TEST_SIZE];

/* 信号id */
static osSemaphoreId_t sid;  

/* 线程id */
static osThreadId_t produce_tid, deal_tid;

/* 测试用的数据处理函数 */
static void deal_data(void)
{
    uint16_t i = rand()%TEST_SIZE;
    memset((uint8_t*)&test_buf[0], 0, sizeof(test_buf));
    
    while(i--)
    {
        test_buf[i] = rand() & 0xAB;
    }
}

/* 测试用的数据显示函数 */
static void print_data(void)
{
    uint16_t i = 0;
    printf(">>>Buffer:\t");
    for(i=0; i<TEST_SIZE; i++)
    {
        printf("%d\t", test_buf[i]);                    
    }
    printf("\r\n");  
}

/* 接收信号的线程 */
static void deal_semaphore_thread(void *arg)
{
    osStatus sta;
    for(;;)
    {
        sta = osSemaphoreAcquire(sid, 10);
        if(sta==osOK)
        {
            printf("Get the Data.\r\n");
            print_data();
        }
        
        osThreadYield();
    }
}

/* 发出信号的线程 */
static void produce_semaphore_thread(void *arg)
{
    sid = osSemaphoreNew(1, 0, NULL);
    if(sid != NULL)
    {
        printf("A semaphore created.\r\n");
    }
    for(;;)
    {
        printf("Deal Data.\r\n");
        deal_data();
        osSemaphoreRelease(sid);
        osDelay(3000);
    }
}
```

* 测试结果

| ![](02_CMSIS接口应用示例\40_binary_semaphore_result.png) |
| :------------------------------------------------------: |

### 2.8.1 计数信号

* 例程：`08_3_semaphore_counting`
* 接口原型

```c
uint32_t osSemaphoreGetCount (osSemaphoreId_t semaphore_id);
osStatus_t osSemaphoreDelete (osSemaphoreId_t semaphore_id);
```

* 接口解析

  函数`osSemaphoreGetCount`是获取某个信号当前的计数值，它不会改变计数值；

  函数`osSemaphoreDelete`是删除某个信号；

* 例程代码

  例程中让线程`deal_semaphore_thread`去获取信号的计数值，如果计数值有更新则将更新的计数值打印出来；让线程`produce_semaphore_thread`先新建一个计数值范围是0~10的信号，然后每隔1s去释放一次信号，让信号的计数值自增，直到自增到不能继续变化后，删除这个信号且推出线程。

```c
static osSemaphoreId_t sid;   // semaphore id
static osThreadId_t produce_tid, deal_tid;

static void deal_semaphore_thread(void *arg)
{
    uint32_t last_cnt = 0, cur_cnt = 0;
    osStatus sta;
    for(;;)
    {
        cur_cnt = osSemaphoreGetCount(sid);
        if(last_cnt != cur_cnt)
        {
            printf("Get the count semaphore %d\r\n", cur_cnt);
            last_cnt = cur_cnt;
        }
        osThreadYield();
    }
}
static void produce_semaphore_thread(void *arg)
{
    osStatus sta;
    sid = osSemaphoreNew(10, 0, NULL);
    if(sid != NULL)
    {
        printf("A semaphore created.\r\n");
    }
    for(;;)
    {
        sta = osSemaphoreRelease(sid);
        if(sta != osOK)
        {
            printf("The Data deal finished.\r\n");
            sta = osSemaphoreDelete(sid);
            if(sta == osOK)
            {
                printf("Delete the semaphore and Exit the tread.\r\n");
                osThreadTerminate(deal_tid);
                osThreadExit();
            }
        }

        osDelay(1000);
    }
}
```

* 测试结果

| ![](02_CMSIS接口应用示例\41_count_semaphore_result.png) |
| :-----------------------------------------------------: |

## 2.9 内存池管理函数

​	对于FreeRTOS内核，CMSIS中没有这部分的代码封装。

## 2.10 消息队列管理函数

* 例程：`10_0_message_queue_api`
* 接口原型

```c
osMessageQueueId_t osMessageQueueNew (uint32_t msg_count, 
                                      uint32_t msg_size, 
                                      const osMessageQueueAttr_t *attr);
osStatus_t osMessageQueuePut (osMessageQueueId_t mq_id, 
                              const void *msg_ptr,
                              uint8_t msg_prio, 
                              uint32_t timeout);
osStatus_t osMessageQueueGet (osMessageQueueId_t mq_id, 
                              void *msg_ptr,
                              uint8_t *msg_prio, 
                              uint32_t timeout);
uint32_t osMessageQueueGetCapacity (osMessageQueueId_t mq_id);
uint32_t osMessageQueueGetMsgSize (osMessageQueueId_t mq_id);
uint32_t osMessageQueueGetCount (osMessageQueueId_t mq_id);
uint32_t osMessageQueueGetSpace (osMessageQueueId_t mq_id);
osStatus_t osMessageQueueReset (osMessageQueueId_t mq_id);
osStatus_t osMessageQueueDelete (osMessageQueueId_t mq_id);
```

* 接口解析

  函数`osMessageQueueNew`是新建一个队列，它规定了这个队列最多可以存多少个消息，每个消息最大的内存空间是多少个字节，它的属性定义如下：

```C
typedef struct {
    const char                   *name;   ///< name of the message queue
    uint32_t                 attr_bits;   ///< attribute bits
    void                      *cb_mem;    ///< memory for control block
    uint32_t                   cb_size;   ///< size of provided memory for control block
  	void                      *mq_mem;    ///< memory for data storage
  	uint32_t                   mq_size;   ///< size of provided memory for data storage
} osMessageQueueAttr_t;
```

可以不设置属性，直接设置为NULL，根据自己的设计需求来定。

​	函数`osMessageQueuePut`是往队列中写入消息，要注意的是消息的大小不能超过新建的时候规定的大小，如果只有一个队列，那么优先级、超时等都可以设置为0。

​	函数`osMessageQueueGetCapacity`是获取消息队列中可存入消息的最大个数；

​	函数`osMessageQueueGetMsgSize`是获取消息队列中每个消息占用的空间是多少字节；

​	函数`osMessageQueueGetCount`是获取消息队列中已存入的消息个数；

​	函数`osMessageQueueGetSpace`s 获取消息队列中还剩多少个可以写入新的消息即还剩多少个消息是空的可以被写入的；

​	函数`osMessageQueueReset`是将某个消息队列复位，即将里面所有已存入的消息清除掉，使队列可以被从头开始写；

​	函数`osMessageQueueDelete`是删除某个消息队列；

* 例程代码

  例程中使用了一个结构体来表明设计中可能会用到的比较复杂的数据类型，让消息队列的每个消息的内存空间就是这个结构体的大小，以保证每次写入一帧这个结构体这样的数据不会超出消息队列的规定范围；

  其实例程中有3个线程：check、put和get；

  check是检查消息队列的各个参数，比如最大个数、消息大小、剩余个数等；

  put线程则是往消息队列中写入一个id规律变化，数据值随机变化的结构体变量，如果写满了则获取已存入的消息个数和剩余可写的消息个数，并且暂停本线程；

  get线程则是从消息队列中依次将消息读取出来并打印出来，如果无法再继续读取则取已存入的消息个数和剩余可写的消息个数，并且暂停本线程；

  check线程由于每次调度周期较长，而put、get线程调度周期短，所以当check周期走到复位和删除队列的时候，put和get线程早已完成了数据交互。

```c
#define MSGQUEUE_OBJECTS    (4)
typedef struct{
    uint16_t id;
    uint16_t data;
}FRAME_DATA, *pFRAME_DATA;

static osMessageQueueId_t mq_id;

mq_id = osMessageQueueNew(MSGQUEUE_OBJECTS, sizeof(FRAME_DATA), NULL);

ret = osMessageQueueGetCapacity(mq_id);
if(ret != 0)
{
    printf("The maximum number of messages in the message queue object is %d\r\n", ret);
}

ret = osMessageQueueGetMsgSize(mq_id);
if(ret != 0)
{
    printf("The maximum message size in bytes for the message queue object is %d\r\n", ret);
}

osMessageQueueReset(mq_id);
osMessageQueueDelete(mq_id);

static void PutQueue_Thread(void *arg)
{
    uint32_t ret = 0;
    FRAME_DATA frame;
    osStatus sta;
    
    for(;;)
    {
        frame.data = rand()%0xFF;
        frame.id = rand()%0xFF;
        sta = osMessageQueuePut(mq_id, &frame, 0, 0);
        if(sta == osOK)
        {
            printf(">>> Put ID:0x%x\tData: %d\r\n", frame.id, frame.data);
        }
        else
        {
            ret = osMessageQueueGetCount(mq_id);
            printf("Put Error. %d count<<<\r\n", ret);
            
            ret = osMessageQueueGetSpace(mq_id);
            printf("Put Error. %d spcae<<<\r\n", ret);
            
            printf("Suspend Put Data Thread\r\n");
            osThreadSuspend(put_queue_tid);
        }
        osThreadYield();
    }
}

static void GetQueue_Thread(void *arg)
{
    uint16_t i = 0;
    FRAME_DATA frame;
    osStatus sta;
    uint32_t ret = 0;
    
    for(;;)
    {
        sta = osMessageQueueGet(mq_id, &frame, NULL, 0);
        if(sta == osOK)
        {
            printf("<<< Get ID: 0x%x\tData: %d\r\n", frame.id, frame.data);
        }
        else
        {
            ret = osMessageQueueGetCount(mq_id);
            printf("Get Error. %d count !!!\r\n", ret);
            
            ret = osMessageQueueGetSpace(mq_id);
            printf("Get Error. %d spcae !!!\r\n", ret);
            
            printf("Suspend Get Data Thread\r\n");
            osThreadSuspend(get_queue_tid);
        }
        osThreadYield();
    }
}
```

* 测试结果

| <img src="02_CMSIS接口应用示例\42_msg_queue_result.png" style="zoom:67%;" /> |
| :----------------------------------------------------------: |

