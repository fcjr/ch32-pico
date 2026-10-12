// SPDX-License-Identifier: MIT
// Copyright (c) 2026 ch32-pico contributors
#include "ch32fun.h"
#include <stdio.h>

// Print through reserved PD1/SWIO. Header GPIOs remain at their reset states.
int main(void)
{
    SystemInit();
    unsigned count = 0;
    for (;;) {
        printf("ch32-pico debug console: %u\n", count++);
        Delay_Ms(1000);
    }
}
