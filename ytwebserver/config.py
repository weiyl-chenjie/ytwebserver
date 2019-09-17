import platform
if platform.system() == 'Windows':
    DATABASE_PASSWORD_default = 'it-profi'
    HOST_default = '10.40.254.196'
    EMAIL_HOST = '10.40.3.8'
    EMAIL_HOST_USER = 'yulin.wei@huf-group.com'
    ADMINS = [('尉玉林', 'yulin.wei@huf-group.com')]
elif platform.system() == 'Linux':
    DATABASE_PASSWORD_default = 'it-profi'
    HOST_default = '192.168.0.4'
    EMAIL_HOST = '10.40.3.8'
    EMAIL_HOST_USER = 'yulin.wei@huf-group.com'
    ADMINS = [('尉玉林', 'yulin.wei@huf-group.com')]
