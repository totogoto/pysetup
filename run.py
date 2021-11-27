import os
import platform
import getpass
import pip
from shutil import copytree, which, copyfile
from contextlib import contextmanager
import requests
import hashlib
import sys
import glob

EXERSIZE_PROJECT_REPO = 'https://github.com/totogoto/python-exercises'
SOURCE_FOLDER = 'src'
DEST_FOLDER = 'exercises'
USERNAME = getpass.getuser()
CONDA_ENV_NAME = 'totogoto'
PLATFORM = platform.system().lower()
SELF_ORIGIN_PATH = "https://raw.githubusercontent.com/totogoto/pysetup/main/run.py"


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_red(msg):
    print(f"{bcolors.FAIL}{msg}{bcolors.ENDC}")


def print_blue(msg):
    print(f"{bcolors.OKBLUE}{msg}{bcolors.ENDC}")


def print_green(msg):
    print(f"{bcolors.OKGREEN}{msg}{bcolors.ENDC}")


def print_orange(msg):
    print(f"{bcolors.WARNING}{msg}{bcolors.ENDC}")


def is_bin_exist(name):
    return which(name) is not None


def remote_file_hash():
    m = hashlib.md5()
    r = requests.get(SELF_ORIGIN_PATH)
    for data in r.iter_content(8192):
        m.update(data)
    return m.hexdigest()


def local_file_hash():
    m = hashlib.md5()
    with open(sys.argv[0], 'rb') as fh:
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()


def check_if_run_changed():
    return local_file_hash() != remote_file_hash()


def run_command(cmd):
    stream = os.popen(cmd)
    op = stream.read()
    return op


@contextmanager
def pushd(dir):
    old_dir = os.getcwd()
    os.chdir(dir)
    yield
    os.chdir(old_dir)


def copy_folder(folder_name):
    src_path = os.path.join(SOURCE_FOLDER, folder_name)
    dest_path = os.path.join(DEST_FOLDER, folder_name)
    if not os.path.isdir(DEST_FOLDER):
        os.mkdir(DEST_FOLDER)
    if not os.path.isdir(src_path):
        print("invalid setup src missing")
        return
    if not os.path.isdir(dest_path):
        copytree(src_path, dest_path)
        print(f"Created {dest_path}.")
    else:
        print(f"{dest_path} exists. Updating")
        #updating worlds directory
        copytree(os.path.join(src_path, 'worlds'), os.path.join(
            dest_path, "worlds"), dirs_exist_ok=True)
        
        #adding new files
        for x in os.listdir(src_path):
            dst_file = os.path.join(dest_path, x)
            if x.endswith(".ipynb") and not os.path.isfile(dst_file):
                copyfile(os.path.join(src_path, x), dst_file)
                print_orange(f"Added: {dst_file}")



def find_project_folder(project_str):
    all_folders = sorted(os.listdir(SOURCE_FOLDER))
    selected = list(filter(lambda f: project_str in f.lower(), all_folders))
    return selected


def copy_project(project_str):
    folders = find_project_folder(project_str)
    if len(folders) == 0:
        print("Invalid Project Name")
        return

    for pname in folders:
        copy_folder(pname)


def get_project_id():
    for _ in range(4):
        project_str = input("Enter Project Name: ")
        if len(project_str.strip()) > 1:
            copy_project(project_str=project_str)
            return
        else:
            print("You need to enter a valid project name")


def setup_exersice():
    from ottopy import __version__
    if os.path.isdir(SOURCE_FOLDER):
        update_project()
    else:
        clone_project()
    f = open(os.path.join(SOURCE_FOLDER, 'version.md'), 'r')
    version_txt = f.read()
    print("\n")
    print_blue(f"- ottopy@{__version__}")
    print_green(version_txt)
    print("\n")


def clone_project():
    run_command(f"git clone {EXERSIZE_PROJECT_REPO} {SOURCE_FOLDER}")


def update_project():
    with pushd(SOURCE_FOLDER):
        run_command(f"git pull --rebase --autostash")


def update_ottopy():
    pip.main(["install", "--upgrade", "ottopy"])


def check_env_is_activated():
    ouput = run_command('conda env list').split("\n")[2:]
    env_names = list(filter(lambda x: "*" in x, ouput))

    print(f"Enviroment detected: {env_names[0]}")
    if CONDA_ENV_NAME not in env_names[0]:
        print(
            f"Please activate conda environment by running: `conda activate {CONDA_ENV_NAME}`")
        return False
    return True


def download_file(url, file_name):
    get_response = requests.get(url, stream=True)
    with open(file_name, 'wb') as f:
        for chunk in get_response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def main():
    if check_env_is_activated():
        if check_if_run_changed():
            download_file(SELF_ORIGIN_PATH, 'run_py_new.py')
            print_red("Run File is Changed. Please Re-RUN the file.")
            os.rename('run.py', 'old_run.py')
            os.rename('run_py_new.py', 'run.py')
            os.remove('old_run.py')
            sys.exit()

        update_ottopy()
        setup_exersice()
        get_project_id()


if __name__ == "__main__":
    main()
