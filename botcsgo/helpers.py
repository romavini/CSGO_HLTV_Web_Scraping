import os


def get_data_path(filename):
    if not (
        "datacs" in os.listdir(os.path.join(os.path.dirname(__file__), ".."))
    ):
        os.mkdir(os.path.dirname(__file__), "..", "datacs")

    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "datacs", filename)
    )
