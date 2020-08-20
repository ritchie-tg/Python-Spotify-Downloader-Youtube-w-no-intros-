# Python-Spotify-Downloader-Youtube-w-no-intros-

There are plenty of "Spotify Downloaders" available already. However, they include unwanted video intros and whatnot - in a .mp3. This is an example script to strictly require videos to have "audio" or "lyrics" in the title. Or otherwise, ask or skip it.

pip install tkinter youtube_dl youtube_search progress. It also needs spotipy, which I had issues installing via pip. So I include it alongside the script for a local imported library. If your pip install works, you don't need that spotipy folder. Alternatively, go download the latest.

Edit sp_api_auth.py to include your Spotify API creds. Otherwise, delete it and have the API creds in your env variables.

This script was quickly thrown together for LINUX so take it as just an example and expect to customize it. For Windows, you'll have to adjust the directories.
