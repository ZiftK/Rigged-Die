import os
import json


def dir_exists(dir_path: str) -> bool:
    return os.path.isdir(dir_path)


def file_exists(file_path: str):
    return os.path.isfile(file_path)


def is_graph_root(dir_path: str) -> bool:
    return os.path.isfile(f"{dir_path}\\root.nd")


def create_dir(dir_path: str):
    os.mkdir(dir_path)


def dump_json_in_file(file_path: str, build_params: dict, **kwargs):

    kwargs.setdefault("indent", 2)

    with open(file_path, "w") as file:
        file.seek(0)
        file.write(json.dumps(build_params, **kwargs))


def read_json_from_file(file_path: str, **kwargs):

    with open(file_path, "r") as file:
        dictionary = json.load(file)

    return dictionary


if __name__ == "__main__":
    dct = {
        "peperemi": "asdas",
        "Asdasdasd": "asdasdas",
        "asdasdas": {
            "asdasdasdasd": 1,
            "awdas": 2
        }
    }
    path = "C:\\Users\\ZiftK\\Desktop\\prueba.txt"
    dump_json_in_file(path, dct)
