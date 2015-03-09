from sqlobject import *

DB_CONFIG = {'host': 'argus.vlx.cc',
            'user': 'collector',
            'password': 'eeH1shoRa0po1wu3We7Aerai4eebaiCu',
            }

class WundergroundForecast(SQLObject):
    fc_datetime = DateTimeCol(notNone=True)
    target_datetime = DateTimeCol(notNone=True)
    country = UnicodeCol()
    location = UnicodeCol()
    area = UnicodeCol()
    zmw = StringCol(default=None)
    wdird = FloatCol(default=None)
    hum = FloatCol(default=None)
    wspdm = FloatCol(default=None)
    conds = UnicodeCol(default=None)
    tempm = FloatCol(default=None)
    pressurem = FloatCol(default=None)
    cloud_cover = FloatCol(default=None)
    ozone = FloatCol(default=None)

class WundergroundObservation(SQLObject):
    datetime = DateTimeCol(notNone=True)
    country = UnicodeCol()
    location = UnicodeCol()
    zmw = StringCol(default=None)
    wdire = UnicodeCol(default=None)
    wdird = FloatCol(default=None)
    conds = UnicodeCol(default=None)
    metar = UnicodeCol(default=None)
    hail = FloatCol(default=None)
    tornado = FloatCol(default=None)
    hum = FloatCol(default=None)
    snow = FloatCol(default=None)
    tempm = FloatCol(default=None)
    pressurem = FloatCol(default=None)
    fog = FloatCol(default=None)
    rain = FloatCol(default=None)
    dewptm = FloatCol(default=None)
    thunder = FloatCol(default=None)
    wspdm = FloatCol(default=None)
    vism = FloatCol(default=None)


class PM25Observation(SQLObject):
    time_point = DateTimeCol()
    station_code = UnicodeCol()
    primary_pollutant = UnicodeCol()
    area = UnicodeCol()
    quality = UnicodeCol()
    position_name = UnicodeCol()
    co = FloatCol()
    o3 = FloatCol()
    pm2_5 = FloatCol()
    pm10 = FloatCol()
    aqi = FloatCol()
    so2 = FloatCol()
    no2 = FloatCol()

sqlhub.processConnection = postgres.builder()(db='wunderground', **DB_CONFIG)
