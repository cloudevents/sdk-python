## Quickstart

Install dependencies

```sh
pip3 install -r requirements.txt
```

Start server

```sh
python3 server.py
```

Open a new terminal and run the client code which sends a HTTP POST binary
CloudEvent to your local server

```sh
python3 client.py http://localhost:3000/
```
