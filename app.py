from flask import Flask, request, jsonify, Response, render_template, session, redirect, url_for
from globus_sdk import AuthClient, AccessTokenAuthorizer, ConfidentialAppAuthClient
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from werkzeug import secure_filename
import phpserialize
import json
import os
import random
import stat
from shutil import copyfile, copy2, rmtree
from datetime import datetime
import pathlib
import sys, traceback
import requests
from PIL import Image
from io import BytesIO
import ast
import urllib.parse
import urllib.request
import requests
import string
import random
from flask_mail import Mail, Message
from functools import wraps
from slugify import slugify

# For debugging
from pprint import pprint


# Init app and use the config from instance folder
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('app.cfg')

# Remove trailing slash / from URL base to avoid "//" caused by config with trailing slash
app.config['FLASK_APP_BASE_URI'] = app.config['FLASK_APP_BASE_URI'].strip('/')
app.config['CONNECTION_IMAGE_URL'] = app.config['CONNECTION_IMAGE_URL'].strip('/')

# The `stage_user` and `user_connection` tables don't use this prefix
wp_db_table_prefix = app.config['WP_DB_TABLE_PREFIX']

# Prefix for the Connections meta fields
connection_meta_key_prefix = app.config['CONNECTION_META_KEY_PREFIX']

# Flask-Mail instance
mail = Mail(app)

# Init DB
db = SQLAlchemy(app)

# Init MA
ma = Marshmallow(app)

# User-Connection mapping table
# No prefix
connects = db.Table('user_connection',
    db.Column('user_id', db.Integer, db.ForeignKey(wp_db_table_prefix + 'users.id')),
    db.Column('connection_id', db.Integer, db.ForeignKey(wp_db_table_prefix + 'connections.id'))
)

# StageUser Class/Model
class StageUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    globus_user_id = db.Column(db.String(100), unique=True)
    globus_username = db.Column(db.String(200))
    email = db.Column(db.String(200))
    first_name = db.Column(db.String(200))
    last_name = db.Column(db.String(200))
    component = db.Column(db.String(200))
    other_component = db.Column(db.String(200))
    organization = db.Column(db.String(200))
    other_organization = db.Column(db.String(200))
    role = db.Column(db.String(100))
    other_role = db.Column(db.String(200))
    photo = db.Column(db.String(500))
    photo_url = db.Column(db.String(500))
    access_requests = db.Column(db.String(500)) # Checkboxes
    globus_identity = db.Column(db.String(200))
    google_email = db.Column(db.String(200))
    github_username = db.Column(db.String(200))
    slack_username = db.Column(db.String(200))
    protocols_io_email = db.Column(db.String(200))
    phone = db.Column(db.String(100))
    website = db.Column(db.String(500))
    bio = db.Column(db.Text)
    orcid = db.Column(db.String(100))
    pm = db.Column(db.Boolean)
    pm_name = db.Column(db.String(100))
    pm_email = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    deny = db.Column(db.Boolean)

    def __init__(self, a_dict):
        try:
            self.globus_user_id = a_dict['globus_user_id'] if 'globus_user_id' in a_dict else ''
            self.globus_username = a_dict['globus_username'] if 'globus_username' in a_dict else ''
            self.email = a_dict['email'] if 'email' in a_dict else ''
            self.first_name = a_dict['first_name'] if 'first_name' in a_dict else ''
            self.last_name = a_dict['last_name'] if 'last_name' in a_dict else ''
            self.component = a_dict['component'] if 'component' in a_dict else ''
            self.other_component = a_dict['other_component'] if 'other_component' in a_dict else ''
            self.organization = a_dict['organization'] if 'organization' in a_dict else ''
            self.other_organization = a_dict['other_organization'] if 'other_organization' in a_dict else ''
            self.role = a_dict['role'] if 'role' in a_dict else ''
            self.other_role = a_dict['other_role'] if 'other_role' in a_dict else ''
            self.photo = a_dict['photo'] if 'photo' in a_dict else ''
            self.photo_url = a_dict['photo_url'] if 'photo_url' in a_dict else ''
            self.access_requests = json.dumps(a_dict['access_requests']) if 'access_requests' in a_dict else ''
            self.globus_identity = a_dict['globus_identity'] if 'globus_identity' in a_dict else ''
            self.google_email = a_dict['google_email'] if 'google_email' in a_dict else ''
            self.github_username = a_dict['github_username'] if 'github_username' in a_dict else ''
            self.slack_username = a_dict['slack_username'] if 'slack_username' in a_dict else ''
            self.protocols_io_email = a_dict['protocols_io_email'] if 'protocols_io_email' in a_dict else ''
            self.phone = a_dict['phone'] if 'phone' in a_dict else ''
            self.website = a_dict['website'] if 'website' in a_dict else ''
            self.bio = a_dict['bio'] if 'bio' in a_dict else ''
            self.orcid = a_dict['orcid'] if 'orcid' in a_dict else ''
            self.pm = a_dict['pm'] if 'pm' in a_dict else ''
            self.pm_name = a_dict['pm_name'] if 'pm_name' in a_dict else ''
            self.pm_email = a_dict['pm_email'] if 'pm_email' in a_dict else ''
        except e:
            raise e

# Define output format with marshmallow schema
class StageUserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'globus_user_id', 'globus_username', 'email', 'first_name', 'last_name', 'component', 'other_component', 'organization', 'other_organization',
                    'role', 'other_role', 'photo', 'photo_url', 'access_requests', 'globus_identity', 'google_email', 'github_username', 'slack_username', 'protocols_io_email', 'phone', 'website',
                    'bio', 'orcid', 'pm', 'pm_name', 'pm_email', 'created_at', 'deny')

# WPUserMeta Class/Model
class WPUserMeta(db.Model):
    __tablename__ = wp_db_table_prefix + 'usermeta'

    umeta_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(wp_db_table_prefix + 'users.id'), nullable=False)
    meta_key = db.Column(db.String(255), nullable=False)
    meta_value = db.Column(db.Text)

# WPUserMeta Schema
class WPUserMetaSchema(ma.Schema):
    class Meta:
        model = WPUserMeta
        fields = ('umeta_id', 'user_id', 'meta_key', 'meta_value')

# ConnectionMeta
class ConnectionMeta(db.Model):
    __tablename__ = wp_db_table_prefix + 'connections_meta'

    meta_id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, db.ForeignKey(wp_db_table_prefix + 'connections.id'), nullable=False)
    meta_key = db.Column(db.String(255), nullable=False)
    meta_value = db.Column(db.Text)

# ConnectionMeta Schema
class ConnectionMetaSchema(ma.Schema):
    class Meta:
        fields = ('meta_id', 'entry_id', 'meta_key', 'meta_value')

class ConnectionEmail(db.Model):
    __tablename__ = wp_db_table_prefix + 'connections_email'

    id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, db.ForeignKey(wp_db_table_prefix + 'connections.id'), nullable=False)
    order = db.Column(db.Integer)
    preferred = db.Column(db.Integer)
    type = db.Column(db.Text)
    address = db.Column(db.Text)
    visibility = db.Column(db.Text)

class ConnectionPhone(db.Model):
    __tablename__ = wp_db_table_prefix + 'connections_phone'

    id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, db.ForeignKey(wp_db_table_prefix + 'connections.id'), nullable=False)
    order = db.Column(db.Integer)
    preferred = db.Column(db.Integer)
    type = db.Column(db.Text)
    number = db.Column(db.Text)
    visibility = db.Column(db.Text)

# Connection
class Connection(db.Model):
    __tablename__ = wp_db_table_prefix + 'connections'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    organization = db.Column(db.Text)
    options = db.Column(db.Text)
    phone_numbers = db.Column(db.Text)
    date_added = db.Column(db.Text)
    entry_type = db.Column(db.Text)
    visibility = db.Column(db.Text)
    slug = db.Column(db.Text)
    family_name = db.Column(db.Text)
    honorific_prefix = db.Column(db.Text)
    middle_name = db.Column(db.Text)
    honorific_suffix = db.Column(db.Text)
    title = db.Column(db.Text)
    department = db.Column(db.Text)
    contact_first_name = db.Column(db.Text)
    contact_last_name = db.Column(db.Text)
    addresses = db.Column(db.Text)
    im = db.Column(db.Text)
    social = db.Column(db.Text)
    links = db.Column(db.Text)
    dates = db.Column(db.Text)
    birthday = db.Column(db.Text)
    anniversary = db.Column(db.Text)
    bio = db.Column(db.Text)
    notes = db.Column(db.Text)
    excerpt = db.Column(db.Text)
    added_by = db.Column(db.Integer)
    edited_by = db.Column(db.Integer)
    owner = db.Column(db.Integer)
    user = db.Column(db.Integer)
    status = db.Column(db.String(20))
    metas = db.relationship('ConnectionMeta', backref='connection', lazy='joined')
    emails = db.relationship('ConnectionEmail', backref='connection', lazy='joined')
    phones = db.relationship('ConnectionPhone', backref='connection', lazy='joined')

# Connection Schema
class ConnectionSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_numbers', 'organization', 'department', 'title', 'bio', 'options', 'metas')

    metas = ma.Nested(ConnectionMetaSchema, many=True)

# WPUser Class/Model
class WPUser(db.Model):
    __tablename__ = wp_db_table_prefix + 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_login = db.Column(db.String(60), nullable=False)
    user_pass = db.Column(db.String(255), nullable=False)
    user_email = db.Column(db.String(500), nullable=False)
    metas = db.relationship('WPUserMeta', backref='user', lazy='joined')
    connection = db.relationship('Connection', secondary=connects, backref=db.backref('owners', lazy='dynamic'))

# WPUser Schema
class WPUserSchema(ma.Schema):
    class Meta:
        model = WPUser
        fields = ('id', 'user_login', 'user_email', 'metas', 'connection')
    
    metas = ma.Nested(WPUserMetaSchema, many=True)
    connection = ma.Nested(ConnectionSchema, many=True)

# Init schema
stage_user_schema = StageUserSchema(strict=True)
stage_users_schema = StageUserSchema(many=True, strict=True)

wp_user_schema = WPUserSchema(strict=True)
wp_users_schema = WPUserSchema(many=True, strict=True)

wp_user_meta_schema = WPUserMetaSchema(strict=True)
wp_user_metas_schema = WPUserMetaSchema(many=True, strict=True)

connection_schema = ConnectionSchema(strict=True)
connections_schema = ConnectionSchema(many=True, strict=True)


# Send email confirmation of new user registration to admins
def send_new_user_registered_mail(data):
    msg = Message('New user registration submitted', recipients=app.config['MAIL_ADMIN_LIST'])
    msg.body = render_template('email/new_user_registered_email.txt', data = data)
    msg.html = render_template('email/new_user_registered_email.html', data = data)
    mail.send(msg)

