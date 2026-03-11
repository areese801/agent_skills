# Unit Converter Skill

**Version:** 1.0.0  
**Author:** Grok Example (inspired by Claude Agent Skill best practices)  
**Description:** A simple, self-contained skill that lets agents convert values between units of length, weight, and temperature.

## Purpose
This skill serves as a **model** for how to structure any agent skill. It demonstrates:
- Clean YAML metadata
- Progressive disclosure (only load REFERENCE.md or FORMS.md when needed)
- Script execution via the agent's bash tool
- Resource file usage
- Form-based input collection
- Real examples and references

## How to Use This Skill
1. Place the entire `unit-converter` folder in your agent's skill directory (e.g., `.claude/skills/`).
2. The agent will automatically discover it via the `name` and `description` in SKILL.md.
3. Trigger example: "Convert 5 meters to feet" or "What's 32°F in Celsius?"

## Why This Is a Good Example
- **Simple**: Only ~100 lines total across all files.
- **Complete**: Uses every recommended component.
- **Extensible**: Easy to add more units or scripts later.
- **Best Practices Followed**: Concise instructions, explicit script calls, error handling, and clear boundaries.

Copy and modify this structure for your own skills!