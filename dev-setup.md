## Instalación de un ambiente de desarrollo para el proyecto

# Servidor de base de datos
$ sudo apt-get install mysql-server

# Web-server
$ sudo apt-get install 

# Dependencias de python previas a la instalación
$ sudo apt-get install build-essential checkinstall
$ sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
$ sudo apt-get install gettext libz-dev libjpeg-dev libfreetype6-dev libmysqlclient-dev
$ sudo apt-get install apache2 apache2-dev libapache2-mod-wsgi-py3 

NO INSTALAR ESTO
$ sudo apt-get install psutils

# Instalación de Python 3.6.2
$ mkdir /tmp/py-install
$ cd /tmp/py-install
$ wget https://www.python.org/ftp/python/3.6.2/Python-3.6.2.tgz
$ tar zxvf Python-3.6.2.tgz
$ cd Python-3.6.2

$ ./configure --prefix=/usr/local/lib/python3.6.2/ --enable-shared 
$ ./configure --prefix=/usr/local/lib/python3.6.2/ --enable-shared LDFLAGS="-Wl,--rpath=/usr/local/lib/python3.6.2/lib"

$ make
$ sudo make install

# Meter python3.6 en el path
$ echo "" >> ~/.bashrc
$ echo "export PATH=/usr/local/lib/python3.6.2/bin:$PATH" >> ~/.bashrc
$ echo "" >> ~/.bashrc
$ . ~/.bashrc

# Instalar pip para python 3
$ sudo apt-get install python3-pip

$ sudo apt-get install language-pack-en-base
$ sudo dpkg-reconfigure locales
$ sudo pip3 install --upgrade pip

# Instala virtualenv
$ sudo pip3 install virtualenv

# Crear workspace. Elegir el directorio a gusto personal. Este directorio tiene que albergar tanto el ambiente como el proyecto en su directorio trackeado con git. No trackeamos en git el directorio de environment, sólo el proyecto.
$ mkdir -p ~/workspace/python/kwyjibo
$ cd ~/workspace/python/kwyjibo

# Crear ambiente virtual
$ virtualenv -p /usr/local/lib/python3.6.2/bin/python3 env

# Activar ambiente virtual
$ . env/bin/activate

# Clonar proyecto
$ git clone git@github.com:pelgoros/kwyjibo.git
$ git clone https://github.com/pelgoros/kwyjibo.git

# Instalar dependencias con pip (OJO: SIN 'sudo')
$ cd ~/workspace/python/kwyjibo/kwyjibo
$ pip install -r pip-dependencies

# Desactivar ambiente virtual
$ deactivate

