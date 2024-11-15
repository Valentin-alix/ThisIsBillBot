import os
import pstats
from pathlib import Path

if __name__ == "__main__":
    path_profile = os.path.join(
        Path(__file__).parent.parent.parent, "resources", "profile.prof"
    )
    profile_stat = pstats.Stats(path_profile)
    profile_stat.sort_stats(pstats.SortKey.CUMULATIVE)
    profile_stat.print_stats("gui", 50)
