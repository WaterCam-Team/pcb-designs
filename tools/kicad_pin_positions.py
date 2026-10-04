"""Absolute schematic coordinates of every symbol pin in a KiCad schematic.

KiCad stores pins relative to each library symbol; this applies each placed
symbol's position, rotation and mirroring to get sheet coordinates (mm), which
is what you need to check a wire really lands on a pin.

    python tools/kicad_pin_positions.py WaterCam_mDot_WittyPi_AHT_BNO_Lepton.kicad_sch J2 Q1

Validated against the WaterCam v6 schematic on 2026-09-09: J2.18 at
(121.92, 128.27) and J2.15 at (134.62, 125.73) match eeschema.
"""
import argparse
import re


def pin_positions(s):
    """{(reference, pin number): (x, y)} for schematic text `s`."""
    def top_blocks(txt,head):
        out=[];i=0
        while True:
            j=txt.find(head,i)
            if j<0: break
            d=0;k=j
            while True:
                if txt[k]=='(':d+=1
                elif txt[k]==')':
                    d-=1
                    if d==0:break
                k+=1
            out.append(txt[j:k+1]);i=k+1
        return out
    libsec=top_blocks(s,'\t(lib_symbols')[0]
    libpins={}
    for blk in top_blocks(libsec,'\t\t(symbol "'):
        name=re.match(r'\t\t\(symbol "([^"]+)"',blk).group(1)
        ps=re.findall(r'\(pin \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+) ([\d.]+)\)(?:(?!\(pin ).)*?\(number "([^"]+)"',blk,re.S)
        if ps: libpins.setdefault(name,[]).extend([(p[3],float(p[0]),float(p[1])) for p in ps])
    # merge unit sub-symbols into their parent lib name
    merged={}
    for k,v in libpins.items():
        base=k.rsplit('_',2)[0] if re.search(r'_\d+_\d+$',k) else k
        merged.setdefault(base,[]).extend(v)
    def place(lx,ly,rot,mx,my):
        if rot==0:   X,Y= lx, ly
        elif rot==90:X,Y=-ly, lx
        elif rot==180:X,Y=-lx,-ly
        else:        X,Y= ly,-lx
        if my: X=-X
        if mx: Y=-Y
        return X,Y
    out={}
    for blk in top_blocks(s,'\t(symbol\n'):
        lib=re.search(r'\(lib_id "([^"]+)"\)',blk)
        at=re.search(r'\(at ([-\d.]+) ([-\d.]+) ([\d.]+)\)',blk)
        ref=re.search(r'\(property "Reference" "([^"]+)"',blk)
        if not(lib and at and ref): continue
        px,py,rot=float(at.group(1)),float(at.group(2)),int(float(at.group(3)))
        my='(mirror y)' in blk; mx='(mirror x)' in blk
        for num,lx,ly in merged.get(lib.group(1),[]):
            X,Y=place(lx,ly,rot,mx,my)
            out[(ref.group(1),num)]=(round(px+X,4),round(py-Y,4))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("schematic", help="path to a .kicad_sch file")
    ap.add_argument("refs", nargs="*", help="references to print (default: all)")
    a = ap.parse_args()
    with open(a.schematic, encoding="utf-8") as f:
        pins = pin_positions(f.read())
    for (ref, num), (x, y) in sorted(pins.items()):
        if not a.refs or ref in a.refs:
            print(f"{ref}.{num}\t{x}\t{y}")


if __name__ == "__main__":
    main()
