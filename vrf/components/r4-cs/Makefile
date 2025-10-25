CC=gcc
CFLAGS += -O3 -march=native -std=c11 -Wall -Wextra
LDLIBS=-lcrypto -lpthread

all: r4cs_cat

r4cs_cat: r4cs_cat.o r4cs.o

clean:
	rm -f *.o r4cs_cat
CPPFLAGS +=
