/**
 * gcc -Wall -Werror -Wno-unused-variable -O2 jp2_ranged_reader.c -o jp2_ranged_reader && ([ -e astronaut.jp2 ] || python glymur-create.py) && ./jp2_ranged_reader astronaut.jp2 768 768 512 512
 */

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/mman.h> /* mmap() is defined in this header */
#include <fcntl.h>

#define SUCCESS 0
#define FAIL(n) (n)

#define UINT32_BE(bytes, offset) (bytes[offset] << 24 | bytes[offset+1] << 16 | bytes[offset+2] << 8 | bytes[offset+3] << 0)
#define UINT16_BE(bytes, offset) (bytes[offset] << 8 | bytes[offset+1] << 0)

int die(int ret_val, char* msg) {
  printf("%s\n", msg);
  return ret_val;
}

void jumpto_tag(char* four_letter_name, size_t* tag_offset_out, uint32_t* tag_size_out, size_t jp2_offset, unsigned char* jp2_bytes, size_t file_size) {
  if (jp2_offset+8 > file_size) {
    printf("WARNING: jumpto_tag(%s, ...) fell off the file!\n", four_letter_name);
    return; // fell off the file!
  }
  // Read this tag size, big-endian
  uint32_t tag_size = UINT32_BE(jp2_bytes, jp2_offset);
  if (tag_size < 8) {
    // Generally impossible, exit!
    printf("WARNING: jumpto_tag(%s, ...) read an impossible tag_size of %d!\n", four_letter_name, tag_size);
    return;
  }
  // Read current tag name, if four_letter_name return!
  if (jp2_bytes[jp2_offset+4] == four_letter_name[0] &&
      jp2_bytes[jp2_offset+5] == four_letter_name[1] &&
      jp2_bytes[jp2_offset+6] == four_letter_name[2] &&
      jp2_bytes[jp2_offset+7] == four_letter_name[3]) {
    *tag_size_out = tag_size;
    *tag_offset_out = jp2_offset;
  }
  else {
    jumpto_tag(four_letter_name, tag_offset_out, tag_size_out, jp2_offset + tag_size, jp2_bytes, file_size);
  }
}


