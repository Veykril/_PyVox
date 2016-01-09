import discord
import asyncio
import re
import time
import youtube_dl
from discord.game import Game


if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in.
    discord.opus.load_opus('libopus-0')

# TODO RECREATE THE PLAYER AND MAKE DEFAULTS FOR THE TRY COMMAND AND MAJOR CLEAN UP CAUSE SHITS SLOW AF
class Video:
    """
    a class to handle all video informations
    objects of this class are getting queued up
    """
    def __init__(self, loaderurl, url, user, title="Unknown", uploader="Unknown", duration=-1, view_count=-1):
        self.loaderurl = loaderurl
        self.url = url
        self.title = title.strip()
        self.uploader = uploader
        self.duration = duration
        self.view_count = view_count
        self.user = user
        self.type = type

    def compact_print(self):
        if self.duration == -1:
            return "**{}** by **{}**".format(self.title, self.uploader)
        elif self.view_count == -1:
            return "**{}** by **{}**[{}]".format(self.title, self.uploader, self.format_time())
        else:
            return "**{}** by **{}** ({} views) [{}]".format(self.title, self.uploader, self.view_count, self.format_time())

    def full_print(self):
        return "{} added by <@{}>".format(self.compact_print(), self.user.id)

    def format_time(self):
        minutes = int(self.duration/60)
        rest = self.duration % 60
        return '{}:{}'.format(minutes, '0{}'.format(rest) if rest<10 else rest)