# Send email to admins once user profile updated
# Only email when the access requests has changed
def send_user_profile_updated_mail(data, old_access_requests_data):
    msg = Message('User profile updated', recipients=app.config['MAIL_ADMIN_LIST'])
    msg.body = render_template('email/user_profile_updated_email.txt', data = data, old_access_requests_data = old_access_requests_data)
    msg.html = render_template('email/user_profile_updated_email.html', data = data, old_access_requests_data = old_access_requests_data)
    mail.send(msg)

# Once admin approves the new user registration, email the new user as well as the admins
def send_new_user_approved_mail(recipient, data):
    msg = Message('New user registration approved', recipients=[recipient] + app.config['MAIL_ADMIN_LIST'])
    msg.body = render_template('email/new_user_approved_email.txt', data = data)
    msg.html = render_template('email/new_user_approved_email.html', data = data)
    mail.send(msg)

# Send user email once registration is denied
def send_new_user_denied_mail(recipient, data):
    msg = Message('New user registration denied', recipients=[recipient] + app.config['MAIL_ADMIN_LIST'])
    msg.body = render_template('email/new_user_denied_email.txt', data = data)
    msg.html = render_template('email/new_user_denied_email.html', data = data)
    mail.send(msg)

# Get user info from globus with the auth access token
def get_globus_user_info(token):
    auth_client = AuthClient(authorizer=AccessTokenAuthorizer(token))
    return auth_client.oauth2_userinfo()

# Create user info based on submitted form data
def construct_user(request):
    photo_file = None
    imgByteArr = None

    # Users can only choose to upload image ,pull image from URL, or just the default image
    # Values: "upload", "url", "default", or "existing"
    # When "default" or "existing" (only happens when updating approved profile) selected
    # no need to handle image from the client side
    profile_pic_option = request.form['profile_pic_option'].lower()

    if profile_pic_option == 'upload':
        if 'photo' in request.files and request.files['photo']:
            photo_file = request.files['photo']
    elif profile_pic_option == 'url':
        photo_url = request.form['photo_url']
        if photo_url:
            response = requests.get(photo_url)
            img = Image.open(BytesIO(response.content))
            imgByteArr = BytesIO()
            img.save(imgByteArr, format=img.format)
            imgByteArr = imgByteArr.getvalue()

    # strip() removes any leading and trailing whitespaces including tabs (\t)
    user_info = {
        # Get the globus user id and globus username from session data
        "globus_user_id": session['globus_user_id'],
        "globus_username": session['globus_username'],
        # All others are from the form data
        "email": request.form['email'].strip(),
        "first_name": request.form['first_name'].strip(),
        "last_name": request.form['last_name'].strip(),
        "phone": request.form['phone'].strip(),
        "component": request.form['component'],
        "other_component": request.form['other_component'].strip(),
        "organization": request.form['organization'],
        "other_organization": request.form['other_organization'].strip(),
        "role": request.form['role'],
        "other_role": request.form['other_role'].strip(),
        "photo": '',
        "photo_url": request.form['photo_url'].strip(),
        # multiple checkboxes
        "access_requests": request.form.getlist('access_requests'),
        "globus_identity": request.form['globus_identity'].strip(),
        "google_email": request.form['google_email'].strip(),
        "github_username": request.form['github_username'].strip(),
        "slack_username": request.form['slack_username'].strip(),
        "protocols_io_email": request.form['protocols_io_email'].strip(),
        "website": request.form['website'].strip(),
        "bio": request.form['bio'],
        "orcid": request.form['orcid'].strip(),
        "pm": get_pm_selection(request.form['pm']),
        "pm_name": request.form['pm_name'].strip(),
        "pm_email": request.form['pm_email'].strip()
    }

    img_to_upload = photo_file if photo_file is not None else imgByteArr if imgByteArr is not None else None

    return user_info, profile_pic_option, img_to_upload


def get_pm_selection(value):
    # Make comparison case insensitive
    value = value.lower()
    if value == 'yes':
        return True
    elif value == 'no':
        return False
    else:
        return None

# Generate CSRF tokens for registration form and profile form
def generate_csrf_token(stringLength = 10):
    if 'csrf_token' not in session:
        letters = string.ascii_lowercase
        session['csrf_token'] = ''.join(random.choice(letters) for i in range(stringLength))
    return session['csrf_token']


def show_registration_form():
    # If user registered with their direct globus ID, we can't gurentee the "Full name" contains a space
    # Because it's possible the users only entered firstname in "Full name" during globus ID registration on globus site
    name_words = session['name'].split(" ")

    context = {
        'isAuthenticated': True,
        'username': session['name'],
        'csrf_token': generate_csrf_token(),
        'globus_user_id': session['globus_user_id'],
        'globus_username': session['globus_username'],
        'first_name': name_words[0],
        # Use empty for last name if not present
        'last_name': name_words[1] if (len(name_words) > 1) else "",
        'email': session['email'],
        'recaptcha_site_key': app.config['GOOGLE_RECAPTCHA_SITE_KEY']
    }

    return render_template('register.html', data = context)

# Three different types of message for authenticated users
def show_user_error(message):
    context = {
        'isAuthenticated': True,
        'username': session['name'],
        'message': message
    }
    return render_template('user_message/user_error.html', data = context)

def show_user_confirmation(message):
    context = {
        'isAuthenticated': True,
        'username': session['name'],
        'message': message
    }
    return render_template('user_message/user_confirmation.html', data = context)

def show_user_info(message):
    context = {
        'isAuthenticated': True,
        'username': session['name'],
        'message': message
    }
    return render_template('user_message/user_info.html', data = context)

# Admin messages
def show_admin_error(message):
    context = {
        'isAuthenticated': True,
        'username': session['name'],
        'message': message
    }
    return render_template('admin_message/admin_error.html', data = context)

def show_admin_confirmation(message):
    context = {
        'isAuthenticated': True,
        'username': session['name'],
        'message': message
    }
    return render_template('admin_message/admin_confirmation.html', data = context)

def show_admin_info(message):
    context = {
        'isAuthenticated': True,
        'username': session['name'],
        'message': message
    }
    return render_template('admin_message/admin_info.html', data = context)

# Check if the user is registered and approved
# meaning this user is in `wp_users`, `wp_connections`, and `user_connection` tables and 
# the user has the role of "member" or "administrator", the role is assigned when the user is approved
# A use with a submitted registration but pending is not consodered to be an approved user
def user_is_approved(globus_user_id):
    user_meta = WPUserMeta.query.filter(WPUserMeta.meta_key.like('openid-connect-generic-subject-identity'), WPUserMeta.meta_value == globus_user_id).first()
    if not user_meta:
        print('user_is_approved(): No user found with globus_user_id: ' + globus_user_id)
        return False
    users = [user_meta.user]
    result = wp_users_schema.dump(users)
    user = result[0][0]
    capabilities = next((meta for meta in user['metas'] if meta['meta_key'] == wp_db_table_prefix + 'capabilities'), {})
    if (('meta_value' in capabilities) and ('member' in capabilities['meta_value'] or 'administrator' in capabilities['meta_value'])):
        return True
    else:
        return False

# Check if user has the "administrator" role
def user_is_admin(globus_user_id):
    user_meta = WPUserMeta.query.filter(WPUserMeta.meta_key.like('openid-connect-generic-subject-identity'), WPUserMeta.meta_value == globus_user_id).first()
    if not user_meta:
        print('user_is_admin(): No user found with globus_user_id: ' + globus_user_id)
        return False
    users = [user_meta.user]
    result = wp_users_schema.dump(users)
    user = result[0][0]
    capabilities = next((meta for meta in user['metas'] if meta['meta_key'] == wp_db_table_prefix + 'capabilities'), {})
    if (('meta_value' in capabilities) and ('administrator' in capabilities['meta_value'])):
        return True
    else:
        return False


# Check if the user registration is still pending for approval in `stage_user` table
def user_in_pending(globus_user_id):
    stage_user = StageUser.query.filter(StageUser.globus_user_id == globus_user_id)
    if stage_user.count() == 0:
        return False
    return True

# Add new user reigstration to `stage_user` table
def add_new_stage_user(user_info, profile_pic_option, img_to_upload):
    # First handle the profile image and save it to target directory
    user_info['photo'] = handle_stage_user_profile_pic(user_info, profile_pic_option, img_to_upload)

    try:
        stage_user = StageUser(user_info)
    except Exception as e:
        print('User data is invalid')
        print(e)
    
    if StageUser.query.filter(StageUser.globus_user_id == stage_user.globus_user_id).first():
        print('The same stage user exists')
    else:
        try:
            db.session.add(stage_user)
            db.session.commit()
        except Exception as e:
            print('Failed to add a new stage user')
            print(e)
     
# Given a new user's first name and last name, get the unique slug name for `wp_connections`
# Expecially useful when multiple users have the same names: joe-smith, joe-smith-1, joe-smith-2
# The connections plugin uses slug as image folder name in cconnection-images   
def unique_connection_slug(first_name, last_name, connection_id = None):
    first_name = first_name.lower()
    last_name = last_name.lower()
    slug = slugify(first_name + '-' + last_name)

    # If exisiting user updates first name and last name, make sure the new slug is not used
    if connection_id:
        # Filter conditions: different connection ID but the same first/last name
        # Meaning the same user won't get a new slug
        connections = Connection.query.filter(Connection.id != connection_id, db.func.lower(Connection.first_name) == first_name, db.func.lower(Connection.last_name) == last_name)
    # If a new user's first name and last name the same as an exisiting user, also create a unique slug
    else:
        connections = Connection.query.filter(db.func.lower(Connection.first_name) == first_name, db.func.lower(Connection.last_name) == last_name)
        
    if connections.count() > 0:
        slug = slug + '-' + str(connections.count())

    return slug

# Query the user data to populate into profile form
# This is different from get_wp_user() in that it also returns the meta and connection data
# from where we can parse all the profile data
def get_user_profile(globus_user_id):
    user_meta = WPUserMeta.query.filter(WPUserMeta.meta_key.like('openid-connect-generic-subject-identity'), WPUserMeta.meta_value == globus_user_id).first()
    if not user_meta:
        print('No WP user found with globus_user_id: ' + globus_user_id)
        return None
    users = [user_meta.user]
    result = wp_users_schema.dump(users)
    user = result[0][0]
    return user

# Only save image to the stage dir, once approved, will copy to target dir
def handle_stage_user_profile_pic(user_info, profile_pic_option, img_to_upload):
    save_path = ''
    
    if profile_pic_option == 'upload':
        _, extension = img_to_upload.filename.rsplit('.', 1)
        img_file = img_to_upload

        save_path = os.path.join(app.config['STAGE_USER_IMAGE_DIR'], secure_filename(f"{user_info['globus_user_id']}.{extension}"))
        img_file.save(save_path)
    elif profile_pic_option == 'url':
        response = requests.get(user_info['photo_url'])
        img_file = Image.open(BytesIO(response.content))
        extension = img_file.format

        save_path = os.path.join(app.config['STAGE_USER_IMAGE_DIR'], secure_filename(f"{user_info['globus_user_id']}.{extension}"))
        img_file.save(save_path)
    else:
        # Use default image
        save_path = os.path.join(app.config['STAGE_USER_IMAGE_DIR'], secure_filename(f"{user_info['globus_user_id']}.png"))
        source_file_path = os.path.join(app.root_path, 'static', 'images', 'default_profile.png')
        copyfile(source_file_path, save_path)
        # Also keep the file owner and group
        keep_file_owner_and_group(source_file_path, save_path)

    return save_path

