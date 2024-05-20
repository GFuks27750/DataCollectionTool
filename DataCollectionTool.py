# TODO
# Użytkownik w trakcie działania programu powinien móc wielokrotnie wybierać to ile zdjęć chce wykonań
# Fajnie by było jakby na ekranie wyświetlał się jakiś feedback, że zdjęcie zostało wykonane/ile pozostało
# do wykonania.
# Potrzebna jest jakaś wyraźna przerwa, albokomunikat żeby przygotować się do kolejnego zdjęci, żeby foty nie
# wychodziły rozmazane, bo jak na razie może ci w ruchu zrobić zdjęcie. (Będzie trzeba mniej czasu poświęcić na
# oczyszczanie danych)

import cv2
import time
import threading
import os


def capture_image(directory, img_name, frame, remaining_images):
    if not os.path.exists(directory):
        os.makedirs(directory)
    full_path = os.path.join(directory, img_name)
    cv2.imwrite(full_path, frame)
    print(f"{full_path} written! Remaining images: {remaining_images}")


def take_pictures(how_many_img, cam, directory, img_prefix):
    global img_counter, remaining_images, taking_pictures
    remaining_images = how_many_img
    for _ in range(how_many_img):
        ret, frame = cam.read()
        if ret:
            img_name = f"{img_prefix}_opencv_frame_{img_counter}.png"
            threading.Thread(target=capture_image, args=(directory, img_name, frame.copy(), remaining_images - 1)).start()
            img_counter += 1
            remaining_images -= 1
            time.sleep(1)
        else:
            print("failed to grab frame")
    taking_pictures = False


cam = cv2.VideoCapture(0)
cv2.namedWindow("test")

global img_counter, remaining_images, taking_pictures
img_counter = 0
remaining_images = 0
taking_pictures = False

while True:
    how_many_img = int(input("How many pictures do you want to take?\n"))
    directory = input("Enter the directory name (single letter) where images will be saved:\n")
    img_prefix = directory

    taking_pictures = False
    while True:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break

        if taking_pictures:
            feedback_text = f"Taking picture... Remaining: {remaining_images}"
        else:
            feedback_text = "Press SPACE to start taking pictures"

        cv2.putText(frame, feedback_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow("test", frame)

        k = cv2.waitKey(1)
        if k % 256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            cam.release()
            cv2.destroyAllWindows()
            exit()  # Exit the program
        elif k % 256 == 32 and not taking_pictures:
            # SPACE pressed
            taking_pictures = True
            threading.Thread(target=take_pictures, args=(how_many_img, cam, directory, img_prefix)).start()

        if not taking_pictures and remaining_images == 0:
            break

cam.release()
cv2.destroyAllWindows()

