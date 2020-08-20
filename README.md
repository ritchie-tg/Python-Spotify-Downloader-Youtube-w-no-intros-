# Python-Spotify-Downloader-Youtube-w-no-intros-

There are plenty of "Spotify Downloaders" available already. However, they don't take into consideration that videos have intros and whatnot. They make sense for a video, but no for just audio. So this is an example script to strictly require videos to have "audio" or "lyrics" in the title. Otherwise, ask.

This script was quickly thrown together so take it as just an example and expect to customize it. For Windows, you'll have to adjust the directories.

pip install tkniter youtube_dl youtube_search progress. it also uses spotipy, which I had issues with installing via pip. So I included alongside the script for a local imported library.

Edit sp_api_auth.py to include your Spotify API creds. Otherwise, delete it if you have the API creds in env variables.
