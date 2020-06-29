import pyscreenshot
import cv2

from Classes import FaceProfile


def main():

    face_cascade = cv2.CascadeClassifier("Data/haarcascade_frontalface_default.xml")

    curr_is_face = False
    prev_is_face = False

    face_profile_list = []

    while True:

        temp_image_path = "temp_face.jpg"

        screenshot = pyscreenshot.grab(bbox=(2980, 460, 3080, 600))
        screenshot.save(temp_image_path)

        image = cv2.imread(temp_image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        face_list = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        curr_is_face = len(face_list) != 0

        if curr_is_face and not prev_is_face:

            if len(face_profile_list) != 0:
                face_profile_list[-1].get_target_image().save("Faces/{}.jpg".format(face_profile_list[-1].face_id))

            print("--------------------------")
            print("new prof added - face num {}".format(profile_count := len(face_profile_list) + 1))
            face_profile_list.append(
                FaceProfile.FaceProfile(
                    face_id="FaceProfile - {}".format(profile_count),
                    init_image=screenshot
                )
            )
        elif curr_is_face and prev_is_face:
            print("\tadding face")
            face_profile_list[-1].add_image_to_list(screenshot)

        prev_is_face = curr_is_face


main()
