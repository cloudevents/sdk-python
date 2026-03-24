## Image Payloads Quickstart

Install dependencies:

```sh
pip install -r requirements.txt
```

Start server:

```sh
python image_sample_server.py
```

In a new shell, run the client code which sends a structured and binary
cloudevent to your local server:

```sh
python client.py http://localhost:3000/
```

## Test

```sh
pytest
```
