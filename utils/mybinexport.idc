#include <idc.idc>

static main() {

  Batch(0);

  Wait();

  RunPlugin( "binexport12_ida64", 2 );

  Exit(0);

}
