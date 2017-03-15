# About
This project was created for Linux Server Configuration project of Udacity's full stack developer nano degree program.

The project involves configuring an apache server on a Linux remote server and deploying a previous project "Item Catalog" to the server.

# IP ADDRESS
* http://54.172.181.146/

# URL
* http://54.172.181.146/

# Configurations
* Updated all packages of Linux server as of 15 March 2017
* Changes ssh port from 22 to 2200
* Disabled password login
* Configured UFW to accept connection from ports 2200,80, 123, 443 only
* 443 was added as it is required by facebook for oAuth2
* Synchronized the time zone to UTC
* Installed Postgresql and Flask
* Created a a new database Catolog
* Created user catalog with permissions to login, select, insert, update and delete

# Resources
* GOOGLE oAuth video: https://youtu.be/YLHyeSuBspI
* https://www.digitalocean.com/community/tutorials/
* how-to-deploy-a-flask-application-on-an-ubuntu-vps
* https://www.digitalocean.com/community/tutorials
* how-to-use-roles-and-manage-grant-permissions-in-postgresql-on-a-vps--2
* http://docs.sqlalchemy.org/en/latest/core/engines.html#postgresql# About
* http://flask.pocoo.org/docs/0.12/deploying/mod_wsgi/
* Stackoverflow