// output_rgb8_buff MUST be at LEAST w*h*3 bytes large to hold the decoded pixel data.
int read_pixels_from(char* jp2_file, unsigned char* output_rgb8_buff, int x0, int y0, int w, int h) {
  int file_fd = open(jp2_file, O_RDWR);
  struct stat st;
  fstat(file_fd, &st);
  size_t file_size = st.st_size;

  unsigned char* jp2_bytes = mmap(0, file_size, PROT_READ|PROT_EXEC , MAP_SHARED, file_fd, 0);
  size_t jp2_offset = 0;

  size_t ftyp_offset = 0;
  uint32_t ftyp_len = 0;
  jumpto_tag("ftyp", &ftyp_offset, &ftyp_len, jp2_offset, jp2_bytes, file_size);

  printf("ftyp_offset=%ld ftyp_len=%d\n", ftyp_offset, ftyp_len);
  // Use the offsets to ensure "jp2 " exists at ftyp_offset+8
  if (strncmp((char*) (jp2_bytes+ftyp_offset+8) , "jp2 ", 4) != 0) {
    printf("Error: %s is not a jp2 file!\n", jp2_file);
    return FAIL(1);
  }

  size_t jp2h_offset = 0;
  uint32_t jp2h_len = 0;
  jumpto_tag("jp2h", &jp2h_offset, &jp2h_len, ftyp_offset, jp2_bytes, file_size);

  printf("jp2h_offset=%ld jp2h_len=%d\n", jp2h_offset, jp2h_len);

  size_t ihdr_offset = 0;
  uint32_t ihdr_len = 0;
  jumpto_tag("ihdr", &ihdr_offset, &ihdr_len, jp2h_offset+8, jp2_bytes, file_size); // Interior box may be parsed by jumping to the known beginning! (+8 in this case)

  printf("ihdr_offset=%ld ihdr_len=%d\n", ihdr_offset, ihdr_len);

  size_t jp2_width =            UINT32_BE(jp2_bytes, ihdr_offset + 8);
  size_t jp2_height =           UINT32_BE(jp2_bytes, ihdr_offset + 12);
  uint16_t jp2_num_components = UINT16_BE(jp2_bytes, ihdr_offset + 16);
  uint8_t jp2_bits_per_component = jp2_bytes[ihdr_offset + 18];
  uint8_t jp2_compression_type =   jp2_bytes[ihdr_offset + 19];

  if (jp2_compression_type != 7) {
    printf("Error: %s does not use compression type 7! (got %d)!\n", jp2_file, jp2_compression_type);
    return FAIL(2);
  }

  uint8_t jp2_UnkC =   jp2_bytes[ihdr_offset + 20]; // ???
  uint8_t jp2_IPR =    jp2_bytes[ihdr_offset + 21];

  printf("jp2_width=%ld jp2_height=%ld jp2_num_components=%d jp2_bits_per_component=%d\n", jp2_width, jp2_height, jp2_num_components, jp2_bits_per_component);
  printf("jp2_compression_type=%d jp2_UnkC=%d jp2_IPR=%d\n", jp2_compression_type, jp2_UnkC, jp2_IPR);


  size_t colr_offset = 0;
  uint32_t colr_len = 0;
  jumpto_tag("colr", &colr_offset, &colr_len, ihdr_offset, jp2_bytes, file_size);

  printf("colr_offset=%ld colr_len=%d\n", colr_offset, colr_len);

  uint8_t jp2_meth =       jp2_bytes[colr_offset + 8];
  uint8_t jp2_precedence = jp2_bytes[colr_offset + 9];
  uint8_t jp2_approx =     jp2_bytes[colr_offset + 10];

  printf("jp2_meth=%d jp2_precedence=%d jp2_approx=%d\n", jp2_meth, jp2_precedence, jp2_approx);

  if (jp2_meth == 1) { // Enumerated color space
    uint32_t jp2_EnumCS = UINT32_BE(jp2_bytes, colr_offset + 11);
    printf("jp2_EnumCS=%d\n", jp2_EnumCS);
    /* // jp2_EnumCS is the enumerated color-space being used, with the following possible values
    CMYK = 12
    SRGB = 16
    GREYSCALE = 17
    YCC = 18
    E_SRGB = 20
    ROMM_RGB = 21
    */
    if (jp2_EnumCS == 14) { // CIELab?

    }
    else if (jp2_EnumCS == 16) { // SRGB

    }
    else {
      printf("Warning: %s has unknown jp2_EnumCS = %d (expected 14 or 16)!\n", jp2_file, jp2_EnumCS);
    }
  }
  else if (jp2_meth == 2) { // ICC Profile color space

  }
  else {
    printf("Warning: %s has unknown jp2_meth = %d (expected 1 or 2)!\n", jp2_file, jp2_meth);
  }

  size_t jp2c_offset = 0;
  uint32_t jp2c_len = 0;
  jumpto_tag("jp2c", &jp2c_offset, &jp2c_len, jp2h_offset, jp2_bytes, file_size);

  printf("jp2c_offset=%ld jp2c_len=%d\n", jp2c_offset, jp2c_len);




  return SUCCESS;
}


int main(int argc, char** argv) {
  if (argc < 2) {
    return die(1, "Missing a filename.jp2!");
  }
  char* jp2_file = argv[1];

  int x0 = 768;
  int y0 = 768;
  int w = 512;
  int h = 512;
  if (argc < 6) {
    printf("WARNING: No 'x0 y0 width height' argument after image, defaulting to '%d %d %d %d'!\n", x0, y0, w, h);
  }
  else {
    x0 = atoi(argv[2]);
    y0 = atoi(argv[3]);
    w = atoi(argv[4]);
    h = atoi(argv[5]);
  }

  printf("Reading %s region %d,%d %dx%d\n", jp2_file, x0, y0, w, h);
  unsigned char* output_rgb8_buff = malloc(w*h*3);

  int err_code = read_pixels_from(jp2_file, output_rgb8_buff, x0, y0, w, h);
  if (err_code != SUCCESS) {
    printf("Error reading, code %d\n", err_code);
  }
  else {
    // Write buffer to "rgb-out.bin"
    FILE* rgb_out_f = fopen("rgb-out.bin", "wb");
    fwrite(output_rgb8_buff, w*h*3, 1, rgb_out_f);
    fclose(rgb_out_f);
  }

  free(output_rgb8_buff);

  return SUCCESS;
}
