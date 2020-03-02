from pathlib import Path


def real_path(file_name, path = __file__):
    parent_folder = Path(path).parent
    return parent_folder.joinpath(file_name)