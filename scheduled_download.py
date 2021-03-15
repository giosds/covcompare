#!/usr/bin/python3.6

"""
Script used by a scheduler at the end of the day
"""

import os
from tasks import scheduled_reset_operations


# Set cwd to project directory
try:
    os.chdir("cov_compare")
except:
    pass
finally:
    scheduled_reset_operations()