# Save the profile image to target dir directly per user, no need to use stage image dir 
def update_user_profile_pic(user_info, profile_pic_option, img_to_upload, image_dir, current_image_filename):
    save_path = ''

    if profile_pic_option == 'existing':
        save_path = os.path.join(image_dir, current_image_filename)
    elif profile_pic_option == 'upload':
        _, extension = img_to_upload.filename.rsplit('.', 1)
        img_file = img_to_upload

        save_path = os.path.join(image_dir, secure_filename(f"{user_info['globus_user_id']}.{extension}"))
        img_file.save(save_path)
    elif profile_pic_option == 'url':
        response = requests.get(user_info['photo_url'])
        img_file = Image.open(BytesIO(response.content))
        extension = img_file.format

        save_path = os.path.join(image_dir, secure_filename(f"{user_info['globus_user_id']}.{extension}"))
        img_file.save(save_path)
    else:
        # Use default image
        save_path = os.path.join(image_dir, secure_filename(f"{user_info['globus_user_id']}.png"))
        source_file_path = os.path.join(app.root_path, 'static', 'images', 'default_profile.png')
        copyfile(source_file_path, save_path)
        # Also keep the file owner and group
        keep_file_owner_and_group(source_file_path, save_path)

    return save_path

# Update user profile with user-provided information 
def update_user_profile(connection_id, user_info, profile_pic_option, img_to_upload):
    # First get the exisiting wp_user record with globus id
    # this has no connection data
    wp_user = get_wp_user(session['globus_user_id'])

    # Get connection profile by connection id
    connection_profile = get_connection_profile(connection_id)

    # If by any chance the user updates first name or last name 
    # We need to copy old dir to the new image directory
    # There won't be an existing dir due to unique_connection_slug()
    # Copy old image to new image dir if user changed first/last name, AKA new unique slug name
    current_slug = connection_profile.slug
    current_image_dir = os.path.join(app.config['CONNECTION_IMAGE_DIR'], current_slug)

    # If we see 'image' field in options, it means this user is added either via registration or WP connections plugin with an image
    # thus there's an image folder with an image
    try:
        options = json.loads(connection_profile.options)
        current_image_path = options['image']['meta']['original']['path']
        current_image_filename = current_image_path.split('/')[-1]
        # In case the image folder is gone if someone manually deleted it, we check to make and create one to avoid unknown errors
        if not pathlib.Path(current_image_dir).exists():
            pathlib.Path(current_image_dir).mkdir(parents=True, exist_ok=True)
    # Otherwise, this connection entry is created directly from WP connections plugin without uploading an image
    # thus there's no image folder created
    except KeyError:
        # We create the image folder
        pathlib.Path(current_image_dir).mkdir(parents=True, exist_ok=True)
        # Copy over the default image       
        current_image_filename = 'default_profile.png'
        save_path = os.path.join(current_image_dir, secure_filename(f"{user_info['globus_user_id']}.png"))
        source_file_path = os.path.join(app.root_path, 'static', 'images', current_image_filename)
        copyfile(source_file_path, save_path)
        # Also keep the file owner and group
        keep_file_owner_and_group(source_file_path, save_path)
    except TypeError:
        # We create the image folder
        pathlib.Path(current_image_dir).mkdir(parents=True, exist_ok=True)
        # Copy over the default image       
        current_image_filename = 'default_profile.png'
        save_path = os.path.join(current_image_dir, secure_filename(f"{user_info['globus_user_id']}.png"))
        source_file_path = os.path.join(app.root_path, 'static', 'images', current_image_filename)
        copyfile(source_file_path, save_path)
        # Also keep the file owner and group
        keep_file_owner_and_group(source_file_path, save_path)

    # This exisiting user doesn't change first name and last name, so no need to get new unique slug
    if (user_info['first_name'].lower() == connection_profile.first_name.lower()) and (user_info['last_name'].lower() == connection_profile.last_name.lower()):
        # Update profile image directly
        user_info['photo'] = update_user_profile_pic(user_info, profile_pic_option, img_to_upload, current_image_dir, current_image_filename)
    # Otherwise, we need a new slug and create the new image folder and copy old images to this new location
    else:
        new_slug = unique_connection_slug(user_info['first_name'], user_info['last_name'], connection_id)
        new_image_dir = os.path.join(app.config['CONNECTION_IMAGE_DIR'], new_slug)

        # Create the new image folder
        pathlib.Path(new_image_dir).mkdir(parents=True, exist_ok=True)
        # Copy all old images to this new folder
        for file in os.listdir(current_image_dir):
            file_path = os.path.join(current_image_dir, file)
            new_file_path = os.path.join(new_image_dir, file)
            
            if os.path.isfile(file_path):
                copy2(file_path, new_image_dir)
                # Also keep the file owner and group
                keep_file_owner_and_group(file_path, new_file_path)

        # Finally delete the old image folder        
        try:
            rmtree(current_image_dir)
        except Exception as e:
            print("Failed to delete the old profile image folder due to new slug: " + current_image_dir)
            print(e)

        user_info['photo'] = update_user_profile_pic(user_info, profile_pic_option, img_to_upload, new_image_dir, current_image_filename)

    # Convert the user_info dict into object via StageUser() model
    # So edit_connection() can be reused for approcing new user by editing matched and updating exisiting approved user
    user_obj = StageUser(user_info)
    edit_connection(user_obj, wp_user, connection_profile)
    db.session.commit()


# This is user approval without using existing mathicng profile
# Approving by moving user data from `stage_user` into `wp_user` and `wp_connections`
# also add the ids to the `user_connection` table
def approve_stage_user_by_creating_new(stage_user):
    # First need to check if there's an exisiting wp_user record with the same globus id
    wp_user = get_wp_user(stage_user.globus_user_id)

    if not wp_user:
        # Create new user and meta
        new_wp_user = create_new_user(stage_user)
        # MUST do this before create_new_connection()
        db.session.add(new_wp_user)
        # Create profile in `wp_connections`
        create_new_connection(stage_user, new_wp_user)
    else:
        edit_wp_user(stage_user)
        create_new_connection(stage_user, wp_user)

    db.session.delete(stage_user)
    db.session.commit()


def approve_stage_user_by_editing_matched(stage_user_obj, connection_profile):
    # First need to check if there's an exisiting wp_user record with the same globus id
    wp_user = get_wp_user(stage_user_obj.globus_user_id)

    if not wp_user:
        # Create new user and meta
        new_wp_user = create_new_user(stage_user_obj)
        db.session.add(new_wp_user)
        # Edit profile in `wp_connections`
        edit_connection(stage_user_obj, new_wp_user, connection_profile, True)
        
    else:
        # Update the `wp_users` record
        edit_wp_user(stage_user_obj)
        edit_connection(stage_user_obj, wp_user, connection_profile, True)

    db.session.delete(stage_user_obj)
    db.session.commit()


# Edit the exisiting wp_user role as "member"
def edit_wp_user(stage_user_obj):
    wp_user = get_wp_user(stage_user_obj.globus_user_id)
    wp_user.user_login = stage_user_obj.email
    wp_user.user_email = stage_user_obj.email

    meta_capabilities = next((meta for meta in wp_user.metas if meta.meta_key == wp_db_table_prefix + 'capabilities'), None)
    if meta_capabilities:
        meta_capabilities.meta_value = "a:1:{s:6:\"member\";b:1;}"
    
def create_new_user(stage_user_obj):
    # Create a new wp_user record
    new_wp_user = WPUser()
    new_wp_user.user_login = stage_user_obj.email
    new_wp_user.user_email = stage_user_obj.email
    new_wp_user.user_pass = generate_password()

    # Create new usermeta for "member" role
    meta_capabilities = WPUserMeta()
    meta_capabilities.meta_key = wp_db_table_prefix + 'capabilities'
    meta_capabilities.meta_value = "a:1:{s:6:\"member\";b:1;}"
    new_wp_user.metas.append(meta_capabilities)
    
    # Create new usermeta for globus id
    meta_globus_user_id = WPUserMeta()
    meta_globus_user_id.meta_key = "openid-connect-generic-subject-identity"
    meta_globus_user_id.meta_value = stage_user_obj.globus_user_id
    new_wp_user.metas.append(meta_globus_user_id)

    # Create new usermeta for globus username
    meta_globus_username = WPUserMeta()
    meta_globus_username.meta_key = "globus_username"
    meta_globus_username.meta_value = stage_user_obj.globus_username
    new_wp_user.metas.append(meta_globus_username)

    return new_wp_user

def generate_password():
    s = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
    passlen = 16
    return "".join(random.sample(s, passlen))

