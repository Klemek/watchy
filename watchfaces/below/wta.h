#ifndef WTA_H
#define WTA_H

#include <Watchy.h>

#define WTA_URL "http://worldtimeapi.org/api/timezone/"
#define WTA_TIMEZONE "Europe/Paris"
#define WTA_UPDATE_SHORT_INTERVAL 30 //minutes
#define WTA_UPDATE_LONG_INTERVAL 300 //minutes
#define WTA_UPDATE_TIMEOUT 10000     //ms

class WatchySynced : public Watchy
{
    using Watchy::Watchy;
    public:
        void readWorldTime();
};

#endif