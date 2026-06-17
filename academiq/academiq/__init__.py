# Utilise PyMySQL comme connecteur MySQL/MariaDB afin d'éviter la compilation de
# mysqlclient sur l'hébergement mutualisé O2Switch.
# Sans effet en développement local si PyMySQL n'est pas installé (SQLite).
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
