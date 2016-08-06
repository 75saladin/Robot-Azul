import sys
import os

#PYCMIX, which is used to invoke RTcmix python scripts, causes the path to only
#have the location of PYCMIX. Need this line to add the script's directory
sys.path.insert(0, os.getcwd())


from real.meat import *

def shoutChorus(st, amp, BPM, phrases, length, res, df, ampEnv=1,
		octaves=3, highTendancy=0, lowTendancy=0, short=True, bpmAdd=0):
  """A mega-instrument. Plays a random shout chorus on all instruments. Bass 
  plays only every other note for the length of two notes. Each "horn"s pitch 
  is altered randomly by less than 50 cents to create a bigger, more "real 
  ensemble" sound.
  Parameters:
    st - Start time for the whole thing
    amp - A rough total amplitude
    BPM
    phrases - Number of phrases to generate. Keep in mind that putting in a 
      high number isn't quite the same as repeatedly calling this function; the
      last phrase in a call always ends on a quarter note.
    length - number of beats in a phrase
    res - Resolution: the smallest fraction of the beat that will be included
    df - Degrees of freedom. Compared to the maximum number of notes for a 
      given length and res, this is the number of notes fewer contained in each
      phrase. Essentially, it creates df*res beats of wiggle room for note 
      lengths to vary.
    ampEnv - an amplitude envelope to apply to each note
    highTendancy, lowTendancy - cheack out meat.skip. Keep them below the 
      length of scale.
    short - a manual setting to tell the bass not to hold out because it's 
      going to be a short (usu. 1-note) chorus.
    bpmAdd - a BPM to be added to the BPM between notes. Can create a 
       rushing/dragging effect.
  """
  x = .01
  
  for j in range(phrases):
    leave = 0
    if res<=1:
      leave = random.randint(0,1/res-1)
      if j==phrases-1:
        leave = 1/res-1	# last phrase always ends with whole beat
    phraseNotes = int(length/res-df-leave)
    phraseScDegs = improvNotes(phraseNotes, octaves, highTendancy, lowTendancy)
    phraseBeats = improvBeats(phraseNotes, length, res, leave=leave)
    for i in range(phraseNotes):
      BPM+=bpmAdd
      pitchEnv=1
      pitchEnv2=1
      if phraseBeats[i]>res:
        pitchEnv = scoop(res*.5,5,sf["te"]/2)
        pitchEnv2 = scoop(res*.5,5,sf["sol"]/2)
      
      brass("a", st, phraseBeats[i], phraseScDegs[i%len(scales[0])], amp/3, BPM, loopy=True,
	    pitchEnv=pitchEnv*random.uniform(1-x,1+x), ampEnv=ampEnv)
      brass("s", st, phraseBeats[i], phraseScDegs[i%(3*len(scales[0]))], amp/7, BPM, loopy=True,
	    pitchEnv=pitchEnv*random.uniform(1-x,1+x), ampEnv=ampEnv)
      brass("t", st, phraseBeats[i], phraseScDegs[i], amp/7, BPM, loopy=True, 
	    pitchEnv=pitchEnv*random.uniform(1-x,1+x), ampEnv=ampEnv)
      brass("b", st, phraseBeats[i], phraseScDegs[i], amp/4, BPM, loopy=True, 
	    pitchEnv=pitchEnv*random.uniform(1-x,1+x), ampEnv=ampEnv)
      
      sax("a", st, phraseBeats[i], phraseScDegs[i%len(scales[0])], amp/3, BPM, 
	  loopy=True, pitchEnv=random.uniform(1-x,1+x), ampEnv=ampEnv)
      sax("s", st, phraseBeats[i], phraseScDegs[i%(3*len(scales[0]))], amp/6, BPM, 
	  loopy=True, pitchEnv=random.uniform(1-x,1+x), ampEnv=ampEnv)
      sax("t", st, phraseBeats[i], phraseScDegs[i], amp/6, BPM, 
	  loopy=True, pitchEnv=random.uniform(1-x,1+x), ampEnv=ampEnv)
      sax("b", st, phraseBeats[i], phraseScDegs[i], amp/4, BPM, 
	  loopy=True, pitchEnv=random.uniform(1-x,1+x), ampEnv=ampEnv)
      
      if i%2==0:
	dur = phraseBeats[i]+phraseBeats[(i+1)%phraseNotes]
	if short:
	  dur = phraseBeats[i]
        bass(st, dur, phraseScDegs[i], amp/3, BPM, loopy=True, craziness=5, 
	     ampEnv=ampEnv)
      #guit(st, phraseBeats[i], phraseScDegs[i], amp/7, BPM, 
      #     loopy=True, feedgain=.03, pitchEnv=pitchEnv, voice="a")
      guit(st, phraseBeats[i], phraseScDegs[i], amp/3, BPM, 
	   loopy=True, feedgain=.03, pitchEnv=pitchEnv2, ampEnv=ampEnv)
      st = guit(st, phraseBeats[i], phraseScDegs[i], amp/3, BPM, 
		loopy=True, feedgain=.03, pitchEnv=pitchEnv2, ampEnv=ampEnv)
  return st

