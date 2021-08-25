#include "Watchy_Tetris.h"

const unsigned char *tetris_nums[10] = {tetris0, tetris1, tetris2, tetris3, tetris4, tetris5, tetris6, tetris7, tetris8, tetris9};

const unsigned char *tetris_small_nums[10] = {tetrissmall0, tetrissmall1, tetrissmall2, tetrissmall3, tetrissmall4, tetrissmall5, tetrissmall6, tetrissmall7, tetrissmall8, tetrissmall9};

WatchyTetris::WatchyTetris() {} //constructor

void WatchyTetris::drawWatchFace()
{
    display.fillScreen(GxEPD_WHITE);
    display.drawBitmap(0, 0, tetrisbg, DISPLAY_WIDTH, DISPLAY_HEIGHT, GxEPD_BLACK);

    //Hour
    display.drawBitmap(25, 20, tetris_nums[currentTime.Hour / 10], 40, 60, GxEPD_BLACK); //first digit
    display.drawBitmap(75, 20, tetris_nums[currentTime.Hour % 10], 40, 60, GxEPD_BLACK); //second digit

    //Minute
    display.drawBitmap(25, 110, tetris_nums[currentTime.Minute / 10], 40, 60, GxEPD_BLACK); //first digit
    display.drawBitmap(75, 110, tetris_nums[currentTime.Minute % 10], 40, 60, GxEPD_BLACK); //second digit

    //Steps
    if (currentTime.Hour == 0 && currentTime.Minute == 0)
    {
        sensor.resetStepCounter();
    }
    uint32_t stepCount = sensor.getCounter();
    if (stepCount > 1000000)
        display.drawBitmap(131, 41, tetris_small_nums[(stepCount / 1000000) % 10], 8, 8, GxEPD_BLACK);
    if (stepCount > 100000)
        display.drawBitmap(141, 41, tetris_small_nums[(stepCount / 100000) % 10], 8, 8, GxEPD_BLACK);
    if (stepCount > 10000)
        display.drawBitmap(151, 41, tetris_small_nums[(stepCount / 10000) % 10], 8, 8, GxEPD_BLACK);
    if (stepCount > 1000)
        display.drawBitmap(161, 41, tetris_small_nums[(stepCount / 1000) % 10], 8, 8, GxEPD_BLACK);
    if (stepCount > 100)
        display.drawBitmap(171, 41, tetris_small_nums[(stepCount / 100) % 10], 8, 8, GxEPD_BLACK);
    if (stepCount > 10)
        display.drawBitmap(181, 41, tetris_small_nums[(stepCount / 10) % 10], 8, 8, GxEPD_BLACK);
    display.drawBitmap(191, 41, tetris_small_nums[(stepCount) % 10], 8, 8, GxEPD_BLACK);

    //Voltage
    float VBAT = getBatteryVoltage();
    display.drawBitmap(161, 81, tetris_small_nums[(int)(VBAT * 1) % 10], 8, 8, GxEPD_BLACK);
    display.drawBitmap(171, 81, tetris_small_nums[(int)(VBAT * 10) % 10], 8, 8, GxEPD_BLACK);
    display.drawBitmap(181, 81, tetris_small_nums[(int)(VBAT * 100) % 10], 8, 8, GxEPD_BLACK);

    //Date
    if (currentTime.Month > 10)
        display.drawBitmap(151, 111, tetris_small_nums[currentTime.Month / 10], 8, 8, GxEPD_BLACK);
    display.drawBitmap(161, 111, tetris_small_nums[currentTime.Month % 10], 8, 8, GxEPD_BLACK);
    display.drawBitmap(171, 111, tetris_small_nums[currentTime.Day / 10], 8, 8, GxEPD_BLACK);
    display.drawBitmap(181, 111, tetris_small_nums[currentTime.Day % 10], 8, 8, GxEPD_BLACK);
}