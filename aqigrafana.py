#! /usr/local/bin/python
# -*- coding: utf-8 -*-
from calendar import timegm
from functools import lru_cache
import datetime
from flask import Flask, request, jsonify
import requests

from creds import API_TOKEN

app = Flask(__name__)

app.debug = False

URL_PM = "https://www.data.act.gov.au/resource/ufvu-jybu.json"
URL_AQI = "https://www.data.act.gov.au/resource/94a5-zqnn.json"


def auth_get_json(url):

    return requests.get(url, headers={"X-App-Token": API_TOKEN}).json()


@lru_cache(maxsize=100)
def get_series_names():
    # This assumes that the most recent 10 data points includes all measurements from all times. A bit hacky, but it
    # works.

    aqi_data = auth_get_json(URL_AQI + "?$limit=10")

    pm_data = auth_get_json(URL_PM + "?$limit=10")

    print(aqi_data)
    print(pm_data)

    all_aqi_meas = [
        [
            "AQI:" + r["name"] + ":" + i
            for i in r.keys()
            if i not in ["name", "gps", "date", "time", "datetime"]
        ]
        for r in aqi_data
    ]

    all_pm_meas = [
        [
            "PM:" + r["station"] + ":" + i
            for i in r.keys()
            if i not in ["station", "gps", "date", "time", "datetime"]
        ]
        for r in pm_data
    ]

    measurements = list(
        set([item for sublist in (all_aqi_meas + all_pm_meas) for item in sublist])
    )

    return measurements


@app.route("/")
def health_check():
    return "This datasource is healthy."


@app.route("/search", methods=["POST"])
def search():
    return jsonify(get_series_names())


@app.route("/query", methods=["POST"])
def query():
    def format_time_for_query(in_datetime):
        return (in_datetime + datetime.timedelta(hours=10)).isoformat()

    def to_datetime_from_grafana(in_str):
        return datetime.datetime.strptime(in_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    req = request.get_json()

    # This is for backwards compatibility with the previous version, if the target doesn't begin with API or PM, prepend
    # API.

    raw_targets = [
        r["target"]
        if (r["target"].startswith("AQI") or r["target"].startswith("PM"))
        else "AQI:" + r["target"]
        for r in req["targets"]
    ]

    data_sources = set([r.split(":")[0] for r in raw_targets])

    all_data = []
    for ds in data_sources:

        targets = [r.split(":")[1:] for r in raw_targets if r.startswith(ds)]

        if ds == "AQI":
            base_url = URL_AQI
            id = "name"
        elif ds == "PM":
            base_url = URL_PM
            id = "station"

        sites = list(set([i[0] for i in targets]))
        meas = list(set([i[1] for i in targets]))

        start_time = to_datetime_from_grafana(req["range"]["from"])
        stop_time = to_datetime_from_grafana(req["range"]["to"])
        all_meas = [id, "datetime"] + meas

        name_query = " OR ".join([f'{id}="{s}"' for s in sites])

        query_url = (
            base_url + f"?"
            f"$select={','.join(all_meas)}&"
            f"$order=datetime%20DESC&"
            f"$where=datetime%3E=%22{format_time_for_query(start_time)}%22%20AND%20"
            f"datetime%3C=%22{format_time_for_query(stop_time)}%22 AND ({name_query})"
        )

        resp = auth_get_json(query_url)

        for t_site, t_meas in targets:
            t_target = ds + ":" + t_site + ":" + t_meas

            this_data = []
            this_data_time = []
            for r in resp:
                if r[id] == t_site:
                    try:
                        this_data.append(float(r[t_meas]))
                        r_time = 1000 * timegm(
                            (
                                datetime.datetime.strptime(
                                    r["datetime"], "%Y-%m-%dT%H:%M:%S.%f"
                                )
                                - datetime.timedelta(hours=10)
                            ).timetuple()
                        )
                        this_data_time.append(r_time)
                    except KeyError:
                        pass  # print("Inconsistent Data")

            this_block = {
                "target": t_target,
                "datapoints": [
                    (a, b)
                    for a, b in zip(reversed(this_data), reversed(this_data_time))
                ],
            }
            all_data.append(this_block)

    return jsonify(all_data)


if __name__ == "__main__":
    # Create cache of series names.
    get_series_names()

    app.run()
