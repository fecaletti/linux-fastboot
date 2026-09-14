#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>

#define SPLASH_DISPLAY_SECONDS 3

int main(void) {
    /* Disable buffering so output appears immediately */
    setvbuf(stdout, NULL, _IONBF, 0);

    FILE *tty1 = fopen("/dev/tty1", "w");
    if (tty1) setvbuf(tty1, NULL, _IONBF, 0);

    /* 1. Hold the splash image visible for some seconds */
    sleep(SPLASH_DISPLAY_SECONDS);

    /* 2. Erase the splash screen and reset scroll region:
     *    \033[r  -> Reset top/bottom margins to full screen (unreserves logo space)
     *    \033[2J -> Erase entire display
     *    \033[H  -> Move cursor to row 1, column 1
     */
    const char *clear_cmd = "\033[r\033[2J\033[H";
    fputs(clear_cmd, stdout);
    fflush(stdout);
    if (tty1) {
        fputs(clear_cmd, tty1);
        fflush(tty1);
    }

    /* 3. Stream binary output from the top of the clean display */
    while (1) {
        printf("Booted!\n");
        fflush(stdout);
        if (tty1) {
            fprintf(tty1, "Booted!\n");
            fflush(tty1);
        }
        sleep(3);
    }

    if (tty1) fclose(tty1);
    return 0;
}