def create_new_connection(stage_user_obj, new_wp_user):
    # First get the id of admin user in `wp_usermeta` table
    admin_id = WPUserMeta.query.filter(WPUserMeta.meta_key.like('openid-connect-generic-subject-identity'), WPUserMeta.meta_value == session['globus_user_id']).first().user_id

    connection = Connection()
    connection_email = ConnectionEmail()
    connection_email.order = 0
    connection_email.preferred = 0
    connection_email.type = 'work'
    connection_email.address = stage_user_obj.email
    connection_email.visibility = 'public'
    connection.emails.append(connection_email)

    connection_phone = ConnectionPhone()
    connection_phone.order = 0
    connection_phone.preferred = 0
    connection_phone.type = 'workphone'
    connection_phone.number = stage_user_obj.phone
    connection_phone.visibility = 'public'
    connection.phones.append(connection_phone)

    connection.first_name = stage_user_obj.first_name
    connection.last_name = stage_user_obj.last_name

    connection.organization = stage_user_obj.organization
    connection.department = stage_user_obj.component
    connection.title = stage_user_obj.role

    connection.date_added = str(datetime.today().timestamp())
    connection.entry_type = 'individual'
    connection.visibility = 'public'
    # slug for new user doesn't require connection ID
    connection.slug = unique_connection_slug(stage_user_obj.first_name, stage_user_obj.last_name, None)
    connection.family_name = ''
    connection.honorific_prefix = ''
    connection.middle_name = ''
    connection.honorific_suffix = ''
    

    connection.contact_first_name = ''
    connection.contact_last_name = ''
    connection.addresses = 'a:0:{}'
    connection.im = 'a:0:{}'
    connection.social = 'a:0:{}'
    connection.links = 'a:0:{}'
    connection.dates = 'a:0:{}'
    connection.birthday = ''
    connection.anniversary = ''
    connection.bio = stage_user_obj.bio
    connection.notes = ''
    connection.excerpt = ''
    connection.added_by = admin_id
    connection.edited_by = admin_id
    connection.owner = admin_id
    connection.user = 0
    connection.status = 'approved'
    
    # Initial values use empty then update later
    connection.email = ''
    connection.phone_numbers = ''
    connection.options = ''

    connection.owners.append(new_wp_user)

    db.session.commit()

    # Then update the rest and add metas
    # Now get the id for email and phone to compose the email and phone for connections
    connection.email = f"a:1:{{i:0;a:7:{{s:2:\"id\";i:{connection.emails[0].id};s:4:\"type\";s:4:\"work\";s:4:\"name\";s:10:\"Work Email\";s:10:\"visibility\";s:6:\"public\";s:5:\"order\";i:0;s:9:\"preferred\";b:0;s:7:\"address\";s:{len(connection.emails[0].address)}:\"{connection.emails[0].address}\";}}}}"
    connection.phone_numbers = f"a:1:{{i:0;a:7:{{s:2:\"id\";i:{connection.phones[0].id};s:4:\"type\";s:9:\"workphone\";s:4:\"name\";s:10:\"Work Phone\";s:10:\"visibility\";s:6:\"public\";s:5:\"order\";i:0;s:9:\"preferred\";b:0;s:6:\"number\";s:{len(connection.phones[0].number)}:\"{connection.phones[0].number}\";}}}}"

    # Handle profile image
    # For new user registration, stage_user_obj.photo will never be empty
    # So no need to check if stage_user_obj.photo === '' here like in edit_connection()
    photo_file_name = stage_user_obj.photo.split('/')[-1]
    target_image_dir = os.path.join(app.config['CONNECTION_IMAGE_DIR'], connection.slug)
    pathlib.Path(target_image_dir).mkdir(parents=True, exist_ok=True)
    new_file_path = os.path.join(target_image_dir, photo_file_name)
    copyfile(stage_user_obj.photo, new_file_path)
    # Also keep the file owner and group
    keep_file_owner_and_group(stage_user_obj.photo, new_file_path)
    # Delete stage image file
    os.unlink(stage_user_obj.photo)

    # Get the MIME type of image
    image = Image.open(new_file_path)
    content_type = Image.MIME[image.format]

    image_path = os.path.join(app.config['CONNECTION_IMAGE_DIR'], connection.slug, photo_file_name)
    image_url = app.config['CONNECTION_IMAGE_URL'] + "/" + connection.slug + "/" + photo_file_name
    connection.options = "{\"entry\":{\"type\":\"individual\"},\"image\":{\"linked\":true,\"display\":true,\"name\":{\"original\":\"" + photo_file_name + "\"},\"meta\":{\"original\":{\"name\":\"" + photo_file_name + "\",\"path\":\"" + image_path + "\",\"url\": \"" + image_url + "\",\"width\":200,\"height\":200,\"size\":\"width=\\\"200\\\" height=\\\"200\\\"\",\"mime\":\"" + content_type + "\",\"type\":2}}}}"

    globus_identity = stage_user_obj.globus_identity
    google_email = stage_user_obj.google_email
    github_username = stage_user_obj.github_username
    slack_username = stage_user_obj.slack_username
    protocols_io_email = stage_user_obj.protocols_io_email

    # Other connections metas
    connection_meta_component = ConnectionMeta()
    connection_meta_component.meta_key = connection_meta_key_prefix + 'component'
    connection_meta_component.meta_value = stage_user_obj.component
    connection.metas.append(connection_meta_component)

    connection_meta_other_component = ConnectionMeta()
    connection_meta_other_component.meta_key = connection_meta_key_prefix + 'other_component'
    connection_meta_other_component.meta_value = stage_user_obj.other_component
    connection.metas.append(connection_meta_other_component)

    connection_meta_organization = ConnectionMeta()
    connection_meta_organization.meta_key = connection_meta_key_prefix + 'organization'
    connection_meta_organization.meta_value = stage_user_obj.organization
    connection.metas.append(connection_meta_organization)

    connection_meta_other_organization = ConnectionMeta()
    connection_meta_other_organization.meta_key = connection_meta_key_prefix + 'other_organization'
    connection_meta_other_organization.meta_value = stage_user_obj.other_organization
    connection.metas.append(connection_meta_other_organization)

    connection_meta_role = ConnectionMeta()
    connection_meta_role.meta_key = connection_meta_key_prefix + 'role'
    connection_meta_role.meta_value = stage_user_obj.role
    connection.metas.append(connection_meta_role)

    connection_meta_other_role = ConnectionMeta()
    connection_meta_other_role.meta_key = connection_meta_key_prefix + 'other_role'
    connection_meta_other_role.meta_value = stage_user_obj.other_role
    connection.metas.append(connection_meta_other_role)

    connection_meta_access_requests = ConnectionMeta()
    connection_meta_access_requests.meta_key = connection_meta_key_prefix + 'access_requests'
    connection_meta_access_requests.meta_value = stage_user_obj.access_requests
    connection.metas.append(connection_meta_access_requests)

    connection_meta_globus_identity = ConnectionMeta()
    connection_meta_globus_identity.meta_key = connection_meta_key_prefix + 'globus_identity'
    connection_meta_globus_identity.meta_value = globus_identity
    connection.metas.append(connection_meta_globus_identity)

    connection_meta_google_email = ConnectionMeta()
    connection_meta_google_email.meta_key = connection_meta_key_prefix + 'google_email'
    connection_meta_google_email.meta_value = google_email
    connection.metas.append(connection_meta_google_email)

    connection_meta_github_username = ConnectionMeta()
    connection_meta_github_username.meta_key = connection_meta_key_prefix + 'github_username'
    connection_meta_github_username.meta_value = github_username
    connection.metas.append(connection_meta_github_username)

    connection_meta_slack_username = ConnectionMeta()
    connection_meta_slack_username.meta_key = connection_meta_key_prefix + 'slack_username'
    connection_meta_slack_username.meta_value = slack_username
    connection.metas.append(connection_meta_slack_username)

    connection_meta_protocols_io_email = ConnectionMeta()
    connection_meta_protocols_io_email.meta_key = connection_meta_key_prefix + 'protocols_io_email'
    connection_meta_protocols_io_email.meta_value = protocols_io_email
    connection.metas.append(connection_meta_protocols_io_email)

    connection_meta_website = ConnectionMeta()
    connection_meta_website.meta_key = connection_meta_key_prefix + 'website'
    connection_meta_website.meta_value = stage_user_obj.website
    connection.metas.append(connection_meta_website)

    connection_meta_orcid = ConnectionMeta()
    connection_meta_orcid.meta_key = connection_meta_key_prefix + 'orcid'
    connection_meta_orcid.meta_value = stage_user_obj.orcid
    connection.metas.append(connection_meta_orcid)

    connection_meta_pm = ConnectionMeta()
    connection_meta_pm.meta_key = connection_meta_key_prefix + 'pm'
    connection_meta_pm.meta_value = stage_user_obj.pm
    connection.metas.append(connection_meta_pm)

    connection_meta_pm_name = ConnectionMeta()
    connection_meta_pm_name.meta_key = connection_meta_key_prefix + 'pm_name'
    connection_meta_pm_name.meta_value = stage_user_obj.pm_name
    connection.metas.append(connection_meta_pm_name)

    connection_meta_pm_email = ConnectionMeta()
    connection_meta_pm_email.meta_key = connection_meta_key_prefix + 'pm_email'
    connection_meta_pm_email.meta_value = stage_user_obj.pm_email
    connection.metas.append(connection_meta_pm_email)


