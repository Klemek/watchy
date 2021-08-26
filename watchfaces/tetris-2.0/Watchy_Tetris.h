#ifndef WATCHY_TETRIS_H
#define WATCHY_TETRIS_H

#include <Watchy.h>
#include "tetris.h"

class WatchyTetris : public Watchy
{
public:
    WatchyTetris();
    void drawWatchFace();
    void drawNumber(uint32_t x, uint32_t y, uint32_t v);
};

#endif