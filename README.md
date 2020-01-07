# aqi-grafana

This code acts as a bridge between the ACT Health Air Quality data (https://www.data.act.gov.au/Environment/Air-Quality-Monitoring-Data/94a5-zqnn) and Grafana.

It does not cache results locally, requesting them from data.act.gov.au every time. At the present time it does not 
utilise API keys, so the length of data requests are capped. This will probably change eventually.

## Installation
It's a Python script. Install requirements and then execute it to run using the Flask development environment. 
The example service file included starts the server using gunicorn on port 8128, but will require some configuration. 

For Grafana, it uses the Grafana Simple JSON Datasource plugin: https://grafana.com/grafana/plugins/grafana-simple-json-datasource. 
Simply point this plugin to the location the server is running and it should work. 

Thanks to Jon for his post on using the endpoint: https://blog.jonathanmccall.com/2018/10/09/creating-a-grafana-datasource-using-flask-and-the-simplejson-plugin/