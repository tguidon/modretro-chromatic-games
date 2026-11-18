#include <gb/gb.h>
#include <gbdk/console.h>
#include <stdio.h>

static const char * const names[8] = {
    "UP", "DOWN", "LEFT", "RIGHT", "A", "B", "START", "SELECT"
};
static const UINT8 masks[8] = {
    J_UP, J_DOWN, J_LEFT, J_RIGHT, J_A, J_B, J_START, J_SELECT
};

void main(void) {
    UINT8 held, seen = 0, previous = 0, first = 1;
    UINT8 i, count;

    printf("       TEST");
    gotoxy(1, 2); printf("BUTTON   HELD SEEN");
    for (i = 0; i != 8; ++i) {
        gotoxy(1, i + 4); printf("%s", names[i]);
    }
    gotoxy(1, 13); printf("PRESS EVERY BUTTON");
    gotoxy(1, 17); printf("REBOOT TO RESET");

    while (1) {
        wait_vbl_done();
        held = joypad();
        seen |= held;
        if (first || held != previous) {
            first = 0;
            previous = held;
            count = 0;
            for (i = 0; i != 8; ++i) {
                gotoxy(10, i + 4);
                printf("%s", (held & masks[i]) ? "YES" : " - ");
                gotoxy(15, i + 4);
                printf("%s", (seen & masks[i]) ? "OK" : "--");
                if (seen & masks[i]) ++count;
            }
            gotoxy(1, 15); printf("%u/8 TESTED", (unsigned int)count);
            if (seen == 0xFF) {
                gotoxy(1, 16); printf("ALL BUTTONS OK!");
            }
        }
    }
}
