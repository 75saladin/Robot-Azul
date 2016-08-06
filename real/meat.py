from rtcmix import *
import math
import random


"""Every instrument here is modeled after my own system of proxying. I have
attempted to create an interface between MINC functions and "instruments" that
I have defined. My instruments call MINC functions, but they handle the
annoyances I have found when dealing with MINC. The main feature I care about
that makes my life a million times easier is each intsrument returning the time
for right after it stops sounding. That way a string of st=inst(st);
st=inst(st); st=inst(st); will produce consecutive notes, but leaving out a
"st=" allows multiple notes to sound at once. By keeping track of many start
times that were returned, it is extremely intuitive to compose using lines
of code. Because I have separated the concept of "duration" and "length
envelope", notes can be easily stretched or shrunk within their own x-beat
length of time without affecting the all-important returned start time.
For example, if you call an instrument to last 2 beats but with a lenEnv of .5,
the instrument will sound for 1 beat and return the start time for 2 beats 
after its start time. All the functions and other goodies are attempts to make
my life easy.
"""

def preamble(cr=0):
  """Initialize the nonsense. Return the list of scales."""
  print_off()
  rtsetparams(44100, 2)
  rtoutput("mysound", "wav")
  if cr!=0:
    control_rate(cr)
  load("WAVETABLE")
  load("FMINST")
  load("HALFWAVE")
  load("STRUMFB")
  return scalesGen()

def scalesGen():
  """Returns a list of scales, indexed by octave. A "scale" is a sequential 
  list of arguments to go into cpsmidi(). Meant to be called once and stored.
  """
  scales = []
  for octave in range(8):
    scale = [24 +12*octave, 
	     27 +12*octave, 
	     29 +12*octave, 
	     30 +12*octave, 
	     31 +12*octave, 
	     34 +12*octave]
    scales.append(scale)
  print "Scales generated"
  return scales

# Global variables for functions. To avoid regenerating each time.
scales = preamble()
sine = maketable("wave", 1000, "sine")
saxSaw = maketable("wave", 90, "saw45")
saxTri = maketable("wave", 45, "tri")
brassSquare = maketable("wave", 90, "square90")
bassTri = maketable("wave", 32, "tri5")
bassIEnvs = {"basic":maketable("curve", 1000, 0,0,-5, .5,1,5, 1,0), 
	     "crazy":maketable("line", 1000, 0,0, 1,3, 2,2, 3,4, 4,3, 5,7, 6,3,
			       7,12, 8,9, 9,20,10,16,11,32,12,36, 13,15, 14,24,
			       15,8, 16,12, 17,5, 18,7, 19,2, 20,3, 21,0)}
sf = {"ra":1.05946, "re":1.12246, "me":1.18921, "mi":1.25992, 
      "fa":1.33483, "fi":1.41421, "sol":1.49831, "le":1.58740, 
      "la":1.68179, "te":1.78180, "ti":1.88775}

def improvNotes(n, octaves=3, highTendancy=0, lowTendancy=0):
  """Generates a list of n scale degrees representing a sequence of improvised
  notes.
  Currently, it starts on 0 and continuously picks a random scale degree skip 
  between -octave and +octave, unless there isn't an octave above or below, in 
  which case the max/min skip is whatever's possible.
  """
  notes = []
  maximum = octaves*len(scales[0])
  indecies = range(0,maximum+1)
  index = 0
  
  for i in range(n):
    notes.append(indecies[index])
    index = skip(index, maximum, highTendancy, lowTendancy)+index
    
  return notes

def skip(last, maxIndex, highTendancy=0, lowTendancy=0):
  """Returns a scaleDeg skip value for picking the index of the next note to 
  improvise, based on the previous index. Randomly picks a jump =< 1 octave.
  If high/lowTendancy is specified, it cuts off that many possible jumps from the 
  low/high (corresponding) end of the probbility list.
  """
  octave = len(scales[0])
  maxUpSkip = maxIndex - last
  maxDownSkip = last
  skipsLow = octave*-1
  if maxDownSkip<octave:
    skipsLow = maxDownSkip*-1
  skipsHigh = octave
  if maxUpSkip<octave:
    skipsHigh = maxUpSkip
  skips = range(skipsLow+highTendancy,skipsHigh+1-lowTendancy)
  skip = skips[random.randint(0, len(skips)-1)]
  return skip
  

