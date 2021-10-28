import os
import shutil
from datetime import datetime
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS


SCAN_PATH = Path("e:/photo_sort_test")
BUILD_PATH = Path("e:/photo_sort_test/sorted_photos_test")


def find_photos():
    filetypes = [".jpg", ".png"]
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
        photo_data.append(data)
    return photo_data


def plan_directories(photo_data):
    directory_plan = {}
    for photo in photo_data:
        if "DateTime" in photo:
            taken_date = datetime.strptime(photo["DateTime"][:10], "%Y:%m:%d")
            photo["taken_date"] = datetime.strftime(taken_date, "%Y-%m-%d")
            year = taken_date.year

            if year not in directory_plan:
                directory_plan[year] = {}
            month = taken_date.strftime("%b")

            if month not in directory_plan[year]:
                directory_plan[year][month] = []

            directory_plan[year][month].append(photo["taken_date"])

            photo["destination_path"] = Path.joinpath(
                BUILD_PATH,
                str(year),
                month,
                photo["taken_date"],
                photo["path"].name,
            )
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


if __name__ == "__main__":
    photo_paths = find_photos()
    photo_data = find_photo_data(photo_paths)
    directory_plan = plan_directories(photo_data)
    build_directories(directory_plan)
    move_photos(photo_data)
