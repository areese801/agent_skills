
---

### FORMS.md
```markdown
# Input Collection (Forms Guidance)

When the user requests a conversion but is missing information, ask ONE clear question at a time:

1. **Value**: "What number would you like to convert?"
2. **From unit**: "What unit is that in? (e.g., m, kg, C)"
3. **To unit**: "What unit do you want to convert to? (e.g., ft, lb, F)"

Only proceed to run the script once you have all three pieces.

**Validation rules** (tell the user if invalid):
- Value must be a number.
- Units must be in the supported list (see REFERENCE.md).
- Do not convert between different categories (length ↔ weight).

After running the script, respond naturally, e.g.:
"5 meters is approximately 16.40 feet."