def improv(st, amp, BPM, phrases, length, res, df, inst, voice="t", 
	   octaves=3, highTendancy=0, lowTendancy=0,
	   craziness=5, carMult=.5,
	   squish=8, distgain=1000, feedgain=.006, clean=1, dist=1, fMult=1,
	     decayMult=1,
	   delay=0, tight=True, pitchEnvs=0, ampEnvs=0):
  """Same as shoutChorus, but with only one insturment. No random pitch 
  altering and no special bass conditions. !!!Generalize!!!
  New parameters:
     inst - the instrument to use
     voice - the instrument voice to use
     craziness, carMult - for bass() only; see bass() for more info
     squish, distgain, feedgain, clean, dist, fMult, decayMult - see above, but 
       for guit() and strummit()
     delay, tight, pitchEnvs, ampEnvs - see above, but only for strummit()
  """
  for j in range(phrases):
    leave = 0
    if res<=1:
      # Add btw 0 and howeverManyItTakesToCreate1Beat to last note in phrase
      leave = random.randint(0,1/res-1) 
      if j==phrases-1:
        leave = 1/res-1	# last phrase always ends with whole beat
    phraseNotes = length/res-df-leave
    phraseNotes = int(phraseNotes)
    phraseScDegs = improvNotes(phraseNotes, octaves, highTendancy, lowTendancy)
    phraseBeats = improvBeats(phraseNotes, length, res, leave=leave)
    for i in range(phraseNotes):
      pitchEnv=1
      pitchEnv2=1
      if phraseBeats[i]>res and voice!="b":
        pitchEnv = scoop(res*.5,5,sf["te"]/2)
        pitchEnv2 = scoop(res*.5,5,sf["sol"]/2)
      if inst=="brass":
	st = brass(voice, st, phraseBeats[i], phraseScDegs[i], amp, BPM, 
	    loopy=True, pitchEnv=pitchEnv)
      elif inst=="sax":
	st = sax(voice, st, phraseBeats[i], phraseScDegs[i], amp, BPM, 
	  loopy=True)
      elif inst=="bass":
	st = bass(st, phraseBeats[i], phraseScDegs[i], amp, BPM, 
	   loopy=True, craziness=craziness, carEnv=pitchEnv)
      elif inst=="guit":
	st = guit(st, phraseBeats[i], phraseScDegs[i], amp, BPM, loopy=True, 
             pitchEnv=pitchEnv2, squish=squish, distgain=distgain, 
             feedgain=feedgain, clean=clean, dist=dist, decayMult=decayMult)
      elif inst=="strummit":
	strumList = [10,14,20,25,31,35,41]
	strummit(st, phraseBeats[i], strumList, amp/len(strumList), BPM, 
	         feedgain=feedgain, tight=tight, delay=delay, distgain=distgain, 
	         pitchEnvs=pitchEnvs, ampEnvs=ampEnvs)
	

  return st


'''========================================================================='''
'''========================================================================='''

