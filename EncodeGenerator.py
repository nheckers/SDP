#python EncodeGenerator.py
import cv2
import face_recognition
import pickle 
import os

#importing people images
folderPath = 'Images'
pathList = os.listdir(folderPath)
print(pathList)
imgList = []
personIds = []

#Loop over each file in the directory
for path in pathList:
    # Only process files that have an image extension (.png, .jpg, or .jpeg)
    if path.endswith('.png') or path.endswith('.jpg') or path.endswith('.jpeg'):
        img_path = os.path.join(folderPath, path)  # Construct the full path to the image file
        img = cv2.imread(img_path)  # load image using OpenCV
        if img is None:  # If the image is None, it means it couldn't be loaded, so print an error
            print(f"Failed to load image at {img_path}")
        else:
            imgList.append(img)  # Append the successfully loaded image to the imgList
            personIds.append(os.path.splitext(path)[0])  # Extract the image name without extension

#Print the number of images loaded
print(len(imgList))  # Shows number of images loaded
print(personIds)

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # convert BGR to RGB
        encode = face_recognition.face_encodings(img)[0]  # get the face encoding
        encodeList.append(encode)  # append the encoding to the list
    return encodeList

print("Encoding Started ...")
encodeListKnown = findEncodings(imgList)  # will generate all known faces and save it here
encodeListKnownWithIds = [encodeListKnown, personIds]  # Encoding and the Id 
print("Encoding Complete")

#create a file to save encodeListKnownWithIds
file = open("EncodeFile.p", 'wb')  # made "EncodeFile.p" into name of file. wb is the permissions 
pickle.dump(encodeListKnownWithIds, file)  # put or "dump" encodeListKnownWithIds into the file
file.close()  # close file
print("File saved") 
