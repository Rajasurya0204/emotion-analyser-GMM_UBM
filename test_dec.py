from __future__ import division
import numpy as numpy
import pickle
import os
from mfcc import  mfcc, vad_thr, cmvn, writehtk
from accStat import Collect_Stats, MAPaDapt, Loglikelihood, htkread, multi_thread ,test,test_decision
from record import start_record
from Play import start_play

print "Say YES or NO"
nmix=4
ubmDir= 'GMM' + str(nmix)
wFile = "Test_dec.wav"
start_record(wFile,3)
fFile= "feat/Test/"+wFile+".htk"

with open(ubmDir + '/' + 'ubm') as f:
    print "lood ubm .. %s" %(f)
    ubm_mu, ubm_cov, ubm_w = pickle.load(f)

winlen, ovrlen, pre_coef, nfilter, nftt = 0.025, 0.02, 0.97, 26 , 512
opts=1

try:

    #call MFCC feature extraction subroutine
    f, E, fs=mfcc(wFile,winlen, ovrlen, pre_coef, nfilter, nftt)


    # VAD part
    if opts == 1:

        f=vad_thr(f,E)       #Energy threshold based VAD [comment this  line if you would like to plugin the rVAD labels]

    elif opts == 0:

        l=numpy.loadtxt('..corresponding vad label file');     #[Pluggin the VAD label generated by rVAD matlab]

        if (len(f) - len(l)) ==1: #1-[end-frame] correction [matlab/python]
            l= numpy.append(l,l[-1:,])
        elif (len(f) -len(l)) == -1:
            l=numpy.delete(l,-1)

        if (len(l) == len(f)) and (len(numpy.argwhere(l==1)) !=0):
            idx=numpy.where(l==1)
            f=f[idx]
        else:
            print "mismatch frames between: label and feature files or no voice-frame in VAD"
            exit()



    # Zero mean unit variance  normalize after VAD
    f=cmvn(f)

    #write the VAD+normalized features  in file
    if not os.path.exists(os.path.dirname(fFile)): # create director for the feature file
        os.makedirs(os.path.dirname(fFile))

    #print("%s --> %s\n" %(wFile,fFile))

    writehtk(fFile, f , 0.01)

except:
    print("Fail ..%s ---> %s\n" %(wFile, fFile))

decision=test_decision(fFile,'DEC3_Tau10.0',ubm_mu,ubm_cov, ubm_w)

if(decision=="YES"):
    print "YES"
else:
    print "NO PROBLEM"