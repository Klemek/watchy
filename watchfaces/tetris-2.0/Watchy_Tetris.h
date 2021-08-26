#ifndef WATCHY_TETRIS_H
#define WATCHY_TETRIS_H

#include <Watchy.h>
#include "tetris.h"

class WatchyTetris : public Watchy
{
public:
    WatchyTetris();
    void drawWatchFace();
    void drawNumber(int x, int y, int value, int max_digits);
};

#endif