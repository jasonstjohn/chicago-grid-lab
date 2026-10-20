# Chicago Grid Lab

An interactive page for asking questions about Chicago's street grid, part of the
Chicago GIS Games project. It computes the same measures as
`chicago_streets_stats.py`, live in the browser:

- orientation entropy and grid order φ (Boeing 2019), plus the share of street
  length within 2° of north, south, east and west
- an orientation rose and a segment-length histogram
- intersection topology: dead ends, T-junctions, 4-way intersections, mean degree
- straightness index, total length, longest streets
- every separate piece of a street ("show the other parts of Ancona")
- the shortest streets, shortest first: 20 at a time, up to all ~1,240 ordinary
  streets, using the same pool and end-to-end measure as the Python shortest list

By default it shows the whole grid. You can narrow it to individual streets
(type a name; the dropdown lists every street containing what you've typed),
to notable lists (old trail diagonals, mile-line streets, expressways, most
crooked, most broken up…), to a dragged-out area, or to street classes, and pin
one view to compare against another.

## Data

The page loads one file, `data/streets.geojson`: all 56,336 Street Center Lines
segments (City of Chicago, last updated 2016), 19 MB, about 3 MB as GitHub Pages
serves it gzipped. There is no other data source; if the file is missing the
page says so.

Rebuild it from the portal's shapefile export with

    python3 tools/shp_to_geojson.py ../transportation_20261011/geo_export_*.shp

(standard library only; keeps street_nam, street_typ, pre_dir, class, status, ewns).
`tools/fetch_streets.py` is an alternative that downloads the same table from the
portal's SODA API.

To try it locally, serve the folder (browsers won't fetch files from a `file://`
page): `python3 -m http.server 8000`, then open http://localhost:8000.

## Hosting on GitHub Pages

1. Create a repository and push this folder (`index.html` at the root).
2. Settings → Pages → Build and deployment → Deploy from a branch → `main` / root.
3. The site appears at `https://<user>.github.io/<repo>/`.

`.nojekyll` stops GitHub from running Jekyll over the files.

## Notes

- Coordinates are projected to feet around State & Madison, the zero point of
  the address grid, so the map readout shows approximate addresses
  (800 house numbers per mile).
- Nodes are segment endpoints snapped to 1 ft. Selecting an area cuts segments
  at its edge, which adds dead ends.
- Street identity follows the project rule: `STREET_NAM` alone (type and
  N/S/E/W prefix may change along a street), except Pl, which stays separate.
- Default filter, as in `chicago_streets_stats.py`: CLASS 2, 3, 4, 5, 7 with
  STATUS N (surface public streets). Class and status chips change it.
- Pieces of a street: segments whose endpoints come within 250 ft of each other
  are joined (same tolerance as `--gap-ft`).
- Bearings use true north (the data is lon/lat). The Python script works in
  EPSG:3435, whose grid north is rotated from true north, so its "within 2° of
  N/S/E/W" share comes out lower (79.8% vs 85.5% here); entropy and φ agree.
- If this folder lives inside the ChicagoStreetGridFun repo, its `.gitignore`
  line `data/` also ignores `chicago-grid-lab/data/`. Change it to `/data/`.
