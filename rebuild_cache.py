from eitbapi.utils import _get_tv_program_data
from eitbapi.utils import _get_radio_program_data

import json
import os


def rebuild_cache():
    cache_file = os.path.join(os.path.dirname(__file__), "cache.json")
    data = _get_tv_program_data()
    with open(cache_file, "w") as fp:
        json.dump(data, fp)

    cache_file = os.path.join(os.path.dirname(__file__), "radio-cache.json")
    data = _get_radio_program_data()
    with open(cache_file, "w") as fp:
        json.dump(data, fp)


if __name__ == "__main__":
    rebuild_cache()
