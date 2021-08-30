#include "Watchy_Below.h"

WatchyBelow::WatchyBelow()
{
} //constructor

void WatchyBelow::drawWatchFace()
{
    display.fillScreen(GxEPD_BLACK);

    display.drawBitmap(0, 0, background, DISPLAY_WIDTH, DISPLAY_HEIGHT, GxEPD_WHITE);

    float time = currentTime.Hour + currentTime.Minute / 60.0;

    int height;

    height = min(48, (int)(time * 16.0));
    display.fillRect(52, 96 - height, 5, height, GxEPD_WHITE);

    height = max(0, min(48, (int)((time - 3) * 16.0)));
    display.fillRect(65, 104, 5, height, GxEPD_WHITE);

    height = max(0, min(48, (int)((time - 6) * 16.0)));
    display.fillRect(78, 96 - height, 5, height, GxEPD_WHITE);

    height = max(0, min(48, (int)((time - 9) * 16.0)));
    display.fillRect(91, 104, 5, height, GxEPD_WHITE);

    height = max(0, min(48, (int)((time - 12) * 16.0)));
    display.fillRect(104, 96 - height, 5, height, GxEPD_WHITE);

    height = max(0, min(48, (int)((time - 15) * 16.0)));
    display.fillRect(117, 104, 5, height, GxEPD_WHITE);

    height = max(0, min(48, (int)((time - 18) * 16.0)));
    display.fillRect(130, 96 - height, 5, height, GxEPD_WHITE);

    height = max(0, min(48, (int)((time - 21) * 16.0)));
    display.fillRect(143, 104, 5, height, GxEPD_WHITE);
}