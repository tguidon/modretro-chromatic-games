#ifndef DD_COMBAT_FX_H
#define DD_COMBAT_FX_H
#include <gbdk/platform.h>
#include "gbs_types.h"
void dd_combat_start(UBYTE pistol, direction_e direction, UBYTE distance, UBYTE hit) BANKED;
void dd_combat_update(void) BANKED;
void dd_combat_reset(void) BANKED;
#endif
