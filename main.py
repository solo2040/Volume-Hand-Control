import cv2
import numpy as np
import HandTrackingModule as htm
import math
from pynput.keyboard import Key,Controller
keyboard = Controller()
from time import sleep
import time

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

############################################
wCam, hCam = 640, 480
############################################


cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector()


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]


vol = 0
vol_bar = 400
vol_bar_num = 0
while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2

        cv2.circle(img, (x1, y1), 15, (255,0,255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2,y2),(255, 0, 255), 3)
        cv2.circle(img, (cx,cy), 15, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2-x1,y2-y1)
        #print(length)

        # Hand Range 50 to 300
        # Volume Range -65 to 0
        vol = np.interp(length,[50,300],[minVol, maxVol])
        vol_bar = np.interp(length, [50, 300], [400, 150])
        vol_bar_num = np.interp(length, [50, 300], [0, 100])
        #print(vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length<50:
            cv2.circle(img, (cx, cy), 15, (0, 0, 0), cv2.FILLED)
        # max: thumb/4,323,392 to pointer finger/8,258,66 --> 332
        # min: thumb/4,310,332 to pointer finger/8,333,297 --> 42
        # equation: y = (x-42)/2.9
    cv2.rectangle(img, (50,150), (85,400), (0,255,0),3)
    cv2.rectangle(img, (50, int(vol_bar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'VOL: {int(vol_bar_num)}', (20, 430), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40,50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)

    cv2.imshow("Img", img)
    cv2.waitKey(1)
