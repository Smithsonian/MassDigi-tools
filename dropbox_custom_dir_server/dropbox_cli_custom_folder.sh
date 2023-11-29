#!/bin/bash
# Install headless dropbox
#  and set home to a location other
#  than the default in the home folder.
#  Useful when the home doesn't have enough
#  space.


# From https://superuser.com/a/1265649

# Install using:
#   HOME=/mnt/[DISK]/Dropbox dropbox.py start -i

# Run using:

HOME=/mnt/[DISK]/Dropbox /mnt/[DISK]/Dropbox/.dropbox-dist/dropboxd

# From https://superuser.com/a/1222247
# Add to the home dropbox.py file:
os.environ["HOME"] = "/mnt/[DISK]/Dropbox"
