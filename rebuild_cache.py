from eitbapi.utils import _get_tv_program_data

import json


def rebuild_cache():
    data = _get_tv_program_data()
    with open('cache.json', 'w') as fp:
        json.dump(data, fp)


if __name__ == '__main__':
    rebuild_cache()
