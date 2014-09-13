# Chicago Neighborhood Lookup from Latitude & Longitude

This code demonstrates how to take the shapefile provided on the City of Chicago Open Data Portal and converts it to a JSON file, with top-level keys named for each neighborhood, and associated values that give the latitude and longitude pairs corresponding to the neighborhood's boundaries.  For example:

```
{
  "Edgewater": [
    [
      -87.6472903440513,
      41.9777476245164
    ],
    [
      -87.6488601283915,
      41.9770421499064
    ],
    [
      -87.6489575350607,
      41.9770421499062
    ],
    ...
  ],
  "Uptown": [
    [
      -87.6739766577115,
      41.9615254357625
    ],
    [
      -87.6739804054091,
      41.9616379544119
    ],
    ...
  ]
}
```

## Usage

Running the script ``chicago_community_areas.py`` will fetch down the shapefiles from the web and put them in the ``data/`` subdirectory, and then parse out these shapefiles to a JSON blob, which is put in the current working directory with the name ``community_areas.json``.

Running ``test_chicago_community_areas.py`` will download the shapefiles if they do not already exist, and then test for a few sample coordinates that the correct neighborhoods are identified.

## Installation

Install the Python requirements for this code with pip

    pip install -r requirements.txt

In order to convert the StatePlane coordinates to latitudes and longitudes, the code relies on gdal.  This needs to be installed.  On Debian flavors of Linux:

    sudo apt-get install gdal-bin

On Mac OSX using Homebrew:

    brew install gdal
