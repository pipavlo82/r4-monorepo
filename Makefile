CC      := gcc
CFLAGS  := -O2 -Wall -Wextra -std=c11
INCLUDES:= -Ipackages/core/examples_vrf/src -Ipackages/core/examples_vrf/src/ref
LDFLAGS := 

SRC_DIR := packages/core/examples_vrf/src
BIN_DIR := bin

# minimal smoke client for CI
SRCS    := $(SRC_DIR)/r4cat_light.c
OBJS    := $(SRCS:.c=.o)

TARGET  := $(BIN_DIR)/r4cat

.PHONY: all clean dirs

all: dirs $(TARGET)

dirs:
	mkdir -p $(BIN_DIR)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) $(INCLUDES) -o $@ $(OBJS) $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

clean:
	rm -rf $(OBJS) $(TARGET)
