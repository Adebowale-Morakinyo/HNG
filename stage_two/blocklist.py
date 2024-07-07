"""
blacklist.py

This file just contains the blacklist of the JWT tokens. It will be imported by
project and the logout resource so that tokens can be added to the blacklist when the
user logs out.
"""

BLOCKLIST = set()
