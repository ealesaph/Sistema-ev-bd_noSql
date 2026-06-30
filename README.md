# Sistema-ev-bd_noSql
1.- Abrir Terminal
2.- Escribir pip install -r requirements.txt

opcion 2:
pip install y el siguiente listado
    Flask
    Flask-SQLAlchemy
    Flask-PyMongo
    psycopg2-binary
    pymongo
    python-dotenv
    PyJWT
    bcrypt
    flask-cors
    faker

Se necesita primero abrir el Docker ( dockeer exec -it basededtos2 bash)
Luego se debe iniciar el contenedor Debian
Luego se debe iniciar el Posgre dentro del Debian con el comando sudo systemcl start postgresql
para vereficar que esta en linea se usa sudo systemctl status postgresql  y al ya estar en linea se entra en la consola con sudo-u postgres psql

Finalmente inciar el MongoDB en otro terminal
poner las credenciales del docker para  poder iniciar el servicio con sudo systemclt status mongod y para vereficar que esta en linea  sudo systemctl status mongod
y para ya iniciarlo se usa mongosh o mongo

Finalmente debemos acceder mediante terminal 