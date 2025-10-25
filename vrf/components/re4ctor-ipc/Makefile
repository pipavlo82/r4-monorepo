CC=gcc
CFLAGS=-O3 -march=native -std=c11 -Wall -Wextra -Iinclude
LDLIBS=-lcrypto
BIN=bin/r4cat
LIB=lib/libr4.a

all: $(BIN) $(LIB)

bin/r4cat: src/r4cat.c src/r4_client.c include/r4.h
	@mkdir -p bin
	$(CC) $(CFLAGS) src/r4cat.c src/r4_client.c -o $@ $(LDLIBS)

lib/libr4.a: src/r4_client.c include/r4.h
	@mkdir -p lib
	$(CC) $(CFLAGS) -c src/r4_client.c -o lib/r4_client.o
	ar rcs $@ lib/r4_client.o

clean:
	rm -rf bin lib
