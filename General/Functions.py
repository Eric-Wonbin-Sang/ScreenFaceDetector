import cv2


def get_child_image_from_parent_image(image, image_area_dict, child_area_dict, scale=None):
    y_delta = child_area_dict["y"] - image_area_dict["y"]
    x_delta = child_area_dict["x"] - image_area_dict["x"]
    image = image[y_delta: y_delta + child_area_dict["height"], x_delta: x_delta + child_area_dict["width"]]
    if scale is not None:
        return cv2.resize(image, (0, 0), fx=scale, fy=scale)
    return image
