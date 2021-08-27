from typing import List, Optional
import re
import os.path

from image import Image


class File:
    FILE_TYPES = [("Header File", "*.h"), ("All Files", "*.*")]

    def __init__(self, path: str) -> None:
        self.path = path
        if path is None:
            self.images = []
        else:
            self.images = self.__read_file()

    @property
    def filename(self) -> str:
        if self.path is None:
            return None
        return os.path.basename(self.path)

    @property
    def modified(self) -> bool:
        return any(image.modified for image in self.images)

    def search(self, name) -> Optional[Image]:
        for image in self.images:
            if image.name == name:
                return image
        return None

    def __read_file(self) -> List[Image]:
        images = []

        current_image = None

        with open(self.path) as f:
            for line in f:
                header = re.match(
                    r"const unsigned char (\w+) \[\] PROGMEM \= \{",
                    line,
                )
                if header:
                    groups = header.groups()
                    if current_image is None:
                        current_image = Image(groups[0], 0, 0)
                    current_image.name = groups[0]
                elif current_image is not None and current_image.name is not None:
                    data = re.match(r"((0x\w+,? ?)+)", line.strip())
                    if data:
                        current_image.add_data(
                            data.groups()[0].strip().strip(",").split(", ")
                        )
                    else:
                        images += [current_image]
                        current_image.finalize()
                        current_image = None
                comment_header = re.match(r"// '(\w+)', (\d+)x(\d+)px", line)
                if comment_header:
                    groups = comment_header.groups()
                    current_image = Image(groups[0], int(groups[1]), int(groups[2]))

        return images

    def export(self, path: str) -> None:
        with open(path, mode="w") as f:
            for image in self.images:
                f.write(image.export_cpp())

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.path == other.path
        else:
            return False
