import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
import pygame
import os
import threading

os.chdir(os.path.dirname(os.path.realpath(__file__)))

root = tk.Tk()
root.geometry("384x216")
root.title("Raspbian Music Player")

largeFont = font.Font(size=18) #large font for gui elements
PlayPauseState = 0 #if the song is playing or not
#0 = not started yet
#1 = playing
#2 = paused
CurrentSongVar = tk.StringVar() #displays what song is currently playing
VolumeVar = tk.IntVar() #the value is the volume of the song
LoopedColor = None #this should be set to red if the song is being looped. Otherwise it should be None
LoadList = [] #list of loaded files when loading a folder
CurrentTrackNumber = None #the number of the current song (when a folder is loaded)
OneSong = None #sees if one song is playing

#starting value for stringvars
CurrentSongVar.set("No File Selected")
VolumeVar.set(100)

def PlaySong(): #opens a song
    global PlayPauseState
    global VolumeVar
    global OneSong
    LoadedBox.delete(0, tk.END)
    OpenFile = filedialog.askopenfile("r", filetypes=[("Music", "*.mp3")]) #sends a file dialog getting the music file that the user wants to listen too
    pygame.mixer.init() #initializes pygame mixer
    pygame.mixer.music.load(OpenFile.name) #loads the file
    CurrentSongVar.set(f"Current File: {OpenFile.name}") #sets the status text
    PlayPauseState = 0 #makes sure that the program knows that the song hasn't started yet
    ApplySongVolume()
    LoadedBox.insert(tk.END, f"{OpenFile.name}")
    OneSong = True

def PlayPause(): #plays and pauses the music
    global PlayPauseState
    AutoPlayThread = threading.Thread(target=AutoRunThread)
    if PlayPauseState == 0:
        if LoopedColor == "red":
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.play()
            if OneSong == False:
                AutoPlayThread.start()
        PlayPauseState = 1
    elif PlayPauseState == 1:
        pygame.mixer.music.pause()
        PlayPauseState = 2
    elif PlayPauseState == 2:
        pygame.mixer.music.unpause()
        PlayPauseState = 1
        if OneSong == False:
            AutoPlayThread.start()

def PlayStop(): #stops the music
    global PlayPauseState
    PlayPauseState = 0
    pygame.mixer.music.stop()

def PlayUnload(): #unloads the current file from the mixer
    global PlayPauseState
    global LoadList
    PlayPauseState = 0
    pygame.mixer.music.unload()
    LoadedBox.delete(0, tk.END) #clears the LoadedBox
    LoadList = [] #Clears the list of loaded songs
    CurrentSongVar.set("No File Selected")

def ApplySongVolume(): #applys the volume to the current song
    global VolumeVar
    pygame.mixer.music.set_volume((0.01 * VolumeVar.get()))
    print(pygame.mixer.music.get_volume)

def PlusOne(): #adds one volume point to the volume
    global VolumeVar
    VolumeVar.set(VolumeVar.get() + 1)

def MinusOne(): #removes one volume point from the volume
    global VolumeVar
    VolumeVar.set(VolumeVar.get() - 1)

def SongVolume():
    #sets up a new window
    global VolumeVar
    VolWin = tk.Toplevel(root)
    VolWin.title("Set Volume")
    VolWin.geometry("200x100")

    #for centering
    VolWin.columnconfigure(0, weight=1)
    VolWin.columnconfigure(1, weight=1)
    VolWin.columnconfigure(2, weight=1)

    #frames
    VolTopFrame = tk.Frame(VolWin)
    VolTopFrame.pack()
    Volbottomframe = tk.Frame(VolWin)
    Volbottomframe.pack()

    #Normal GUI stuff
    MinusOneButton = tk.Button(VolTopFrame, text="-1", command=MinusOne).pack(anchor="center", side=tk.LEFT)
    VolScale = tk.Scale(VolTopFrame, variable = VolumeVar, from_ = 0, to = 100, orient = tk.HORIZONTAL).pack(anchor="center", side=tk.LEFT)
    PlusOneButton = tk.Button(VolTopFrame, text="+1", command=PlusOne).pack(anchor="center", side=tk.LEFT)
    VolButton = tk.Button(Volbottomframe, text="Apply Volume", command=ApplySongVolume).pack(anchor="center", side=tk.BOTTOM)

def AboutProgram():
    messagebox.showinfo("About Raspbian Music Player", "Raspbian Music Player\nBy Wizard Studios\nVersion 2\nCopyleft MMXXIII - MMXXV, Some Rights Reserved")

def LoopSong():
    global LoopedColor
    global PlayPauseState
    global LoopButton
    pygame.mixer.init()
    if LoopedColor == None:
        pygame.mixer.music.play(-1)
        LoopedColor = "red"
        PlayPauseState = 1
    elif LoopedColor == "red":
        pygame.mixer.music.play()
        LoopedColor = None
        PlayPauseState = 1
    LoopButton = tk.Button(BottomBarFrame, text="🔁", font=largeFont, bg=LoopedColor, command=LoopSong).grid(row=2, column=6)

def LoadFolder():
    global LoadList
    global OneSong
    LoadedBox.delete(0, tk.END) #clears the LoadedBox
    LoadList = [] #Clears the list of loaded songs
    OpenFolder = filedialog.askdirectory() #Asks what folder you want to use
    os.chdir(OpenFolder) #changes directory to said folder
    pygame.mixer.init()
    OneSong = False
    for song in os.listdir(OpenFolder): #lists through the directory of the folder
        if song[-3:] == "mp3": #checks of the files are mp3s
            LoadList.append(song) #adds the songs to the list of loaded songs
            LoadedBox.insert(tk.END, song) #adds the songs to the LoadedBox
    print(LoadList)

