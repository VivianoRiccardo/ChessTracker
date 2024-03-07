# ChessTracker

ChessTracker is an OpenSource code repository written in python that tracks from chess.com and lichess.org the games of your favourite chess players,
recreates the boards on your local machine using python libraries and stockfish and streams the games on your favourite platforms such as Twitch / Youtube / Kick.
At the moment the implementation is with Chess.com and Twitch.
Future works will involve Youtube / Kick streams and Lichess tracking

ChessTracker is a Linux based implementation.

Docker ubuntu image with base requirements (geckodriver, python3.10, python needed libraries, ffmpeg) is provided.

# Architecture

<p align="center">
  <img src="https://i.ibb.co/Pjp9y2y/chesstracker.png" alt="logo">
</p>

# Requirements

- geckodriver >= 0.34.0 (https://github.com/mozilla/geckodriver/releases) (M - {07/03/2024})
- python >= 3.10 (M - {07/03/2024})
- pip >= 22.0.2 (M -{07/03/2024})
- look at requirements.txt for python libraries (M - {07/03/2024})
- ffmpeg (M - {07/03/2024})
- Firefox Profile Directory already logged in Chess.com (M - {07/03/2024})
- Twitch channel (https://www.twitch.tv/) (M - {07/03/2024})
- Twitch streaming key (M - {07/03/2024})
- Twitch client_id, Twitch client_secret (O - {07/03/2024})
- libvips-dev (M -{07/03/2024})

# JSON

## players.json

Here you can set the players you want to stream from either chess.com or lichess.
At the moment only chess.com (Since is the most used by famous players) is available.
the "priority" field set in the json tells you how important a streamer is. So in this case if the number of players you want to stream
exceeds the number of possible games to set in the frames sent to Twitch/Youtube/Kick the priority parameter lets you prioritize some players rather than others.

## streaming_configuration.json  

Here you can set the streaming key (At the moment availble only for Twitch {07/03/2024}) and the server used for streaming.
As default the first one is the one taken.

## api.json

Here you can define the client_id and client_secret for the api interaction (At the moment {07/03/2024} only twitch is available)

## firefox_profile.json

Here you just select the path of your firefox directory where you have a profile logged into chesscom


# GeckoDriver

```
apt-install wget
wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz
tar -xvzf ./*tar.gz
chmod +x geckodriver
export PATH=$PATH:{path_of_this_readme}/geckodriver
```

# ffmpeg

```
apt-get install -y ffmpeg
```

# libvips-dev

```
apt -y install libvips-dev
```

# Python3.10

```
apt update && apt upgrade -y
apt install software-properties-common -y
add-apt-repository ppa:deadsnakes/ppa
apt install python3.10
apt-get install vim
vim ~/.bashrc
```

- Add this line to the file you opened (~/.bashrc)
```
alias python=python3.10
```

- To save and exit from vim :wq + Enter

- Run the file with source:
```
source ~/.bashrc
```

# Requirements.txt

```
python -m pip install -r requirements.txt
```

# Docker

python3.10, pip22.0.2, all python libraries, libvips-dev, ffmpeg, geckodriver

```
sudo docker pull erre577/chesstracker
sudo docker run -it --net=host --rm -v <ABSOLUTE PATH OF THE PROJECT>:/project erre577/chesstracker /bin/bash --login
```

# Run

```
cd project
python Globalvals.py
```

# To Fix

 - [ ] ffmpeg configuration (to avoid lag and low framerate)
 - [ ] closing connection to twitch server after a while (sometimes)
 - [ ] how frames are sent to twitch

# To update/add
 - [x] Twitch stream
 - [ ] change background image
 - [ ] Youtube stream
 - [ ] Events on chess.com behaves differently w.r.t. game sniping (cannot connect via websocket when a player plays in an evenet e.g. title tuesday)
 - [ ] Twitch API
 - [ ] Youtube API
 - [ ] Lichess sniping
 
