#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import os
import pickle
import json
from bson import json_util
import pandas as pd
import sqlobject
from sqlobject import AND
from datetime import datetime as dt, timedelta
import memcache
import time
import logging

from pm25.db_config import DB_CONFIG
from pm25.db_config import PM25Observation as pm_db
from pm25.db_config import WundergroundForecast as fcs_db

# Setup logging
FORMAT = "%(asctime)s %(module)s %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)

## Helper functions
def wdird_to_direction(inp):
    return math.sin(inp*2*math.pi/360)

def to_sin_hour(date, h):
    return math.sin(date.hour*2*math.pi*h/24)

def to_cos_hour(date, h):
    return math.cos(date.hour*2*math.pi*h/24)

def get_sunhours(date, lon=116.4166666667, lat=39.91666666667):
    "Returns daylight hours in Beijing on the day specified in input."
    import ephem

    bjg      = ephem.Observer()
    bjg.lon  = str(lon)
    bjg.lat  = str(lat)
    bjg.date = date.date()

    #day
    sunrise = bjg.previous_rising(ephem.Sun())
    sunset = bjg.next_setting(ephem.Sun())

    # night
    if sunrise > sunset:
        sunrise = bjg.next_rising(ephem.Sun())
        sunset = bjg.previous_setting(ephem.Sun())

    diff = sunset.datetime() - sunrise.datetime()
    return diff.total_seconds() / 3600.

def is_holiday(date):
    "Simple function to set working days. TODO: use real calendar."
    if date.isoweekday() == 6:
        return 0.5
    elif date.isoweekday() == 7:
        return 0
    else:
        return 1

def features_as_df(AREA = u'北京', FC_DATETIME = dt(2015, 2, 17, 13)):
    "Pull pollution and climate data from various DBs."

    logging.info('Pulling data from database.')

    ## Pull all pollution stations for an area
    sqlobject.sqlhub.processConnection = sqlobject.postgres.builder()(db='pm25', **DB_CONFIG)
    df_pm = pm_db.select(AND(pm_db.q.area == AREA, pm_db.q.time_point >= FC_DATETIME))
    df_pm = pd.DataFrame([dict((c, getattr(o, c)) for c in o.sqlmeta.columns) for o in df_pm])
    df_pm.index = df_pm['time_point']
    df_pm = df_pm.drop(['position_name', 'primary_pollutant', 'quality'], axis=1)
    df_pm = df_pm.sort_index().dropna() #.resample('h', how='mean')

    
    ## 24h weather forecast.io goes into dfw
    sqlobject.sqlhub.processConnection = sqlobject.postgres.builder()(db='wunderground', **DB_CONFIG)

    fcs = fcs_db.select(AND(fcs_db.q.fc_datetime>=FC_DATETIME, fcs_db.q.area == AREA))
    dfw = pd.DataFrame([dict((c, getattr(o, c)) for c in o.sqlmeta.columns) for o in fcs])
    # dfw.index = dfw['target_datetime']

    # dfw['time_point'] = dfw['target_datetime']
    # dfw = dfw.drop(['country', 'fc_datetime', 'conds', 'target_datetime'], axis=1)
    dfw = dfw.drop(['area'], axis=1).sort().dropna()

    ## Pivot weather data by station
    piv_w = pd.pivot(index=df_pm.time_point, columns=df_pm.station_code, values=df_pm.pm2_5)
    stations = piv_w.columns
    piv_w.columns = ['PM_%s'%s for s in stations]
    comps = ['so2', 'no2', 'aqi', 'co']
    for c in comps:
        piv_temp = pd.pivot(index=df_pm.time_point, columns=df_pm.station_code, values=df_pm[c])
        piv_temp.columns = ['%s_%s'%(c, s) for s in stations]
        piv_w = piv_w.join(piv_temp)


    ## Align weather forcast in row
    features = ['tempm', 'hum', 'ozone', 'pressurem', 'wdird', 'wspdm']

    temp_fc = None
    for fc_datetime in set(dfw.fc_datetime):
        temp_feat = None
        for f in features:
            temp = dfw[dfw.fc_datetime == fc_datetime].pivot(index='fc_datetime', columns='target_datetime', values=f)
            temp.columns = ['%s_%s'% (f, i) for i in range(len(temp.columns))]
            if temp_feat is None:
                temp_feat = temp
            else:
                temp_feat = temp_feat.join(temp)
        
        if temp_fc is None:
            temp_fc = temp_feat
        else:
            temp_fc = temp_fc.append(temp_feat)
    dfw_piv = temp_fc.sort_index()
    piv = piv_w.join(dfw_piv).dropna()
    
    piv['Daylight'] = [get_sunhours(h) for h in piv.index]
    piv['WorkingTime'] = [is_holiday(h) for h in piv.index]
    piv['SinusDayNight1'] = [to_sin_hour(h, 1) for h in piv.index]
    piv['SinusDayNight2'] = [to_sin_hour(h, 2) for h in piv.index]
    
    return piv, df_pm


