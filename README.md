# PyVox
YouTube and Soundcloud playback bot for Discord. Supports some other websites as well.  
Feel free to contribute, this bot is poorly made by me and I appreciate any help I can get it.

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
Run PyVox by using the command line arguments

```
python pyvox.py botemail botpassword
```
Commands are runned by mentioning the bot followed by the command

```
@Bot init
```

Bot = the bot's name

## Commands

`init [voice channel name]`: Initiliazes the bot to the voice channel and makes him join the given channel. It also binds itself to the text channel this command got executed in.  
`destroy`: Destroys the voice connection and channel binding.  

The following commands are meant for the bound channel:  
`yt [id]`: Queues the youtube video with the given video id.  
`yp [playlist-id]`: Queues a youtube playlist.  
`yq [search-value]`: Queues the first video found by the given search term on youtube.  
`sc [song "ID"]`: Queues the soundcloud audio with the given id.  
`sp [set "ID"]`: Queues a soundcloud playlist.  
`try [url]`: Tries to queue the audio of a video on the given website.  
`list`: Lists the videos on the queue.  
`link`: Sends the link of the currently playing video.  
`next`: Skips the current song.  
`time`: Shows the current playback time.  