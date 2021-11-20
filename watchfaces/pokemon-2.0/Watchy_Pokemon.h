#ifndef WATCHY_POKEMON_H
#define WATCHY_POKEMON_H

#include <Watchy.h>
#include "FreeMonoBold10pt7b.h"
#include "FreeMonoBold7pt7b.h"
#include "wta.h"

#ifdef FR
#include "pokemon_fr.h"
#else
#include "pokemon.h"
#endif

class WatchyPokemon : public WatchySynced
{
public:
    WatchyPokemon();
    void drawWatchFace();
    double randomDay();
    double randomHour();
    double randomMinute();
};

#endif