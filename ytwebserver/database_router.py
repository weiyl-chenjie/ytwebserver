from django.conf import settings

DATABASE_MAPPING = settings.DATABASE_APPS_MAPPING


"""
官方实例：
class AuthRouter:
    
    # A router to control all database operations on models in the auth application.
    
    def db_for_read(self, model, **hints):
        
        # Attempts to read auth models go to auth_db.
        # 将所有读操作指向特定的数据库。
        if model._meta.app_label == 'auth':
            return 'auth_db'
        return None

    def db_for_write(self, model, **hints):
     
        # Attempts to write auth models go to auth_db.
        # 将所有写操作指向特定的数据库。
        if model._meta.app_label == 'auth':
            return 'auth_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
     
        # Allow relations if a model in the auth app is involved.
        # 允许使用相同数据库的应用程序之间的任何关系
        if obj1._meta.app_label == 'auth' or \
           obj2._meta.app_label == 'auth':
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
    
        # Make sure the auth app only appears in the 'auth_db' database.
        # 确保身份验证应用程序只出现在“authdb”数据库中。
        if app_label == 'auth':
            return db == 'auth_db'
        return None
"""


class DatabaseAppsRouter(object):
    """
        A router to control all database operations on models for different
        databases.

        In case an app is not set in settings.DATABASE_APPS_MAPPING, the router
        will fallback to the `default` database.

        Settings example:

        DATABASE_APPS_MAPPING = {'app1': 'db1', 'app2': 'db2'}
        """

    def db_for_read(self, model, **hints):
        """"Point all read operations to the specific database."""
        """将所有读操作指向特定的数据库。"""
        if model._meta.app_label in DATABASE_MAPPING:
            return DATABASE_MAPPING[model._meta.app_label]
        return None

    def db_for_write(self, model, **hints):
        """Point all write operations to the specific database."""
        """将所有写操作指向特定的数据库。"""
        if model._meta.app_label in DATABASE_MAPPING:
            return DATABASE_MAPPING[model._meta.app_label]
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Allow any relation between apps that use the same database."""
        """允许使用相同数据库的应用程序之间的任何关系"""
        db_obj1 = DATABASE_MAPPING.get(obj1._meta.app_label)
        db_obj2 = DATABASE_MAPPING.get(obj2._meta.app_label)
        if db_obj1 and db_obj2:
            if db_obj1 == db_obj2:
                return True
            else:
                return False
        return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        """
        Make sure the auth app only appears in the 'default'
        database.
        """
        """确保身份验证应用程序只出现在“default”数据库中。"""
        if db in DATABASE_MAPPING.values():
            return DATABASE_MAPPING.get(app_label) == db
        elif app_label in DATABASE_MAPPING:
            return False
        return None
        # if app_label == 'auth':
        #     return db == 'default'
        # return None

