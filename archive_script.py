import subprocess
import os
import shutil
import time
from PIL import Image
from pydub import AudioSegment
from datetime import datetime

import warnings
import numpy as np

def run_batch_file(batch_file_path):
    status = subprocess.run(batch_file_path, shell=True)
    return status

def scan_files(path):
    video_extensions = [".mp4", ".m4v", ".mkv"]
    image_extensions = [".jpg", ".png", ".webp"]
    desc_extensions = [".description"]
    #files = {"videos": [], "thumbnails": [], "descriptions": []}
    files = {}

    for filename in os.listdir(path):
        base, ext = os.path.splitext(filename)

        if ext in video_extensions:
            if base in files:
                files[base]["video"] = filename
                #files[base]["video_ext"] = ext
            else:
                files[base] = {}
                files[base]["video"] = filename
                #files[base]["video_ext"] = ext
        elif ext in image_extensions:
            if base in files:
                files[base]["thumbnail"] = filename
            else:
                files[base] = {}
                files[base]["thumbnail"] = filename
        elif ext in desc_extensions:
            if base in files:
                files[base]["description"] = filename
            else:
                files[base] = {}
                files[base]["description"] = filename
        #else:
            #raise ValueError("Unsuppported file: " + filename)

    for base in list(files.keys()):
        if "video" not in files[base] or "thumbnail" not in files[base] or "description" not in files[base]:
            print("Removing from list: " + base)
            files.pop(base)

    return files

def convert_webp_to_png(image_file):
    try:
        with Image.open(image_file) as im:
            if im.format == 'WEBP':
                png_file = os.path.splitext(image_file)[0] + '.png'
                im.save(png_file)
                os.remove(image_file)
                print("Removed: " + image_file)
                print("Conversion complete")
    except OSError:
        pass

def check_and_convert(files, folder_path):
    for base, file_group in list(files.items()):
            thumbnail_file = os.path.join(folder_path, file_group["thumbnail"])
            convert_webp_to_png(thumbnail_file)


def run_uploader_script(video_file, thumbnail_file, description_file, title, captions_file):
    with open(description_file, 'r', encoding='utf-8') as f:
        original_description = f.read()

    description = "Original video description: " + original_description
    tags = "Utatane Nasa,phase-connect,archive,vtuber,dragon,phaseconnect,AI,translation"

    return_value = subprocess.call(["python", "upload_video.py",
                     "--file=" + video_file,  
                     "--title=" + title,
                     "--description=" + description,
                     "--keywords=" + tags,
                     "--category=" + "24", #Entertainment
                     "--privacy=" + "public",
                     "--thumbnail=" + thumbnail_file,
                     "--captions=" + captions_file,
                     "--captions_lang=" + "en"])
    return return_value

def sort_files(files):
    sorted_filenames = sorted(files, key=lambda x: (
        x.split(' - ')[0],
        int(x.split(' - ')[1].replace('[Archive] ', '').replace('.', ''))
    ))
    return sorted_filenames

def translate_audio(audio_file, output_dir):
    #encoded_audio_file = audio_file.encode("utf-8")
    #encoded_output_dir = output_dir.encode("utf-8")
    cmd = ["python", "-m", "whisper.whisper", audio_file, "--language", "Japanese", "--task",  "translate", "--output_dir", output_dir, "--output_format", "srt", "--model", "medium"]
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        try:
            decoded_stderr = result.stderr.decode('utf-8')
        except UnicodeDecodeError:
            decoded_stderr = result.stderr.decode('cp1252')
        print("Error from translate: ", decoded_stderr,)
    else:
        print("Transcription saved to: ", output_dir, ", " + datetime.now().strftime('%HH:%MM %m/%d/%Y'))


