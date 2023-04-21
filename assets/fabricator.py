import moviepy.editor as mp
import random
import math
import soundfile as sf
import os

# get images + durations
# now we know for how long each image would be visible before swapping to the next one
filenames = [f for f in os.listdir('imgs/temp')]
images = [os.path.join("imgs/temp", f) for f in filenames]
# duration stored respectively to images list
def get_duration(file_list):
    durations = []
    for file in file_list:
        with sf.SoundFile(file) as sound:
            durations.append(math.floor(sound.frames / sound.samplerate))
    return durations

voice_list = [os.path.join(r"sounds\temp",f) for f in os.listdir('sounds/temp')]
audio_objs = [mp.AudioFileClip(f) for f in voice_list]
durations = get_duration(voice_list)
print(voice_list)
print(durations)
# Cut random x minutes snippet from the background
bg = mp.VideoFileClip(f'bg/background.mp4')
if bg.duration <= sum(durations):
    snippet = bg
else:
    start = random.uniform(0, bg.duration - sum(durations))
    snippet = bg.subclip(start, start+ sum(durations))
# 7yd l audio original
snippet = snippet.without_audio()
#Place Screenshots + audio into Video.

clips = []
for image in images:
    img = (mp.ImageClip(image).set_position('center')).set_duration(durations[images.index(image)]+0.5)
    clips.append(img)
concatenated_imagery = mp.concatenate_videoclips(clips)
print(concatenated_imagery.size[0], snippet.w)
if snippet.w < concatenated_imagery.size[0]:
    scale_factor = min(snippet.size[0] / concatenated_imagery.size[0], snippet.size[1] / concatenated_imagery.size[1])
    n= math.ceil(snippet.h / concatenated_imagery.size[0])
    final_video = mp.CompositeVideoClip([snippet, (concatenated_imagery.set_pos('center')).resize(height=((concatenated_imagery.size[1]) * scale_factor))])
    final_video = mp.CompositeVideoClip([snippet, (concatenated_imagery.set_pos('center')).resize(width=snippet.w)])
else: final_video = mp.CompositeVideoClip([snippet, concatenated_imagery.set_pos("center")], size=snippet.size)
audio_obj = [mp.AudioFileClip(f) for f in voice_list]
final_audio = mp.concatenate_audioclips(audio_obj)
final_product = final_video.set_audio(final_audio)
final_product.write_videofile('Result/Final.mp4')

print('Your Video Was made successfully! enjoy!')
