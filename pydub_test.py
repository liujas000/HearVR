import os
import glob
from pydub import AudioSegment

video_dir = '/Users/jasonliu/treehacks/music/'  # Path where the videos are located
extension_list = ('*.mp3')

os.chdir(video_dir)
for extension in extension_list:
    for video in glob.glob(extension):
        mp3_filename = os.path.splitext(os.path.basename(video))[0] + '.wav'
        AudioSegment.from_file(video).export(mp3_filename, format='wav')