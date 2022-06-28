# SenNet Member Registration and Profile Portal

This repo contains code that handles the SenNet member registration and profile management. It's built on top of Python Flask micro-framework and has a tight-coupling with Wordpress. And the following Wordpress plugins are required:

- [Code Snippets](https://wordpress.org/plugins/code-snippets/)
- [Members – Membership & User Role Editor Plugin](https://wordpress.org/plugins/members/)
- [OpenID Connect Generic Client](https://wordpress.org/plugins/daggerhart-openid-connect-generic/)
- [Connections](https://connections-pro.com/)
- [Admin Bar & Dashboard Control](https://wordpress.org/plugins/admin-bar-dashboard-control/)


## Install dependencies

Create a new Python 3.x virtual environment:

````
python3 -m venv venv-member-ui
source venv-member-ui/bin/activate
````

Upgrade pip:
````
python3 -m pip install --upgrade pip
````

Then install the dependencies:

````
pip install -r requirements.txt
````

## Configuration

The confiuration file `app.cfg` is located under `instance` folder. You can read more about [Flask Instance Folders](http://flask.pocoo.org/docs/1.0/config/#instance-folders). 

There's an example configuration file `instance/app.cfg.example` for your quick start.

## Start the server

Either methods below will run the search-api web service at `http://localhost:5005`. Choose one:

### Directly via Python

````
python3 app.py
````

### With the Flask Development Server

````
cd src
export FLASK_APP=app.py
export FLASK_ENV=development
python3 -m flask run -p 5005
````

## Deployment

For deployment on remote VM, we'll use Nignx as a reverse proxy to forward the requests to uWSGI server. 

First copy the `nginx/conf.d/member-ui.conf` to `/etc/nginx/conf.d` and edit the configurations with domain and SSL certificate based on the deployment. For example:

```
server {
    listen 80;
    server_name profile.dev.sennetconsortium.org;
    
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name profile.dev.sennetconsortium.org;   
    root /usr/share/nginx/html;

    access_log /var/log/nginx/nginx_access_sennet_member-ui.log;
    error_log /var/log/nginx/nginx_error_sennet_member-ui.log warn;

    ssl_certificate /etc/letsencrypt/live/dev.sennetconsortium.org/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/dev.sennetconsortium.org/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

    # HTTP requests get passed to the uwsgi server using the "uwsgi" protocol on port 5003
    location / { 
        include uwsgi_params;
        uwsgi_pass uwsgi://127.0.0.1:5003;
    }
    
}
```

For quick testing:
```
uwsgi --ini /opt/sennet/member-ui/uwsgi.ini -H /opt/sennet/member-ui/venv-member-ui/
```

Once everything in place, we can copy the `sennet-member-ui.uwsgi.service` file to `/etc/systemd/system` and create a service. 

To enable the service with system reboot:

```
systemctl enable sennet-member-ui.uwsgi.service
```

### Start and Stop service

```
systemctl start sennet-member-ui.uwsgi.service
```

```
systemctl stop sennet-member-ui.uwsgi.service
```

We can also restart the running service to reflect Python code changes:

```
systemctl restart sennet-member-ui.uwsgi.service
```

## Wordpress DEV to PROD migration and release

First make a copy of the DEV database and `/opt/sennet/wp-site` directory and transfer the files to PROD VM.

On the PROD VM, import the database dump file and replace `/opt/sennet/wp-site` with the content from DEV, also use the PROD configuration for `/opt/sennet/member-ui/instance/app.cfg`. Then set the correct ownership and file permissions:

```
chown -R nginx:nginx /opt/sennet/wp-site
chmod -R 755 /opt/sennet/wp-site
```

The WordPress CLI utility is installed under /usr/local/bin/, when migrating from old domain to new domain, we'll need to run:

```
cd /usr/local/bin/
./wp search-replace 'dev.sennetconsortium.org' 'sennetconsortium.org' --all-tables --path=/opt/sennet/wp-site/
./wp search-replace 'https://dev.sennetconsortium.org' 'https://sennetconsortium.org' --all-tables --path=/opt/sennet/wp-site/
```

Run the above replacement connads a few times until 0 place from both file systems and the database to be replaced.

Restart the PHP process with `systemctl restart php-fpm`.

Releasing the `member-ui` can be done next by pulling the changes from github and then restart the uWSGI server `systemctl restart sennet-member-ui.uwsgi.service`.

## Post migration and release

Login to the Admin dashboard of Wordpress and deactivate the `Jetpack` plugin then reactivate it to delete those cache files from DEV.
