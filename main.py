import pyttsx3
from info import reddit
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import soundfile as sf
import os
import asyncio
from pytube import YouTube

# INITIAL STUFF
def delete_temp(temp):
    for fname in os.listdir(temp):
        fpath = os.path.join(temp, fname)
        try:
            if os.path.isfile(fpath):
                os.unlink(fpath)
        except Exception as e:
            print(e)

video = {}
thread = {}
# pre-define tts
py_obj = pyttsx3.init()
py_obj.setProperty('voice', py_obj.getProperty('voices')[1].id)
py_obj.setProperty('rate', 145)
# Main Input
while True:
    sub = str(input('Subreddit name: r/'))
    if sub != "":
        sp = str(input('Do you want to cache a specific Reddit thread? ["yes/no"]: '))
        if sp.lower() == "yes" or sp.lower() == "y":
            link = str(input("Paste Thread's Link: "))
            if link != "": break
        else:
            break
while True:
    video_duration = str(input('Select Video Duration in minutes [ 0.5 / 1 / 3 / 5 ]: '))
    if video_duration.lower() == "1" or video_duration.lower() == "3" or video_duration.lower() == "5" or video_duration.lower() == "0.75":
        video["video-len"] = float(video_duration) * 60 - 10
        break
x =0
while True:
    bg_link = str(input("Please Provide a Background to use using its youtube link: "))
    if bg_link != "":
        print(f"{'-'*40} \n Getting Background... \n{'-'*40}")
        if bg_link.lower() == "skip":
            print('Skipped Background.')
            break
        try:
            delete_temp("assets/bg")
            print(f'streams: \n {YouTube(bg_link).streams.filter(file_extension="mp4", progressive=True)}')
            streams = YouTube(bg_link).streams.filter(file_extension="mp4", progressive=True)
            high_quality = [stream for stream in streams if int(stream.resolution.split('p')[0]) >= 480]
            print(high_quality)
            high_quality[0].download(filename="background.mp4",output_path="assets/bg")
            print('Downloaded background successfully!')

            break
        except Exception as err:
            print("error:", err, " | try again later or download the file manually in assets/bg")
            if x == 10:
                print(f"Now i'm no genius but I'm pretty sure you're having trouble with your connection... \n Please Download the background manually and put in assets/bg")
                break
            x += 1

subreddit = reddit.subreddit(sub)
hot = subreddit.hot(limit=5)
if sp.lower() == "yes" or sp.lower() == 'y':
    submission = reddit.submission(url=link)
    thread["thread-title"] = submission.title
    thread['id'] = submission.id
    thread['c-quantity'] = len(submission.comments)
    thread['url'] = link
    thread['comments'] = []
    for comment in submission.comments:

        try:
            thread['comments'].append({
                "content": comment.body,
                'c-id': comment.id,
                "c-url": comment.permalink
            })
        except AttributeError as err:
            pass
else:
    for submission in hot:
        if not submission.stickied:
            thread["thread-title"] = submission.title
            thread['id'] = submission.id
            thread['c-quantity'] = len(submission.comments)
            thread['url'] = f'https://reddit.com/r/{sub}/comments/{submission.id}/{(submission.title).replace(" ", "_")}'
            thread['comments'] = []
            for comment in submission.comments:
                try:
                    thread['comments'].append({
                        "content": comment.body,
                        'c-id': comment.id,
                        "c-url": comment.permalink
                    })
                except AttributeError as err:
                    pass
            break

def make_mp3_audios(t):
    print('getting thread ...')
    print('Thread Title:', thread["thread-title"])
    # say & save Title
    length = 0
    delete_temp("assets/sounds/temp")
    py_obj.save_to_file(t['thread-title'], f"assets/sounds/temp/aTitle.mp3")
    py_obj.runAndWait()

    for n, com in enumerate(t['comments']):
        if length >= video['video-len']:
            break
        py_obj.save_to_file(com['content'], f"assets/sounds/temp/comment#{n}.wav")
        py_obj.runAndWait()
        file = sf.SoundFile(f"assets/sounds/temp/comment#{n}.wav")
        duration = round(file.frames / file.samplerate)
        length += duration
        print(f'comment #{n} was generated!')
    print(f' All comments generated! , length: {length} seconds , \n Whole Video estimated duration is: {length + 4} seconds! \n There are {n} comments in total and a title!')
    return n, length

number_of_comments, video["comment_section_length"] = make_mp3_audios(thread)

def generate_screenshots(t):
    delete_temp("assets/imgs/temp")
    print('getting assest png files... ( Can and Will take a long time )')
    with sync_playwright() as sp:
        browser = sp.chromium.launch(headless=True, channel="chrome")

        page = browser.new_page()
        page.goto(t["url"], timeout=0)
        ttl = page.wait_for_selector(f'#t3_{t["id"]}', timeout=0)
        ttl.screenshot(path=f"assets/imgs/temp/aTitle.png")
        print('generated Title screenshot')
        browser.close()
    try:
        async def genertator():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True, channel="chrome")
                page = await browser.new_page()
                for idx, c in enumerate(t["comments"]):
                    if idx >= number_of_comments:
                        break
                    await page.goto(f'https://reddit.com/r/{sub}/comments/{t["id"]}/comment/{c["c-id"]}',timeout=0)
                    scr = await page.wait_for_selector(f'#t1_{c["c-id"]}', timeout=0)
                    await scr.screenshot(path=f"assets/imgs/temp/comment#{idx}.png")
                    print(f'Screenshot #{idx} taken successfully!')
                await browser.close()
                print(f'{idx} Screenshots generated!')
        asyncio.run(genertator())
    except Exception as e:
        print(f'Error! \n {e} \n skipping screenshot...')
generate_screenshots(thread)

print('Generation Process Done')
print('editor started.')

os.chdir('assets')
with open('fabricator.py', "r") as f:
    exec(f.read())

