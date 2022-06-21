from flask import Flask, request
from typing import Iterable, Optional
import re
from pathlib import Path
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

def query_builder(iterable_var: Iterable, cmd: Optional[str], value: Optional[str]) -> Iterable:
    mapped_data = map(lambda v: v.strip(), iterable_var)

    if cmd == 'unique':
        return set(mapped_data)

    if value:
        if cmd == 'filter':
            return filter(lambda x: value in x, mapped_data)
        elif cmd == 'regex':
            regex = re.compile(value)
            return filter(lambda x: regex.search(x), mapped_data)
        elif cmd == 'map':
            arg = int(value)
            return map(lambda x: x.split(' ')[arg], mapped_data)
        elif cmd == 'limit':
            arg = int(value)
            return list(mapped_data)[:arg]
        elif cmd == 'sort':
            reverse = value == 'desc'
            return sorted(iterable_var, reverse=reverse)
    return mapped_data


@app.route("/perform_query", methods=['GET', 'POST'])
def perform_query():
    if request.method == 'POST':
        data = request.json
    else:
        data = request.args

    file_name = data['file_name'] or None
    cmd1 = data['cmd1'] or None
    value1 = data['value1'] or None
    cmd2 = data['cmd2'] or None
    value2 = data['value2'] or None

    if file_name is None:
        return BadRequest

    file_path = Path.cwd() / 'data' / file_name
    if Path.exists(file_path):
        with open(file_path, 'r', encoding='utf8') as fd:
            result = query_builder(fd, cmd1, value1)
            result = query_builder(result, cmd2, value2)
            result = '\n'.join(result)

        return app.response_class(result, 200, content_type="text/plain")
    else:
        return BadRequest


if __name__ == "__main__":
    app.debug = True
    app.run(host="localhost", port=5000)
