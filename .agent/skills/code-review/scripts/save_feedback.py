import argparse
from datetime import datetime
from pathlib import Path


def save_commit_feedback_artifact(reviewed_module_name: str, feedback: str) -> str:
    """
    Save the feedback artifact to a file.

    Args:
        reviewed_module_name: Path to the reviewed module. Should be relative to the project root.
        feedback: The feedback to save.

    Returns:
        The path to the saved feedback artifact.

    Example:
        >>> save_commit_feedback_artifact("src/services/embedding_service", "This is the feedback.")
        >>> python ~/.claude/skills/code-review/scripts/save_feedback.py --reviewed_module_name "src/services/embedding_service" --feedback "This is the feedback."
    """
    date_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    project_root = Path.cwd()
    feedback_path = (
        project_root
        / ".agent"
        / "artifacts"
        / reviewed_module_name
        / "code-review"
        / date_str
        / "feedback.md"
    )
    feedback_path.parent.mkdir(parents=True, exist_ok=True)

    with open(feedback_path, "w") as f:
        f.write(feedback)

    return str(feedback_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviewed_module_name", type=str, required=True)
    parser.add_argument("--feedback", type=str, required=True)
    args = parser.parse_args()
    save_commit_feedback_artifact(args.reviewed_module_name, args.feedback)
