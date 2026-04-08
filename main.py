import yt_dlp
import pygame
import os
import sys
from pytubefix import Playlist
from pytubefix import YouTube as pytYouTube
import random
import threading
from pydub import AudioSegment
import json
from mutagen.oggvorbis import OggVorbis
import subprocess
import time
from inputimeout import inputimeout


ydl_opts = {}
isFileLoaded = False
loadedFilePath = ""
loadedTitle = ""
pygame.init()
pygame.mixer.init()
currentPlaylist = []
currentQueue = []
_playlistTitle = "NULL"
_loopToggle = "OFF"
_shuffleToggle = "OFF"
_isPaused = ""
_currentIndex = 0
_currentVolume = 5
_currentlyPlaying = []
_homeDirectory = ""
_threads = []
exit_flag = False
purge_flag = False

MUSIC_END = pygame.USEREVENT+1
def purgeThreads():
    global purge_flag
    global _threads

    
    purge_flag = True
    for _thread in _threads:
        _thread.join()
    if len(_threads) > 0:
        _threads = [_threads[-1]]
    purge_flag = False




def threadHandler():
    if len(_threads) > 1:
        purge = _threads[:-1]
        _threads = [_threads[-1]]
        purgeThreads()

try:

    def showError(errorIndex, inputDiag=True, var=None):
        errors = {
            "8_UIvolumeInput_ValErr": f"Error, Input value must be between min and max.\nSupplied Value: {var}"""
        }
        if errorIndex in errors.keys():
            print(errors[errorIndex])
        else:
            print(f"Error, no errorIndex found for {errorIndex}")
        if inputDiag == True:
            input("Press enter to continue...")

    def clear():
        pass
        # try:
        #     os.system("cls")
        # except:
        #     os.system("clear")

    # def convert_mp3_to_ogg(input_mp3_path, output_ogg_path, returnPath=False, deleteMP3=False):
    #         print(os.getcwd())
    #         try:
    #             try:
    #                 audio = AudioSegment.from_file(input_mp3_path, "mp3")
    #             except:
    #                 audio = AudioSegment.from_file(input_mp3_path, format="mp4")
    #             audio.export(output_ogg_path, format="ogg")
    #             #print(f"Successfully converted '{input_mp3_path}' to '{output_ogg_path}'")
    #             if returnPath == True:
    #                 return output_ogg_path
    #             if deleteMP3 == True:
    #                 os.remove(input_mp3_path)
    #         except Exception as e:
    #             print(f"Error converting file: {e}")
    #             input("Press enter to continue...")
    #             exit()

    def convert_mp3_to_ogg(input_mp3_path, output_ogg_path, returnPath=False, deleteMP3=False):
            print(os.getcwd())
            try:
                subprocess.run(["ffmpeg", "-y", "-i", input_mp3_path, output_ogg_path])
                #print(f"Successfully converted '{input_mp3_path}' to '{output_ogg_path}'")
                if returnPath == True:
                    return output_ogg_path
                if deleteMP3 == True:
                    os.remove(input_mp3_path)
            except Exception as e:
                print(f"Error converting file: {e}")
                input("Press enter to continue...")
                exit()

    def dwl_mp3(link, index, returnPath=False, deleteMP3=False):
        print(link)
        yt = pytYouTube(link)
        stream = yt.streams.filter(only_audio=True).first()
        #os.chdir(f"sd/playlists/{_playlistTitle}")
        stream.download(filename=f"{index}.mp3")
        #os.chdir(currentPath)
        if returnPath == True:
            return convert_mp3_to_ogg(f"{index}.mp3", f"{index}.ogg", True)
        else:
            convert_mp3_to_ogg(f"{index}.mp3", f"{index}.ogg", False)

    def menu_updater():
        print("UPDATED MENU")
        menu()

    def check_event():
        global exit_flag
        global purge_flag
        global _isPaused
        def main_loop():
            while not purge_flag and not exit_flag:
                #print("check event")
                for event in pygame.event.get():
                    print(f"TYPE:{event.type}")
                    if event.type == MUSIC_END:
                        print("MUSIC END")
                        loadNextFile()
                        pygame.mixer.music.set_endevent(MUSIC_END)
                        clear()
                        menuUpdateThread = threading.Thread(target=menu_updater)
                        menuUpdateThread.start()
                time.sleep(0.5)
            print("loop exited")
        main_loop()
        print("THREAD EXITED")


    def loadFile(index):
        purgeThreads()
        checker = threading.Thread(target=check_event)
        checker.start()
        _threads.append(checker)   

        os.chdir(_homeDirectory)
        file_path = currentQueue[index][1]
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.set_endevent(MUSIC_END)
        _currentIndex = index
        

    def loadNextFile():
        global _currentIndex
        if _shuffleToggle == "OFF":
            if _currentIndex < len(currentQueue) - 1:
                _currentIndex += 1
                loadFile(_currentIndex)
        else:
            _currentIndex = random.randint(0, currentPlaylist.length-1)
            loadFile(_currentIndex)
        if not _isPaused == "[+]":
            playFile()

    def loadPrevFile():
        global _currentIndex
        if _shuffleToggle == "OFF":
            if _currentIndex > 0:
                _currentIndex -= 1
                loadFile(_currentIndex)
        else:
            _currentIndex = random.randint(0, currentPlaylist.length-1)
            loadFile(_currentIndex)
        if not _isPaused == "[+]":
            playFile()
        

    def playlistHandler(redownload=False):
        global currentPlaylist
        global _homeDirectory
        purgeThreads()
        checker = threading.Thread(target=check_event)
        checker.start()
        _threads.append(checker)
        _homeDirectory = os.getcwd()

        if redownload or not os.path.exists(f"sd/playlists/{_playlistTitle}"):
            if not os.path.exists(f"sd/playlists/{_playlistTitle}"):
                os.mkdir(f"sd/playlists/{_playlistTitle}")
            os.chdir(f"sd/playlists/{_playlistTitle}")

            videoTitles = []

            for index, video in enumerate(currentPlaylist.video_urls):
                yt = pytYouTube(video)
                title = yt.title
                oggPath = dwl_mp3(video, index, True, True)
                currentQueue.append([title, oggPath])
                videoTitles.append(title)

            if redownload or not os.path.exists("roster.txt"):
                with open("roster.txt", "w") as f:
                    for videoTitle in videoTitles:
                        f.write(f"{videoTitle}\n")
                    f.close()

            for file in os.listdir(os.getcwd()):
                if "mp3" in file[-4:]:
                    os.remove(file)
        if not f"sd/playlists/{_playlistTitle}" in os.getcwd():
            os.chdir(f"sd/playlists/{_playlistTitle}")
        if os.path.exists(f"roster.txt"):
            with open(f"roster.txt", "r") as f:
                content = f.read()
                rosterTitles = content.split("\n")[:currentPlaylist.length]
                f.close()
            print(rosterTitles)
            for index, file in enumerate(os.listdir(os.getcwd())):
                if file.endswith(".ogg"):
                    print(file)
                    print(index)
                    currentQueue.append([rosterTitles[index], f"sd/playlists/{_playlistTitle}/{file}"])
        else:
            for file in os.listdir(os.getcwd()):
                if file.endswith(".ogg"):
                    currentQueue.append([file, f"sd/playlists/{_playlistTitle}/{file}"])
        os.chdir(_homeDirectory)
        print(currentQueue)




    def playFile():
        #purgeThreads()
        pygame.mixer.music.play()
        pygame.mixer.music.set_endevent(MUSIC_END)



    def pauseFile():
        global _isPaused
        if _isPaused == "":
            _isPaused = "[+]"
            pygame.mixer.music.pause()
            return
        if _isPaused == "[+]":
            _isPaused = ""
            pygame.mixer.music.unpause()
            return

    def stopFile():
        pygame.mixer.music.rewind()

    def skipFile():
        global _isPaused
        global isFileLoaded
        purgeThreads()
        checker = threading.Thread(target=check_event)
        checker.start()
        _threads.append(checker)    
        loadNextFile()
        #playFile()
        if _isPaused == "[+]":
            _isPaused = ""
            pygame.mixer.music.unpause()

    def prevFile():
        #purgeThreads()    
        global _isPaused
        global isFileLoaded
        purgeThreads()
        checker = threading.Thread(target=check_event)
        checker.start()
        _threads.append(checker)
        loadPrevFile()
        #playFile()
        if _isPaused == "[+]":
                _isPaused = ""
                pygame.mixer.music.unpause()


    def setVolume():
        global _currentVolume
        pygame.mixer.music.pause()
        UIvolumeInput = input("Input 0-10 > ")
        try:
            UIvolumeInput = int(UIvolumeInput)
            if UIvolumeInput <= 10 and UIvolumeInput >= 0:
                _currentVolume = UIvolumeInput
            else:
                showError("8_UIvolumeInput_ValErr", True, UIvolumeInput)
        except:
            pass
        level = UIvolumeInput
        converted_volume = level / 10.0

        pygame.mixer.music.set_volume(converted_volume)
        pygame.mixer.music.unpause()


    def menu():
        global _playlistTitle
        global currentPlaylist
        global _shuffleToggle
        global _loopToggle
        global _isPaused
        global _currentVolume
        #print(currentQueue)
        print(_threads)
        if len(currentQueue) > 0:
            playing = currentQueue[_currentIndex][0]
        else:
            playing = "NONE"
        menuOpts = f"""
    ==========================
    Currently Playing | {playing}

    1. Set Playlist   | {_playlistTitle} 
    2. Toggle Shuffle | {_shuffleToggle}  | 
    3. Toggle Loop    | {_loopToggle}  |

    4. Play   >
    5. Pause || {_isPaused}
    6. Rewind <
    7. Next  >>
    8. Prev  <<

    9. Volume | {_currentVolume}

    ==========================
    
Input Choice > """
        print(menuOpts, end="", flush=True)
        menuChoice = input("")
        if menuChoice == "1":
            UIplaylistLink = input("Copy & paste the [PLAYLIST] URL > ")
            redownload = input("Redownload Playlist? [y/n] > ").lower()
            currentPlaylist = Playlist(UIplaylistLink)
            _playlistTitle = currentPlaylist.title
            if redownload == "y":
                playlistHandler(True)
            else:
                playlistHandler(False)
            if _shuffleToggle == "OFF":
                loadFile(0)
            else:
                loadFile(random.randint(0, currentPlaylist.length-1))
            clear()
        if menuChoice == "2":
            if _shuffleToggle == "OFF":
                _shuffleToggle = "ON "
            else:
                _shuffleToggle = "OFF"
            clear()
        if menuChoice == "3":
            if _loopToggle == "OFF":
                _loopToggle = "ALL"
            elif _loopToggle == "ALL":
                _loopToggle = "ONE"
            elif _loopToggle == "ONE":
                _loopToggle = "OFF"
            else:
                pass
            clear()
        if menuChoice == "4":
            #purgeThreads()
            playFile()
            clear()
        if menuChoice == "5":
            pauseFile()
            clear()
        if menuChoice == "6":
            stopFile()
            clear()
        if menuChoice == "7":
            #purgeThreads()
            skipFile()
            clear()
        if menuChoice == "8":
            #purgeThreads()
            prevFile()
            clear()
        if menuChoice == "9":
            setVolume()
            clear()
        menu()
    clear()
    menu()

except KeyboardInterrupt:
    exit_flag = True
    purgeThreads()

    