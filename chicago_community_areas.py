import requests
import os
import zipfile
import StringIO
import glob
import shapefile
import tempfile
import json

def point_inside_polygon(x,y,poly):
    """Return True if the point described by x, y is inside of the polygon
    described by the list of points [(x0, y0), (x1, y1), ... (xn, yn)] in
    ``poly``

    Code from http://www.ariel.com.au/a/python-point-int-poly.html which
    in turn was adapted from C code found at
    http://local.wasp.uwa.edu.au/~pbourke/geometry/insidepoly/
    """
    n = len(poly)
    inside =False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside


def download_shapefiles():
    """Retrieve the community area shapefiles from the Chicago open data portal
    and unzip them to data/"""

    comm_area_url = ("https://data.cityofchicago.org/download/"
                    "9wp7-iasj/application/zip")
    try:
        os.mkdir("data")
    except OSError:
        #Directory alreay exists.  Continue
        pass

    # GET the zip file stored at ``comm_area_url`` and put it into an in-memory
    # buffer.  Extract the contents of the buffer to data/
    r = requests.get(comm_area_url)
    f = StringIO.StringIO()
    f.write(r.content)
    with zipfile.ZipFile(f, 'r') as zipf:
        zipf.extractall("data")


def get_community_area_coords():
    """Read in the shapefile downloaded from the Chicago open data portal.  This
    contains coordinates for the boundaries of Chicago's community areas.  Use
    gdaltransform to get these to latitude and longitude and return a dict,
    keyed off of neighborhood ID containing these coordinates."""

    shapefiles = list(glob.glob("data/*.shp"))
    if len(shapefiles) != 1:
        raise ValueError("There is more than one shapefile matching the"
                         "glob 'data/*.shp'")
    shapefile_name = shapefiles[0]

    sf = shapefile.Reader(shapefile_name)
    shapes = sf.shapes()
    recs   = sf.records()

    #Loop through community areas:
    results = {}
    for i, (shape, rec)  in enumerate(zip(shapes, recs)):
        _, temp_out_filename = tempfile.mkstemp()
        _, temp_in_filename = tempfile.mkstemp()

        with open(temp_out_filename, "w") as f:
            for coords in shape.points:
                f.write("%f %f\n"%(coords[0],coords[1]))

        #Use gdaltransform to convert StatePlane coordinates to lat and long:
        os.system("gdaltransform -s_srs '+proj=tmerc +lat_0=36.66666666666666 "
                  "+lon_0=-88.33333333333333 +k=0.9999749999999999 "
                  "+x_0=300000.0000000001 +y_0=0 +ellps=GRS80 "
                  "+towgs84=0,0,0,0,0,0,0 +units=us-ft +no_defs' "
                  " -t_srs epsg:4326 < "+temp_out_filename+" > "+
                  temp_in_filename)

        with open(temp_in_filename, "r") as f:
            coords = []
            for latlng in f:
                lat, lng, _ = latlng.split()
                coords.append((float(lat), float(lng)))
        results[rec[0]] = coords
    return results


def get_neighborhood_for_point(lat, lng, commareas):
    """Given a latitude and longitude, find the neighborhood that this point is
    inside.  The third argument to this function is the output from
    get_community_area_coords()"""

    for commarea, commdata in commareas.iteritems():
        if point_inside_polygon(lng, lat, commdata):
            return commarea
    else:
        return None


if __name__ == "__main__":

    # Retrieve the community area shapefile from the Chicago open data portal:
    download_shapefiles()

    # Build a dictionary, keyed off community area name, containing lat,lng
    # tuples:
    areas = get_community_area_coords()

    # Dump the results to a JSON file:
    json.dump(areas, open("community_areas.json", "w"), indent=2)
