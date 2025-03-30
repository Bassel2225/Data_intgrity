#include <stdio.h>
#include <string>

#define READ 0x4
#define WRITE 0x2
#define EXEC 0x1


typedef struct{
	int uid;
	int perms;
}userEntry;

typedef struct{
	int gid;
	int perms;
}groupEntry;


