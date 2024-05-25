/**
 * gcc -O2 jp2_ranged_reader.c -o jp2_ranged_reader && ([ -e astronaut.jp2 ] || python glymur-create.py) && ./jp2_ranged_reader astronaut.jp2
 */


#include <stdio.h>


int die(int ret_val, char* msg) {
  printf("%s\n", msg);
  return ret_val;
}

int main(int argc, char** argv) {
  if (argc < 2) {
    return die(1, "Missing a filename.jp2!");
  }

  char* file = argv[1];
  printf("Reading %s\n", file);


  return 0;
}
