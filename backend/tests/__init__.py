"""
Backend test package.
Sets test environment markers to prevent tests from modifying or requiring production databases.
"""

import os

os.environ["TESTING"] = "1"
os.environ["ENVIRONMENT"] = "testing"
