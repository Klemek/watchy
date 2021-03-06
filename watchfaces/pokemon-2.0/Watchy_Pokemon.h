#ifndef WATCHY_POKEMON_H
#define WATCHY_POKEMON_H

#include <Watchy.h>
#include "FreeMonoBold10pt7b.h"
#include "FreeMonoBold7pt7b.h"
#include "wta.h"

#define FR

#ifdef FR
#include "pokemon_fr.h"
#else
#include "pokemon.h"
#endif

class WatchyPokemon : public WatchySynced
{
    using WatchySynced::WatchySynced;
    public:
        void drawWatchFace();
        double randomDay();
        double randomHour();
        double randomMinute();
};

#endif