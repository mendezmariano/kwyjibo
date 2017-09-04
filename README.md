## Synopsis

Servicio online para gestión de entregas

## Motivation

Gestión orientada a trabajos prácticos de materias de programación.

## Installation

# Dependencies
Python 3.6.2
Ver pip-dependencies


# Setup de ambiente de desarrollo
Ver dev-setup.md


# Ubuntu install

  * Logging configured dir
    /var/log/kwyjibo

  # DATABASE
  * $ mysql -u root -p < __handwork/create_schema.sql

  # APACHE 2 MODS
  * Enabling apache mods.
    $ sudo a2enmod headers


  # WSGI: check https://modwsgi.readthedocs.io/en/develop/user-guides/quick-installation-guide.html
  * $ cd /tmp
  * $ mkdir mod_wsgi
  * $ cd mod_wsgi
  * $ wget https://github.com/GrahamDumpleton/mod_wsgi/archive/4.5.14.tar.gz
  * $ tar xvfz 4.5.14.tar.gz
  * $ cd mod_wsgi-4.5.14
  * $ ./configure --with-python=/usr/bin/python3
  * $ make
  * $ sudo make install
  * echo "LoadModule wsgi_module modules/mod_wsgi.so" >> /etc/apache2/sites-available/some.conf  # Ver esta línea
  * kwyjibo.conf:
[BEGIN CONF]
LoadModule wsgi_module modules/mod_wsgi.so

# Kwyjibo
Listen *:80
<VirtualHost *:80>

    ServerAdmin webmaster@localhost
    ServerName kwyjibo

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/kwyjibo.log combined

    RequestHeader unset Accept-Language
    AddLanguage es *
    LanguagePriority es
    ForceLanguagePriority Prefer

    Alias /robots.txt /var/www/kwyjibo/static/robots.txt
    Alias /favicon.ico /var/www/kwyjibo/static/favicon.ico

    Alias /media/ /var/www/kwyjibo/media/
    Alias /static/ /var/www/kwyjibo/static/

    <Directory /var/www/kwyjibo/static>
      Require all granted
    </Directory>

    <Directory /var/www/kwyjibo/media>
      Require all granted
    </Directory>

    WSGIDaemonProcess kwyjibo processes=2 threads=15 python-path=/var/www/kwyjibo inactivity-timeout=60 display-name=[wsgi-kwyjibo]httpd
    WSGIProcessGroup kwyjibo
    WSGIScriptAlias / /var/www/kwyjibo/kwyjibo/wsgi.py

    <Directory /var/www/kwyjibo/kwyjibo>
      <Files wsgi.py>
        Require all granted
      </Files>
    </Directory>

    <Directory /var/www/env>
      Require all granted
    </Directory>
</VirtualHost>
[END CONF]




  # Troubleshooting
  * locale:
    * "locale.Error: unsupported locale setting"
      * See: http://stackoverflow.com/questions/14547631/python-locale-error-unsupported-locale-setting
      * $ sudo apt-get install language-pack-en-base
        $ sudo dpkg-reconfigure locales
    OR
    * other option found

          ubuntu@srvmock:~$ sudo pip3 install --upgrade pip
          Traceback (most recent call last):
            File "/usr/bin/pip3", line 11, in <module>
              sys.exit(main())
            File "/usr/lib/python3/dist-packages/pip/__init__.py", line 215, in main
              locale.setlocale(locale.LC_ALL, '')
            File "/usr/lib/python3.5/locale.py", line 594, in setlocale
              return _setlocale(category, locale)
          locale.Error: unsupported locale setting
          ubuntu@srvmock:~$ sudo locale-gen es_AR.UTF-8
          Generating locales (this might take a while)...
            es_AR.UTF-8... done
          Generation complete.
          ubuntu@srvmock:~$ sudo pip3 install --upgrade pip
          The directory '/home/ubuntu/.cache/pip/http' or its parent directory is not owned by the current user and the cache has been disabled. Please check the permissions and owner of that directory. If executing pip with sudo, you may want sudo's -H flag.
          The directory '/home/ubuntu/.cache/pip' or its parent directory is not owned by the current user and caching wheels has been disabled. check the permissions and owner of that directory. If executing pip with sudo, you may want sudo's -H flag.
          Collecting pip
            Downloading pip-9.0.1-py2.py3-none-any.whl (1.3MB)
              100% |████████████████████████████████| 1.3MB 853kB/s 
          Installing collected packages: pip
            Found existing installation: pip 8.1.1
              Not uninstalling pip at /usr/lib/python3/dist-packages, outside environment /usr
          Successfully installed pip-9.0.1
          ubuntu@srvmock:~$ 

    #==========================#

# CHROOT installation
See chroot-setup.md

# REVISIONS automation


## API Reference

#Depending on the size of the project, if it is small and simple enough the reference docs can be added to the README. For medium size to larger projects it is important to at least provide a link to where the API reference docs live.
TBD

## Tests

Describe and show how to run the tests with code examples.

## Contributors

Let people know how they can dive into the project, include important links to things like issue trackers, irc, twitter accounts if applicable.

## License

#A short snippet describing the license (MIT, Apache, etc.)
GNU
