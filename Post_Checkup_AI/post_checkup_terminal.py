"""Try the post-checkup AI in the terminal: python post_checkup_terminal.py [visit_id]"""

import sys
from dotenv import load_dotenv

from Post_Checkup_AI import PostCheckUpAI, SAMPLE_NOTES


def main():
    load_dotenv()
    visit_id = sys.argv[1] if len(sys.argv) > 1 else "V001"
    note = SAMPLE_NOTES.get(visit_id)
    if note is None:
        sys.exit(f"Unknown Visit id: {', '.join(SAMPLE_NOTES)}")
    print(PostCheckUpAI(note).build_report().to_text())


if __name__ == "__main__":
    main()