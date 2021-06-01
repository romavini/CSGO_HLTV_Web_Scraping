import os
import time
import pandas as pd


def get_data_path(filename):
    if not ("datacs" in os.listdir(os.path.join(os.path.dirname(__file__), ".."))):
        os.mkdir(os.path.dirname(__file__), "..", "datacs")

    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "datacs", filename)
    )


def read_datacs(filename: str = "total_details.json") -> pd.DataFrame:
    df = pd.read_json(get_data_path("total_details.json"))

    df["timestamp"] = df.apply(
        lambda row: time.mktime(
            time.strptime(
                f"{str(row['date']).split(' ')[0]} {row['time']}:00",
                "%Y-%m-%d %H:%M:%S",
            )
        ),
        axis=1,
    )

    return df.sort_values("timestamp", axis=0, ascending=False).reset_index(drop=True)
