#!/usr/bin/env python3
"""
Convert the portal's Street Center Lines shapefile export (EPSG:4326, e.g.
transportation_20261011/geo_export_*.shp) into the compact GeoJSON the site
loads, data/streets.geojson. Standard library only.

Keeps only the fields the page uses and rounds lon/lat to 6 decimals (~10 cm).

    python3 tools/shp_to_geojson.py ../transportation_20261011/geo_export_*.shp
"""
import json, pathlib, struct, sys

KEEP = ["street_nam", "street_typ", "pre_dir", "class", "status", "ewns"]
ND = 6


def read_dbf(path, keep):
    with open(path, "rb") as f:
        n, hlen, rlen = struct.unpack("<IHH", f.read(12)[4:12])
        f.seek(32)
        fields, off = [], 1
        while True:
            d = f.read(32)
            if d[0] == 0x0D:
                break
            name = d[:11].split(b"\0")[0].decode().lower()
            fields.append((name, chr(d[11]), off, d[16]))
            off += d[16]
        want = [x for x in fields if x[0] in keep]
        f.seek(hlen)
        for _ in range(n):
            rec = f.read(rlen)
            row = {}
            for name, typ, o, L in want:
                v = rec[o:o + L].replace(b"\0", b"").decode("latin1").strip()
                if typ in "NF":
                    try:
                        x = float(v)
                        v = int(x) if x == int(x) else x
                    except ValueError:
                        v = None
                row[name] = v if v != "" else None
            yield row


def read_shp(path):
    with open(path, "rb") as f:
        f.seek(100)
        while True:
            h = f.read(8)
            if len(h) < 8:
                break
            clen = struct.unpack(">i", h[4:])[0] * 2
            c = f.read(clen)
            t = struct.unpack("<i", c[:4])[0]
            if t not in (3, 13, 23):
                yield []
                continue
            np_, npt = struct.unpack("<ii", c[36:44])
            parts = list(struct.unpack(f"<{np_}i", c[44:44 + 4 * np_])) + [npt]
            base = 44 + 4 * np_
            pts = struct.unpack(f"<{2 * npt}d", c[base:base + 16 * npt])
            yield [[[round(pts[2 * k], ND), round(pts[2 * k + 1], ND)] for k in range(parts[i], parts[i + 1])]
                   for i in range(np_)]


def main():
    shp = pathlib.Path(sys.argv[1])
    out = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else pathlib.Path(__file__).resolve().parent.parent / "data/streets.geojson")
    feats = []
    for parts, props in zip(read_shp(shp), read_dbf(shp.with_suffix(".dbf"), KEEP)):
        parts = [p for p in parts if len(p) >= 2]
        if not parts:
            continue
        geom = {"type": "LineString", "coordinates": parts[0]} if len(parts) == 1 else {"type": "MultiLineString", "coordinates": parts}
        feats.append({"type": "Feature", "properties": props, "geometry": geom})
    out.parent.mkdir(parents=True, exist_ok=True)
    gj = {"type": "FeatureCollection", "name": "Street Center Lines (City of Chicago)", "features": feats}
    out.write_text(json.dumps(gj, separators=(",", ":")))
    print(f"{len(feats):,} features -> {out} ({out.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