def main():
        error = 1

        folder_path = r"Nasa Ch. 転寝ナサ 【Phase Connect】"
        audio_path = r"Nasa Ch. 転寝ナサ 【Phase Connect】 Audio"
        caption_path = r"Nasa Ch. 転寝ナサ 【Phase Connect】 Captions"
        uploaded_path = r"Nasa Ch. 転寝ナサ 【Phase Connect】 Uploaded"

        files = scan_files(folder_path)

        #for base, file_info in files.items():
        #    print(f"{base}: {file_info}")

        check_and_convert(files, folder_path)

        sorted_files = sort_files(files)

        # Save the sorted list to a file
        with open('sorted_files.txt', 'w', encoding='utf-8') as f:
            for filename in sorted_files:
                f.write(filename + '\n')

        # cycle through list of files until complete 
        for filename in sorted_files:

        #perform audio rip
        #for videoname in sorted_files:
            video_file = os.path.join(folder_path, files[filename].get("video", ""))
            audio_file = os.path.join(audio_path, filename + ".wav")
            if not os.path.exists(audio_file):
                print("Ripping: " + video_file + ", " + datetime.now().strftime('%HH:%MM %m/%d/%Y'))
                video = AudioSegment.from_file(video_file)
                audio = video.set_channels(1) # change to mono
                audio.export(audio_file, format="wav")
            else:
                print("Audio exists, skipping: ", files[filename].get("video", ""), ", " + datetime.now().strftime('%HH:%MM %m/%d/%Y'))

        #do captioning from audio
        #for audioname in sorted_files:
            audio_file = os.path.join(audio_path, filename + ".wav")
            caption_file = os.path.join(caption_path, filename + ".srt")
            caption_dir = os.path.join(caption_path)
            if not os.path.exists(caption_file):
                print("Begun captioning: " + filename + ", " + datetime.now().strftime('%HH:%MM %m/%d/%Y'))
                translate_audio(audio_file, caption_dir)
                if not os.path.exists(caption_file):
                    print("Captioning issue, " + datetime.now().strftime('%HH:%MM %m/%d/%Y'))
                    error = 1
                break
            else:
                print("Caption exists, skipping:", filename + ".srt")


        #for filename in sorted_files:
            video_file = os.path.join(folder_path, files[filename].get("video", ""))
            thumbnail_file = os.path.join(folder_path, files[filename].get("thumbnail", ""))
            description_file = os.path.join(folder_path, files[filename].get("description", ""))
            caption_file = os.path.join(caption_path, filename + ".srt")

            #print(filename + " \n" + video_file + " \n" + thumbnail_file + " \n" + description_file + " \n" + title + " \n" + "\n")

            print("Prepping to upload: " + filename + ", " + datetime.now().strftime('%HH:%MM %m/%d/%Y'))

            status = 1
            status = run_uploader_script(video_file, thumbnail_file, description_file, filename, caption_file)


            if status != 0:
                print("Upload issue, " + datetime.now().strftime('%HH:%MM %m/%d/%Y'))
                error = status
                break
            else:
                with open('uploaded_files.txt', 'a', encoding='utf-8') as g: #append filename
                    g.write(video_file + '\n')
                #os.remove(video_file)
                #os.remove(description_file)

                # Move video file to uploaded_path
                shutil.move(video_file, os.path.join(uploaded_path, os.path.basename(video_file)))

                # Move thumbnail file to uploaded_path
                shutil.move(thumbnail_file, os.path.join(uploaded_path, os.path.basename(thumbnail_file)))

                # Move description file to uploaded_path
                shutil.move(description_file, os.path.join(uploaded_path, os.path.basename(description_file)))

                # Move caption file to uploaded_path
                shutil.move(caption_file, os.path.join(uploaded_path, os.path.basename(caption_file)))
                
                print("Upload complete, file moved: " + video_file)
                #print("Upload complete, file moved: " + description_file)

                print("Sleep while brief process, " + datetime.now().strftime('%HH:%MM %m/%d/%Y'))
                time.sleep(1 * 30 * 60)  # sleep for 30 minutes
                print("Awake, continue, " + datetime.now().strftime('%HH:%MM %m/%d/%Y'))

        if error != 0:
            error = 0
            print("Error, entering 24 hour sleep, " + datetime.now().strftime('%HH:%MM %m/%d/%Y'))
            time.sleep(24 * 60 * 60)  # sleep for 24 hours
        else:
            print("All operations completed, entering 4 hour sleep, " + datetime.now().strftime('%HH:%MM %m/%d/%Y'))
            time.sleep(4 * 60 * 60)  # sleep for 4 hours

if __name__ == '__main__':
    main()