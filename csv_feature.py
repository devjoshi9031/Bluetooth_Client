import csv, json, time

from jinja2 import TemplateAssertionError

measurement = "SCD"
time_t = time.ctime()
tag = "All_Sensors"
Temp = 20.00
Humidity = 100
Gas = 1000
header = ["measurement", "time_t","tag", "Temperature", "Humidity", "Gas Co2" ]
data = [measurement, time_t, tag, Temp, Humidity, Gas]

with open("SCD.csv", "w") as f:
    writer=csv.writer(f)
    writer.writerow(header)
    writer.writerow(data)