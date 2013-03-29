#! /bin/sh
if python -c 'import sys as _sys; _sys.exit(_sys.version_info[0] != 2)'; then
    # Python 2
    if python -c 'import sys as _sys; _sys.exit(_sys.version_info[1] != 6)'; then
        # Python 2.6
        pip install ordereddict unittest2
    fi
fi