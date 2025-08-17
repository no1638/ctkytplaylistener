import pygame
import os
import sys
from pytubefix import Playlist
from pytubefix import YouTube as pytYouTube
import random
import threading
import json
import subprocess
import time
import signal

from customtkinter import *
from PIL import Image

pygame.init()
pygame.mixer.init()
global_purgeFlag = False
titleUpdater = []



class App(CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



        self.ydl_opts = {}
        self.isFileLoaded = False
        self.loadedFilePath = ""
        self.loadedTitle = ""
        self.currentPlaylist = None
        self.currentQueue = []
        self._playlistTitle = "NULL"
        self._loopToggle = "N"
        self._shuffleToggle = False
        self._isPaused = False
        self._currentIndex = 0
        self._currentVolume = 5
        self._currentlyPlaying = []
        self._homeDirectory = ""
        self._threads = []
        self.exit_flag = False
        self.purge_flag = False
        self.MUSIC_END = pygame.USEREVENT+1
        self.playlistButtons = []

        # BOTTOM CONTROL BAR
        self.controlButtonWrapper = CTkFrame(master=self, width=201, height=49)
        self.controlButtonWrapper.pack_propagate(False)
        self.controlButtonWrapper.pack(side="bottom", fill="x")
        self.rewindButton = CTkButton(master=self.controlButtonWrapper, text="<", width=43, anchor="center", command=lambda:pygame.mixer.music.rewind())
        self.rewindButton.pack(padx=(44, 3), side="left")
        self.previousButton = CTkButton(master=self.controlButtonWrapper, text="<<", width=43, command=self.prevFile)
        self.previousButton.pack(pady=(0, 0), padx=(0, 3), side="left")
        self.playButton = CTkButton(master=self.controlButtonWrapper, text=">", height=28, width=43, command=self.playFile)
        self.playButton.pack(padx=(0, 3), side="left")
        self.pauseButton = CTkButton(master=self.controlButtonWrapper, text="| | ", height=28, width=43, command=self.pauseFile)
        self.pauseButton.pack(padx=(0, 3), side="left")
        self.nextButton = CTkButton(master=self.controlButtonWrapper, text=">>", width=43, command=self.skipFile)
        self.nextButton.pack(side="left")


        # SONG TITLE FRAME
        self.songTitleWrapper = CTkFrame(master=self, height=53)
        self.songTitleWrapper.pack_propagate(False)
        self.songTitleWrapper.pack(pady=(0, 1), fill="x", side="bottom")
        self.songTitle = CTkLabel(master=self.songTitleWrapper, text="Song Title", font=CTkFont(size=17, weight="normal"), anchor="w")
        self.songTitle.pack(padx=(8, 0), side="left")


        #SONG LIST FRAME
        self.playlistWrapper = CTkScrollableFrame(master=self, orientation="vertical", height=265, bg_color=("gray92", "#171717"), fg_color=("gray86", "#171717"), border_color=("gray65", "#1a1a1a"))
        self.playlistWrapper.pack(pady=(0, 7), fill="x", side="bottom")
        # self.PLACEHOLDER_SONG_BUTTON = CTkButton(master=self.playlistWrapper, text=" Insert Song Title", width=286, height=37, anchor="w", compound="left", corner_radius=0, fg_color=("#676767", "#676767"), font=CTkFont(size=13, weight="normal"))
        # self.PLACEHOLDER_SONG_BUTTON.pack(pady=(0, 6))


        # FRAME AT TOP WITH CONTROLS
        self.topWrapper = CTkFrame(master=self)
        self.topWrapper.pack_propagate(False)
        self.topWrapper.pack(fill="x")
        self.downloadButton = CTkButton(master=self.topWrapper, text="Download YT", width=88, command=self.playlistHandler)
        self.downloadButton.pack(pady=(25, 0), padx=(0, 5), side="right")
        self.shuffleToggle = CTkSwitch(master=self.topWrapper, text="Shuffle", command=setattr(self, '_isPaused', not getattr(self, '_isPaused')))
        self.shuffleToggle.pack(pady=(25, 0), side="right")
        self.loopButton = CTkButton(master=self.topWrapper, text="Loop: N", width=30, command=self.loopButtonCommand)
        self.loopButton.pack(pady=(25, 0), padx=(0, 5), side="right")
        self.playlistSelectMenu = CTkOptionMenu(master=self.topWrapper, width=88, command=self.playlistProxyHandler)
        self.playlistSelectMenu.place(x=175, y=0)

        self.volumeInputSlider = CTkSlider(master=self.topWrapper, from_=0, to=10, number_of_steps=10, orientation="horizontal", width=156, command=self.setVolume)
        self.volumeInputSlider.place(x=0, y=6)
        self.volumeLabel = CTkLabel(master=self.topWrapper, text=f"Volume", font=CTkFont(size=13, weight="normal"))
        self.volumeLabel.place(x=7, y=20)

        optvalues = []
        for item in os.listdir(f"sd/playlists"):
            if os.path.isdir(f"sd/playlists/{item}"):
                optvalues.append(item)
        self.playlistSelectMenu.configure(values=optvalues)
        self.playlistSelectMenu.set("Playlists                  ")

        _songTitleUpdater = threading.Thread(target=self.songTitleHandler)
        _songTitleUpdater.start()
        titleUpdater.append(_songTitleUpdater)

    def songTitleHandler(self):
        while not global_purgeFlag:
            if len(self.songTitle.cget("text")) > 25:
                time.sleep(2)
                for i, char in enumerate(self.songTitle.cget("text")):
                    if global_purgeFlag:
                        break
                    #print(f"LEN {len(self.songTitle.cget('text'))}")
                    #print(i)
                    self.songTitle.configure(text=self.songTitle.cget("text")[i+1:])
                    self.update()
                    if i >= len(self.songTitle.cget("text"))+4/2:
                        if len(self.currentQueue) > 0:
                            self.songTitle.configure(text=self.currentQueue[self._currentIndex][0])
                            self.update()
                            break
                        else:
                            self.songTitle.configure(text="Song Title")
                            self.update()
                            break
                    time.sleep(1)

            time.sleep(0.5)


    def purgeThreads(self):
        self.purge_flag = True
        for _thread in self._threads:
            _thread.join()
        if len(self._threads) > 0:
            self._threads = [self._threads[-1]]
        purge_flag = False



    def showError(self, errorIndex, inputDiag=True, var=None):
        pass
        # errors = {
        #     "8_UIvolumeInput_ValErr": f"Error, Input value must be between min and max.\nSupplied Value: {var}"""
        # }
        # if errorIndex in errors.keys():
        #     print(errors[errorIndex])
        # else:
        #     print(f"Error, no errorIndex found for {errorIndex}")
        # if inputDiag == True:
        #     input("Press enter to continue...")

    def menu_updater(self):
        pass

    def check_event(self, internalIndex):
        while not self.purge_flag and not self.exit_flag:
            #print("check event")
            if self._currentIndex != internalIndex:
                break
            for event in pygame.event.get():
                print(f"TYPE:{event.type}")
                if event.type == self.MUSIC_END:
                    print("MUSIC END")
                    self.loadNextFile()
                    pygame.mixer.music.set_endevent(self.MUSIC_END)
                    self.clear()
                    # menuUpdateThread = threading.Thread(target=menu_updater)
                    # menuUpdateThread.start()
            time.sleep(0.5)
        print("THREAD EXITED")

    def clear(self):
        pass
        # try:
        #     os.system("cls")
        # except:
        #     os.system("clear")

    def convert_mp3_to_ogg(self, input_mp3_path, output_ogg_path, returnPath=False, deleteMP3=False):
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

    def dwl_mp3(self, link, index, returnPath=False, deleteMP3=False):
        print(link)
        yt = pytYouTube(link)
        stream = yt.streams.filter(only_audio=True).first()
        #os.chdir(f"sd/playlists/{_playlistTitle}")
        stream.download(filename=f"{index}.mp3")
        #os.chdir(currentPath)
        if returnPath == True:
            return self.convert_mp3_to_ogg(f"{index}.mp3", f"{index}.ogg", True)
        else:
            self.convert_mp3_to_ogg(f"{index}.mp3", f"{index}.ogg", False)



    def loadFile(self, index):
        #self.purgeThreads()   
        print(index)
        print(self.currentQueue)
        os.chdir(self._homeDirectory)
        file_path = self.currentQueue[index][1]
        if self._playlistTitle in os.path.basename(os.getcwd()):
            pygame.mixer.music.load(file_path.split("/")[-1])
        else:
            pygame.mixer.music.load(file_path)
        pygame.mixer.music.set_endevent(self.MUSIC_END)
        self._currentIndex = index
        checker = threading.Thread(target=self.check_event, args=(self._currentIndex,))
        checker.start()
        self._threads.append(checker)
        self.songTitle.configure(text=f"{self.currentQueue[index][0]}")
        self.update()
        

    def loadNextFile(self):
        if self._loopToggle == "N" or self._loopToggle == "A":
            if self.shuffleToggle.get() == 0:
                if self._currentIndex < len(self.currentQueue) - 1:
                    self._currentIndex += 1
                    self.loadFile(self._currentIndex)
                    return
                if self._loopToggle == "A":
                    print("IS A")
                    if self._currentIndex == len(self.currentQueue)-1:
                        self._currentIndex = 0
                        self.loadFile(self._currentIndex)
                        pygame.mixer.music.play()
                        return
                    if self._currentIndex < len(self.currentQueue) - 1:
                        self._currentIndex += 1
                        self.loadFile(self._currentIndex)
                        return
                if self._loopToggle == "N":
                    print("IS N")
                    if self._currentIndex == len(self.currentQueue)-1:
                        print("setting to 0")
                        self._currentIndex = 0
                        self.loadFile(self._currentIndex)
                        pygame.mixer.music.pause()
                        return
            else:
                self._currentIndex = random.randint(0, len(self.currentQueue)-1)
                self.loadFile(self._currentIndex)
        if self._loopToggle == "O":
            self.loadFile(self._currentIndex)
        try:
            pygame.mixer.music.unpause()
        except:
            pass
        self._isPaused = False
        self.playFile()

    def loadPrevFile(self):
        if self.shuffleToggle.get() == 0:
            if self._currentIndex > 0:
                self._currentIndex -= 1
                self.loadFile(self._currentIndex)
        else:
            self._currentIndex = random.randint(0, len(self.currentQueue)-1)
            self.loadFile(self._currentIndex)
        try:
            pygame.mixer.music.unpause()
        except:
            pass
        self._isPaused = False
        self.playFile()


    def playlistProxyHandler(self, choice):
        print(choice)
        self._playlistTitle = choice
        for button in self.playlistButtons:
            button.destroy()
        self.playlistButtons = []
        self.playlistHandler(False, choice)


    def playlistHandler(self, promptURL=True, selectedTitle=None):
        if len(self.currentQueue) > 0:
            self.currentQueue = []
        redownload = False
        playlistURL = None

        if promptURL == True or not os.path.exists(f"sd/playlists/{self._playlistTitle}"):
            self.playlistEntryDiag = CTkInputDialog(text="Enter Playlist URL > ", title="Youtube Playlist Downloader")
            playlistURL = self.playlistEntryDiag.get_input()
            self.currentPlaylist = Playlist(playlistURL)
            self._playlistTitle = self.currentPlaylist.title
        if promptURL == False:
            self._playlistTitle = selectedTitle

        if os.path.exists(f"sd/playlists/{self._playlistTitle}"):
            self.redownloadEntryDiag = CTkInputDialog(text="Redownload Playlist? [y/N] > ", title="Youtube Playlist Downloader")
            redownloadIn = self.redownloadEntryDiag.get_input()
            if redownloadIn.lower() == "y":
                redownload = True
                with open(f"sd/playlists/{self._playlistTitle}/roster.txt", "r") as f:
                    playlistURL = f.read().split("\n")[-1]
                    f.close()
                self.currentPlaylist = Playlist(playlistURL)
                self._playlistTitle = self.currentPlaylist.title

        
        

        # checker = threading.Thread(target=self.check_event)
        # checker.start()
        # self._threads.append(checker)
        self._homeDirectory = os.getcwd()

        if redownload or not os.path.exists(f"sd/playlists/{self._playlistTitle}"):
            if not os.path.exists(f"sd/playlists/{self._playlistTitle}"):
                os.mkdir(f"sd/playlists/{self._playlistTitle}")
            os.chdir(f"sd/playlists/{self._playlistTitle}")

            videoTitles = []

            for index, video in enumerate(self.currentPlaylist.video_urls):
                yt = pytYouTube(video)
                title = yt.title
                oggPath = self.dwl_mp3(video, index, True, True)
                #self.currentQueue.append([title, oggPath])
                videoTitles.append(title)

            if redownload or not os.path.exists("roster.txt"):
                with open("roster.txt", "w") as f:
                    for videoTitle in videoTitles:
                        f.write(f"{videoTitle}\n")
                    f.write(playlistURL)
                    f.close()

            for file in os.listdir(os.getcwd()):
                if "mp3" in file[-4:]:
                    os.remove(file)
        if not f"{self._playlistTitle}" in os.getcwd():
            print(os.getcwd())
            print(self._playlistTitle)
            os.chdir(f"sd/playlists/{self._playlistTitle}")
        if os.path.exists(f"roster.txt"):
            with open(f"roster.txt", "r") as f:
                content = f.read()
                rosterTitles = content.split("\n")[:len(os.listdir(os.getcwd()))-1]
                f.close()
            print(rosterTitles)
            for index, file in enumerate(os.listdir(os.getcwd())):
                if file.endswith(".ogg"):
                    print(file)
                    print(index)
                    self.currentQueue.append([rosterTitles[index], f"sd/playlists/{self._playlistTitle}/{file}"])
        else:
            print("CALLED ELSE")
            for file in os.listdir(os.getcwd()):
                if file.endswith(".ogg"):
                    self.currentQueue.append([file, f"sd/playlists/{self._playlistTitle}/{file}"])
        #os.chdir(self._homeDirectory)
        print(self.currentQueue)
        #self.currentQueue = []
        for item in self.currentQueue:
            song_title = item[0]  # Get the song title from the inner list
            song_button = CTkButton(master=self.playlistWrapper, text=song_title, width=286, height=37, anchor="w", compound="left", corner_radius=0, fg_color=("#676767", "#676767"), font=CTkFont(size=13, weight="normal"))
            song_button.configure(command=lambda obj=song_button: self.songButtonOnClick(obj))
            song_button.pack(pady=(0, 6))
            self.playlistButtons.append(song_button)

        if self.shuffleToggle.get() == 0:
            self.loadFile(self._currentIndex)
        if self.shuffleToggle.get() == 1:
            self.loadFile(random.randint(0, len(self.currentQueue)-1))


    def playFile(self):
        #self.purgeThreads()
        pygame.mixer.music.play()
        pygame.mixer.music.set_endevent(self.MUSIC_END)

    def pauseFile(self):
        if self._isPaused == False:
            self._isPaused = True
            pygame.mixer.music.pause()
            return
        if self._isPaused == True:
            self._isPaused = False
            pygame.mixer.music.unpause()
            return

    def stopFile(self):
        pygame.mixer.music.rewind()

    def skipFile(self):
        #self.purgeThreads()
        #self._threads.append(checker)    
        self.loadNextFile()
        #playFile()
        if self._isPaused:
            self._isPaused = False
            pygame.mixer.music.unpause()

    def prevFile(self):
        #self._threads.append(checker)
        self.loadPrevFile()
        #playFile()
        if self._isPaused:
                self._isPaused = False
                pygame.mixer.music.unpause()


    def setVolume(self, value):
        pygame.mixer.music.pause()
        UIvolumeInput = value
        _currentVolume = value
        converted_volume = UIvolumeInput / 10.0
        pygame.mixer.music.set_volume(converted_volume)
        pygame.mixer.music.unpause()
        self.update()

    def songButtonOnClick(self, widget):
        selectedTitle = widget.cget("text")
        for i, video in enumerate(self.currentQueue):
            if selectedTitle == video[0]:
                self._currentIndex = i
                self.loadFile(self._currentIndex)
                self.playFile()

    def loopButtonCommand(self):
        currentSelect = self.loopButton.cget("text")
        if currentSelect == "Loop: N":
            self.loopButton.configure(text="Loop: A")
            self._loopToggle = "A"
            self.update()
            return
        if currentSelect == "Loop: A":
            self.loopButton.configure(text="Loop: O")
            self._loopToggle = "O"
            self.update()
            return
        if currentSelect == "Loop: O":
            self.loopButton.configure(text="Loop: N")
            self._loopToggle = "N"
            self.update()
            return


def on_closing():
    global global_purgeFlag
    print("closing")
    try:
        pygame.mixer.music.stop()
    except:
        pass
    global_purgeFlag = True
    if len(titleUpdater) > 0:
        titleUpdater[0].join()
    root.destroy()
    os.kill(os.getpid(), signal.SIGTERM)
    exit()

        
set_default_color_theme("green")
root = App()
root.geometry("310x455")
root.protocol("WM_DELETE_WINDOW", on_closing)
root.resizable(False, False)
root.title("Fuckin MP3 player idfk")
root.configure(fg_color=['gray92', '#191919'])
root.mainloop()
            