def improvBeats(n, total, res, leave=1, base=2):
  """Generates a list of n beat values representing an improvised rhythm.
  Parmeters:
     n - number of beat values
     total - the total length (in beat values) required
     res - All beat values will be a multiple of res. If total/res<n, then it
       is impossible to fit all of the beats in. In this case, res will divided
       by 2 until it is possible. 
     leave - multiple of res to save to add to last note. For example, with a 
       res of .25 and a leave of 1, 1*.25 would be saved to add to the last 
       beat. (Keep in mind that all beats have a minimum value of res.) This
       results in an overall minimum of .5 for the last beat. If leave is too 
       long to fit all of the beats in, it will brought down to its max 
       possible value.
  The current version gives each beat has a minimum value of res, and randomly
  spreads it out, in multiples of res, amongst the other beats. The only 
  exception is the last beat, which has a minimum of res+res*leave.
  """
  res = float(res); leave = int(leave)
  while n*res>total:
    res=res/2

  if leave>total/res-n:
    print "leave is too damn high"
    leave = total/res-n
    
  beatValues = []
  for i in range(n):
    beatValues.append(res)
  
  resToSpread = int((total - res*n)/res)
  while resToSpread>leave:
    resQuant = random.choice(lowChoiceList(resToSpread-leave, base))
    toAdd = res*resQuant
    index = random.randint(0, len(beatValues)-1)
    beatValues[index]+=toAdd
    resToSpread -= resQuant
  beatValues[len(beatValues)-1]+=res*leave
  
  return beatValues

def lowChoiceList(max, b=2, min=1):
  """Generates a list to be input into random.choice(). Has b^(maxi+1) copies of 0,
  b^maxi copies of 1, b^maxi-1 copies of 2 ... and b^1 copys of maxi. If passed
  a base of 0, returns a list containing only 1.
  Parameters:
    maxi - the maximum vaue to appear in the list
    b - the base of the exponential expression used to generate copies of each 
      number from 0-maxi. Can be a floating point number. The higher the base, 
      the smaller the preportion of higher values. A base of 1 results in one 
      entry for each number min-maxi.
    min - an optional minimum value for the list. Simply skips values below min
  """
  if b==0:
    return [1]
  theList = []
  for i in range(min, max+1):
    for j in range(int(math.pow(b, max+1-i))):
      theList.append(i)
  return theList

def sax(voice, start, length, scaleDeg, amp, beat, lenEnv=1, pitchEnv=1, 
	ampEnv=1, loopy=False, w1=saxSaw, w2=saxTri, n1=.8, n2=.5):
  """An intuitive proxy instrument. I'm pretending it sounds like a sax.
  Parameters:
    voice: "b" for bass, "t" for tenor, "s" for soprano. Fundamental will be 
      C1, C2, or C3 respectively
   start: simply the start time
    length: length of the note in beats. 1 = quarter note, or one beat.
    scaleDeg: zero-indexed scale degree. Ones place is degree, tens place is 
      number of octaves above fundamental note of this degree.
    amp: simply amplitude
    beat: BPM
    lenEnv: A multiplier for the note length. >1 bleeds, <1 clips
    pitchEnv: a maketable to multiply pitch by
    ampEnv: a number or maketable to multiply amplitude by
    loopy: 'true' changes the meaning of scaleDeg. If loopy, the scale degree 
      will be continuous, not broken up into tens. In a 6-note scale, loopy 
      scale degree 6 is an octave above scale degree 0, for ex.
    other 4: used in halfwave generation. Defaults to sax, but others can be
      overridden in
  """	      
  if voice == "b": 
    octave = 1
  elif voice == "t": 
    octave = 2
  elif voice == "s": 
    octave = 3
  elif voice == "a":
    octave = 7
  else:
    octave = 2
    print "ERROR\nERROR\nERROR\nERROR\n"
  scale = scales[octave]
  if scaleDeg<0:
    amp = 0
  if not loopy:
    o = scaleDeg/10
    p = scaleDeg%10
  else:
    o = scaleDeg/len(scale)
    p = scaleDeg%len(scale)
  
  HALFWAVE(start, 
	   length*(60.0/beat)*lenEnv, 
	   cpsmidi(scale[p])*(math.pow(2,o))*pitchEnv, 
	   amp*ampEnv, 
	   saxSaw, 
	   saxTri, 
	   n1, n2)

  return start + length*(60.0/beat)

def brass(voice, start, length, scaleDeg, amp, beat, lenEnv=1, pitchEnv=1, 
	ampEnv=1, loopy=False):
  """A clone of sax that my insanity claims to sound like a brass instrument"""
  return sax(voice, start, length, scaleDeg, amp, beat, lenEnv=lenEnv, 
	     pitchEnv=pitchEnv, ampEnv=ampEnv, loopy=loopy, 
	     w1=brassSquare, w2=sine, n1=.2, n2=.5)

