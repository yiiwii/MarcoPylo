# this file includes the emitter class, which is a moving target in our gameplay

# source: http://ajaxsoundstudio.com/pyodoc/about.html
from pyo import *


# define sound emitter class
# inherit PyoObjects
class Emitter(PyoObject):
    emitterList = []
    path = ['./wav/orange.wav','./pylo.wav']
    def __init__(self,id,sCol,sRow,azi,ele,spn,depth=0.75,lfofreq=0.2,feedback=0.5,mul=1,add=0):
        # Properly initialize PyoObject's basic attributes
        PyoObject.__init__(self)

        # Overwriting parameters in this project
        # Binural parameters 
        self.id = id
        self.r = 5
        self.color = 'green'
        self.sCol, self.sRow = sCol, sRow
        #self.theta = theta
        self.azi = azi
        self.ele = ele
        self.spn = spn
        amp= 1*spn**3
        print('spn=',spn,'amp=' ,amp)
        self.mm = None
        
        self.pyloplayer = SfPlayer(Emitter.path[id+1],speed=1.4,loop=False, mul=amp)
        self.pyfx = Freeverb(self.pyloplayer, damp=.9, bal=.9)
        self.player = SfPlayer(Emitter.path[id],speed=1.0,loop=True, mul=amp)
        self.bin = Binaural(self.player, azimuth=self.azi, elevation=self.ele, azispan=self.spn, elespan=self.spn)

        # reference source: http://ajaxsoundstudio.com/pyodoc/tutorials/pyoobject2.html?highlight=amplitude
        # Properly initialize PyoObject's basic attributes
        # Keep references of all raw arguments
        self._depth = depth
        self._lfofreq = lfofreq
        self._feedback = feedback

        # Convert all arguments to lists for "multi-channel expansion"
        depth, lfofreq, feedback, mul, add, lmax = convertArgsToLists(depth, lfofreq, feedback, mul, add)

        # Apply processing
        self._modamp = Sig(depth, mul=0.005)
        self._mod = Sine(freq=lfofreq, mul=self._modamp, add=0.005)

        # self._base_objs is the audio output seen by the outside world!
        self._base_objs = self.bin.getBaseObjects()


    def __repr__(self):
        return f'emAt({self.sCol},{self.sRow})'


    # method to regenerate Emittor position
    def reGen(self):
        self.uRow = random.randint(6,60-6)
        self.uCol = random.randint(6,80-6)


