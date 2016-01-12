# PyVox
[![Version](https://img.shields.io/badge/Version-1.0.0-green.svg?style=flat-square)](https://github.com/Hiroyu/_PyVox)
[![Twitter](https://img.shields.io/twitter/follow/_Hiroyu.svg?style=social)](http://twitter.com/_Hiroyu)  
YouTube and Soundcloud playback bot for Discord. Supports some other websites as well.  
Feel free to contribute, I appreciate any help I can get.

## Installation

Use pip installations first

```
pip install git+https://github.com/Rapptz/discord.py@async
```

```
pip install youtube-dl
```

Then, install [ffmpeg](https://www.ffmpeg.org/download.html).
This bot requires [opus](https://www.opus-codec.org/downloads/) to work. If on windows put the opus .dll in to the same folder as the bot file.

## Usage
Run PyVox by using the command line arguments:

```
python pyvox.py bot_email bot_password
```
Replace `bot_email` and `bot_password` with the bot's email and passwords respectively.

Commands are run by mentioning the bot followed by the command:

```
@Bot init
```
Bot = the bot's username

## Commands

`init [voice channel name]`: Initialises the bot to the voice channel and makes him join the given channel. It also binds itself to the text channel this command got executed in.  
`destroy`: Destroys the voice connection and channel binding.  

The following commands are meant for the bound channel:  
`yt [id]`: Queues the youtube video with the given video id.  
`yp [playlist-id]`: Queues a youtube playlist.  
`yq [search-value]`: Queues the first video found by the given search term on youtube.  
`sc [song "ID"]`: Queues the soundcloud audio with the given id.  
`sp [set "ID"]`: Queues a soundcloud playlist.  
`vc [link "ID"]`: Queues a vocaroo voice message.  
`try [url]`: Tries to queue the audio of a video on the given website.  
`list`: Lists the videos on the queue.  
`link`: Sends the link of the currently playing video.  
`next`: Vote to skip the current song.  
`time`: Shows the current playback time.  
