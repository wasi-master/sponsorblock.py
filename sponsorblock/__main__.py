"""CLI for sponsorblock"""

import sys
from datetime import timedelta
from typing import Dict, Tuple
import sponsorblock

try:
    import rich
    from rich.text import Text

    RICH_INSTALLED = True
except ImportError:
    print("Consider installing rich for better output with colors and stuff")
    RICH_INSTALLED = False


def run():
    try:
        video_id = sys.argv[1]
    except IndexError:
        print("No video was passed")
        sys.exit(1)

    client = sponsorblock.Client()
    COLORS: Dict[str, Tuple[str, str]] = {
        "sponsor": ("Sponsor", "green"),
        "selfpromo": ("Unpaid/Self Promotion", "yellow"),
        "interaction": ("Interaction Reminder", "magenta1"),
        "intro": ("Intermission/Intro Animation", "cyan"),
        "outro": ("Endcards/Credits", "blue"),
        "preview": ("Preview/Recap", "light_sky_blue1"),
        "music_offtopic": ("Music: Non-Music Section", "orange1"),
        "poi_highlight": ("Point of Interest", "red"),
        "filler": ("Filler", "purple3"),
        "preview": ("Preview/Recap", "sky_blue3"),
    }

    segments = client.get_skip_segments(video_id)

    for num, segment in enumerate(sorted(segments, key=lambda s: s.start)):
        name, color = COLORS[segment.category]
        if RICH_INSTALLED:
            rich.print(
                Text(
                    f"Segment #{num} ({name}):\n"
                    f"\tStart: {str(timedelta(seconds=int(segment.start)))}\n"
                    f"\tEnd: {str(timedelta(seconds=int(segment.end)))}",
                    style=color,
                )
            )
        else:
            print(
                f"Segment #{num} ({name}):\n"
                f"\tStart: {str(timedelta(seconds=int(segment.start)))}\n"
                f"\tEnd: {str(timedelta(seconds=int(segment.end)))}"
            )


if __name__ == "__main__":
    run()
