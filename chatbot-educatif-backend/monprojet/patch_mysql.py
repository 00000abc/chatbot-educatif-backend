# patch_mysql.py
import django.db.backends.mysql.base
from django.db.backends.mysql.base import DatabaseWrapper

# Patch pour accepter PyMySQL
django.db.backends.mysql.base.Database = type(
    'Database',
    (object,),
    {
        '__version__': (2, 2, 1),
        'threadsafety': 1,
    }
)

# Appliquer le patch
DatabaseWrapper.data_types = DatabaseWrapper._data_types