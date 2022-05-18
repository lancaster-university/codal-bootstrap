#include "MicroBit.h"

// The Micro:bit control object
MicroBit uBit;

// Out main function, run at startup
void main() {

    // Loop forever
    while( true ) {
        // Scroll some text on the display
        uBit.display.scroll( "Hello, Bootstrap!" );
    }

}