def guit(start, length, scaleDeg, amp, beat, lenEnv=1, pitchEnv=1, ampEnv=1, 
	 loopy=False, squish=8, distgain=1000, feedgain=.006, clean=1, dist=1,
	 fMult=1, decayMult=1, voice=""):
  """See sax() for explinations of intuitive parameters.
  Squish, distgain, feedgain, clean, and dist exist for STRUMFB-level fiddling.
  Unique parameters:
    fMult - a multiplier to pitch which creates the feedback pitch.
    decayMult - a multiplier to duration which creates both delays.
    voice - Only specify if you want "a": ailiased.
  """
  if voice == "a":
    octave = 7
  else:
    octave = 1
  scale = scales[octave]
  
  if scaleDeg<0:
    amp = 0
  if not loopy:
    o = scaleDeg/10
    p = scaleDeg%10
  else:
    o = scaleDeg/len(scale)
    p = scaleDeg%len(scale)
  pitch = cpsmidi(scale[p])*(math.pow(2,o))
  dur = length*(60.0/beat)*lenEnv
    
  STRUMFB(start,
	  dur,
	  amp*ampEnv,
	  pitch*pitchEnv,
	  pitch*pitchEnv*fMult,
	  squish,
	  dur*decayMult,
	  dur*decayMult,
	  distgain,
	  feedgain,
	  clean,
	  dist,
	  .5)
  return start + length*(60.0/beat)

def strummit(start, length, scaleDegs, amp, beat, 
	     delay=0, tight=False, loopy=False, voice="", lenEnv=1, 
	     pitchEnv=1, pitchEnvs=0, ampEnv=1, ampEnvs=0, 
	     squish=8, distgain=1000, feedgain=.006, clean=1, dist=1,
	     fMult=1, decayMult=1):
  """Strums guitar based on input list of scaleDegs(strings) and input delay 
  between string plucks. See sax() for explinations of intuitive parameters and
  guit() for STRUMFB parameters.
  Unique parameters:
     scaleDegs - A list of scaleDegs to be plucked in order
     delay - delay between plucks of each string, in beats
     tight - if true, all plucks end at the same time instead of staggering.
     pitchEnvs - A list of pitch envelopes. If specified, 'pitchEnv' is ignored
                 Applied corresponding to the scDeg in the same list position, 
                 but if pitchEnvs is shorter, it loops back to the first Env.
     ampEnvs - see pitchEnvs, but for pitch
  See guit() for other parameters.
  """
  if pitchEnvs==0:
    pitchEnvs=[pitchEnv]
  if ampEnvs==0:
    ampEnvs=[ampEnv]
  
  for i in range(len(scaleDegs)):
    if tight:
      length = length - delay
    st = guit(start+i*(delay*60.0/beat), length, scaleDegs[i], amp, beat, 
	      lenEnv=lenEnv, pitchEnv=pitchEnvs[i%len(pitchEnvs)], 
	      ampEnv=ampEnvs[i%len(ampEnvs)], loopy=loopy, squish=squish,
              distgain=distgain, feedgain=feedgain, clean=clean, dist=dist, 
              fMult=fMult, decayMult=decayMult, voice=voice)
  return st
    
def bass(start, length, scaleDeg, amp, beat, lenEnv=1, ampEnv=1, pitchEnv=1, 
	 carMult=.5, carEnv=1, iEnv="basic", loopy=False, craziness=3, voice=""):
  """A bass. It's versitile and stuff, I hope. See sax() for explinations of 
  intuitive parameters.
  Unique parameters:
    craziness - Simply index_high. cr=0 sounds like an electric bass.
    carMult - a multiplier to pitch which determines the carrier pitch
    carEnv - an envelope to the carrier pitch, if you so please.
    iEnv - a string representing an entry in IEnvs{}, a global dictionary of
      index envelopes for this instrument specficially.
    voice - same as guit()
  """
  if voice == "a":
    octave = 7
  else:
    octave = 1
  scale = scales[octave]
  
  if scaleDeg<0:
    amp = 0
  if not loopy:
    o = scaleDeg/10
    p = scaleDeg%10
  else:
    o = scaleDeg/len(scale)
    p = scaleDeg%len(scale)
  pitch = cpsmidi(scale[p])*(math.pow(2,o))
  dur = length*(60.0/beat)*lenEnv
  
  FMINST(start,
	 dur,
	 amp*ampEnv,
	 pitch*carMult*carEnv,
	 pitch*pitchEnv,
	 craziness,
	 0,
	 .5,
	 bassTri,
	 bassIEnvs.get(iEnv))
  return start + length*(60.0/beat)