# Overwrite the existing fields with the ones from user registration or profile update
def edit_connection(user_obj, wp_user, connection, new_user = False):
    # First get the id of user in `wp_usermeta` table
    # If this profile is approved by using a matching connection, the edit_user_id is the admin user id
    # If this profile is updated by the user after approval, it's the user's id
    edit_user_id = WPUserMeta.query.filter(WPUserMeta.meta_key.like('openid-connect-generic-subject-identity'), WPUserMeta.meta_value == session['globus_user_id']).first().user_id

    # Handle the connections email and phone first
    connection_email = ConnectionEmail()
    connection_email.order = 0
    connection_email.preferred = 0
    connection_email.type = 'work'
    connection_email.address = user_obj.email
    connection_email.visibility = 'public'

    connection_phone = ConnectionPhone()
    connection_phone.order = 0
    connection_phone.preferred = 0
    connection_phone.type = 'workphone'
    connection_phone.number = user_obj.phone
    connection_phone.visibility = 'public'

    existing_email = next((e for e in connection.emails if e.type == 'work'), None)
    existing_phone = next((e for e in connection.phones if e.type == 'workphone'), None)
    if existing_email:
        existing_email.order = 0
        existing_email.preferred = 0
        existing_email.type = 'work'
        existing_email.address = user_obj.email
        existing_email.visibility = 'public'
    else:
        connection.emails.append(connection_email)

    if existing_phone:
        existing_phone.order = 0
        existing_phone.preferred = 0
        existing_phone.type = 'workphone'
        existing_phone.number = user_obj.phone
        existing_phone.visibility = 'public'
    else:
        connection.phones.append(connection_phone)

    db.session.commit()

    # If this exisiting user doesn't change first name and last name, no need to get new unique slug
    # Otherwise, we need to update the first/last name and create a new slug
    if (user_obj.first_name.lower() != connection.first_name.lower()) or (user_obj.last_name.lower() != connection.last_name.lower()):
        connection.first_name = user_obj.first_name
        connection.last_name = user_obj.last_name
        connection.slug = unique_connection_slug(user_obj.first_name, user_obj.last_name, connection.id)

    # Get the id for connection email and phone
    connection.email = f"a:1:{{i:0;a:7:{{s:2:\"id\";i:{connection.emails[0].id};s:4:\"type\";s:4:\"work\";s:4:\"name\";s:10:\"Work Email\";s:10:\"visibility\";s:6:\"public\";s:5:\"order\";i:0;s:9:\"preferred\";b:0;s:7:\"address\";s:{len(connection.emails[0].address)}:\"{connection.emails[0].address}\";}}}}"
    connection.phone_numbers = f"a:1:{{i:0;a:7:{{s:2:\"id\";i:{connection.phones[0].id};s:4:\"type\";s:9:\"workphone\";s:4:\"name\";s:10:\"Work Phone\";s:10:\"visibility\";s:6:\"public\";s:5:\"order\";i:0;s:9:\"preferred\";b:0;s:6:\"number\";s:{len(connection.phones[0].number)}:\"{connection.phones[0].number}\";}}}}"
    
    connection.department = user_obj.component
    connection.organization = user_obj.organization
    connection.title = user_obj.role

    connection.bio = user_obj.bio
    connection.edited_by = edit_user_id

    # Handle profile image
    # user_obj.photo is the image file path when pic option is (One of "existing", "default", "upload", or "url")
    # It's possible the user has changed first/last name, resulting a new slug with number
    # In this special case, if the user chose to reuse "exisiting" image, we'll also need to update the image path and url in connection.options in database
    photo_file_name = user_obj.photo.split('/')[-1]

    # Profile update for an approved user doesn't need to mkdir and copy image
    # Approving a new user by editing an exisiting profile requires to mkdir and copy the image
    target_image_dir = os.path.join(app.config['CONNECTION_IMAGE_DIR'], connection.slug)
    if new_user:
        pathlib.Path(target_image_dir).mkdir(parents=True, exist_ok=True)
        new_file_path = os.path.join(target_image_dir, photo_file_name)
        copyfile(user_obj.photo, new_file_path)
        # Also keep the file owner and group
        keep_file_owner_and_group(user_obj.photo, new_file_path)
        # Delete stage image file
        os.unlink(user_obj.photo)
    else:
        # For existing profile image update, remove all the old images and leave the new one there
        # since the one image has already been copied there
        for file in os.listdir(target_image_dir):
            file_path = os.path.join(target_image_dir, file)
            
            if os.path.isfile(file_path) and (file_path != user_obj.photo):
                try:
                    os.unlink(file_path)
                except Exception as e:
                    print("Failed to empty the profile image folder: " + target_image_dir)
                    print(e)

    # Get the MIME type of image
    image = Image.open(os.path.join(target_image_dir, photo_file_name))
    content_type = Image.MIME[image.format]

    image_path = os.path.join(app.config['CONNECTION_IMAGE_DIR'], connection.slug, photo_file_name)
    image_url = app.config['CONNECTION_IMAGE_URL'] + "/" + connection.slug + "/" + photo_file_name
    connection.options = "{\"entry\":{\"type\":\"individual\"},\"image\":{\"linked\":true,\"display\":true,\"name\":{\"original\":\"" + photo_file_name + "\"},\"meta\":{\"original\":{\"name\":\"" + photo_file_name + "\",\"path\":\"" + image_path + "\",\"url\": \"" + image_url + "\",\"width\":200,\"height\":200,\"size\":\"width=\\\"200\\\" height=\\\"200\\\"\",\"mime\":\"" + content_type + "\",\"type\":2}}}}"

    # Update corresponding metas
    connection_meta_component = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'component', ConnectionMeta.entry_id == connection.id).first()
    if connection_meta_component:
        connection_meta_component.meta_value = user_obj.component
    else:
        connection_meta_component = ConnectionMeta()
        connection_meta_component.meta_key = connection_meta_key_prefix + 'component'
        connection_meta_component.meta_value = user_obj.component
        connection.metas.append(connection_meta_component)

    connection_meta_other_component = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'other_component', ConnectionMeta.entry_id == connection.id).first()
    if connection_meta_other_component:
        connection_meta_other_component.meta_value = user_obj.other_component
    else:
        connection_meta_other_component = ConnectionMeta()
        connection_meta_other_component.meta_key = connection_meta_key_prefix + 'other_component'
        connection_meta_other_component.meta_value = user_obj.other_component
        connection.metas.append(connection_meta_other_component)

    connection_meta_organization = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'organization', ConnectionMeta.entry_id == connection.id).first()
    if connection_meta_organization:
        connection_meta_organization.meta_value = user_obj.organization
    else:
        connection_meta_organization = ConnectionMeta()
        connection_meta_organization.meta_key = connection_meta_key_prefix + 'organization'
        connection_meta_organization.meta_value = user_obj.organization
        connection.metas.append(connection_meta_organization)

    connection_meta_other_organization = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'other_organization', ConnectionMeta.entry_id == connection.id).first()
    if connection_meta_other_organization:
        connection_meta_other_organization.meta_value = user_obj.other_organization
    else:
        connection_meta_other_organization = ConnectionMeta()
        connection_meta_other_organization.meta_key = connection_meta_key_prefix + 'other_organization'
        connection_meta_other_organization.meta_value = user_obj.other_organization
        connection.metas.append(connection_meta_other_organization)

    connection_meta_role = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'role', ConnectionMeta.entry_id == connection.id).first()
    if connection_meta_role:
        connection_meta_role.meta_value = user_obj.role
    else:
        connection_meta_role = ConnectionMeta()
        connection_meta_role.meta_key = connection_meta_key_prefix + 'role'
        connection_meta_role.meta_value = user_obj.role
        connection.metas.append(connection_meta_role)

    connection_meta_other_role = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'other_role', ConnectionMeta.entry_id == connection.id).first()
    if connection_meta_other_role:
        connection_meta_other_role.meta_value = user_obj.other_role
    else:
        connection_meta_other_role = ConnectionMeta()
        connection_meta_other_role.meta_key = connection_meta_key_prefix + 'other_role'
        connection_meta_other_role.meta_value = user_obj.other_role
        connection.metas.append(connection_meta_other_role)

    connection_meta_access_requests = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'access_requests', ConnectionMeta.entry_id == connection.id).first()
    if connection_meta_access_requests:
        connection_meta_access_requests.meta_value = user_obj.access_requests
    else:
        connection_meta_access_requests = ConnectionMeta()
        connection_meta_access_requests.meta_key = connection_meta_key_prefix + 'access_requests'
        connection_meta_access_requests.meta_value = user_obj.access_requests
        connection.metas.append(connection_meta_access_requests)

    connection_meta_globus_identity = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'globus_identity', ConnectionMeta.entry_id == connection.id).first()
    if connection_meta_globus_identity:
        connection_meta_globus_identity.meta_value = user_obj.globus_identity
    else:
        connection_meta_globus_identity = ConnectionMeta()
        connection_meta_globus_identity.meta_key = connection_meta_key_prefix + 'globus_identity'
        connection_meta_globus_identity.meta_value = user_obj.globus_identity
        connection.metas.append(connection_meta_globus_identity)

    connection_meta_google_email = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'google_email', ConnectionMeta.entry_id == connection.id).first()
    if connection_meta_google_email:
        connection_meta_google_email.meta_value = user_obj.google_email
    else:
        connection_meta_google_email = ConnectionMeta()
        connection_meta_google_email.meta_key = connection_meta_key_prefix + 'google_email'
        connection_meta_google_email.meta_value = user_obj.google_email
        connection.metas.append(connection_meta_google_email)

    connection_meta_github_username = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'github_username', ConnectionMeta.entry_id == connection.id).first()
    if connection_meta_github_username:
        connection_meta_github_username.meta_value = user_obj.github_username
    else:
        connection_meta_github_username = ConnectionMeta()
        connection_meta_github_username.meta_key = connection_meta_key_prefix + 'github_username'
        connection_meta_github_username.meta_value = user_obj.github_username
        connection.metas.append(connection_meta_github_username)

    connection_meta_slack_username = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'slack_username', ConnectionMeta.entry_id == connection.id).first()
    if connection_meta_slack_username:
        connection_meta_slack_username.meta_value = user_obj.slack_username
    else:
        connection_meta_slack_username = ConnectionMeta()
        connection_meta_slack_username.meta_key = connection_meta_key_prefix + 'slack_username'
        connection_meta_slack_username.meta_value = user_obj.slack_username
        connection.metas.append(connection_meta_slack_username)

    connection_meta_protocols_io_email = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'protocols_io_email', ConnectionMeta.entry_id == connection.id).first()
    if connection_meta_protocols_io_email:
        connection_meta_protocols_io_email.meta_value = user_obj.protocols_io_email
    else:
        connection_meta_protocols_io_email = ConnectionMeta()
        connection_meta_protocols_io_email.meta_key = connection_meta_key_prefix + 'protocols_io_email'
        connection_meta_protocols_io_email.meta_value = user_obj.protocols_io_email
        connection.metas.append(connection_meta_protocols_io_email)

    connection_meta_website = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'website', ConnectionMeta.entry_id == connection.id).first()
    if connection_meta_website:
        connection_meta_website.meta_value = user_obj.website
    else:
        connection_meta_website = ConnectionMeta()
        connection_meta_website.meta_key = connection_meta_key_prefix + 'website'
        connection_meta_website.meta_value = user_obj.website
        connection.metas.append(connection_meta_website)

    connection_meta_orcid = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'orcid', ConnectionMeta.entry_id == connection.id).first()
    if connection_meta_orcid:
        connection_meta_orcid.meta_value = user_obj.orcid
    else:
        connection_meta_orcid = ConnectionMeta()
        connection_meta_orcid.meta_key = connection_meta_key_prefix + 'orcid'
        connection_meta_orcid.meta_value = user_obj.orcid
        connection.metas.append(connection_meta_orcid)

    connection_meta_pm = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'pm', ConnectionMeta.entry_id == connection.id).first()
    if connection_meta_pm:
        connection_meta_pm.meta_value = user_obj.pm
    else:
        connection_meta_pm = ConnectionMeta()
        connection_meta_pm.meta_key = connection_meta_key_prefix + 'pm'
        connection_meta_pm.meta_value = user_obj.pm
        connection.metas.append(connection_meta_pm)

    connection_meta_pm_name = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'pm_name', ConnectionMeta.entry_id == connection.id).first()
    if connection_meta_pm_name:
        connection_meta_pm_name.meta_value = user_obj.pm_name
    else:
        connection_meta_pm_name = ConnectionMeta()
        connection_meta_pm_name.meta_key = connection_meta_key_prefix + 'pm_name'
        connection_meta_pm_name.meta_value = user_obj.pm_name
        connection.metas.append(connection_meta_pm_name)

    connection_meta_pm_email = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'pm_email', ConnectionMeta.entry_id == connection.id).first()
    if connection_meta_pm_email:
        connection_meta_pm_email.meta_value = user_obj.pm_email
    else:
        connection_meta_pm_email = ConnectionMeta()
        connection_meta_pm_email.meta_key = connection_meta_key_prefix + 'pm_email'
        connection_meta_pm_email.meta_value = user_obj.pm_email
        connection.metas.append(connection_meta_pm_email)

    # Also update the wp_user record
    wp_user.user_login = user_obj.email
    wp_user.user_email = user_obj.email

    if not wp_user in connection.owners:
        connection.owners.append(wp_user)

# Get a list of all approved members (not including admins)
def get_all_members():
    members = list()
    # Order members by ID DESC
    wp_users = WPUser.query.order_by(WPUser.id.desc()).all()
    for user in wp_users:
        # Check if this target user is a member (capabilities will be empty dict if not member role)
        capabilities = next((meta for meta in user.metas if (meta.meta_key == wp_db_table_prefix + 'capabilities') and ('member' in meta.meta_value)), {})
        if capabilities:
            # Use this check in case certain user doesn't have the connection info
            if user.connection:
                # Note user.connection returns a list of connections (should be only one though)
                connection_data = user.connection[0]
                # Also get the globus_user_id
                wp_user_meta_globus_user_id = WPUserMeta.query.filter(WPUserMeta.user_id == user.id, WPUserMeta.meta_key.like('openid-connect-generic-subject-identity')).first()
                
                # Construct a new member dict and add to the members list
                member = {
                    'globus_user_id': wp_user_meta_globus_user_id.meta_value,
                    'first_name': connection_data.first_name,
                    'last_name': connection_data.last_name,
                    'email': user.user_email,
                    'organization': connection_data.organization
                }

                members.append(member)
    
    return members


