#include <stdio.h>
#include <stdlib.h>

#include <dummylib.h>

int main(int argc, char **argv)
{
	int a = function1(1, 2);
	int b = function2(103, 1983);
	int c = function3(1038, 1408);
	
	printf("a %d b %d c %d\n", a, b, c);

	return 0;
}
