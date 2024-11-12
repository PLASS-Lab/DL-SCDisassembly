#include <stdio.h>
#include <stdlib.h>

#include "elmoasmfunctionsdef-extension.h"

// ELMO API :
//  - printbyte(addr): Print single byte located at address 'addr' to output file;
//  - randbyte(addr): Load byte of random to memory address 'addr';
//  - readbyte(addr): Read byte from input file to address 'addr'.
// ELMO API (extension) :
//  - print2bytes, rand2bytes and read2bytes: idem, but for an address pointing on 2 bytes;
//  - print4bytes, rand4bytes and read4bytes: idem, but for an address pointing on 4 bytes.

int main(void) {
  uint16_t num_challenge, nb_challenges;

  read2bytes(&nb_challenges);
  for(num_challenge=0; num_challenge<nb_challenges; num_challenge++) {
    // Set variables for the current challenge

    starttrigger(); // To start a new trace
    // Do the leaking operations here...
    endtrigger(); // To end the current trace

  }

  endprogram(); // To indicate to ELMO that the simulation is finished

  return 0;
}
