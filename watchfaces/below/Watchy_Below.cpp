#include "Watchy_Below.h"

void WatchyBelow::drawWatchFace()
{
    readWorldTime();

    display.fillScreen(GxEPD_BLACK);

    display.drawBitmap(0, 0, background, DISPLAY_WIDTH, DISPLAY_HEIGHT, GxEPD_WHITE);

    float time = currentTime.Hour + currentTime.Minute / 60.0;

    int height;

    height = time < 12 ? min(48, (int)(time * 32.0)) : max(0, min(48, 48 - (int)((time - 12) * 32.0)));
    display.fillRect(52, time < 12 ? 96 - height : 48, 5, height, GxEPD_WHITE);

    height = time < 12 ? max(0, min(48, (int)((time - 1.5) * 32.0))) : max(0, min(48, 48 - (int)((time - 13.5) * 32.0)));
    display.fillRect(65, time < 12 ? 104 : 152 - height, 5, height, GxEPD_WHITE);

    height = time < 12 ? max(0, min(48, (int)((time - 3) * 32.0))) : max(0, min(48, 48 - (int)((time - 15) * 32.0)));
    display.fillRect(78, time < 12 ? 96 - height : 48, 5, height, GxEPD_WHITE);

    height = time < 12 ? max(0, min(48, (int)((time - 4.5) * 32.0))) : max(0, min(48, 48 - (int)((time - 16.5) * 32.0)));
    display.fillRect(91, time < 12 ? 104 : 152 - height, 5, height, GxEPD_WHITE);

    height = time < 12 ? max(0, min(48, (int)((time - 6) * 32.0))) : max(0, min(48, 48 - (int)((time - 18) * 32.0)));
    display.fillRect(104, time < 12 ? 96 - height : 48, 5, height, GxEPD_WHITE);

    height = time < 12 ? max(0, min(48, (int)((time - 7.5) * 32.0))) : max(0, min(48, 48 - (int)((time - 19.5) * 32.0)));
    display.fillRect(117, time < 12 ? 104 : 152 - height, 5, height, GxEPD_WHITE);

    height = time < 12 ? max(0, min(48, (int)((time - 9) * 32.0))) : max(0, min(48, 48 - (int)((time - 21) * 32.0)));
    display.fillRect(130, time < 12 ? 96 - height : 48, 5, height, GxEPD_WHITE);

    height = time < 12 ? max(0, min(48, (int)((time - 10.5) * 32.0))) : max(0, min(48, 48 - (int)((time - 22.5) * 32.0)));
    display.fillRect(143, time < 12 ? 104 : 152 - height, 5, height, GxEPD_WHITE);
}