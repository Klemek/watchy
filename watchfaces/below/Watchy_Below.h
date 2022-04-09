#ifndef WATCHY_BELOW_H
#define WATCHY_BELOW_H

#include <Watchy.h>
#include "below.h"
#include "wta.h"

class WatchyBelow : public WatchySynced
{
    using WatchySynced::WatchySynced;
    public:
        void drawWatchFace();
};

#endif