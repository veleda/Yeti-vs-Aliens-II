#!/usr/bin/env python

import cProfile
import pstats

cProfile.run("main()", "mainprof")
p = pstats.Stats("mainprof")
p.sort_stats('time').print_stats(10)
