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
