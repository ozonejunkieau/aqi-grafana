# aqi-grafana

This code acts as a bridge between the ACT Health Air Quality data (https://www.data.act.gov.au/Environment/Air-Quality-Monitoring-Data/94a5-zqnn), the particle monitor data (https://www.data.act.gov.au/Environment/Particulate-Matter-data-from-ACT-Air-Quality-Monit/ufvu-jybu), and Grafana.

It does not cache results locally, requesting them from data.act.gov.au every time. API Tokens can be optionally used, follow the above links for instructions on their creation.

## Installation
It's a Python script. Install requirements and then execute it to run using the Flask development environment. Copy `creds.example.py` to `creds.py` and include an API Token if you have one.
The example service file included starts the server using gunicorn on port 8128, but will require some configuration. 

For Grafana, it uses the Grafana Simple JSON Datasource plugin: https://grafana.com/grafana/plugins/grafana-simple-json-datasource. 
Simply point this plugin to the location the server is running and it should work. 

Thanks to Jon for his post on using the endpoint: https://blog.jonathanmccall.com/2018/10/09/creating-a-grafana-datasource-using-flask-and-the-simplejson-plugin/