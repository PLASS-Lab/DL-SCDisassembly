#include "elmoasmfunctionsdef.h"

// Extension of the ELMO API for 2-bytes types
static void rand2bytes(uint16_t* elt) {
  randbyte((uint8_t*) elt+1);
  randbyte((uint8_t*) elt);
}
static void print2bytes(uint16_t* elt) {
  printbyte((uint8_t*) elt+1);
  printbyte((uint8_t*) elt);
}
static void read2bytes(uint16_t* elt) {
  readbyte((uint8_t*) elt+1);
  readbyte((uint8_t*) elt);
}

// Extension of the ELMO API for 4-bytes types
static void rand4bytes(uint32_t* elt) {
  randbyte((uint8_t*) elt+3);
  randbyte((uint8_t*) elt+2);
  randbyte((uint8_t*) elt+1);
  randbyte((uint8_t*) elt);
}
static void print4bytes(uint32_t* elt) {
  printbyte((uint8_t*) elt+3);
  printbyte((uint8_t*) elt+2);
  printbyte((uint8_t*) elt+1);
  printbyte((uint8_t*) elt);
}
static void read4bytes(uint32_t* elt) {
  readbyte((uint8_t*) elt+3);
  readbyte((uint8_t*) elt+2);
  readbyte((uint8_t*) elt+1);
  readbyte((uint8_t*) elt);
}
