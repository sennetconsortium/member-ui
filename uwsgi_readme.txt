I needed to do several things.
tear down existing venv

installed the python venv as ec2-user
upgraded pip
installed Flask and Requirements using pip
install uwsgi with pip

testing
I then created a test.py application and ran it to verify the lemp stack was working properly and that I was able to work.
Important note
when creating the sennet-member-ui.uwsgi.service it required changing the execstart from the system bin folder to the venv pip installed uwsgi
ExecStart=/opt/sennet/member-ui/venv-member-ui/bin/uwsgi --ini /opt/sennet/member-ui/uwsgi.ini H /opt/sennet/member-ui/venv-member-ui/

for some reason in the nginx and uwsgi config I couldn't make localhost:5000 work nor could I use 127.0.0.1
those config files, some of them I updated using 0.0.0.0:5000 and when I did that a lot started to work
