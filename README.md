# music-festival-organizer

Music Festival Organizer for competitive music festivals

## Install

I am using *tabula-py* so we need to install the Java run-time:

```
sudo apt install default-jre
```

Then, clone the repo and install the requirements in a virtual environment:

```
git clone https://github.com/blinklet/music-festival-organizer.git
cd music-festival-organizer
python3 -m venv .venv
source ./venv/bin/activate
pip install -r requirements.txt
```

## Run

```
flask --app mfo.app database create
flask --app mfo.app database test_users
flask --app mfo.app database test_data
flask --app mfo.app run
```

