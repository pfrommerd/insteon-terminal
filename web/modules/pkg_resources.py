import os

def resource_filename(pkg_name, file_name):
    path = '/'.join(pkg_name.split('.')[:-1])
    return os.path.join('/app/', path, file_name)