pes = {"strum1":[1,1,1,1,1,1,1]}
aes = {"endFade":endFade(.05, 5), 
       "longEndFade":endFade(.99, 3), 
       "dubFade1":dubFade(.05,.05, 5),
       "gFadeLow":[endFade(.99,5), endFade(.85,4), endFade(.7,3),
		   endFade(.55,2),endFade(.4,1),endFade(.25,0),
		   2*endFade(.1,0)],
       "final":endSwell(.5, .2, 2, 2.5)
       }
voi = {0:"b", 1:"t", 2:"s", 3:"a"}


st = 0
amp = 5000
BPM = 120
phrases = 2
length = 7	# for loop: must be greater than df

'''
res = .25
df = 7
improv(st, amp/2, BPM, phrases, length, res, df, "guit", feedgain=.03, octaves=6)
'''

inst = "brass"
dfMult = 1.75
resMult = 2.0
df = 6		
res = 1
i=0

for j in range(2):
  df = 6
  res = 1
  st = improv(st, amp/3, BPM, phrases , length, res, df, inst, voi[0])
  i+=1
  
for j in range(2):
  df = 6
  res = 1
  improv(st, amp/3, BPM, phrases, length, res, df, inst, voi[0])
  
  res/=resMult; df*=dfMult; df=int(df)
  st = improv(st, amp/3, BPM, phrases, length, res, df, inst, voi[2])
  i+=1
  
for j in range(2):
  df = 6
  res = 1
  improv(st, amp/3, BPM, phrases, length, res, df, inst, voi[0])
  
  res/=resMult; df*=dfMult; df=int(df)
  improv(st, amp/3, BPM, phrases, length, res, df, inst, voi[1])

  res/=resMult; df*=dfMult; df=int(df)
  st = improv(st, amp/3, BPM, phrases, length, res, df, inst, voi[2])

i+=1
df = 6
res = 1

while df>0:
  res = 1
  improv(st, amp/3, BPM, phrases, length, res, df, inst, voi[0])
  
  res/=resMult; df*=dfMult; df=int(df)
  improv(st, amp/3, BPM, phrases, length, res, df, inst, voi[1])
  
  res/=resMult; df*=dfMult; df=int(df)
  improv(st, amp/3, BPM, phrases, length, res, df, inst, voi[2])
  
  df/=6.0; df=int(df)
  st = improv(st, amp/3, BPM, phrases, length, res, df, inst, voi[3])
  i+=1
  amp+=amp/20
for j in range(6):
  res = 1
  improv(st, amp/3, BPM, phrases, length, res, df, inst, voi[0], 
	 lowTendancy=j/2)
  
  res/=resMult
  if j<1:
    df+=1
  improv(st, amp/3, BPM, phrases, length, res, df, inst, voi[1])
  
  res/=resMult
  if j<2:
    df+=1
  improv(st, amp/3, BPM, phrases, length, res, df, inst, voi[2], 
	 highTendancy=j/2)
  
  df = 0
  st = improv(st, amp/2, BPM, phrases, length, res, df, inst, voi[3])

  i+=1
  amp+=amp/10
  BPM*=1.0125
print i, "*", phrases, "phrases of", length, "beats each generated"
print "final amp:", amp


st = shoutChorus(st, amp/3*2, BPM, 1, 8, 1, 0, highTendancy=1, octaves=5)
st = shoutChorus(st, amp/3*2, BPM, 1, 8, 1, 0, bpmAdd=9, highTendancy=2, octaves=5)
BPM += 10*8
st = shoutChorus(st, amp/3*2, BPM, 2, 8, 1, 0, bpmAdd=13, highTendancy=3, octaves=5)
BPM += 15*16
st = shoutChorus(st, amp/3*2, BPM, 2, 8, 1, 0, bpmAdd=-25, highTendancy=4, octaves=5)
BPM-= 25*16
end = shoutChorus(st, amp/3, BPM, 1, 6, 6, 0, ampEnv=aes["final"])
st = st+(end-st)/3
strummit(st, 4, [10,14,20,24,31,35,43], amp/4, BPM, feedgain=.05,tight=True, squish=10, delay=.125/1.25, distgain=100, pitchEnvs=pes["strum1"], ampEnvs=aes["gFadeLow"], decayMult=2)