def build_save_models(piv, df_pm, hours=12):
    "Use existing data and pollution outcome to train ML."

    ## Calculated rows (daylight, working day, sin-hour)
    y = df_pm.groupby('time_point').mean().pm2_5.shift(hours).dropna()
    common_ix = y.index.intersection(piv.dropna().index)
    X = piv.loc[common_ix]
    y = y.loc[common_ix]

    # Cross-validation
    # from sklearn import cross_validation
    # X_train, X_test, y_train, y_test = cross_validation.train_test_split(
    #     X, y, test_size=0.01, random_state=0)

    # RFR model
    from sklearn import ensemble
    rfr = ensemble.RandomForestRegressor(max_depth=4).fit(X, y)

    # from sklearn import metrics
    # model = rfr
    # mae = metrics.mean_absolute_error(y_test, model.predict(X_test))
    # rmse = math.sqrt(metrics.mean_squared_error(y_test, model.predict(X_test)))
    # r2 = metrics.r2_score(y_test, model.predict(X_test))

    if not os.path.exists('/tmp/models'):
        os.makedirs('/tmp/models')
    
    f = open('/tmp/models/rtr_%s.pkl' % hours, 'w')
    f.write(pickle.dumps(rfr))
    f.close()

def forecast_hour(features, offset):
    "Forecast single hour based on offset (t+offset), given features at time t."
    f = open('/tmp/models/rtr_%s.pkl' % offset).read()
    model = pickle.loads(f)
    return features.name, features.name + timedelta(hours=offset), model.predict(features)[0]

def build_forecast_json(features, df_pm, ci=15):
    "Package observed values and forecast values in json."

    preds = [forecast_hour(features, h) for h in range(1, 25)]
    pred_json = {
                 'fc_datetime': features.name.to_datetime(),
                 'length_forecasts': None,
                 'length_observed': None,
                 'generated': dt.now(),
                 'forecasts': [],
                 'observed': []
                }
    pred_json['forecasts'] = [{'min': max(0, p[2] - ci),
                               'max': p[2] + ci,
                               'avg': p[2],
                               'datetime': p[1].to_datetime(),
                              } for p in preds]
    pred_json['length_forecasts'] = len(pred_json['forecasts'])
    observed_index = pd.date_range(end=features.name, periods=48, freq='h')
    pm_observed = df_pm.ix[observed_index].groupby('time_point').pm2_5.quantile([0.2, 0.5, 0.8])
    pred_json['observed'] = [{'min': pm_observed[(h, 0.2)],
                               'max': pm_observed[(h, 0.8)],
                               'avg': pm_observed[(h, 0.5)],
                               'datetime': h,
                              } for h in pm_observed.index.levels[0]]
    pred_json['length_observed'] = len(pred_json['observed'])
    
    return pred_json

    
if __name__ == '__main__':
    while True: #poor man's daemon
        logging.info('Starting scheduler.')
        df_piv, df_pm = features_as_df()
        for h in range(1, 25):
            build_save_models(df_piv, df_pm, h) #TODO rebuild models each hour?
            logging.info('Build classifier for hour %i.' % h)

        pred_json = build_forecast_json(df_piv.ix[-1], df_pm)

        mc = memcache.Client(['127.0.0.1:11211'])
        mc.set('/forecast/beijing.json', json.dumps(pred_json, default=json_util.default))
        logging.info('Saved json.')

        time.sleep(60*60)
        