#!/usr/bin/env python3
"""Exquis H723ZETx DevMode Expression Patch (core v4)

This is the minimal patch set aimed at enabling continuous expression in
Dev/Slave mode by removing MODE_MASK_u32 bit0 gates from:

  - pad_try_activate / pad_try_deactivate (so pads can be active)
  - pressure/pitchbend computations
  - CC74 emission
  - a few pressure housekeeping funcs

It does NOT touch the sensor ring commit logic or the main loop.

Usage:
  python3 patch_mpe_core.py IN.bin OUT.bin

It verifies bytes before patching and aborts on mismatch.

"""

from __future__ import annotations

import argparse
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

FLASH_BASE = 0x08000000


def off(addr: int) -> int:
    return addr - FLASH_BASE


def sha256_hex(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


@dataclass(frozen=True)
class Patch:
    addr: int
    expected: bytes
    repl: bytes
    desc: str


def apply_patches(buf: bytearray, patches: list[Patch]) -> None:
    for p in patches:
        o = off(p.addr)
        cur = bytes(buf[o:o+len(p.expected)])
        if cur == p.repl:
            print(f"[skip] {p.desc} @ 0x{p.addr:08X} already patched")
            continue
        if cur != p.expected:
            raise RuntimeError(
                f"byte mismatch @ 0x{p.addr:08X} (off 0x{o:X})\n"
                f"  expected: {p.expected.hex()}\n"
                f"  found:    {cur.hex()}\n"
                f"  repl:     {p.repl.hex()}\n"
                f"  desc:     {p.desc}"
            )
        buf[o:o+len(p.repl)] = p.repl
        print(f"[patch] 0x{p.addr:08X} : {p.expected.hex()} -> {p.repl.hex()}  ; {p.desc}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("infile", type=Path)
    ap.add_argument("outfile", type=Path)
    args = ap.parse_args()

    data = bytearray(args.infile.read_bytes())
    print(f"IN:  {args.infile} ({len(data)} bytes) sha256={sha256_hex(data)}")

    # Same NOP sequence used elsewhere: movs r0,#0 ; nop
    FORCE_FALSE = bytes.fromhex("00 20 00 BF")

    patches = [
        Patch(0x08025632, bytes.fromhex("DB F7 75 F9"), FORCE_FALSE,
              "pad_try_activate: ignore MODE_MASK bit0 (allow activation)"),
        Patch(0x0802568C, bytes.fromhex("DB F7 48 F9"), FORCE_FALSE,
              "pad_try_deactivate: ignore MODE_MASK bit0 (do not force deactivation)"),
        Patch(0x080257FC, bytes.fromhex("DB F7 90 F8"), FORCE_FALSE,
              "pad_pressure_max_update: ignore MODE_MASK bit0"),
        Patch(0x08025848, bytes.fromhex("DB F7 6A F8"), FORCE_FALSE,
              "pad_pressure_hist_update: ignore MODE_MASK bit0"),
        Patch(0x080259EC, bytes.fromhex("DA F7 98 FF"), FORCE_FALSE,
              "pad_pressure_cache_update: ignore MODE_MASK bit0"),
        Patch(0x08025CF0, bytes.fromhex("DA F7 16 FE"), FORCE_FALSE,
              "compute_pressure_0_127: ignore MODE_MASK bit0 (use sensors)"),
        Patch(0x08025E30, bytes.fromhex("DA F7 76 FD"), FORCE_FALSE,
              "mpe_compute_pitchbend_u14: ignore MODE_MASK bit0 (use sensors)"),
        Patch(0x08026A68, bytes.fromhex("D9 F7 5A FF"), FORCE_FALSE,
              "mpe_emit_cc74: ignore MODE_MASK bit0 (allow CC74)"),
    ]

    apply_patches(data, patches)

    args.outfile.write_bytes(data)
    print(f"OUT: {args.outfile} sha256={sha256_hex(data)}")

    patchlog = args.outfile.with_suffix(args.outfile.suffix + ".patch.txt")
    lines = ["Exquis DevExpr core v4 patch record", ""]
    for p in patches:
        lines.append(f"0x{p.addr:08X} (off 0x{off(p.addr):X}): {p.expected.hex()} -> {p.repl.hex()} ; {p.desc}")
    patchlog.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote patch record: {patchlog}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(2)
