#include "wta.h"

RTC_DATA_ATTR int worldTimeIntervalCounter = 0;

void WatchySynced::readWorldTime()
{
    if (worldTimeIntervalCounter == 0)
    {
        worldTimeIntervalCounter = WTA_UPDATE_SHORT_INTERVAL;
        if (connectWiFi())
        {
            HTTPClient http;
            http.setConnectTimeout(WTA_UPDATE_TIMEOUT);
            String queryURL = String(WTA_URL) + String(WTA_TIMEZONE);
            http.begin(queryURL.c_str());
            int httpResponseCode = http.GET();
            if (httpResponseCode == 200)
            {
                String payload = http.getString();
                JSONVar responseObject = JSON.parse(payload);
                tmElements_t tm;
                String datetime = String((const char *)responseObject["datetime"]);
                tm.Year = y2kYearToTm(datetime.substring(0, 4).toInt());
                tm.Month = datetime.substring(5, 7).toInt();
                tm.Day = datetime.substring(8, 10).toInt();
                tm.Hour = datetime.substring(11, 13).toInt();
                tm.Minute = datetime.substring(14, 16).toInt();
                tm.Second = 0;
                RTC.set(tm);
                RTC.read(currentTime);
                worldTimeIntervalCounter = WTA_UPDATE_LONG_INTERVAL;
            }
            http.end();
            WiFi.mode(WIFI_OFF);
            btStop();
        }
    }
    else
    {
        worldTimeIntervalCounter = worldTimeIntervalCounter < 0 ? 0 : worldTimeIntervalCounter - 1;
    }
}
