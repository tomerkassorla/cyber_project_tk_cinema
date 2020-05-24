import subprocess
import os
import path_class

DIRECTORY = str(path_class.Path.get_project_path()) + "songs"  # the path of the main project Directory
NAME = "Nevermind"  # the name of the file

file_name_audio = "no name audio"
for file in os.listdir(DIRECTORY):
    if file.endswith(".avi") and file == NAME + ".avi":
        file_name_audio = file[0:-4]
os.rename(DIRECTORY + "\\" + file_name_audio + ".avi", DIRECTORY + "\\" + NAME + ".avi")
subprocess.run(
    [DIRECTORY + "\\" + "ffmpeg", "-y", "-i", DIRECTORY + "\\" + NAME + ".avi", "-f", "wav", "-bitexact", "-acodec",
     "pcm_s16le", "-ar", "22050",
     "-ac", "1", DIRECTORY + "\\" + NAME + ".wav"])