# Deny the new user registration
def deny_stage_user(globus_user_id):
    stage_user = get_stage_user(globus_user_id)
    stage_user.deny = True
    db.session.commit()

# Get a list of all the pending registrations
def get_all_stage_users():
    # Order by submission date DESC
    stage_users = StageUser.query.order_by(StageUser.created_at.desc()).all()
    return stage_users

# Get a stage user new registration by a given globus_user_id
def get_stage_user(globus_user_id):
    stage_user = StageUser.query.filter(StageUser.globus_user_id == globus_user_id).first()
    return stage_user

# Get the exisiting user from `wp_users` table by looking for the globus id in `wp_usermeta` table
def get_wp_user(globus_user_id):
    wp_user_meta = WPUserMeta.query.filter(WPUserMeta.meta_key.like('openid-connect-generic-subject-identity'), WPUserMeta.meta_value == globus_user_id).first()
    if not wp_user_meta:
        return None
    wp_user = WPUser.query.filter(WPUser.id == wp_user_meta.user_id).first()
    return wp_user

# Get a list of connections IDs that are already connected to a user
def get_linked_connection_ids():
    users = WPUser.query.filter(WPUser.connection != None).all()
    connection_ids = list()
    for user in users:
        connection_ids.append(user.connection[0].id)
    
    return connection_ids

# Find the matching profiles of a given user from the `wp_connections` table
# Scoring: last_name(6), first_name(4), email(10), organization(2)
def get_matching_profiles(last_name, first_name, email, organization):
    last_name_match_score = 6
    first_name_match_score = 4
    email_match_score = 10
    organization_match_score = 2

    # Get a list of connections IDs that are already connected to a user
    connections_ids = get_linked_connection_ids()

    # Use user email to search for matching profiles
    profiles_by_last_name = Connection.query.filter(Connection.id.notin_(connections_ids), Connection.last_name.like(f'%{last_name}%')).all()
    profiles_by_first_name = Connection.query.filter(Connection.id.notin_(connections_ids), Connection.first_name.like(f'%{first_name}%')).all()
    profiles_by_email = Connection.query.filter(Connection.id.notin_(connections_ids), Connection.email.like(f'%{email}%')).all()
    profiles_by_organization = Connection.query.filter(Connection.id.notin_(connections_ids), Connection.organization.like(f'%{organization}%')).all()
    
    # Now merge the above lists into one big list and pass into a set to remove duplicates
    profiles_set = set(profiles_by_last_name + profiles_by_first_name + profiles_by_email + profiles_by_organization)
    # convert back to a list for sorting later
    profiles_list = list(profiles_set)

    filtered_profiles = list()
    if len(profiles_list) > 0:
        for profile in profiles_list:
            # Add a new aroperty
            profile.score = 0

            # See if the target profile can be found in each search resulting list
            # then add up the corresponding score
            if profile in profiles_by_last_name:
                profile.score = profile.score + last_name_match_score

            if profile in profiles_by_first_name:
                profile.score = profile.score + first_name_match_score

            if profile in profiles_by_email:
                profile.score = profile.score + email_match_score

            if profile in profiles_by_organization:
                profile.score = profile.score + organization_match_score
            
            # Ditch the profile that has matching score <= first_name_match_score
            if profile.score > first_name_match_score:
                # Deserialize the email value to a python dict
                deserilized_email_dict = phpserialize.loads(profile.email.encode('utf-8'), decode_strings=True)
                # Add another new property for display only
                if deserilized_email_dict:
                    profile.deserilized_email = (deserilized_email_dict[0])['address']
                filtered_profiles.append(profile)

    # Sort the filtered results by scoring
    profiles = sorted(filtered_profiles, key=lambda x: x.score, reverse=True)
    # Return a set of sorted matching profiles by score or an empty set if no match
    return profiles

# Get profile from `wp_connections` for a given connection ID
def get_connection_profile(connection_id):
    connection_profile = Connection.query.filter(Connection.id == connection_id).first()
    return connection_profile


# `shutil.copyfile`, even the higher-level file copying functions (shutil.copy(), shutil.copy2()) cannot copy all file metadata.
# On POSIX platforms, this means that file owner and group are lost as well as ACLs.
def keep_file_owner_and_group(source_file_path, target_file_path):
    st = os.stat(source_file_path)
    os.chown(target_file_path, st.st_uid, st.st_gid)

# Login Required Decorator
# To use the decorator, apply it as innermost decorator to a view function. 
# When applying further decorators, always remember that the route() decorator is the outermost.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'isAuthenticated' not in session:
            return render_template('login.html')
        return f(*args, **kwargs)
    return decorated_function

# Admin Required Decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not user_is_admin(session['globus_user_id']):
            return show_user_error("Access denied! You need to login as an admin user to access this page!")
        return f(*args, **kwargs)
    return decorated_function


# Routing

# Default
@app.route("/")
@login_required
def index():
    if user_is_approved(session['globus_user_id']):
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('register'))

# Redirect users from react app login page to Globus auth login widget then redirect back
@app.route('/login')
def login():
    redirect_uri = url_for('login', _external=True)
    confidential_app_auth_client = ConfidentialAppAuthClient(app.config['GLOBUS_APP_ID'], app.config['GLOBUS_APP_SECRET'])
    confidential_app_auth_client.oauth2_start_flow(redirect_uri)

    # If there's no "code" query string parameter, we're in this route
    # starting a Globus Auth login flow.
    # Redirect out to Globus Auth
    if 'code' not in request.args:                                        
        auth_uri = confidential_app_auth_client.oauth2_get_authorize_url()
        return redirect(auth_uri)
    # If we do have a "code" param, we're coming back from Globus Auth
    # and can start the process of exchanging an auth code for a token.
    else:
        auth_code = request.args.get('code')

        token_response = confidential_app_auth_client.oauth2_exchange_code_for_tokens(auth_code)
        
        # Get auth token
        auth_token = token_response.by_resource_server['auth.globus.org']['access_token']

        # Also get the user info (sub, email, name, preferred_username) using the AuthClient with the auth token
        user_info = get_globus_user_info(auth_token)

        # Store the resulting tokens in server session
        session['isAuthenticated'] = True
        # For rendering admin menu 
        session['isAdmin'] = user_is_admin(user_info['sub'])
        # Globus ID and username parsed from login
        session['globus_user_id'] = user_info['sub']
        session['globus_username'] = user_info['preferred_username']
        session['name'] = user_info['name']
        # Normalize email to lowercase
        session['email'] = user_info['email'].lower()
        session['auth_token'] = auth_token

        # Finally redirect back to the home page default route
        return redirect("/")

@app.route('/logout')
def logout():
    """
    - Revoke the tokens with Globus Auth.
    - Destroy the session state.
    - Redirect the user to the Globus Auth logout page.
    """
    confidential_app_auth_client = ConfidentialAppAuthClient(app.config['GLOBUS_APP_ID'], app.config['GLOBUS_APP_SECRET'])

    # Revoke the tokens with Globus Auth
    if 'auth_token' in session:    
        confidential_app_auth_client.oauth2_revoke_token(session['auth_token'])

    # Destroy the session state
    session.clear()

    # build the logout URI with query params
    # there is no tool to help build this (yet!)
    globus_logout_url = (
        'https://auth.globus.org/v2/web/logout' +
        '?client={}'.format(app.config['GLOBUS_APP_ID']) +
        '&redirect_uri={}'.format(app.config['FLASK_APP_BASE_URI']) +
        '&redirect_name={}'.format(app.config['FLASK_APP_NAME']))

    # Redirect the user to the Globus Auth logout page
    return redirect(globus_logout_url)

# Register is only for authenticated users who has never registered
@app.route("/register", methods=['GET', 'POST'])
@login_required
def register():
    # A not approved user can be a totally new user or user has a pending registration
    if not user_is_approved(session['globus_user_id']):
        if user_in_pending(session['globus_user_id']):
            # Check if this pening registration has been denied
            stage_user = get_stage_user(session['globus_user_id'])
            # Note: stage_user.deny stores 1 or 0 in database
            if not stage_user.deny:
                return show_user_info("Your registration has been submitted for approval. You'll get an email once it's approved or denied.")
            else:
                return show_user_info("Sorry, your registration has been denied.")
        else:
            if request.method == 'POST':
                # reCAPTCHA validation
                recaptcha_response = request.form['g-recaptcha-response']
                values = {
                    'secret': app.config['GOOGLE_RECAPTCHA_SECRET_KEY'],
                    'response': recaptcha_response
                }
                data = urllib.parse.urlencode(values).encode()
                req = urllib.request.Request(app.config['GOOGLE_RECAPTCHA_VERIFY_URL'], data = data)
                response = urllib.request.urlopen(req)
                result = json.loads(response.read().decode())

                # For testing only
                #result['success'] = True

                # Currently no backend form validation
                # Only front end validation and reCAPTCHA
                if result['success']:
                    # CSRF check
                    session_csrf_token = session.pop('csrf_token', None)

                    if not session_csrf_token or session_csrf_token != request.form['csrf_token']:
                        return show_user_error("Oops! Invalid CSRF token!")
                    else:
                        user_info, profile_pic_option, img_to_upload = construct_user(request)

                        # Add user info to `stage_user` table for approval
                        try:
                            add_new_stage_user(user_info, profile_pic_option, img_to_upload)
                        except Exception as e: 
                            print("Failed to add new stage user, something wrong with add_new_stage_user()")
                            print(e)
                            return show_user_error("Oops! The system failed to submit your registration!")
                        else:
                            # Send email to admin for new user approval
                            try:
                                send_new_user_registered_mail(user_info)
                            except Exception as e: 
                                print("send email failed")
                                print(e)
                                return show_user_error("Oops! The system has submited your registration but failed to send the confirmation email!")

                        # Show confirmation
                        return show_user_confirmation("Your registration has been submitted for approval. You'll get an email once it's approved or denied.")
                # Show reCAPTCHA error
                else:
                    return show_user_error("Oops! reCAPTCHA error!")
            # Handle GET
            else:
                return show_registration_form()
    else:
        return show_user_info('You have already registered, you can click <a href="/profile">here</a> to view or update your user profile.')

