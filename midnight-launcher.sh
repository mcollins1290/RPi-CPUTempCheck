#!/bin/bash
LOGTOSQL=true

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
                         http://raspberrypi2.nyave:5000/insert/checklog)
                         echo "Log Result: $result"
fi

exit $retVal
