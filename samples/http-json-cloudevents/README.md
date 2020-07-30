## Quickstart

Install dependencies:

```sh
pip3 install -r requirements.txt
```

Start server:

```sh
python3 json_sample_server.py
```

In a new shell, run the client code which sends a structured and binary
cloudevent to your local server:

```sh
python3 client.py http://localhost:3000/
```

## Test

```sh
pytest
```
