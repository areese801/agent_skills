#!/usr/bin/env python3
import json
import argparse
import sys

def load_factors():
    with open("resources/conversion_factors.json") as f:
        return json.load(f)

def convert(value, from_unit, to_unit):
    factors = load_factors()
    
    # Temperature (special handling)
    if from_unit in ["C", "F", "K"] or to_unit in ["C", "F", "K"]:
        if from_unit == "C" and to_unit == "F":
            return value * 9/5 + 32
        elif from_unit == "F" and to_unit == "C":
            return (value - 32) * 5/9
        elif from_unit == "C" and to_unit == "K":
            return value + 273.15
        elif from_unit == "K" and to_unit == "C":
            return value - 273.15
        else:
            raise ValueError("Unsupported temperature conversion")
    
    # Length or weight (multiplicative)
    for category in ["length", "weight"]:
        if from_unit in factors[category] and to_unit in factors[category]:
            return value * (factors[category][to_unit] / factors[category][from_unit])
    
    raise ValueError(f"Unsupported conversion: {from_unit} → {to_unit}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--value", type=float, required=True)
    parser.add_argument("--from_unit", required=True)
    parser.add_argument("--to_unit", required=True)
    args = parser.parse_args()
    
    try:
        result = convert(args.value, args.from_unit, args.to_unit)
        print(result)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)