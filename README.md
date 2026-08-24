# RPi-CPUTempCheck
A Python script which can be run by CRON to check the CPU temp and send an email if it meets or exceeds a certain temp threshold (provided as an argument during script execution).

The launcher scripts send results to the local Pi Health Check API by default.
Set `HEALTHCHECK_API_URL` to override the API host for a remote deployment, for
example `http://raspberrypi2.totten:5000`.
