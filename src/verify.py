#!/usr/bin/env python3
"""Independent reference checker. No solver imports, FFT, floats in scoring."""
import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


def parse_sequence(value):
    if isinstance(value, str):
        value = "".join(value.split())
        if not value:
            raise ValueError("empty sequence")
        if set(value) <= {"0", "1"}:
            return [1 if c == "1" else -1 for c in value]
        if set(value) <= {"+", "-"}:
            return [1 if c == "+" else -1 for c in value]
        raise ValueError("string must contain only 01 or +-")
    if not isinstance(value, list) or not value:
        raise ValueError("sequence must be a nonempty string or list")
    if any(type(x) is not int or x not in (-1, 1) for x in value):
        raise ValueError("list entries must be integer +1/-1 (not bool or float)")
    return value[:]


def orbit(sequence):
    s = tuple(sequence)
    return {
        tuple(sign * x * (-1 if alt and i % 2 else 1)
              for i, x in enumerate(v))
        for v in (s, s[::-1]) for sign in (-1, 1) for alt in (False, True)
    }


def canonical(sequence):
    return min("".join("1" if x == 1 else "0" for x in s)
               for s in orbit(sequence))


def score(sequence):
    s = parse_sequence(sequence)
    n = len(s)
    c = [sum(s[i] * s[i + k] for i in range(n - k))
         for k in range(1, n)]
    e = sum(x * x for x in c)
    f = Fraction(n * n, 2 * e) if e else None
    key = canonical(s)
    return dict(N=n, autocorrelations=c, E=e,
                F_exact=str(f) if f is not None else "infinity",
                F_decimal=float(f) if f is not None else None,
                PSL=max(map(abs, c), default=0), canonical=key,
                canonical_sha256=hashlib.sha256(key.encode()).hexdigest())


def verify_object(obj):
    if not isinstance(obj, dict) or "sequence" not in obj:
        raise ValueError("certificate requires a sequence")
    result = score(obj["sequence"])
    for key in ("N", "E", "PSL"):
        if key in obj and type(obj[key]) is not int:
            raise ValueError(f"{key} must be an integer")
    if "autocorrelations" in obj and (
        not isinstance(obj["autocorrelations"], list)
        or any(type(x) is not int for x in obj["autocorrelations"])
    ):
        raise ValueError("autocorrelations must be an integer list")
    for key in ("N", "E", "PSL", "F_exact", "canonical", "canonical_sha256",
                "autocorrelations"):
        if key in obj and obj[key] != result[key]:
            raise ValueError(f"{key}: claimed {obj[key]!r}, computed {result[key]!r}")
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--sequence")
    g.add_argument("--file", type=Path)
    a = p.parse_args()
    try:
        result = (verify_object(json.loads(a.file.read_text())) if a.file
                  else score(a.sequence))
    except (ValueError, TypeError) as e:
        p.exit(1, f"REJECT: {e}\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
