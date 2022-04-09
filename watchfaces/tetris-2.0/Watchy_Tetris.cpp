#include "Watchy_Tetris.h"

const unsigned char *tetris_nums_0[3] = {tetris0_0, tetris1_0, tetris2_0};
const unsigned char *tetris_nums_1[10] = {tetris0_1, tetris1_1, tetris2_1, tetris3_1, tetris4_1, tetris5_1, tetris6_1, tetris7_1, tetris8_1, tetris9_1};
const unsigned char *tetris_nums_2[6] = {tetris0_2, tetris1_2, tetris2_2, tetris3_2, tetris4_2, tetris5_2};
const unsigned char *tetris_nums_3[10] = {tetris0_3, tetris1_3, tetris2_3, tetris3_3, tetris4_3, tetris5_3, tetris6_3, tetris7_3, tetris8_3, tetris9_3};

const unsigned char *tetris_small_nums[10] = {tetrissmall0, tetrissmall1, tetrissmall2, tetrissmall3, tetrissmall4, tetrissmall5, tetrissmall6, tetrissmall7, tetrissmall8, tetrissmall9};

const unsigned char *pieces[19] = {
    piece0_0, piece0_1,
    piece1_0, piece1_1,
    piece2_0, piece2_1, piece2_2, piece2_3,
    piece3_0, piece3_1, piece3_2, piece3_3,
    piece4_0, piece4_1,
    piece5_0,
    piece6_0, piece6_1, piece6_2, piece6_3};

const float MAX_VBAT = 4.20;
const float MIN_VBAT = 3.80;

void WatchyTetris::drawWatchFace()
{
    readWorldTime();

    //Voltage
    float VBAT = getBatteryVoltage();
    uint32_t percent = (int)(100.0 * ((VBAT - MIN_VBAT) / (MAX_VBAT - MIN_VBAT)));
    if (percent < 0)
        percent = 0;
    if (percent > 100)
        percent = 100;

    //Steps
    if (currentTime.Hour == 0 && currentTime.Minute == 1)
    {
        sensor.resetStepCounter();
    }
    uint32_t stepCount = sensor.getCounter();

    display.fillScreen(GxEPD_WHITE);

    //Save battery life
    WiFi.mode(WIFI_OFF);
    btStop();

    // Background
    display.drawBitmap(0, 0, tetrisbg, DISPLAY_WIDTH, DISPLAY_HEIGHT, GxEPD_BLACK);

    //Hour
    display.drawBitmap(25, 20, tetris_nums_0[currentTime.Hour / 10], 40, 60, GxEPD_BLACK); //first digit
    display.drawBitmap(75, 20, tetris_nums_1[currentTime.Hour % 10], 40, 60, GxEPD_BLACK); //second digit

    //Minute
    display.drawBitmap(25, 110, tetris_nums_2[currentTime.Minute / 10], 40, 60, GxEPD_BLACK); //first digit
    display.drawBitmap(75, 110, tetris_nums_3[currentTime.Minute % 10], 40, 60, GxEPD_BLACK); //second digit

    
    drawNumber(181, 41, stepCount, 6);

    drawNumber(176, 81, percent, 3);

    //Date
    drawNumber(176, 111, currentTime.Day * 100 + currentTime.Month, 4);

    //Random piece
    display.drawBitmap(150, 140, pieces[int(random() * 19)], 40, 40, GxEPD_BLACK);
}

void WatchyTetris::drawNumber(int x, int y, int value, int max_digits)
{
    for (int8_t i = 0; i < max_digits; i++)
    {
        display.drawBitmap(x - i * 10, y, tetris_small_nums[value % 10], 8, 8, GxEPD_BLACK);
        value /= 10;
        if (value == 0)
            break;
    }
}

double WatchyTetris::random()
{
    uint32_t seed = currentTime.Year;
    seed = seed * 12 + currentTime.Month;
    seed = seed * 31 + currentTime.Day;

    double v = pow(seed, 6.0 / 7.0);
    v *= sin(v) + 1;

    return v - floor(v);
}