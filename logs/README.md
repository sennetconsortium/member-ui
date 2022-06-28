# API Logging

All the API logging is forwarded to the uWSGI server and gets written into the log file `uwsgi-member-ui.log`. 

## Log rotation

On the host system, the log rotation is handled via `logrotate` utility with a daily logging rotation schedule. The configuration file is located at `/etc/logrotate.d/`.