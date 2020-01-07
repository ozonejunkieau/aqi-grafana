# aqi-grafana

This code acts as a bridge between the ACT Health Air Quality data (https://www.data.act.gov.au/Environment/Air-Quality-Monitoring-Data/94a5-zqnn) and Grafana.

It does not cache results locally, requesting them from data.act.gov.au every time. At the present time it does not utilise API keys, so the length of data requests are capped. This may change.

## Installation
It's a Python script. Install requirements and then execute it to run using the Flask development environment. I'll add the scripts to support gunicorn soon.

For Grafana, it uses the Grafana Simple JSON Datasource plugin: https://grafana.com/grafana/plugins/grafana-simple-json-datasource

HT to Jon for his post on using the endpoint: https://blog.jonathanmccall.com/2018/10/09/creating-a-grafana-datasource-using-flask-and-the-simplejson-plugin/