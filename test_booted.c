#include <stdio.h>
#include <unistd.h>

int main(void) {
    /* Disable buffering on stdout so messages appear immediately on HDMI */
    setvbuf(stdout, NULL, _IONBF, 0);

    while (1) {
        printf("Booted!\n");
        fflush(stdout);
        sleep(3);
    }

    return 0;
}
