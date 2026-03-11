---
name: unit-converter
description: Converts values between units of measurement (length, weight, temperature). Use when the user asks to convert meters to feet, kg to lbs, Celsius to Fahrenheit, etc.
version: 1.0.0
author: Brian Henson
---

## When to Use This Skill
- Use for any unit conversion request involving length, weight, or temperature.
- Do NOT use for currency, time zones, or complex scientific units.

## Quick Start
1. Collect input values using the guidance in FORMS.md.
2. Verify unit inputs are correct by checking REFERENCE.md.
3. Run the conversion script (see below).
4. Return the result in a friendly sentence.

## How to Perform a Conversion
Run this exact command (the agent has access to the filesystem):

```bash
python scripts/convert_units.py --value VALUE --from_unit FROM --to_unit TO