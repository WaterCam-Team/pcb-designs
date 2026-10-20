"""Pull straight-line geometry out of a vector PDF drawing.

Used to read a breakout board's header pinout off a vendor schematic PDF when
the drawing is vector art rather than text. Reads uncompressed content
streams, applies each drawing block's `a 0 0 d tx ty cm` scale-and-translate,
and collects every move/line segment in PDF points. Compressed (FlateDecode)
streams are skipped; decompress the PDF first, e.g. `qpdf --qdf in.pdf out.pdf`.

    python tools/pdf_vector_extract.py drawing-qdf.pdf --out segs.pkl
"""
import argparse
import pickle
import re


def extract_segments(pdf_bytes):
    """[((x1, y1), (x2, y2)), ...] for every line segment, zero-length ones dropped."""
    d = pdf_bytes.decode("latin1")
    segs = []
    for s in re.findall(r"stream\n(.*?)\nendstream", d, re.S):
        if " cm" not in s:
            continue
        # each drawing block: q <a> 0 0 <d> <tx> <ty> cm ... m ... l ... S Q
        for blk in re.finditer(r"q\s+([-\d.]+) 0 0 ([-\d.]+) ([-\d.]+) ([-\d.]+) cm(.*?)Q", s, re.S):
            a, dd, tx, ty = map(float, blk.group(1, 2, 3, 4))
            cur = None
            for X, Y, op in re.findall(r"([-\d.]+)\s+([-\d.]+)\s+([ml])", blk.group(5)):
                x, y = a * float(X) + tx, dd * float(Y) + ty
                if op == "m":
                    cur = (x, y)
                else:
                    if cur is not None:
                        segs.append((cur, (x, y)))
                    cur = (x, y)
    return [t for t in segs
            if abs(t[0][0] - t[1][0]) > 0.05 or abs(t[0][1] - t[1][1]) > 0.05]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pdf", help="uncompressed PDF (see qpdf --qdf)")
    ap.add_argument("--out", help="pickle the segment list to this file")
    a = ap.parse_args()
    with open(a.pdf, "rb") as f:
        segs = extract_segments(f.read())
    print("total segments:", len(segs))
    if segs:
        xs = [p[0] for t in segs for p in t]
        ys = [p[1] for t in segs for p in t]
        print(f"bbox x {min(xs):.1f}..{max(xs):.1f} y {min(ys):.1f}..{max(ys):.1f}")
    if a.out:
        with open(a.out, "wb") as f:
            pickle.dump(segs, f)


if __name__ == "__main__":
    main()