# Profile is only for authenticated users who has an approved registration
@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    if user_is_approved(session['globus_user_id']):
        # Handle POST
        if request.method == 'POST':
            # CSRF check
            session_csrf_token = session.pop('csrf_token', None)
            if not session_csrf_token or session_csrf_token != request.form['csrf_token']:
                return show_user_error("Oops! Invalid CSRF token!")
            else:
                user_info, profile_pic_option, img_to_upload = construct_user(request)
                # Also get the connection_id
                connection_id = request.form['connection_id']
                
                # Get this before calling update_user_profile()
                access_requests_value = ''
                access_requests_record = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'access_requests', ConnectionMeta.entry_id == connection_id).first()
                if access_requests_record:
                    access_requests_value = access_requests_record.meta_value

                globus_identity_value = ''
                globus_identity_record = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'globus_identity', ConnectionMeta.entry_id == connection_id).first()
                if globus_identity_record:
                    globus_identity_value = globus_identity_record.meta_value

                google_email_value = ''
                google_email_record = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'google_email', ConnectionMeta.entry_id == connection_id).first()
                if google_email_record:
                    google_email_value = google_email_record.meta_value

                github_username_value = ''
                github_username_record = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'github_username', ConnectionMeta.entry_id == connection_id).first()
                if github_username_record:
                    github_username_value = github_username_record.meta_value

                slack_username_value = ''
                slack_username_record = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'slack_username', ConnectionMeta.entry_id == connection_id).first()
                if slack_username_record:
                    slack_username_value = slack_username_record.meta_value
                
                protocols_io_email_value = ''
                protocols_io_email_record = ConnectionMeta.query.filter(ConnectionMeta.meta_key == connection_meta_key_prefix + 'protocols_io_email', ConnectionMeta.entry_id == connection_id).first()
                if protocols_io_email_record:
                    protocols_io_email_value = protocols_io_email_record.meta_value

                old_access_requests_dict = {
                    # Convert list string respresentation to Python list, if empty string, empty list()
                    'access_requests': ast.literal_eval(access_requests_value) if (access_requests_value != '') else list(),
                    'globus_identity': globus_identity_value,
                    'google_email': google_email_value,
                    'github_username': github_username_value,
                    'slack_username': slack_username_value,
                    'protocols_io_email': protocols_io_email_value
                }

                try:
                    # Update user profile in database
                    update_user_profile(connection_id, user_info, profile_pic_option, img_to_upload)
                except Exception as e: 
                    print("Failed to update user profile!")
                    print(e)
                    return show_user_error("Oops! The system failed to update your profile changes!")
                else:
                    # Only email admin when access requests list changed
                    # Compare list to list, ordering should be the same, no need to sort
                    if user_info['access_requests'] != old_access_requests_dict['access_requests']: 
                        try:
                            # Send email to admin for user profile update
                            # so the admin can do furtuer changes in globus
                            send_user_profile_updated_mail(user_info, old_access_requests_dict)
                        except Exception as e: 
                            print("Failed to send user profile update email to admin.")
                            print(e)
                            return show_user_error("Your profile has been updated but the system failed to send confirmation email to admin. No worries, no action needed from you.")

                # Also notify the user
                return show_user_confirmation("Your profile information has been updated successfully. The admin will handle additional changes to your account as needed.")
        # Handle GET
        else:
            # Fetch user profile data
            try:
                wp_user = get_user_profile(session['globus_user_id'])
            except Exception as e: 
                print("Failed to get user profile for globus_user_id: " + session['globus_user_id'])
                print(e)
                return show_user_error("Oops! The system failed to query your profile data!")

            # Parsing the json(from schema dump) to get initial user profile data
            connection_data = wp_user['connection'][0]

            # Deserialize the phone number value to a python dict
            deserilized_phone = ''
            deserilized_phone_dict = phpserialize.loads(connection_data['phone_numbers'].encode('utf-8'), decode_strings=True)
            # Add another new property for display only
            if deserilized_phone_dict:
                deserilized_phone = (deserilized_phone_dict[0])['number']

            initial_data = {
                # Data pulled from the `wp_connections` table
                'first_name': connection_data['first_name'],
                'last_name': connection_data['last_name'],
                'component': connection_data['department'], # Store the component value in department field
                'organization': connection_data['organization'], 
                'role': connection_data['title'], # Store the role value in title field
                'bio': connection_data['bio'],
                # email is pulled from the `wp_users` table that is linked with Globus login so no need to deserialize the wp_connections.email filed
                'email': wp_user['user_email'].lower(),
                # Other values pulled from `wp_connections_meta` table as customized fileds
                'phone': deserilized_phone,
                'other_component': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'other_component'), {'meta_value': ''})['meta_value'],
                'other_organization': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'other_organization'), {'meta_value': ''})['meta_value'],
                'other_role': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'other_role'), {'meta_value': ''})['meta_value'],
                'access_requests': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'access_requests'), {'meta_value': ''})['meta_value'],
                'globus_identity': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'globus_identity'), {'meta_value': ''})['meta_value'],
                'google_email': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'google_email'), {'meta_value': ''})['meta_value'],
                'github_username': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'github_username'), {'meta_value': ''})['meta_value'],
                'slack_username': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'slack_username'), {'meta_value': ''})['meta_value'],
                'protocols_io_email': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'protocols_io_email'), {'meta_value': ''})['meta_value'],
                'website': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'website'), {'meta_value': ''})['meta_value'],
                'orcid': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'orcid'), {'meta_value': ''})['meta_value'],
                'pm': 'Yes' if next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'pm'), {'meta_value': ''})['meta_value'] == '1' else 'No',
                'pm_name': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'pm_name'), {'meta_value': ''})['meta_value'],
                'pm_email': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'pm_email'), {'meta_value': ''})['meta_value'],
            }

            # Convert string representation to list
            if not initial_data['access_requests'].strip() == '':
                initial_data['access_requests'] = ast.literal_eval(initial_data['access_requests'])
       
            # Connections created in WP connections plugin without uploading image won't have the 'image' field
            # Use empty and display the default profile image
            profile_pic_url = ''

            try:
                options = json.loads(connection_data['options'])
                profile_pic_path = options['image']['meta']['original']['path']

                # Also check if the file exists, otherwise profile_pic_url = '' still
                # It's possible the path and url in database but the actual file or dir not on the disk
                if pathlib.Path(profile_pic_path).exists():
                    if 'url' in options['image']['meta']['original']:
                        profile_pic_url = options['image']['meta']['original']['url']
            except KeyError:
                profile_pic_url = ''
            except TypeError:
                profile_pic_url = ''

            context = {
                'isAuthenticated': True,
                'username': session['name'],
                'globus_user_id': session['globus_user_id'],
                # For individual user profile, use the globus_username from session
                'globus_username': session['globus_username'],
                'csrf_token': generate_csrf_token(),
                'connection_id': connection_data['id'],
                'profile_pic_url': profile_pic_url
            }
            
            # Merge initial_data and context as one dict 
            data = {**context, **initial_data}
            # Populate the user data in profile
            return render_template('profile.html', data = data)
    else:
        if user_in_pending(session['globus_user_id']):
            # Check if this pening registration has been denied
            stage_user = get_stage_user(session['globus_user_id'])
            if not stage_user.deny:
                return show_user_info("Your registration is pending for approval, you can view/update your profile once it's approved.")
            else:
                return show_user_info("Sorry, you don't have a profile because your registration has been denied.")
        else:
            return show_user_info('You have not registered, please click <a href="/register">here</a> to register.')

# Only for admin to see a list of all the approved members (not including admins)
# Currently only handle deleting a member
# globus_user_id is optional
@app.route("/members/", defaults={'globus_user_id': None}, methods=['GET']) # need the trailing slash
@app.route("/members/<globus_user_id>", methods=['GET'])
@login_required
@admin_required
def members(globus_user_id):
    # Show a list of all members if globus_user_id not present
    if not globus_user_id:
        members = get_all_members()
        context = {
            'isAuthenticated': True,
            'username': session['name'],
            'members': members
        }

        return render_template('all_members.html', data = context)
    else:
        # Fetch user profile data
        try:
            wp_user = get_user_profile(globus_user_id)
        except Exception as e: 
            print("Failed to get user profile for globus_user_id: " + globus_user_id)
            print(e)
            return show_user_error("Oops! The system failed to query the target member's profile data!")

        # Below is the same code as GET /profile (with minor modifications)
        # Parsing the json(from schema dump) to get initial user profile data
        connection_data = wp_user['connection'][0]

        # Deserialize the phone number value to a python dict
        deserilized_phone = ''
        deserilized_phone_dict = phpserialize.loads(connection_data['phone_numbers'].encode('utf-8'), decode_strings=True)
        # Add another new property for display only
        if deserilized_phone_dict:
            deserilized_phone = (deserilized_phone_dict[0])['number']

        initial_data = {
            # Data pulled from the `wp_connections` table
            'first_name': connection_data['first_name'],
            'last_name': connection_data['last_name'],
            'component': connection_data['department'], # Store the component value in department field
            'organization': connection_data['organization'], 
            'role': connection_data['title'], # Store the role value in title field
            'bio': connection_data['bio'],
            # email is pulled from the `wp_users` table that is linked with Globus login so no need to deserialize the wp_connections.email filed
            'email': wp_user['user_email'].lower(),
            # Other values pulled from `wp_connections_meta` table as customized fileds
            'phone': deserilized_phone,
            'other_component': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'other_component'), {'meta_value': ''})['meta_value'],
            'other_organization': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'other_organization'), {'meta_value': ''})['meta_value'],
            'other_role': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'other_role'), {'meta_value': ''})['meta_value'],
            'access_requests': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'access_requests'), {'meta_value': ''})['meta_value'],
            'globus_identity': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'globus_identity'), {'meta_value': ''})['meta_value'],
            'google_email': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'google_email'), {'meta_value': ''})['meta_value'],
            'github_username': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'github_username'), {'meta_value': ''})['meta_value'],
            'slack_username': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'slack_username'), {'meta_value': ''})['meta_value'],
            'protocols_io_email': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'protocols_io_email'), {'meta_value': ''})['meta_value'],
            'website': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'website'), {'meta_value': ''})['meta_value'],
            'orcid': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'orcid'), {'meta_value': ''})['meta_value'],
            # This is slightly different from the GET /profile
            'pm': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'pm'), {'meta_value': ''})['meta_value'] == '1',
            'pm_name': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'pm_name'), {'meta_value': ''})['meta_value'],
            'pm_email': next((meta for meta in connection_data['metas'] if meta['meta_key'] == connection_meta_key_prefix + 'pm_email'), {'meta_value': ''})['meta_value'],
        }

        # Get the globus_username for individual user
        # The system didn't store globus username for old members
        # Use meta_value (either actual value if present or empty string as default)
        globus_username = next((meta for meta in wp_user['metas'] if meta['meta_key'] == 'globus_username'), {'meta_value': ''})['meta_value']
        pprint(initial_data['access_requests'])
        # The above initial_data wil be merged with this context
        context = {
            'isAuthenticated': True,
            'username': session['name'],
            'globus_user_id': globus_user_id,
            'globus_username': globus_username,
            # Need to convert string representation of list to Python list
            'access_requests_list': ast.literal_eval(initial_data['access_requests']) if (initial_data['access_requests'].strip() != '') else list()
        }
        
        # Merge initial_data and context as one dict 
        data = {**context, **initial_data}

        # Populate the user data in profile
        return render_template('individual_member.html', data = data)

