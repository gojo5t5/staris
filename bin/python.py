import re
import os

content = """ Performance counter stats for 'system wide' (3 runs):

             24.27 Joules power/energy-cores/                                           ( +-  0.13% )
              3.62 Joules power/energy-ram/                                             ( +-  0.68% )
              0.00 Joules power/energy-gpu/                                           
             33.40 Joules power/energy-pkg/                                             ( +-  0.06% )

          1.018840 +- 0.000305 seconds time elapsed  ( +-  0.03% )
"""
# match = re.search(r'\d+\.\d+ +- [\d\.]+ seconds time elapsed', content)
match = re.search(r'\d+\.\d+ \+\-', content)
print(match)
