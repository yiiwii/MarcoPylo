# Marco Pylo
## Description
This is a minigame created in Python, inspired by the swimming pool game: Marco Polo.
During the gameplay, you'd explore through a maze to find the source of the sound, leveraging the spatial audio cues.
See this video for more:
https://www.youtube.com/watch?v=8GYdsgnaQmI

## some screen shots
![image](https://github.com/yiiwii/MarcoPylo/blob/main/marco_callout.gif
)

## Shortcuts
press 'Enter' to enter
press arrow keys to move user position and hear the spatial sound
press 'M' to trigger the 'Marco' Shout out

press 'z' or 'x' to modify map complexity(debugging)
press 'v' to reveal the whole map (debugging)

## Credits:
### Library used
pyo(http://ajaxsoundstudio.com/pyodoc/)                   |for spatial audio processing and mixing
cmu_112_graphics.py(https://raw.githubusercontent.com/CMU15-112/module-manager/master/module_manager.py)   |for graphics 
pyaudio(https://pypi.org/project/PyAudio/)               |for audio recording in onboarding


### Media used:
testDrum.wav(http://www.orangefreesounds.com/vintage-analog-drum-machine-disco-beat-127-bpm/)          |Creative Commons Attribution 4.0 International License
orange.wav(https://freesound.org/people/orangefreesounds/sounds/242080/)            |Attribution-NonCommercial 3.0 Unported (CC BY-NC 3.0)
grassFootstep.wav(https://freesound.org/people/Motion_S/sounds/221756/)     |Attribution 3.0 Unported (CC BY 3.0)
marcoDefault.wav      |recorded by yiweih
pyloDefault.wav       |recorded by yiweih


## if run on mac
run main.py to play the game
In order to have recording permission on a mac OS:
you need to run vs code as root user
try run in the terminal: |sudo /Applications/Visual\ Studio\ Code.app/Contents/MacOS/Electron
