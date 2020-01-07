#! /usr/local/bin/python
# -*- coding: utf-8 -*-
from calendar import timegm
import datetime
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

app.debug = False


@app.route("/")
def health_check():
    return "This datasource is healthy."


@app.route("/search", methods=["POST"])
def search():
    latest_data = requests.get(
        "https://www.data.act.gov.au/resource/94a5-zqnn.json?$limit=10"
    ).json()

    all_meas = [
        [
            r["name"] + ":" + i
            for i in r.keys()
            if i not in ["name", "gps", "date", "time", "datetime"]
        ]
        for r in latest_data
    ]

    measurements = list(set([item for sublist in all_meas for item in sublist]))

    return jsonify(sorted(measurements))


@app.route("/query", methods=["POST"])
def query():

    def format_time_for_query(in_datetime):
        return (in_datetime + datetime.timedelta(hours=10)).isoformat()

    def to_datetime_from_grafana(in_str):
        return datetime.datetime.strptime(in_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    req = request.get_json()

    targets = [r["target"].split(":") for r in req["targets"]]

    sites = list(set([i[0] for i in targets]))
    meas = list(set([i[1] for i in targets]))

    start_time = to_datetime_from_grafana(req["range"]["from"])
    stop_time = to_datetime_from_grafana(req["range"]["to"])
    all_meas = ["name", "datetime"] + meas

    name_query = " OR ".join([f'name="{s}"' for s in sites])

    query_url = f"https://www.data.act.gov.au/resource/94a5-zqnn.json?" \
                f"$select={','.join(all_meas)}&" \
                f"$order=datetime%20DESC&" \
                f"$where=datetime%3E=%22{format_time_for_query(start_time)}%22%20AND%20" \
                f"datetime%3C=%22{format_time_for_query(stop_time)}%22 AND ({name_query})"

    resp = requests.get(query_url).json()

    all_data = []
    for t_site, t_meas in targets:
        t_target = t_site + ":" + t_meas

        this_data = []
        this_data_time = []
        for r in resp:
            if r["name"] == t_site:
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
                    print("Inconsistent Data")

        this_block = {
            "target": t_target,
            "datapoints": [
                (a, b) for a, b in zip(reversed(this_data), reversed(this_data_time))
            ],
        }
        all_data.append(this_block)

    return jsonify(all_data)


if __name__ == "__main__":
    app.run()
