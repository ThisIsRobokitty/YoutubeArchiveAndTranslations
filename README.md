# YoutubeArchiveAndTranslations
This script will use several packages to create translated captions for a video and autoupload to the channel of choice.

autorestarter = runs archive_script.py in an infinite loop

archive_script.py = the main script. It handles ripping audio, running the whisper_package, and running the upload script to youtube.

upload_video.py = the video upload script, which also takes the thumbnail, description, captions, etc.


Requirements:

kinda lazy, will add later
tl;dr, you need at least the stuff at the top of the .py scripts, and also the google youtube api python package