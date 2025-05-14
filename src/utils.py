"""
utils.py - Utility functions for Tagify.
"""

import webbrowser

def open_link(url):
    """
    Open the given URL in the default web browser.
    """
    webbrowser.open(url)

def get_link_data(share_link):
    """
    Parse the Spotify share link and return relevant data.
    """
    # First, remove any query parameters
    share_link = share_link.split('?')[0]

    # Next, split the URL into parts
    parts = share_link.split('/')

    # Check for the presence of "track", "album", "artist", or "playlist"
    for i, part in enumerate(parts):
        if part in ["track", "album", "artist", "playlist"]:
            # Check if the next part of the URL is available
            if i + 1 < len(parts):
                return (part, parts[i + 1])

    # If no match is found, return None
    return None