#ifndef WATCHY_TETRIS_H
#define WATCHY_TETRIS_H

#include <Watchy.h>
#include "tetris.h"
#include "wta.h"

#undef WTA_TIMEZONE
#define WTA_TIMEZONE "Europe/Paris"

class WatchyTetris : public WatchySynced
{
public:
    WatchyTetris();
    void drawWatchFace();
    void drawNumber(int x, int y, int value, int max_digits);
    double random();
};

#endif