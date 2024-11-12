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

#include "polyvec.h"
#include "params.h"

int main(void) {
  uint16_t num_challenge, nb_challenges;
  int j, k;
  polyvec skpv;

  read2bytes(&nb_challenges);
  for(num_challenge=0; num_challenge<nb_challenges; num_challenge++) {

    // Load the private vector s
    for(j=0;j<KYBER_K;j++)
      for(k=0;k<KYBER_N;k++)
        read2bytes((uint16_t*) &skpv.vec[j].coeffs[k]);

    starttrigger(); // To start a new trace

    // Do the leaking operations here...
    polyvec_ntt(&skpv);
    
    endtrigger(); // To end the current trace

    // Print the results of the computation
    for(j=0;j<KYBER_K;j++)
      for(k=0;k<KYBER_N;k++)
        print2bytes((uint16_t*) &skpv.vec[j].coeffs[k]);
  }

  endprogram(); // To indicate to ELMO that the simulation is finished

  return 0;
}
