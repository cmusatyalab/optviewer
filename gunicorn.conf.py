# gunicorn config file
bind = '127.0.0.1:8024'
workers = 4
pidfile = 'gunicorn.pid'
proc_name = 'optviewer'
