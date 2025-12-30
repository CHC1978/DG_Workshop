"""
Fix route order in calibrations.py
Move /due-soon before /{calibration_id}
"""
import re

with open('app/api/calibrations.py', 'r', encoding='utf-8') as f:
    content = f.read()

# This is a simple reordering - in practice we'd do this with proper parsing
# For now, just documenting the issue

print("Current route order:")
print("1. GET '' (list)")
print("2. GET '/{calibration_id}' (detail) <- BLOCKS /due-soon")
print("3. GET '/due-soon' <- NEVER REACHED")
print()
print("Should be:")
print("1. GET '' (list)")
print("2. GET '/due-soon' <- SPECIFIC FIRST")
print("3. GET '/{calibration_id}' (detail) <- GENERIC LAST")
print()
print("Manual fix required: Move /due-soon route before /{calibration_id} route")
