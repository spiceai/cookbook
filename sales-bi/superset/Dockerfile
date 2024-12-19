FROM apache/superset:4.0.2
# Switching to root to install the required packages
USER root

# Create a new superset command with a patch to ignore pyarrow version conflicts
# This is a workaround for the pyarrow version conflict issue: https://github.com/apache/superset/issues/31475
RUN echo '#!/usr/local/bin/python3\n\
import pkg_resources\n\
\n\
def patched_require(self, *requirements):\n\
    try:\n\
        return original_require(self, *requirements)\n\
    except pkg_resources.VersionConflict as e:\n\
        if "pyarrow" in str(e):\n\
            return []\n\
        raise\n\
\n\
original_require = pkg_resources.WorkingSet.require\n\
pkg_resources.WorkingSet.require = patched_require\n\
\n\
import sys\n\
from superset.cli.main import superset\n\
\n\
if __name__ == "__main__":\n\
    sys.exit(superset())' > /usr/local/bin/superset

# Make it executable
RUN chmod +x /usr/local/bin/superset

# https://github.com/influxdata/flightsql-dbapi
RUN pip install flightsql-dbapi
RUN pip install --upgrade pyarrow
# Switching back to using the `superset` user
USER superset