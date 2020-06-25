# Description
SMApy is a python framework to extract performance data from SMA Solar inverters
and submit it to InfluxDB. It can run standalone, in Docker or even on
Kubernetes.

# Operation
`submitter.py` is the workhorse. It takes a single argument, pointing to a
YAML configfile, which requires the following structure:

```yaml
sma:
  url: https://url-or-ip-of-inverter
  group: usr
  password: user-password
influxdb:
  host: influx-host
  port: influx-port
  ssl: using ssl?
  verify_ssl: True
  username: username
  password: password
  database: database
tags:
  whichever: tags
  you: want
interval: 30
```

# Reverse engineering Webconnect
I have opened the web portal of my inverter while looking at Chrome inspector to
see which HTTP resources where getting fetched. The application fetches these
files upon startup:
* `ObjectMetadata_Istl.json`
* `en-US.json`

The former is an object model of all tags and their meaning. It looks like this:
```json
{
  "6100_40263F00": {
    "Prio": 1,
    "TagId": 416,
    "TagIdEvtMsg": 10030,
    "Unit": 18,
    "DataFrmt": 0,
    "Scale": 1,
    "Typ": 0,
    "WriteLevel": 5,
    "TagHier": [
      835,
      230
    ],
    "Min": true,
    "Max": true,
    "Sum": true,
    "Avg": true,
    "Cnt": true,
    "SumD": true
  }
}
```

It appeared that `TagId`, `TagIdEvtMsg`, `Unit` and `TagHier` are entries you
can retrieve from the language file (`en-US.json` in my case). Here is an
excerpt:

```json
{
  "18": "W",
  "230": "Grid measurements",
  "416": "Power",
  "835": "AC Side",
  "10030": "Power"
}
```

Next, I saw that I, when watching "Instantaneous values", the app periodically
retrieved the file `getAllOnValues.json`, with the following structure:

```json
{
  "result": {
    "0199-12345678": {
      "6100_40263F00": {
        "1": [
          {
            "val": 2600
          }
        ]
      }
    }
  }
}
```

So, what we see here is: "AC Side - Grid Measurements - Power" with the value
2600 W.

# Links
Other projects that are similar:
* [pysma](https://github.com/kellerza/pysma)
