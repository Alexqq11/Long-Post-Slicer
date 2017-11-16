from PIL import Image
import datetime
import os
import os.path


class ImageSplit:
    def __init__(self):
        self.start_image = None
        self.pixel_map = None
        self.width = None
        self.height = None
        self.split_size = 850  # todo make check if if height less than split
        self.split_epsilon = 50
        self.split_step = 1
        self.split_pages = []  # todo flush option with big data
        self.split_part_file_prefix = "part"
        self.save_directory_path = None
        self.save_directory_exist = False

    def split_image(self, file_path):
        if not os.path.isfile(file_path):
            raise KeyError("Expected file")
        self._open_image(file_path)
        self._init_image_data()
        self._split_image_to_parts()
        self._flush_data()

    def _open_image(self, file_path):
        self.start_image = Image.open(file_path)
        self.save_directory_path, *_ = os.path.split(file_path)
        self.save_directory_path = "imageParts-{}".format(id(file_path))

    def _init_image_data(self):
        self.pixel_map = self.start_image.load()
        self.width, self.height = self.start_image.size

    def _is_text_line(self, check_height):
        is_text = False
        for x in range(0, self.width):
            r, g, b = self.pixel_map[x, check_height]
            is_text = r < 200 or g < 200 or b < 200  # todo make it optional with comparer options
            if is_text:
                return is_text
        return is_text

    def _copy_selected_part(self, start_height, end_height):
        part_box = (0, start_height, self.width, end_height)
        image_part = self.start_image.crop(part_box)
        temp = Image.new('RGB', (self.width, end_height - start_height), (0, 0, 0))
        temp.paste(image_part, (0, 0, self.width, end_height - start_height))
        self.split_pages.append(temp)

    def _multiplication_stream(self):
        for x in range(1, self.split_epsilon // self.split_step, 1):
            yield x
            yield -x

    def _find_slice_line(self, start_height):  # todo check if line selection greater than height
        for x in self._multiplication_stream():
            if not self._is_text_line(start_height + x * self.split_step):
                return start_height + x * self.split_step
        return self._find_slice_line(start_height - 100)

    def _split_image_to_parts(self):
        last_height = 0
        while (last_height + self.split_size) < self.height:
            slice_height = self._find_slice_line(last_height + self.split_size)
            self._copy_selected_part(last_height, slice_height)
            last_height = slice_height
        self._copy_selected_part(last_height, self.height)

    def _flush_part(self, image_part, number):
        self._create_save_directory()
        image_id = id(image_part)
        filename = "{}-{}-{}.jpg".format(number, self.split_part_file_prefix, image_id)
        file_path = os.path.join(self.save_directory_path, filename)
        image_part.save(file_path)

    def _flush_data(self):
        for number, x in enumerate(self.split_pages):
            self._flush_part(x, number)

    def _create_save_directory(self):
        if not self.save_directory_exist:
            os.makedirs(self.save_directory_path)
            self.save_directory_exist = True
if __name__ == "__main__":
    #path = input("enter path to image>:")
    image_split = ImageSplit()
    image_split.split_image("./test3.jpg")
