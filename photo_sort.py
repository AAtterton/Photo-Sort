import os
import shutil
from datetime import datetime
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS


SCAN_PATH = Path("e:/photosortdups")
BUILD_PATH = Path("e:/photosortdups/sorted_photos_test")
MOVE_PHOTOS = True


def find_photos():
    filetypes = [".jpg", ".png", ".JPG", ".PNG"]
    file_paths = []

    for root, _, files in os.walk(SCAN_PATH, topdown=True):
        for file in files:
            for filetype in filetypes:
                if file.lower().endswith(filetype):
                    file_paths.append(os.path.join(root, file))

    return file_paths


def find_photo_data(photo_paths):
    photo_data = []
    for photo_path in photo_paths:
        photo = Image.open(photo_path)
        data = {TAGS[k]: v for k, v in photo.getexif().items() if k in TAGS}
        data["path"] = Path(photo_path)
        if "DateTime" in data:
            taken_date = datetime.strptime(data["DateTime"][:10], "%Y:%m:%d")
            data["taken_date"] = datetime.strftime(taken_date, "%Y-%m-%d")
            data["year"] = taken_date.year
            data["month"] = taken_date.strftime("%b")
        photo_data.append(data)
    return photo_data


def plan_directories(photo_data):
    directory_plan = {}
    for photo in photo_data:
        if "taken_date" in photo:

            year = photo["year"]
            month = photo["month"]

            if year not in directory_plan:
                directory_plan[year] = {}

            if month not in directory_plan[year]:
                directory_plan[year][month] = []

            directory_plan[year][month].append(photo["taken_date"])

            photo["destination_path"] = build_photo_path(photo)

    return directory_plan


def build_directories(directory_plan):
    if not BUILD_PATH.exists():
        os.mkdir(BUILD_PATH)
    for year in directory_plan:
        year_path = Path.joinpath(BUILD_PATH, str(year))
        if not year_path.exists():
            os.mkdir(year_path)
        for month in directory_plan[year]:
            month_path = Path.joinpath(year_path, month)
            if not month_path.exists():
                os.mkdir(month_path)
            for day in directory_plan[year][month]:
                day_path = Path.joinpath(month_path, day)
                if not day_path.exists():
                    os.mkdir(day_path)


def move_photos(photo_data):
    for photo in photo_data:
        if "destination_path" in photo:
            if not photo["destination_path"].exists():
                shutil.move(photo["path"], photo["destination_path"].absolute())


def set_photo_names(photo_data):
    """
    Function to get the name of a photo from the date_time or
    path if no date_time is present, and suffix with a number
    depending on how many times it has been seen,
    to provide unique names. Also strips invalid characters.
    """
    photo_names = {}

    for photo in photo_data:
        file_extension = photo["path"].name[-3:]
        if "DateTime" in photo:
            photo_datetime = photo["DateTime"]
            file_name = "".join(x for x in photo_datetime if x.isalnum())
        else:
            file_name = photo["path"].name[:-4]

        if file_name in photo_names:
            # original name joined by _ with number
            photo_names[file_name] += 1
            photo_name = f"{file_name}_{photo_names[file_name]}.{file_extension}"
            photo["name"] = photo_name
        else:
            photo_names[file_name] = 1
            photo_name = f"{file_name}_1.{file_extension}"
            photo["name"] = photo_name


def build_photo_path(photo):
    year = photo["year"]
    month = photo["month"]
    photo_path = Path.joinpath(
        BUILD_PATH, str(year), month, photo["taken_date"], photo["name"]
    )
    return photo_path


if __name__ == "__main__":
    photo_paths = find_photos()
    photo_data = find_photo_data(photo_paths)
    set_photo_names(photo_data)
    directory_plan = plan_directories(photo_data)

    if MOVE_PHOTOS:
        build_directories(directory_plan)
        move_photos(photo_data)
