# SPDX-License-Identifier: MIT
# Build only. Deliberately no flash target or default hardware operation.
all: main.bin
TARGET := main
TARGET_MCU := CH32V003
CH32FUN ?= ../../build/references/rv003usb/ch32fun/ch32fun
include $(CH32FUN)/ch32fun.mk
