from pathlib import Path

# Utility function to get the absolute path of a file
def real_path(file_name, path = __file__):
    parent_folder = Path(path).parent
    return parent_folder.joinpath(file_name)