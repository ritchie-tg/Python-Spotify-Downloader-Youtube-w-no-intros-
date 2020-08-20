import os, json, youtube_dl, spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tkinter import filedialog
from tkinter import *
from progress.bar import IncrementalBar
from youtube_search import YoutubeSearch
from pathlib import Path
from time import sleep as delay

def echo(flag, layer, msg):
	buffer = ''
	for i in range(layer):
		buffer = buffer + '\t'

	if flag == '+':
		buffer = buffer + '[+]\t' + msg
	elif flag == '-':
		buffer = buffer + '[-]\t' + msg
	elif flag == '?':
		buffer = buffer + '[?]\t' + msg
	elif flag == '!':
		buffer = buffer + '[!]\t' + msg
	print(buffer + '\n')
	return
echo('!', 0, 'starting spotify playlist downloader...')

#Get output folder - start
dname = None
def openFile():
    global dname
    dname = filedialog.askdirectory()
echo('!', 0, 'select the folder where music will be saved')
popup = Tk()
Button(popup, text='Music save folder', command = openFile()).pack(fill=X)
echo('?', 0, 'confirmation to save ALL music files to {0}? [Y/n] '.format(dname))
res = input()
if res == 'n' or res == 'N':
	echo('!', 1, 'exiting')
	popup.destroy()
	exit(1)
else:
	popup.destroy()
	if Path(dname).is_dir:
		dname = Path(dname)
		echo('+', 1, '{0} - ok.'.format(dname))
	else:
		echo('!', 1, '{0} - is not a directory. exiting.'.format(dname))
#Get output folder - end
#
#Get playlist uri - start

echo('+', 0, '\n\n>>>how to find the playlist uri: right click a playlist in spotify > share > copy uri<<<')
echo('?', 1, 'paste in a spotify playlist uri: ')
res = input()
if not res:
	echo('+', 2, 'invalid playlist format. ex: spotify:playlist:37i9dQZF1DX1YPTAhwehsC. exiting.')
	exit(1)
else:
	playlist_id = res.strip()
	echo('+', 2, '{0} - ok.'.format(playlist_id))
#Get playlist uri - end
#
#Classes - start
class Song:
	def __init__(self, artists, title, duration_ms):
		self.artists = artists
		self.title = title
		try:
			int(duration_ms)
			self.duration = round( ((duration_ms/1000)/60), 2)
		except:
			echo('-', 1, 'Song: track time:({0}) is not a number'.format(duration_ms))
			self.duration = 10.0 #avoid this song later
class Video:
	def __init__(self, title, url_suffix, desc, duration):
		self.title = title
		self.url_suffix = url_suffix
		self.desc = desc
		self.duration = float(duration.replace(':', '.'))
class MyLogger(object):
	def debug(self, msg):
		pass
	def warning(self, msg):
		pass
	def error(self, msg):
		echo('+', 2, msg)
#Classes - end

#spotify api auth - start
auth_file = Path(os.path.dirname(os.path.realpath(__file__))) / 'sp_api_auth.py'
if auth_file.is_file:
	#manual entry of auth
	import sp_api_auth
	client_credentials_manager = SpotifyClientCredentials(sp_api_auth.id, sp_api_auth.secret)
else:
	#env auth
	client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
#spotify api auth - end

try:
	results = sp.playlist(playlist_id)
except Exception as e:
	echo('!', 2, 'error pulling data from playlist {0}\n\nerror details:\n{1}'.format(playlist_id, e))
	exit(2)
#print(json.dumps(results, indent=4))

if results:
	playlist_name = results['name']
	if not len(playlist_name):
		echo('!', 2, 'playlist not found:({0}). exiting.'.format(playlist_name))
		exit(2)
	else:
		echo('+', 2, 'playlist: {0} - ok'.format(playlist_name))
else:
	echo('!', 2, 'playlist results error: no results for playlist:({0}). exiting.'.format(playlist_id))
	exit(2)

song_list=[]
for tr in results['tracks']['items']:
	if tr is not None:
		track=duration=''
		if tr['track']['name'] is not None:
			track = tr['track']['name']
			duration = tr['track']['duration_ms']
		else:
			echo('-', 2, 'no track was found')

		if track is not None:
			artists = ''
			for art in tr['track']['artists']:
				if art['name'] is not None:
					artists = artists + '{0} '.format(art['name'])
		else:
			echo('-', 2, 'no artist was found')

		if len(track) and len(artists) and duration > 0:
			song_list.append(Song(artists, track, duration))

#show playlist content
echo('+', 2, 'playlist content: (title, artists, duration)')
delay(2)
for s in song_list:
	echo('+', 3, '{0}\t{1}\t{2} minutes'.format(s.title, s.artists, s.duration))
	delay(0.05)
echo('+', 2, 'playlist length: {0}'.format(len(song_list)))
delay(2)
echo('!', 1, 'press ctrl+c to cancel this script at anytime. press ENTER to continue...')
res=input()


#youtube download
def my_hook(d):
	if d['status'] == 'downloading':
		#print(d['filename'], d['_percent_str'], d['_eta_str'])
		amnt = float(d['_percent_str'].replace('%',''))
		if amnt == 100:
			bar.finish()
		else:
			bar.next(amnt)
	elif d['status'] == 'finished':
		echo('+', 2, 'done, converting ...')
	else:
		echo('-', 2, 'unkown status youtube_dl - {0}'.format(d['status']))

