#include "wta.h"

RTC_DATA_ATTR int worldTimeIntervalCounter = WTA_UPDATE_INTERVAL;

void WatchySynced::readWorldTime()
{
    if (worldTimeIntervalCounter >= WTA_UPDATE_INTERVAL)
    {
        if (connectWiFi())
        {
            HTTPClient http;
            http.setConnectTimeout(10000);
            String queryURL = String(WTA_URL) + String(WTA_TIMEZONE);
            http.begin(queryURL.c_str());
            int httpResponseCode = http.GET();
            if (httpResponseCode == 200)
            {
                String payload = http.getString();
                JSONVar responseObject = JSON.parse(payload);
                tmElements_t tm;
                String datetime = String((const char *)responseObject["datetime"]);
                tm.Year = datetime.substring(0, 4).toInt() - YEAR_OFFSET;
                tm.Month = datetime.substring(5, 7).toInt();
                tm.Day = datetime.substring(8, 10).toInt();
                tm.Hour = datetime.substring(11, 13).toInt();
                tm.Minute = datetime.substring(14, 16).toInt();
                tm.Second = 0;
                time_t t = makeTime(tm);
                RTC.set(t);
                RTC.read(currentTime);
            }
            http.end();
            WiFi.mode(WIFI_OFF);
            btStop();
        }
        worldTimeIntervalCounter = 0;
    }
    else
    {
        worldTimeIntervalCounter++;
    }
}