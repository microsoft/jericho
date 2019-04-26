#include <stdio.h>
#include "frotz_interface.h"

int main (int argc, char *argv[])
{
    // Init
    unsigned char s[8192] = "";
    setup("/home/matthew/workspace/text-agents/roms/reverb.z5", 0);
    printf("%s\n", step("look\n"));
    printf("World Changed %d\n", world_changed());
    test();
    printf("%s\n", step("look\n"));
    printf("World Changed %d\n", world_changed());
    test();
    printf("%s\n", step("look\n"));
    printf("World Changed %d\n", world_changed());
    test();
    /* save("test.qzl"); */
    /* save_str(&s); */
    /* printf("\n\nAfter Save: %s\n", step("s\n")); */
    /* restore("test.qzl"); */
    /* restore_str(&s); */
    /* printf("\n\nFirst: %s\n", step("look\n")); */
    /* printf("%s\n", step("save\n")); */
}