def Search_Results(title, artists):
	limit = 10
	results1 = YoutubeSearch('{0} {1} audio'.format(title, artists), max_results=limit).to_json()
	results1 = json.loads(results1)
	if not results1 or len(results1) < (limit/2):
		echo('-', 2, 'keyword (audio) does not seem promising. trying (lyrics) instead.')
		results2 = YoutubeSearch('{0} {1} lyrics'.format(title, artists), max_results=limit).to_json()
		results2 = json.loads(results2)
		if not results2 or len(results2) < (limit/2):
			echo('-', 2, 'keyword (lyrics) does not seem promising either. using results with most results.')
			if len(results1) > len(results2):
				echo('+', 3, 'using  results from (audio)')
				return results1
			else:
				echo('+', 3, 'using  results from (lyrics)')
				return results2
		else:
			echo('+', 3, 'using  results from (lyrics)')
			return results2
	else:
		echo('+', 3, 'using  results from (audio)')
		return results1

	echo('!', 3, 'error: no results!')
	return None

songs_failed=songs_passed=0
songs_failed_list=[]
for song in song_list: #playlist
	echo('+', 1, 'working on: {0} - {1}'.format(song.title, song.artists))
	#youtube search
	video_list = []
	potential_videos = []
	target_video = None
	results = Search_Results(song.title, song.artists)
	
	if results is not None and len(results['videos']) > 0:
		for v in results['videos']:
			if len(v['duration']) <= 4:
				#1:00:05? why?
				video_list.append(Video(v['title'], v['url_suffix'], v['long_desc'], v['duration']))
		for v in video_list:
			if 'audio' in v.title or 'Audio' in v.title or 'lyrics' in v.title or 'Lyrics' in v.title:
				#print('duration check - sp:{0} vs yt:{1}'.format(song.duration, v.duration))
				if abs(v.duration - song.duration) < 2:
					potential_videos.append(v)

		if len(potential_videos) > 1:
			potential_videos.sort(key = lambda x: float(x.duration))
			target_video = potential_videos[0]
			echo('+', 2, 'sorted: target found with closest duration - sp:{0} ~ yt:{1}'.format(song.duration, target_video.duration))
		elif len(potential_videos) == 1:
			target_video = potential_videos[0]
			echo('+', 2, 'nonsorted: target found with closest duration - sp:{0} ~ yt:{1}'.format(song.duration, target_video.duration))
		else:
			target_video = None



		if not target_video:
			echo('-', 2, 'unable to find suitable video ({0} by {1})'.format(song.title, song.artists))
			echo('-', 2, '>>> pick a title and duration closest to {0} <<<\n'.format(song.duration))
			iter = 1
			video_list = sorted(video_list, key=lambda x: x.duration, reverse=True)
			for v in video_list:
				print('{0}) {1} \n\t {2} \t {3}'.format(iter, v.title, v.desc, v.duration))
				iter += 1
			try:
				echo('?', 3, 'could not find a suitable video. choose one:')
				res = int(input())
				target_video = video_list[res-1]
			except Exception as e:
				echo('!', 3, 'invalid option: {0}'.format(e))
				delay(2)
				songs_failed += 1
				songs_failed_list.append(song)
				target_video = None

		if target_video:
			file_path = dname / Path('/{0}/{1} - {2}.mp3'.format(dname, song.title, str(song.artists)[:-1]))
			if file_path.is_file():
				echo('!', 3, 'duplicate found for ({0} by {1} at {2}). skipping.'.format(song.title, song.artists, file_path))
				delay(2)
				songs_passed += 1
			else:
				ydl_opts = {
					'format': 'bestaudio/best',
					'postprocessors': [{
						'key': 'FFmpegExtractAudio',
						'preferredcodec': 'mp3',
						'preferredquality': '192',
					}],
					'logger': MyLogger(),
					'progress_hooks': [my_hook],
					'outtmpl': '{0}'.format(file_path),
				}

				bar = IncrementalBar('\t\t\t[+]\tprogress:', suffix='%(percent)d%%')
				with youtube_dl.YoutubeDL(ydl_opts) as ydl:
					try:
						#echo('+', 2, 'downloading: {0}'.format(target_video.url_suffix))
						ydl.download(['https://www.youtube.com' + target_video.url_suffix])
						echo('+', 3, 'conversion complete - /{0}/{1} - {2}.mp3'.format(dname, song.title, song.artists))
						songs_passed += 1
					except Exception as e:
						echo('-', 3, 'error: song download/conversion failed \n\n {0}'.format(e))
						songs_failed += 1
						songs_failed_list.append(song)
				echo('+', 1, 'stats: (passed:{0} failed:{1}) Progress:({2}/{3})'.format(songs_passed, songs_failed, (songs_passed+songs_failed), len(song_list)))
				delay(1)
	else:
		echo('!', 1, 'no results on youtube')
		delay(2)

echo('+', 1, 'done.')
echo('+', 2, 'stats: (passed:{0} failed:{1}) Progress:({2}/{3})'.format(songs_passed, songs_failed, (songs_passed+songs_failed), len(song_list)))
if len(songs_failed_list) > 0:
	echo('+', 1, 'List of songs not downloaded.')
	for s in songs_failed_list:
		echo('-', 2, '{0} by {1}'.format(s.title, s.artists))
echo('!', 1, 'press ENTER to exit...')
res=input()
exit(0)