def endFade(fadeTime, curviness):
  """Returns tbl-hdl for an envelope that curves the end amplitude down to 0.
  Parameters:
     fadeTime - from 0-1 exclusive, the ratio of time to be spent fading
     curviness - the "curve" value of the maketable
   """
  return maketable("curve", 1000, 0,1,0, 1-fadeTime,1,curviness, 1,0)

def endSwell(swellTime, fadeTime, curviness, maxMult):
  """Returns tbl-hdl for an envelope that curves the end amplitude up to 0.
  Parameters:
     swellTime - from 0-1 exclusive, the ratio of time to be spent swelling
     fadeTime - from 0-infinity exclusive. The amount of time to be spend 
       fading down to nothing
     curviness - the "curve" value of the maketable
     maxMult - the multiplier for amplitude to create final amplitude
   """
  return maketable("curve", "nonorm", 1000, 0,1,0, 
		   1-swellTime,1,curviness, 1,maxMult,-1*curviness, 1+fadeTime,0)

def dubFade(fadeTimeIn, fadeTimeOut, curviness):
  """Returns a maketable for an envelope that curves the beginning amplitude up
  to 1 and the end amplitude down to 0. The envelope has two halves 0-1 is 
  where the fade in lives ,and 1-2 is where the fade out lives. ie, each fade 
  cannot extend beyond half of the envelope.
  Parameters:
     fadeTimeIn - from 0-1 exclusive, the ratio of time to be spent fading in
     fadeTimeIn - from 0-1 exclusive, the ratio of time to be spent fading out
     curviness - the "cuve" value of the maketable
   """
  return maketable("curve", 1000, 0,0,curviness*-1, fadeTimeIn,1,curviness, 
		   1,1,0, 2-fadeTimeOut,1,curviness, 2,0)

def scoop(scoopTime, curviness, ratio):
  """Returns a maketbale for a pitch scoop or fall. The instrument's pitch 
  will be 1; that is, the ratio*pitch will be the starting pitch, and the 
  instrument's pitch will be the destination.
  Parameters:
    scoopTime - 0-1 exclusive. Preportion of total length to be scooping.
    curviness - MINC curve table "curve" value
    ratio - sf[] ratio for pitch. This will be multiplied by pitch to get pitch
    before scooping to real pitch.
  """
  return maketable("curve", 1000, 0,ratio,curviness, scoopTime,1,0, 1,1)

'''========================================================================='''
'''========================================================================='''



'''========================================================================='''
'''========================================================================='''

'''
preamble()
pitchEnvs = {}
ampEnvs = {"endFade":endFade(.05, 5), 
	   "longEndFade":endFade(.99, 3), 
	   "dubFade1":dubFade(.05,.05, 5)}
scales = scalesGen()
st = 0
BPM = 40

crazy=3
st = bass(st, .25, 14, 20000, BPM, lenEnv=.95, 
	  pitchEnv=scoop(.99, 0, 8.0/9), ampEnv=ampEnvs.get("dubFade1"), craziness=crazy)
st = bass(st, .25, 14, 20000, BPM, lenEnv=.95, 
	  pitchEnv=scoop(.99, 0, 8.0/9), ampEnv=ampEnvs.get("dubFade1"), craziness=crazy)
st = bass(st, .0625, 12, 20000, BPM, 
	  ampEnv=ampEnvs.get("dubFade1"), craziness=crazy)
st = bass(st, .0625, 14, 20000, BPM, 
	  ampEnv=ampEnvs.get("dubFade1"), craziness=crazy)
st = bass(st, .125, 11, 20000, BPM, 
	  lenEnv=1, ampEnv=ampEnvs.get("dubFade1"), craziness=crazy)
st = bass(st, .125, 10, 20000, BPM, 
	  lenEnv=1, ampEnv=ampEnvs.get("dubFade1"), craziness=crazy)
st = bass(st, .125, 5, 20000, BPM, 
	  lenEnv=.95, ampEnv=ampEnvs.get("dubFade1"), craziness=crazy)
bass(st, 4, 0, 20000, BPM, 
	  lenEnv=1, ampEnv=ampEnvs.get("dubFade1"), craziness=3)

strummit(st, 4, [10,14,20,24,31,35,43], 5000, BPM, feedgain=.05,tight=True, delay=.05, distgain=100, pitchEnvs=[1,1,1,1,1,1,1], ampEnvs=[endFade(.99,5),endFade(.85,4),endFade(.7,3),endFade(.55,2),endFade(.4,1),endFade(.25,1),2*endFade(.1,0)])
'''