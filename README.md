# Project: Item Catalog

Author: Erik Johnson  
Date: September 12, 2018  
Course: Udacity Full Stack Web Developer Nanodegree


## Objective

Develop an application that provides a list of items within a variety of
categories as well as provide a user registration and authentication system.
Registered users will have the ability to post, edit and delete their own items.


## Prepare Your Environment

This web application was designed to run on a Linux box. There are several ways
to do this; here, I present the way I did so on my Windows 10 machine by
installing a virtual machine (VM).

### Install VirtualBox

You can download VirtualBox [here](https://www.virtualbox.org/wiki/Downloads).
I built and tested the application using version 5.2.18.


### Install Vagrant

You can download Vagrant [here](https://www.vagrantup.com/downloads.html).
I built and tested the application using version 2.1.5.


### Download the VM Configuration

Fork and clone the following GitHub repository to the location where you
want your VM shared folder to reside:  
https://github.com/udacity/fullstack-nanodegree-vm

### Start the VM

Open a terminal (in my case, Git Bash) inside the **vagrant** subdirectory of
the repo you cloned in the previous step. Then, run the following command:

```
vagrant up
```

Once this process is complete (it may take a long time), run the following
command to log into the VM:

```
vagrant ssh
```


## Start the Web Application


### Deploy Web Application

Fork and clone this repository as a subdirectory (e.g., catalog) 
of the **vagrant** subdirectory of the VM repo you cloned earlier.

For example, /VM-clone/vagrant/catalog

This is the **application directory**.

The application relies on two files not in the repo, **client_secrets.json**
and **app_secrets.json**.

To create **app_secrets.json**, create an empty text file of that name
and drop it in the application directory.
Add the following content:

```
{
    "app": {
        "app_secret_key": "<your_secret_key>"
    }
}
```
Replace <your_secret_key> with a long string that only you know.

Creating **client_secrets.json** takes a bit more work.

This app uses Google authentication, and relies upon a client secrets file
issued by Google. While I don't provide my secrets file in this repo,
here are instructions to register your own app and get your own
secrets file (valid as of 9/12/2018):

1. Visit https://console.developers.google.com/apis/dashboard
2. Create a project for this application
3. Choose **Credentials** from the menu on the left
4. Create an OAuth Client ID
    - This will require you to configure the **consent screen**. Use any email
    and product name you want.
5. When you're presented with a list of application types, choose **Web
application**
6. Set the authorized JavaScript origins to: http://localhost:5000
7. Set the authorized redirect URIs to: https://www.example.com/oauth2callback
8. Click the "Download JSON" button to download the client secrets json file.

Once you have the file, rename it to **client_secrets.json** and drop it in the
application directory.


### Create the Database

SSH into your VM, as described above, and cd to your application directory.

Run the following command to create the application database:
```
python database_setup.py
```


### Seed the Database (Optional)

SSH into your VM, as described above, and cd to your application directory.

Run the following command to pre-populate the database with initial data:
```
python prepopulate_database.py
```
**Note** - The web application will work without doing this. However, there
won't be any initial categories or items. To create categories, a user
with administrator access (see below) must manually create them.


### Start the Application

SSH into your VM, as described above, and cd to your application directory.

Run the following command:
```
python itemcatalog.py
```

Navigate to http://localhost:5000 in your browser to view the site.


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