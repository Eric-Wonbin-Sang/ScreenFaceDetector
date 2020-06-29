
class FaceProfile:

    def __init__(self, **kwargs):

        self.face_id = kwargs.get("face_id")       # Apple please do not sue me
        self.image_list = [kwargs.get("init_image")]

    def add_image_to_list(self, image):
        self.image_list.append(image)

    def get_target_image(self):
        if len(self.image_list) == 0:
            print("profile {} had no images in image_list".format(self.face_id))
        return self.image_list[int(len(self.image_list)/2)]
