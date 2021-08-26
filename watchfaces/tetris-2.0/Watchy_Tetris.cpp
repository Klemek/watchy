#include "Watchy_Tetris.h"

const unsigned char *tetris_nums[10] = {tetris0, tetris1, tetris2, tetris3, tetris4, tetris5, tetris6, tetris7, tetris8, tetris9};

const unsigned char *tetris_small_nums[10] = {tetrissmall0, tetrissmall1, tetrissmall2, tetrissmall3, tetrissmall4, tetrissmall5, tetrissmall6, tetrissmall7, tetrissmall8, tetrissmall9};

const float MAX_VBAT = 4.33;
const float MIN_VBAT = 3.80;

WatchyTetris::WatchyTetris() {} //constructor

void WatchyTetris::drawWatchFace()
{
    display.fillScreen(GxEPD_WHITE);

    // Background
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
    drawNumber(191, 41, stepCount);

    //Voltage
    float VBAT = getBatteryVoltage();
    uint32_t percent = (int)(100.0 * (VBAT - MIN_VBAT) / MAX_VBAT);
    if (percent < 0)
        percent = 0;
    if (percent > 100)
        percent = 100;
    drawNumber(181, 81, percent);

    //Date
    drawNumber(181, 111, currentTime.Month * 100 + currentTime.Day);
}

void WatchyTetris::drawNumber(uint32_t x, uint32_t y, uint32_t v)
{
    for(int8_t i = 0; i < 8; i++){
        if (v == 0) {
            break;
        }
        display.drawBitmap(x - i * 10, y, tetris_small_nums[v % 10], 8, 8, GxEPD_BLACK);
        v /= 10;
    }
}