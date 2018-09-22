# Project: Item Catalog

Author: Erik Johnson  
Date: September 12, 2018  
Course: Udacity Full Stack Web Developer Nanodegree


## Objective

Develop an application that provides a list of items within a variety of
categories as well as provide a user registration and authentication system.
Registered users will have the ability to post, edit and delete their own items.
Deploy the web application to a linux web server running Apache.


## Prepare Your Environment

Prepare the Linux instance and deploy the web application, as described in the
documentation for my Linux Server Configuration project
[here](https://github.com/erjicles/udacity-fsd-project3-linux).

## Changes For Cloud Hosting

This branch of the project was created to make the app work on a Ubuntu Linux
instance hosted in Amazon Lightsail. It was modified to use a PostgreSQL
database instead of sqlite, and to include a public_html directory that
functions as the virtual host document root. This directory contains the WSGI
file required to allow the application to work with Apache's mod_wsgi.

### Administrator Access

Users with administrator privileges can add/edit/delete categories, as well as
add/edit/delete all items (not just their own).

Granting administrator privileges can only be done via a SQL query directly to
the database. First, the user to whom you wish to grant administrator access
must have a user record in the database (i.e., they've logged into the
application at least once). 

Assuming this is true, first ssh into your VM, cd to your application directory,
and open a SQL prompt by opening the database in a SQL session:

```
sqlite3 itemcatalog.db
```
If sqlite3 isn't installed on your VM, install it using this command:
```
sudo apt-get install sqlite3
```

Next, locate the user record:
```
select * from user;
```

Finally, grant administrator access:
```
update user set is_admin = 1 where id = <user_id>;
```
where <user_id> is the id of the user that should receive administrator access.

The user will need to log off and back on for this change to take effect.