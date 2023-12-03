#ifndef MD5_H
#define MD5_H

#include <stdio.h>

typedef unsigned int uint;
typedef unsigned char byte;

typedef struct MD5state
{
	uint len;
  uint state[4];
} MD5state;

MD5state *nil;

MD5state* md5(byte*, uint, byte*, MD5state*);
void sum(FILE*, char*);

#endif MD5_H