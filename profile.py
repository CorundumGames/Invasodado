import cProfile
import pstats
import __init__

cProfile.run('__init__.main()', 'profile.out')
p = pstats.Stats('profile.out')
p.sort_stats('cumtime')
p.print_stats()