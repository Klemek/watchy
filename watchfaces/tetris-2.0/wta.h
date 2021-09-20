#ifndef WTA_H
#define WTA_H

#include <Watchy.h>

#define WTA_URL "http://worldtimeapi.org/api/timezone/"
#define WTA_TIMEZONE "Etc/UTC"
#define WTA_UPDATE_INTERVAL 60 //minutes

class WatchySynced : public Watchy
{
public:
    void readWorldTime();
};

#endif