import cv2
import os
import numpy as np
import pickle
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from datetime import datetime
import time

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL':'https://faceattendancetesting-default-rtdb.firebaseio.com/',
    'storageBucket': "faceattendancetesting.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background3.png')


# Importing the mode images into a list
folderModePath = 'Resources/Modes3'
modePathList = os.listdir(folderModePath)
imgModeList = [cv2.resize(cv2.imread(os.path.join(folderModePath, path)), (414, 633)) for path in modePathList]

#imgModeList = []
#for path in modePathList:
 #   imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# print(len(imgModeList))



# Loading the encoding file
print('Loading encode file...')
file = open('EncodeFile.p', 'rb')
encodeListKnownwithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownwithIds 
#print(studentIds)
print('Encode file loaded')

modeType = 0
counter = 0
id = 1
imgStudent = []



while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0,0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    #imgModeList[modeType] = cv2.resize(imgModeList[modeType], (414, 633))
    #imgModeList_resized = cv2.resize(imgModeList[modeType], (414, 633))
    imgBackground[162:162+480, 55:55+640] = img
    imgBackground[44:44+633, 808:808+414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print('matches', matches)
            # print('faceDis', faceDis)

            matchIndex = np.argmin(faceDis)
            # print('Match Index', matchIndex)

            if matches[matchIndex]:
                # print('Known Face Detected.')
                print(studentIds[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 55+x1, 162+y1, x2-x1, y2-y1
                imgBackground = cvzone.cornerRect(imgBackground,bbox, rt=0)
                id = studentIds[matchIndex]

                if counter == 0:
                    cvzone.putTextRect(imgBackground, 'Loading', (275, 400))
                    cv2.imshow("face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:

            if counter == 1:
                # Getting the Data
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)
                # Getting the Image from the Storage
                blob = bucket.get_blob(f'images/{id}.jpg')
                array = np.frombuffer(blob.download_as_string(), np.int8)
                imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
                # Updating data of attendance
                datetimeObject = datetime.strptime(studentInfo['Last_attendance_time'], '%Y-%m-%d %H:%M:%S')
                secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed >30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('Last_attendance_time').set(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44+633, 808:808+414] = imgModeList[modeType]

               

            if modeType != 3:

                if 10<counter<20:
                    modeType = 2
                    
                imgBackground[44:44+633, 808:808+414] = imgModeList[modeType]
        
                if counter<=10:
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (851,91), 
                                cv2.FONT_HERSHEY_COMPLEX, 0.7, (50,50,50),1)
                    
                    cv2.putText(imgBackground, str(studentInfo['field']), (1002, 575), 
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (50,50,50),1)
                    cv2.putText(imgBackground, str(id), (1002, 510), 
                                cv2.FONT_HERSHEY_COMPLEX, 0.7, (50,50,50),1),
                    cv2.putText(imgBackground, str(studentInfo['standing']), (935, 640), 
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (50,50,50),1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (1045, 640), 
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (50,50,50),1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1147, 640), 
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (50,50,50),1)
                    
                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (484-w)//2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808+offset, 445), 
                                cv2.FONT_HERSHEY_COMPLEX, 0.8, (0,0,0),1)
                    
                    imgStudent_resized = cv2.resize(imgStudent, (216, 216))
                    imgBackground[175:175+216, 909:909+216] = imgStudent_resized

                counter += 1

                if counter>=20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44+633, 808:808+414] = imgModeList[modeType]

    else:
        modeType = 0
        counter = 0

    
    # cv2.imshow("Webcam", img)
    cv2.imshow("face Attendance", imgBackground)
    cv2.waitKey(1)
   
