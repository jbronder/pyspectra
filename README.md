# pyspectra: A CLI for Seismic Design & Analysis Values
A command line application written for a terminal-savvy structural engineer
written in Python.


## About
This application is a CLI alternative to the [browser-based
application](https://ascehazardtool.org/) for retrieving seismic design and
analysis information. The motivation behind building it was picking up more CLI
development experience in Python with the `argparse` library.


## Endpoint Source
- [USGS Web Services](https://earthquake.usgs.gov/ws/designmaps/)


## A Brief (the briefest) Background on Seismic Design & Analysis
Earthquake engineering is one facet of structural engineering concerning the
design of structures under lateral loads and displacements associated with
seismic activity. As a starting point, engineers often need a building code
defined ground motion acceleration value to apply to a structure to simulate the
lateral forces occurring on a structure during a design seismic event. Combining
these accelerations with a structure's Lateral Force Resisting System (LFRS) and
the building's own self-weight, an estimate of the design lateral force on a
structure can be obtained.


## Common CLI Examples & Usage
By default, data prints to the terminal and like any CLI application, can also
be redirected to a file.

Obtaining seismic design data from the ASCE 7-22 Standard at 34 Latitude, -118
Longitude, Risk Category II, and Site Class D:
```bash
$ python3 webspectra.py asce7-22 34 -118 II D

# writing output to a file: out.txt
$ python3 webspectra.py asce7-22 34 -118 II D > out.txt
```

Obtaining seismic design data from the NEHRP-2020 documents at 34 Latitude, -118
Longitude, Risk Category III, and Site Class B formatted to JSON and piping the
JSON into Python's JSON validation tool:
```bash
$ python3 webspectra.py -o json nehrp-2020 34 -118 III B | python3 -m json.tool
```

### Spectrum Only Options
The `-s` or `--spectrum` CLI option allows users to obtain spectrum series data
where available by the web service.

For example, the two period design spectrum formatted as CSV {period, ordinate}
from the ASCE 7-22:
```bash
$ python3 webspectra.py asce7-22 -s two-design 34 -118 II D
```

In JSON,
```bash
$ python3 webspectra.py -o json asce7-22 -s two-design 34 -118 II D
```
