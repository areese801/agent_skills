# Example Interaction

**User**: Convert 100 kilometers to miles.

**Agent** (follows FORMS.md):
- What number would you like to convert? → 100
- What unit is that in? → km
- What unit do you want to convert to? → mi

**Agent runs**:
```bash
python scripts/convert_units.py --value 100 --from_unit km --to_unit mi