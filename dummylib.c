#include <stdio.h>

int function1(int x, int y)
{
	int result = x + y;
	printf("%s : function1(%d, %d) = %d\n", __FUNCTION__, x, y, result);
	return result;
}

int function2(int a, int b)
{
	int result = (((a & b)<<3) | ((a & ~b) >> 4));
	printf("%s : function2(%d, %d) = %d\n", __FUNCTION__, a, b, result);
	return result;
}

int function3(int y, int z)
{
	int result = 108 * (y * z) + 3;
	printf("%s : function3(%d, %d) = %d\n", __FUNCTION__, y, z, result);
	return result;
}
