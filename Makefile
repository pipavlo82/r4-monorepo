CC=gcc
CFLAGS=-O3 -march=native -std=c11 -Wall -Wextra
INCLUDES=-Iinclude
LDLIBS=-lcrypto

all: bin/r4cat lib/libr4.a

bin/r4cat: src/r4cat.c src/r4_client.c include/r4.h
	@mkdir -p bin lib
	$(CC) $(CFLAGS) $(INCLUDES) -o $@ src/r4cat.c src/r4_client.c $(LDLIBS)

lib/libr4.a: src/r4_client.c include/r4.h
	@mkdir -p lib
	$(CC) $(CFLAGS) $(INCLUDES) -c src/r4_client.c -o lib/r4_client.o
	ar rcs $@ lib/r4_client.o

clean:
	rm -rf bin lib
