
from customtkinter import *
from PIL import Image

class App(CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.controlButtonWrapper = CTkFrame(master=self, width=201, height=49)
        self.controlButtonWrapper.pack_propagate(False)
        self.controlButtonWrapper.pack(side="bottom", fill="x")
        self.rewindButton = CTkButton(master=self.controlButtonWrapper, text="<", width=43, anchor="center")
        self.rewindButton.pack(padx=(44, 3), side="left")
        self.previousButton = CTkButton(master=self.controlButtonWrapper, text="<<", width=43)
        self.previousButton.pack(pady=(0, 0), padx=(0, 3), side="left")
        self.playButton = CTkButton(master=self.controlButtonWrapper, text=">", height=28, width=43)
        self.playButton.pack(padx=(0, 3), side="left")
        self.pauseButton = CTkButton(master=self.controlButtonWrapper, text="| | ", height=28, width=43)
        self.pauseButton.pack(padx=(0, 3), side="left")
        self.nextButton = CTkButton(master=self.controlButtonWrapper, text=">>", width=43)
        self.nextButton.pack(side="left")
        self.songTitleWrapper = CTkFrame(master=self, height=53)
        self.songTitleWrapper.pack_propagate(False)
        self.songTitleWrapper.pack(pady=(0, 1), fill="x", side="bottom")
        self.songTitle = CTkLabel(master=self.songTitleWrapper, text="Sub Heading", anchor="center", justify="center", font=CTkFont(size=30, weight="normal"))
        self.songTitle.pack(padx=(8, 0), side="left")
        self.playlistWrapper = CTkScrollableFrame(master=self, orientation="vertical", height=265, bg_color=("gray92", "#171717"), fg_color=("gray86", "#171717"), border_color=("gray65", "#1a1a1a"))
        self.playlistWrapper.pack(pady=(0, 7), fill="x", side="bottom")
        self.PLACEHOLDER_SONG_BUTTON = CTkButton(master=self.playlistWrapper, text=" Insert Song Title", width=286, height=37, anchor="w", compound="left", corner_radius=0, fg_color=("#676767", "#676767"), font=CTkFont(size=13, weight="normal"))
        self.PLACEHOLDER_SONG_BUTTON.pack(pady=(0, 6))
        self.topWrapper = CTkFrame(master=self)
        self.topWrapper.pack_propagate(False)
        self.topWrapper.pack(fill="x")
        self.SLIDER16 = CTkSlider(master=self.topWrapper, from_=0, to=100, number_of_steps=100, orientation="horizontal", width=156)
        self.SLIDER16.pack(pady=(0, 78), side="left")
        self.LABEL18 = CTkLabel(master=self.topWrapper, text="Volume")
        self.LABEL18.pack()
        
set_default_color_theme("green")
root = App()
root.geometry("310x500")
root.title("Fuckin MP3 player idfk")
root.configure(fg_color=['gray92', '#191919'])
root.mainloop()
            