def SelectSong(event):
    global LoadList
    global PlayPauseState
    global CurrentTrackNumber
    pygame.mixer.music.unload() #unloads any currently loaded songs
    pygame.mixer.music.load(LoadedBox.get(LoadedBox.curselection())) #loads the song you selected from the list
    CurrentSongVar.set(LoadedBox.get(LoadedBox.curselection())) #sets the status text to show that you have loaded the song
    CurrentTrackNumber = LoadedBox.curselection()[0] #sets the current track number to the track you selected
    print(CurrentTrackNumber)
    PlayPauseState = 0 #makes sure the program knows that no song is playing

def LastTrack():
    global CurrentTrackNumber
    global PlayPauseState
    pygame.mixer.music.unload() #unloads the current song
    if CurrentTrackNumber > 0: #makes sure you aren't trying to play an invalid song
        CurrentTrackNumber -= 1 #changes the current song index to the previous song
    pygame.mixer.music.load(LoadedBox.get(CurrentTrackNumber)) #loads in the new current (previous) song
    CurrentSongVar.set(LoadedBox.get(CurrentTrackNumber)) #Sets the status text to show that the new song is playing
    PlayPauseState = 0 #lets the program know that no song is playing
    print(CurrentTrackNumber)

def NextTrack():
    global CurrentTrackNumber
    global PlayPauseState
    pygame.mixer.music.unload() #unloads the current song
    if CurrentTrackNumber < LoadedBox.size(): #makes sure you aren't trying to play an invalid song
        CurrentTrackNumber += 1 #changes the current song index to the next song
    pygame.mixer.music.load(LoadedBox.get(CurrentTrackNumber)) #loads in the new current (next) song
    CurrentSongVar.set(LoadedBox.get(CurrentTrackNumber)) #Sets the status text to show that the new song is playing
    PlayPauseState = 0 #lets the program know that no song is playing
    print(CurrentTrackNumber)

def AutoRunThread():
    global CurrentTrackNumber
    global PlayPauseState
    while True: 
        if pygame.mixer.music.get_busy() == True: #checks of the song is playing
            if PlayPauseState == 2: #sees if song has been paused
                return #if so, exit thread
        else:
            #moves to the next song
            if CurrentTrackNumber < LoadedBox.size():
                CurrentTrackNumber += 1
            else:
                CurrentTrackNumber = 0
            PlayPauseState = 1
            pygame.mixer.music.load(LoadedBox.get(CurrentTrackNumber))
            pygame.mixer.music.play()
            CurrentSongVar.set(LoadedBox.get(CurrentTrackNumber))
            print(PlayPauseState)

def OpenHelp():
    os.system("help\\RMPII.chm")

#menu bar controls
menu = tk.Menu(root) #main bar
file = tk.Menu(menu, tearoff=0) #file menu
help = tk.Menu(menu, tearoff=0) #help menu
file.add_command(label="Open Song", command=PlaySong) #choose a song
file.add_command(label="Open Folder", command=LoadFolder) #choose a folder to play through WIP
file.add_command(label="Exit", command=quit) #closes the program
help.add_command(label="Help", command=OpenHelp) #opens the help screen WIP
help.add_command(label="About", command=AboutProgram)
menu.add_cascade(label="File", menu=file) #adds the file menu to the main menu
menu.add_cascade(label="Help", menu=help) #adds the help menu to the main menu
root.configure(menu=menu) #sets the main menu to be the menu for the program

#columnconfigs
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)

#frames
BottomBarFrame = tk.Frame(root) #the frame for all the controls
BottomBarFrame.grid(row=2, column=1, pady=5)
LoadedFrame = tk.Frame(root) #frame for showing loaded files
LoadedFrame.grid(row=1, column=0, columnspan=10)

#normal GUI elements
CurrentSong = tk.Label(root, textvariable=CurrentSongVar).grid(row=0, column=0, columnspan=10) #displays the file being played
PlayPauseButton = tk.Button(BottomBarFrame, text=u"\u23F5\u23F8", font=largeFont, command=PlayPause).grid(row=2, column=3)
StopButton = tk.Button(BottomBarFrame, text=u"\u23F9", font=largeFont, command=PlayStop).grid(row=2, column=1)
UnloadButton = tk.Button(BottomBarFrame, text=u"\u23CF", font=largeFont, command=PlayUnload).grid(row=2, column=0)
VolumeButton = tk.Button(BottomBarFrame, text="🔊", font=largeFont, command=SongVolume).grid(row=2, column=5)
LoopButton = tk.Button(BottomBarFrame, text="🔁", font=largeFont, bg=LoopedColor, command=LoopSong).grid(row=2, column=6)
LoadedScrollBar = tk.Scrollbar(LoadedFrame) #Scrollbar for loaded files box
LoadedScrollBar.grid(row=1, column=1, sticky="ns")
LoadedBox = tk.Listbox(LoadedFrame, height=6, width=30, yscrollcommand=LoadedScrollBar.set) #lists all loaded files
LoadedBox.grid(row=1, column=0)
LoadedScrollBar.config(command=LoadedBox.yview)
LastTrackButton = tk.Button(BottomBarFrame, text=u"\u23EE", font=largeFont, command=LastTrack).grid(row=2, column=2)
NextTrackButton = tk.Button(BottomBarFrame, text=u"\u23ED", font=largeFont, command=NextTrack).grid(row=2, column=4)

#binded Events
LoadedBox.bind("<<ListboxSelect>>", SelectSong)

root.mainloop()