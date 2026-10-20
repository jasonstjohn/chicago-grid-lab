#!/usr/bin/env python3
"""
Download Chicago's Street Center Lines as GeoJSON into data/streets.geojson,
so the GitHub Pages site serves its own copy instead of hitting the city
portal on every visit.

Usage (from the repo root, standard library only):
    python tools/fetch_streets.py            # full precision
    python tools/fetch_streets.py --round 6  # round coordinates to ~10 cm, smaller file

GitHub rejects files over 100 MB; rounding usually brings this well under.
"""
import argparse
import json
import pathlib
import urllib.request

URL = "https://data.cityofchicago.org/resource/pr57-gg9e.geojson?$limit=200000"


def rnd(coords, nd):
    if isinstance(coords[0], (int, float)):
        return [round(c, nd) for c in coords]
    return [rnd(c, nd) for c in coords]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=URL)
    ap.add_argument("--round", type=int, default=None, help="decimal places for lon/lat")
    ap.add_argument("--out", default="data/streets.geojson")
    a = ap.parse_args()

    print(f"Downloading {a.url} ...")
    with urllib.request.urlopen(a.url) as r:
        gj = json.load(r)
    feats = gj.get("features", [])
    print(f"{len(feats):,} features; fields: {sorted((feats[0].get('properties') or {}).keys()) if feats else []}")
    if a.round is not None:
        for f in feats:
            if f.get("geometry"):
                f["geometry"]["coordinates"] = rnd(f["geometry"]["coordinates"], a.round)
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(gj, separators=(",", ":")))
    print(f"Wrote {out} ({out.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
