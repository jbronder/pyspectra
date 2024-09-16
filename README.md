# pyspectra: A CLI for Seismic Design & Analysis Values
A command line application written for a terminal-savvy structural engineer.


## Tools and Technologies
- [Python Standard Libraries](https://python.org)


## About
This application is a CLI alternative to the [browser-based
application](https://ascehazardtool.org/) for retrieving seismic design and
analysis information. The motivation behind building it was picking up more CLI
development in Python with the `argparse` library.


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
By default data prints to the terminal, obtaining seismic design data from the
ASCE 7-22 Standard at 34 Latitude, -118 Longitude, Risk Category II, and Site
Class D:
```bash
$ python3 webspectra.py asce7-22 34 -118 II D

# write output to out.txt file
$ python3 webspectra.py asce7-16 34 -118 II A > out.txt
```

Obtaining seismic design data from the NEHRP-2020 documents at 34 Latitude, -118
Longitude, Risk Category III, and Site Class B formatted to JSON and piping the
JSON into Python's JSON validation tool:
```bash
$ python3 webspectra.py -o json nehrp-2020 34 -118 III B | python3 -m json.tool
```
