import os

from server.script.utils import file_utils


def validate_web_build_exists(project_path):
    web_folder = os.path.join(project_path,'server','script', 'webpage')

    how_to_fix_build_message = \
        'How to fix: ' \
        '\n - PROD: please use stable releases from https://github.com/bugy/script-server/releases/latest' \
        '\n - DEV: please run tools/init.py --no-npm'

    if not os.path.exists(web_folder):
        raise InvalidWebBuildException(web_folder + ' does not exist. \n' + how_to_fix_build_message)

    required_files = ['index.html', 'admin.html', 'login.html', 'js', 'css', 'img']
    for file in required_files:
        file_path = os.path.join(web_folder, file)

        valid = True
        if not os.path.exists(file_path):
            valid = False
        elif os.path.isdir(file_path) and not os.listdir(file_path):
            valid = False

        if not valid:
            raise InvalidWebBuildException('web folder is invalid. \n' + how_to_fix_build_message)


def get_server_version(project_path):
    version_file = os.path.join(project_path, 'version.txt')
    if not os.path.exists(version_file):
        return None

    file_content = file_utils.read_file(version_file).strip()
    if not file_content:
        return None
    return file_content


class InvalidWebBuildException(Exception):
    pass