class MusicBot(discord.Client):
    def __init__(self):
        super().__init__()
        self.bot_mention = ''
        self.bound_channel = None
        self.current = None
        self.mention_regex = re.compile('<@[1-9]{18,19}>')
        self.player = None
        self.play_next_song = asyncio.Event()
        self.play_queue = asyncio.Queue()
        self.vote_next = []

    @asyncio.coroutine
    def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        self.bot_mention = self.format_user(self.user)
        print('Mention: {}'.format(self.bot_mention))
        print('------')

    @asyncio.coroutine
    def on_error(self, event_method, *args, **kwargs):
        super().on_error(event_method, args, kwargs)

    @asyncio.coroutine
    def on_message(self, message):
        print('[{}]{}{}: {}'.format(time.asctime(), message.author, self.format_user(message.author), message.content))  # chatlogger
        if message.author == self.user:  # don't listen to yourself
            return
        if message.channel.is_private:
            yield from self.send_message(message.channel, "Don't use this bot via DM")

        split = message.content.split()

        if message.content.startswith('{} i'.format(self.bot_mention)):  # init
            if self.bound_channel is not None:
                return
            channel_to_join = ''
            i = 0
            for string in split:
                if i<2:
                    i += 1
                    continue
                channel_to_join += string+" "
            for channel in message.server.channels:
                if channel.type == discord.ChannelType.voice:
                    if channel.name == channel_to_join.strip():
                        channel_to_join = channel
                        self.bound_channel = message.channel
                        break
            yield from self.join_voice_channel(channel_to_join)
            yield from self.send_message(message.channel, "Binding to text channel <#{}> and voice channel **{}**".format(self.bound_channel.id, channel_to_join))

        elif message.content.startswith('{} d'.format(self.bot_mention)):  # destroy
            if self.bound_channel is None:
                return
            self.play_queue = asyncio.Queue()
            self.player.stop()
            self.player = None
            yield from self.voice.disconnect()
            yield from self.send_message(message.channel, "Unbinding from <#{}> and destroying voice connection".format(self.bound_channel.id))
            self.bound_channel = None
            self.current = None

        elif message.content.startswith('{} version'.format(self.bot_mention)):  # version
            yield from self.send_message(message.channel, "Made by <@95587342839984128> running on PyVox version: {}".format("1.0"))

        if message.channel != self.bound_channel:  # ignore messages that aren't sent in the bound channel
            return

        elif message.content.startswith('{} yt'.format(self.bot_mention)):  # youtube queueing
            m = re.search('https?\:\/\/www\.youtube\.com\/watch\?v=.+', message.content)
            if m == None:
                yield from self.parse_vid_and_queue("https://www.youtube.com/watch?v={}".format(split[2]), "yt", message)
            else:
                yield from self.parse_vid_and_queue(m)

        elif message.content.startswith('{} sc'.format(self.bot_mention)):  # soundcloud queueing
            yield from self.parse_vid_and_queue("https://soundcloud.com/{}".format(split[2]), "sc", message)

        elif message.content.startswith('{} vc'.format(self.bot_mention)):  # vocaroo queueing
            yield from self.parse_vid_and_queue("http://vocaroo.com/i/{}".format(split[2]), "vc", message)

        elif message.content.startswith('{} yp'.format(self.bot_mention)):  # youtube queueing
            yield from self.parse_vid_and_queue("https://www.youtube.com/playlist?list={}".format(split[2]), "yp", message)

        elif message.content.startswith('{} sp'.format(self.bot_mention)):  # soundcloud playlist
            yield from self.parse_vid_and_queue("https://soundcloud.com/{}".format(split[2]), "sp", message)

        elif message.content.startswith('{} yq'.format(self.bot_mention)):  # youtube query
            search = ''
            i = 0
            for string in split:
                if i<2:
                    i += 1
                    continue
                search += string+" "
            yield from self.parse_vid_and_queue("https://www.youtube.com/results?search_query={}".format(search.strip()), "yq", message)

        elif message.content.startswith('{} try'.format(self.bot_mention)):  # queueing
            yield from self.parse_vid_and_queue(split[2], None, message)

        if self.current is None:  # commands after this need the current song reference
            return

        if message.content.startswith('{} list'.format(self.bot_mention)):  # list
            msg = "" if self.current is None else "Currently playing: {}\n".format(self.current.full_print())
            if self.play_queue.qsize() == 0:
                msg += "The queue is empty!"
            else:
                msg += "Current queue:\n"
                for video in self.play_queue._queue:
                    msg += "{}\n".format(video.full_print())
            yield from self.send_message(self.bound_channel, msg)

        if message.content.startswith('{} time'.format(self.bot_mention)):  # time
            if self.player is None or not self.player.is_playing():
                return
            curr_time = int(time.time()-self.player._start)
            curr_time_pretty = time.strftime("%H:%M:%S", time.gmtime(curr_time))
            total_time_pretty = time.strftime("%H:%M:%S", time.gmtime(self.current.duration))
            yield from self.send_message(self.bound_channel, "**{}** / **{}** ({}%)".format(curr_time_pretty, total_time_pretty, int(curr_time/self.current.duration*100)))

        if message.content.startswith('{} n'.format(self.bot_mention)):  # next
            if message.author.id not in self.vote_next and message.author in self.voice.channel.voice_members:
                self.vote_next.append(message.author.id)
                yield from self.send_message(self.bound_channel, "{} voted to skip the current song.".format(message.author))
            if len(self.vote_next) >= 2 or len(self.vote_next) >= ((len(self.voice.channel.voice_members) - 1) / 2):
                self.player.stop()
                yield from self.send_message(self.bound_channel, "Minimum number of votes achieved! Skipping song.")

        if message.content.startswith('{} link'.format(self.bot_mention)):  # link
            yield from self.send_message(self.bound_channel, "Current song url: {}".format(self.current.url))

        if message.content.startswith('{} pause'.format(self.bot_mention)):  # pause
            self.player.pause()
            yield from self.send_message(self.bound_channel, "Current song paused.")

        if message.content.startswith('{} resume'.format(self.bot_mention)):  # resume
            self.player.resume()
            yield from self.send_message(self.bound_channel, "Current song resumed.")

    # ------------------------------------------------------------------------------------------------------------------

    def parse_vid_and_queue(self, videourl, vtype, message):
        ydl = youtube_dl.YoutubeDL({'prefer_ffmpeg': True})
        if vtype == 'yq':
            info = ydl.extract_info(videourl, download=False, process=False)
            if 'user' in info['entries'][0]['url']:
                yield from self.send_message(self.bound_channel, "Found user, try something else")
                return
            info = ydl.extract_info(info['entries'][0]['url'], download=False)
            if 'list=' in info['webpage_url']:  # if playlist was found
                vtype = 'yp'
        else:
            info = ydl.extract_info(videourl, download=False)
        if vtype == 'yp' or vtype == 'sp':
            videos = []
            for entry in info['entries']:
                video_info = {'url': '', 'webpage_url': '', 'title': '', 'uploader': '', 'duration': -1, 'view_count': -1}
                video_info.update(entry)
                video = Video(video_info['requested_formats'][1]['url'] if vtype == 'yp' else video_info['formats'][0]['url'], video_info['webpage_url'], message.author, video_info['title'], video_info['uploader'], video_info['duration'], video_info['view_count'])
                videos.append(video)
            yield from self.mqueue(videos, message)
        else:
            video_info = {'url': '', 'webpage_url': '', 'title': '', 'uploader': '', 'duration': -1, 'view_count': -1}
            video_info.update(info)
            if vtype == 'vc':
                video = Video(video_info['entries'][1]['url'], video_info['webpage_url'], message.author, video_info['title'], video_info['uploader'], video_info['duration'], video_info['view_count'])
            elif vtype == 'sc':
                video = Video(video_info['url'], video_info['webpage_url'], message.author, video_info['title'], video_info['uploader'], video_info['duration'], video_info['view_count'])
            else:
                video = Video(video_info['formats'][0]['url'], video_info['webpage_url'], message.author, video_info['title'], video_info['uploader'], video_info['duration'], video_info['view_count'])
            yield from self.queue(video, message)

    def toggle_next_song(self):
        self.loop.call_soon_threadsafe(self.play_next_song.set)

    def play(self):
        while True:
            if not self.is_voice_connected():
                yield from self.send_message(message.channel, 'Not connected to a voice channel')
                print('not connected')
                return
            self.vote_next = []
            self.play_next_song.clear()
            self.current = yield from self.play_queue.get()

            self.player = self.voice.create_ffmpeg_player(self.current.loaderurl, after=self.toggle_next_song)
            yield from self.send_message(self.bound_channel, "Playing {}".format(self.current.compact_print()))
            yield from self.change_status(game=Game(name=self.current.title))
            self.player.start()
            yield from self.play_next_song.wait()  # waits for the song to finish
            yield from self.send_message(self.bound_channel, "Finished {}".format(self.current.compact_print()))
            self.current = None
            yield from self.change_status(game=Game(name=""))

    def queue(self, video, message):
        yield from self.send_message(self.bound_channel, "Queued {}".format(video.compact_print()))
        yield from self.play_queue.put(video)
        if self.player is None:
            yield from self.play()

    def mqueue(self, videos, message):
        for video in videos:
            yield from self.play_queue.put(video)
            yield from self.send_message(self.bound_channel, "Queued {}".format(video.compact_print()))
        if self.player is None:
            yield from self.play()

    def format_user(self, user):
        return '<@{0.id}>'.format(user)

import sys

if __name__ == '__main__':
    bot = MusicBot()
    bot.run(sys.argv[1], sys.argv[2])
