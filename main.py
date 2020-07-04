import pyscreenshot
import cv2
import datetime
import pygame
import win32api
import win32con
import win32gui
import csv
import os
import difflib
from ctypes import POINTER, WINFUNCTYPE, windll
from ctypes.wintypes import BOOL, HWND, RECT

from Classes import Profile
from General import Functions, Constants


def assign_window_color_for_transparency(hwnd, color_tuple):
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                           win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*color_tuple), 0, win32con.LWA_COLORKEY)


def get_screen_location(hwnd, top_shift=0, left_shift=0, bottom_shift=0, right_shift=0):
    prototype = WINFUNCTYPE(BOOL, HWND, POINTER(RECT))
    paramflags = (1, "hwnd"), (2, "lprect")
    get_window_rect = prototype(("GetWindowRect", windll.user32), paramflags)
    rect = get_window_rect(hwnd)
    return rect.top + top_shift, rect.left + left_shift, rect.bottom + bottom_shift, rect.right + right_shift


def save_screen_shot(x, y, width, height, save_path, show_image=False):
    screenshot = pyscreenshot.grab(bbox=(x, y, x + width, y + height))
    screenshot.save(save_path)
    if show_image:
        screenshot.show()
    return screenshot


def get_scanning_area(window_name="Pygame Window", area_check_path="scanning_area_check.jpg"):

    pygame.init()
    pygame.display.set_caption(window_name)
    screen = pygame.display.set_mode((300, 300), pygame.RESIZABLE)
    transparent_color = (123, 123, 123)

    hwnd = pygame.display.get_wm_info()["window"]
    assign_window_color_for_transparency(hwnd=hwnd, color_tuple=transparent_color)

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
                top, left, bottom, right = get_screen_location(
                    hwnd=hwnd, left_shift=6, top_shift=34, right_shift=-6, bottom_shift=-6
                )
                area_dict = {"x": left, "y": top, "width": right-left, "height": bottom-top}
                save_screen_shot(*[area_dict[key] for key in area_dict], save_path=area_check_path)
                pygame.quit()
                return area_dict

            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        screen.fill(transparent_color)
        pygame.display.flip()


def run_face_profile_detection(profile_area_dict, face_area_dict, text_area_dict):

    face_cascade = cv2.CascadeClassifier("Data/haarcascade_frontalface_default.xml")
    temp_profile_area_path = "temp_profile_area.jpg"
    start_time = datetime.datetime.now()

    prev_is_face = False
    save_cond = False
    profile_index = 1028390
    time_offset = 0     # in seconds

    face_profile_list = []

    while True:

        screenshot = save_screen_shot(*[profile_area_dict[key] for key in profile_area_dict], temp_profile_area_path)

        profile_image = cv2.imread(temp_profile_area_path)
        face_image = Functions.get_child_image_from_parent_image(profile_image, profile_area_dict, face_area_dict, scale=0.5)
        text_image = Functions.get_child_image_from_parent_image(profile_image, profile_area_dict, text_area_dict)

        face_list = face_cascade.detectMultiScale(
            cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY),    # grayscale version
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        curr_is_face = len(face_list) != 0

        if len(face_list) > 1:
            continue
        if curr_is_face and not prev_is_face:

            face_profile_list.append(Profile.FaceProfile(init_image=screenshot))
            save_cond = True
            print("--------------------------")
            print("new prof added - profile {}".format(profile_index))

        if save_cond:
            face_profile_list[-1].add_image_to_list(screenshot)
            print("\tadding face")
            if face_profile_list[-1].try_parsing_image(
                        text_image=text_image,
                        target_dir=Constants.profile_dir,
                        seconds_into_video=(datetime.datetime.now() - start_time).total_seconds() * 2 + time_offset,
                        profile_num=profile_index
                    ):
                save_cond = False
                profile_index += 1

        prev_is_face = curr_is_face


division_list = [
    "fund services",
    "investment banking",
    "research",
    "equity research",
    "technology",
    "wealth management",
    "quantitative finance",
    "legal and compliance",
    "fixed income",
    "internal audit",
    "operations",
    "institutional equity",
    "global capital markets",
    "bank resource management",
    "finance",
    "investment management",
    "compliance",
    "human resources",
    "company management",
    "prime brokerage client",
    "firm risk management",
    "corporate treasury",
    "corporate services",
    "public finance",
]


def get_similar_division(raw_division):
    for division in division_list:
        if difflib.SequenceMatcher(None, division, raw_division).ratio() > .8:
            return division.title()
    return None


def get_attribs_from_file_path(file_path):
    profile_num, name, division, time = file_path[:-4].split("; ")

    name = "".join([letter for letter in name if letter.isalpha() or letter == " "]).strip().title()
    profile_num = int(profile_num.split(" ")[-1])
    division = get_similar_division(division.lower().strip()) if name != division else None
    time_list = time.split(" ")
    total_seconds = str(datetime.timedelta(seconds=int(time_list[0]) * 60 + int(time_list[2])))

    return total_seconds, profile_num, name, division


def create_csv():

    data_list_list = [get_attribs_from_file_path(file_path) for file_path in list(os.walk(Constants.profile_dir))[0][2]]
    data_list_list = sorted(data_list_list, key=lambda a_list: a_list[0])

    with open("profile.csv", 'w', newline='') as csv_file:
        input_csv = csv.writer(csv_file)
        input_csv.writerow(["Time", "Count", "Name", "Division"])
        for data_list in data_list_list:
            input_csv.writerow(data_list)


def main():

    profile_area_dict = get_scanning_area(window_name="Get Profile Area", area_check_path="area_profile_check.jpg")
    face_area_dict = get_scanning_area(window_name="Get Face Area", area_check_path="face_area_check.jpg")
    text_area_dict = get_scanning_area(window_name="Get Text Area", area_check_path="text_area_check.jpg")

    print(profile_area_dict)
    print(face_area_dict)
    print(text_area_dict)

    run_face_profile_detection(profile_area_dict, face_area_dict, text_area_dict)

    create_csv()


main()
