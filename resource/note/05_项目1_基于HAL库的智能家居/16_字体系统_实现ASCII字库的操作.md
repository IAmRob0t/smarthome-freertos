## 字体系统_实现ASCII字库的操作

本节源码：在GIT仓库中

```shell
rtos_doc_source\RTOS培训资料\
	01_项目1_基于HAL库实现智能家居\
		05_项目1_基于HAL库的智能家居\1_项目源码\10_14_font_ascii
```

### 1. 程序层次

![image-20211008171127692](pic/project1/15_font_levels.png)



### 2. 构造FontLib

编写ascii_font.c，构造一个FontLib结构体：

```c
/* 构造一个FontLib */
static FontLib g_ASCIIFontLib = {
	"ascii",
	NULL,
	ASCIIGetFontSize,
	NULL,
	ASCIIGetFontBitMap,
};
```



函数`ASCIIGetFontSize`用来获得字库点阵的宽度、高度，代码如下：

```c
/**********************************************************************
 * 函数名称： ASCIIGetFontSize
 * 功能描述： 获得ASCII字库中字符点阵的宽、高
 * 输入参数： 无
 * 输出参数： piWidth-保存宽度
 * 输出参数： piHeigh-保存高度
 * 返 回 值： 无
 * 修改日期        版本号     修改人	      修改内容
 * -----------------------------------------------
 * 2021/10/08	     V1.0	  韦东山	      创建
 ***********************************************************************/
static void ASCIIGetFontSize(int *piWidth, int *piHeigh)					/* 获取字体大小 */
{
	if (piWidth)
		*piWidth = 8;
	if (piHeigh)
		*piHeigh = 16;
}
```



核心函数是`ASCIIGetFontBitMap`：

```c
/**********************************************************************
 * 函数名称： ASCIIGetFontBitMap
 * 功能描述： 获得ASCII字库中某个字符的点阵
 * 输入参数： dwCode-哪个字符,字符的ASCII码
 * 输出参数： ptFontBitMap-用来保存字库点阵
 * 返 回 值： 0-成功, -1-失败
 * 修改日期        版本号     修改人	      修改内容
 * -----------------------------------------------
 * 2021/10/08	     V1.0	  韦东山	      创建
 ***********************************************************************/
static int ASCIIGetFontBitMap(unsigned int dwCode, PFontBitMap ptFontBitMap)  /* 获取某个字符的字库 */
{
	int iWidth = 8;
	int iHeigh = 16;
	unsigned char *dots = ascii_font[dwCode];
	if (!ptFontBitMap)
	{
		/* 调用GetFontBitMap之前要设置原点X,Y坐标
		 * 根据它可以算出左上角X,Y坐标
		 * 根据它可以算出下一个字符的原点X,Y坐标
		 */

		/* 计算左上角坐标 */
		ptFontBitMap->iLeftUpX = ptFontBitMap->iCurOriginX;
		ptFontBitMap->iLeftUpY = ptFontBitMap->iCurOriginY - iHeigh + 1;

		/* 计算下一个字符的原点坐标 */
		ptFontBitMap->iNextOriginX = ptFontBitMap->iCurOriginX + iWidth;
		ptFontBitMap->iNextOriginY = ptFontBitMap->iCurOriginY;

		/* 设置点阵宽度/高度 */
		ptFontBitMap->iWidth = iWidth;
		ptFontBitMap->iRows  = iHeigh;

		/* 如果用户没有提供自己的buffer, 直接返回字库数组里的数据 */
		if (!ptFontBitMap->pucBuffer)
			ptFontBitMap->pucBuffer = dots;
		else /* 如果用户提供了自己的buffer, 复制字库数组里的数据 */
			memcpy(ptFontBitMap->pucBuffer, dots, 16);

		return 0;
	}
	return -1;
}
```





### 3. 实现管理层

#### 3.1 font_manager.c

底层字库要向上注册FontLib，函数`FontLibRegister`代码如下：

```c
/**********************************************************************
 * 函数名称： FontLibRegister
 * 功能描述： 注册一个字库
 * 输入参数： ptFontLib-字库
 * 输出参数： 无
 * 返 回 值： 无
 * 修改日期        版本号     修改人	      修改内容
 * -----------------------------------------------
 * 2021/10/09	     V1.0	  韦东山	      创建
 ***********************************************************************/
void FontLibRegister(PFontLib ptFontLib)
{
	ptFontLib->pNext = g_ptFontLibs;
	g_ptFontLibs = ptFontLib;
}
```



所谓注册，就是把底层的FontLib放入上层的链表。

我们还可以根据名字，从链表里把FontLib取出来，函数为`__GetFontLib`：

```c
/**********************************************************************
 * 函数名称： __GetFontLib
 * 功能描述： 获得字库
 * 输入参数： name-字库的名称
 * 输出参数： 无
 * 返 回 值： 成功-PFontLib, 失败-NULL
 * 修改日期        版本号     修改人	      修改内容
 * -----------------------------------------------
 * 2021/10/09	     V1.0	  韦东山	      创建
 ***********************************************************************/
PFontLib __GetFontLib(char *name)
{
	PFontLib pTmp = g_ptFontLibs;
	while (pTmp)
	{
		if (strcmp(pTmp->name, name) == 0)
			return pTmp;
		else
			pTmp = pTmp->pNext;
	}
	return NULL;
}
```



#### 3.2 font_system.c

为了让`font_manager.c`和底层的`ascii_font.c`不相互调用，引入了`font_system.c`。

里面有2个函数：

```c
/**********************************************************************
 * 函数名称： AddFontLibs
 * 功能描述： 注册多个字库
 * 输入参数： 无
 * 输出参数： 无
 * 返 回 值： 无
 * 修改日期        版本号     修改人	      修改内容
 * -----------------------------------------------
 * 2021/10/08	     V1.0	  韦东山	      创建
 ***********************************************************************/
void AddFontLibs(void)
{
	AddFontLibASCII();
}

/**********************************************************************
 * 函数名称： GetFontLib
 * 功能描述： 获得字库
 * 输入参数： name-字库的名称
 * 输出参数： 无
 * 返 回 值： 成功-PFontLib, 失败-NULL
 * 修改日期        版本号     修改人	      修改内容
 * -----------------------------------------------
 * 2021/10/09	     V1.0	  韦东山	      创建
 ***********************************************************************/
PFontLib GetFontLib(char *name)
{
	return __GetFontLib(name);
}
```



