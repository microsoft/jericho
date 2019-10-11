#include <stdio.h>
#include "frotz_interface.h"
#include "tx.h"

int main (int argc, char *argv[])
{
    // Init
    unsigned char s[8192] = "";
    dict_word_t dict[1024];
    int dict_size;
    setup("/home/matthew/workspace/text_agents/roms/zork1.z5", 0);

    for (int i=0; i<100; ++i) {
      shutdown();
      setup("/home/matthew/workspace/text_agents/roms/zork1.z5", 0);
      dict_size = get_dictionary_word_count("/home/matthew/workspace/text_agents/roms/zork1.z5");
      get_dictionary(dict, dict_size);
      ztools_cleanup();
      step("look\n");
      save_str(&s);
      step("s\n");
      restore_str(&s);
    }

    shutdown();

    /* printf("World Changed %d\n", world_changed()); */
    /* test(); */
    /* printf("%s\n", step("look\n")); */
    /* printf("World Changed %d\n", world_changed()); */
    /* test(); */
    /* printf("%s\n", step("look\n")); */
    /* printf("World Changed %d\n", world_changed()); */
    /* test(); */
    /* save("test.qzl"); */
    /* save_str(&s); */
    /* printf("\n\nAfter Save: %s\n", step("s\n")); */
    /* restore("test.qzl"); */
    /* restore_str(&s); */
    /* printf("\n\nFirst: %s\n", step("look\n")); */
    /* printf("%s\n", step("save\n")); */
}
