import pytesseract
import cv2
import numpy

pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'


class FaceProfile:

    def __init__(self, **kwargs):

        self.image_list = [kwargs.get("init_image")]
        self.frames_to_complete_info = 8

    def add_image_to_list(self, image):
        self.image_list.append(image)

    def try_parsing_image(self, text_image, target_dir, seconds_into_video, profile_num):
        if len(self.image_list) > self.frames_to_complete_info:

            name, division = get_name_and_division_from_text_image(text_image)
            print(name, division)

            profile_filename = "{}/{}".format(
                target_dir,
                "{}; {}; {}; {} min {} sec.jpg".format(
                    "Profile " + str(profile_num),
                    name,
                    division,
                    int((seconds_into_video % 3600) // 60) + 60,  # minutes
                    int(seconds_into_video % 60)        # seconds
                )
            )
            print(profile_filename)
            self.image_list[-1].save(profile_filename)
            return True
        return False


def get_text_from_text_image(text_image):
    gray = cv2.cvtColor(text_image, cv2.COLOR_BGR2GRAY)
    sharpen_kernel = numpy.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    sharpen = cv2.filter2D(gray, -1, sharpen_kernel)
    thresh = cv2.threshold(sharpen, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    return pytesseract.image_to_string(thresh).replace("\n\n", "\n").replace("\n\n", "\n")


def get_name_and_division_from_text_image(text_image):
    text_result = get_text_from_text_image(text_image)
    text_result = "".join([letter for letter in text_result if letter not in "\\/:*?`<>|'\"“,.‘"])
    text_list = text_result.split("\n")
    if text_list:
        return text_list[0], text_list[-1]
    return None, None
