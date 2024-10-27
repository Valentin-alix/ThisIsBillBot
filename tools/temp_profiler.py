import pstats

p = pstats.Stats("tools/d3mapping_profiled")
p.strip_dirs().sort_stats(pstats.SortKey.CUMULATIVE).print_stats(100)
