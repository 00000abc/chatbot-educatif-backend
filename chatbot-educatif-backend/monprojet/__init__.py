# monprojet/__init__.py
import pymysql
pymysql.version_info = (2, 2, 1, "final", 0)  # Simuler mysqlclient 2.2.1
pymysql.install_as_MySQLdb()