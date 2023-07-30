#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int m = 12;
unsigned char *secret = "crepeausucre";

void usage()
{
	printf("usage !\n");
}

void dump(unsigned char *str, int len)
{
	int i;
	
	printf("\n");
	for (i = 0; i < len - 1; i++)
	{
		printf("%X:", str[i]);
	}
	printf("%X\n", str[len - 1]);
}

void encrypt(unsigned char *p, unsigned char *key, unsigned char *c, int n, int k)
{
	int i, j;
	for (i = 0; i < n; i++)
	{
		c[i] = p[i] ^ key[i % k] ^ secret[i % m];
	}
}

int main(int argc, unsigned char **argv)
{
	if (argc < 2)
	{
		usage();
		return 0;
	}

	int n = strlen(argv[1]);
	int k = strlen(argv[2]);
	
	unsigned char *crypt = malloc(n);
	encrypt(argv[1], argv[2], crypt, n, k);
	
	dump(crypt, n);

	return 0;
}