# Delete target member records from database and image files
@app.route("/delete_member/<globus_user_id>", methods=['GET']) # need the trailing slash
@login_required
@admin_required
def delete_member(globus_user_id):
    msg = ""

    try:
        wp_user = get_wp_user(globus_user_id)
    except Exception as e: 
        msg = "The system could not find the target member based on the provided globus_user_id: " + globus_user_id
        print(msg)
        print(e)
        return show_user_error(msg)

    try:
        # First get the target dir before deleting the connection record
        image_dir = os.path.join(app.config['CONNECTION_IMAGE_DIR'], wp_user.connection[0].slug)

        # Must delete the connection record before deleting wp_user
        db.session.delete(wp_user.connection[0])

        # Also delete the usermeta records
        WPUserMeta.query.filter(WPUserMeta.user_id == wp_user.id).delete()

        # Then delete the wp user record, this also deletes the mapping record in `user_connection` table
        db.session.delete(wp_user)

        db.session.commit()

        # Delete the connection images from file system after database records being deleted successfully
        if os.path.isdir(image_dir):
            try:
                rmtree(image_dir)
                msg = "The database records and connection images of this member have been deleted successfully!"
                return show_admin_info(msg)
            except Exception as e:
                msg = "The database records of this member have been deleted successfully! But the system failed to delete the member's image directory: " + image_dir + ", please manually delete that directory."
                print(msg)
                print(e)
                return show_admin_error(msg)
        # Still show the success message if no image dir
        msg = "The database records of this member have been deleted successfully!"
        return show_admin_info(msg)
    except Exception as e: 
        db.session.rollback()
        
        # Add error to logging
        msg = "The system failed to delete the records of this member!"
        print(msg)
        print(e)

        # Notify admin
        return show_admin_error(msg)


# Only for admin to see a list of pending new registrations
# Currently only handle approve and deny actions
# globus_user_id is optional
@app.route("/registrations/", defaults={'globus_user_id': None}, methods=['GET']) # need the trailing slash
@app.route("/registrations/<globus_user_id>", methods=['GET'])
@login_required
@admin_required
def registrations(globus_user_id):
    # Show a list of pending registrations if globus_user_id not present
    if not globus_user_id:
        stage_users = get_all_stage_users()
        context = {
            'isAuthenticated': True,
            'username': session['name'],
            'stage_users': stage_users
        }

        return render_template('all_registrations.html', data = context)
    else:
        # Show the individual pending registration
        stage_user = get_stage_user(globus_user_id)

        if not stage_user:
            return show_admin_error("This stage user does not exist!")
        else:
            # Check if there's any matching profiles in the `wp_connections` found
            matching_profiles = get_matching_profiles(stage_user.last_name, stage_user.first_name, stage_user.email, stage_user.organization)
            #pprint(vars(list(matching_profiles)[0]))
            context = {
                'isAuthenticated': True,
                'username': session['name'],
                'stage_user': stage_user,
                # Need to convert string representation of list to Python list
                'access_requests_list': ast.literal_eval(stage_user.access_requests),
                'matching_profiles': matching_profiles
            }

            return render_template('individual_registration.html', data = context)

# Approve a registration
@app.route("/approve/<globus_user_id>", methods=['GET'])
@login_required
@admin_required
def approve(globus_user_id):
    # Check if there's a pending registration for the given globus user id
    stage_user = get_stage_user(globus_user_id)

    if not stage_user:
        return show_admin_error("This stage user does not exist!")
    else:
        try:
            approve_stage_user_by_creating_new(stage_user)
        except Exception as e: 
            print("Failed to approve new registration and create new user record.")
            print(e)
            return show_admin_error("This system failed to approve new registration and create new user record!")
        else:
            try:
                # Send email
                data = {
                    'first_name': stage_user.first_name,
                    'last_name': stage_user.last_name
                }
                send_new_user_approved_mail(stage_user.email, data = data)
            except Exception as e: 
                print("The new registration has been approved, but the system failed to send out user registration approval email.")
                print(e)
                return show_admin_error("The new registration has been approved, but the system failed to send out user registration approval email!")

        return show_admin_info("This registration has been approved successfully!")

# Deny a registration
@app.route("/deny/<globus_user_id>", methods=['GET'])
@login_required
@admin_required
def deny(globus_user_id):
    # Check if there's a pending registration for the given globus user id
    stage_user = get_stage_user(globus_user_id)

    if not stage_user:
        return show_admin_error("This stage user does not exist!")
    else:
        if stage_user.deny:
            return show_admin_info("This registration has already been denied!")
        else:
            try:
                deny_stage_user(globus_user_id)
            except Exception as e: 
                print("The system failed to deny user registration.")
                print(e)
                return show_admin_error("The system failed to deny user registration!")
            else:
                try:
                    # Send email
                    data = {
                        'first_name': stage_user.first_name,
                        'last_name': stage_user.last_name
                    }
                    send_new_user_denied_mail(stage_user.email, data = data)
                except Exception as e: 
                    print("Failed to send user registration denied email.")
                    print(e)
                    return show_admin_error("The user registration has been denied but the system failed to sent out email notification!")

            return show_admin_info("This registration has been denied!")


# Approve a registration by using an exisiting matching profile
@app.route("/match/<globus_user_id>/<connection_id>", methods=['GET'])
@login_required
@admin_required
def match(globus_user_id, connection_id):
    # Check if there's a pending registration for the given globus user id
    stage_user = get_stage_user(globus_user_id)
    if not stage_user:
        return show_admin_error("This stage user does not exist!")

    # Check if there's a connection profile for the given connection id
    connection_profile = get_connection_profile(connection_id)
    if not connection_profile:
        return show_admin_error("This connection profile does not exist!")

    try: 
        approve_stage_user_by_editing_matched(stage_user, connection_profile)
    except Exception as e: 
        print("Failed to approve the registration by using existing matched connection!")
        print(e) 
        return show_admin_error("Failed to approve the registration by using existing matched connection!")
    else:
        try:
            # Send email
            data = {
                'first_name': stage_user.first_name,
                'last_name': stage_user.last_name
            }
            send_new_user_approved_mail(stage_user.email, data = data)
        except Exception as e: 
            print("Failed to send user registration approval email.")
            print(e)
            return show_admin_error("The registration by using existing matched connection has been approved, but the system failed to sent out approval email!")

    return show_admin_info("This registration has been approved successfully by using an exisiting mathcing profile!")


# Instructions
@app.route("/find_globus_identity", methods=['GET'])
@login_required
def find_globus_identity():
    context = {
        'isAuthenticated': True,
        'username': session['name']
    }

    return render_template('instructions/find_globus_identity.html', data = context)


@app.route("/unlink_globus_identities", methods=['GET'])
@login_required
def unlink_globus_identities():
    context = {
        'isAuthenticated': True,
        'username': session['name']
    }

    return render_template('instructions/unlink_globus_identities.html', data = context)


def get_connection_keys():
    return ['other_component', 'other_organization', 'other_role', 'access_requests',
            'globus_identity', 'google_email', 'github_username', 'slack_username', 'protocols_io_email',
            'website', 'orcid', 'pm', 'pm_name', 'pm_email']


# Get a list of all approved users
def get_all_users_with_all_info():
    users = list()
    # Order users by ID DESC
    wp_users = WPUser.query.order_by(WPUser.id.desc()).all()
    for user in wp_users:
        # Check if this target user is a member or administrator (capabilities will be empty dict if not member role)
        capabilities = next((meta for meta in user.metas if (meta.meta_key == wp_db_table_prefix + 'capabilities') and ('member' in meta.meta_value) or ('administrator' in meta.meta_value)), {})
        if capabilities:
            # Use this check in case certain user doesn't have the connection info
            if user.connection:
                # Note user.connection returns a list of connections (should be only one though)
                connection_data = user.connection[0]
                # Also get the globus_user_id
                wp_user_meta_globus_user_id = WPUserMeta.query.filter(WPUserMeta.user_id == user.id, WPUserMeta.meta_key.like('openid-connect-generic-subject-identity')).first()
                # Get the user Capability
                capability = 'administrator' if 'administrator' in capabilities.meta_value else 'member'

                # Construct a new member dict and add to the members list
                member = {
                    'globus_user_id': wp_user_meta_globus_user_id.meta_value,
                    'first_name': connection_data.first_name,
                    'last_name': connection_data.last_name,
                    'organization': connection_data.organization,
                    'component': connection_data.department,
                    'role': connection_data.title,
                    'email': user.user_email.lower(),
                    'capability': capability
                }
                keys = get_connection_keys()
                obj = None
                try:
                    globus_user = next((meta for meta in user.metas if meta.meta_key == 'globus_username'), {'meta_value': ''})
                    if globus_user is not None:
                        member['globus_username'] = globus_user['meta_value'] if isinstance(globus_user, (dict)) else globus_user.meta_value
                    for k in keys:
                        if k == 'pm':
                            obj = next((meta for meta in connection_data.metas if meta.meta_key == connection_meta_key_prefix + 'pm'), {'meta_value': ''})
                            if obj is not None:
                                member['pm'] = 'Yes' if obj.meta_value == '1' else 'No'
                        else:
                            obj = next((meta for meta in connection_data.metas if meta.meta_key == connection_meta_key_prefix + k), {'meta_value': ''})
                            if obj is not None:
                                member[k] = obj['meta_value'] if isinstance(obj, (dict)) else obj.meta_value
                except Exception as e:
                    print(e)
                    # print(user.user_email)

                users.append(member)

    return users


def format_user_entry(val, other):
    if val == 'Other':
        return f"Other: {other}"
    else:
        return val


@app.route("/downloads/users", methods=['GET'])
@login_required
@admin_required
def downloads_users():
    users = get_all_users_with_all_info()
    csv = 'Globus Username Associated, Globus Identity, First Name, Last Name, Email, Organization, Component, PM, PM email, Role, Access Requests, Gdrive account, GitHub, Slack, protocols.io, Capability  \n'

    for user in users:
        i = StageUser(user)
        access_requests = ''
        try:
            access_requests_array = ast.literal_eval(json.loads(i.access_requests))
            access_requests_array.sort()
            access_requests = "; ".join(access_requests_array)
        except Exception as e:
            print(e)

        csv += f"{i.globus_username},{i.globus_identity},{i.first_name},{i.last_name},{i.email},{format_user_entry(i.organization, i.other_organization)},"
        csv += f"{format_user_entry(i.component, i.other_component)},{i.pm_name},{i.pm_email},{format_user_entry(i.role, i.other_role)},{access_requests},"
        csv += f"{i.google_email},{i.github_username},{i.slack_username},{i.protocols_io_email},{user['capability']}\n"

    r = Response(csv, status=200, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    r.headers["Content-Type"] = 'text/csv'
    r.headers['Content-Disposition'] = 'attachment; filename="sennet-members.csv"'

    return r


# Run Server
if __name__ == "__main__":
    app.run(debug=True)
