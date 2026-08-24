#!/bin/bash
LOGTOSQL=true
HEALTHCHECK_API_URL=${HEALTHCHECK_API_URL:-http://localhost:5000}

cd "$(dirname "$0")";
./RPi_TempCheck_email.py T > ./Log/midnight-log 2>&1
retVal=$?

if [ "$LOGTOSQL" = true ] ; then
        logtext=$(cat ./Log/midnight-log)
        echo 'Logging to Pi Health Check MariaDB enabled'
        result=$(curl --silent -G --data-urlencode "code=TEMP" \
                         --data-urlencode "status=${retVal}" \
                         --data-urlencode "context=D" \
                         --data-urlencode "comment=${logtext}" \
                         --data-urlencode "hostname=$HOSTNAME" \
                         "$HEALTHCHECK_API_URL/insert/checklog")
                         echo "Log Result: $result"
fi

exit $retVal
