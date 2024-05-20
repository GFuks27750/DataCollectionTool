#TODO 
#Zabezpieczyć aplikacje na sytuacje wyjątkowe: 
# 1. wpisanie litery zamiast liczby
# 2. pisanie liczby zamiast litery
# 3. Po wpisaniu litery powinna być automatycznie zamieniana na dużą litere
# 4. Powinno się dać wpisać tylko jedną literę

import cv2
import time
import threading
import os

def capture_image(directory, img_name, frame, remaining_images, exit_flag):
    if exit_flag.is_set():
        return
    if not os.path.exists(directory):
        os.makedirs(directory)
    full_path = os.path.join(directory, img_name)
    cv2.imwrite(full_path, frame)
    print(f"{full_path} written! Remaining images: {remaining_images}")

def take_pictures(how_many_img, cam, directory, img_prefix, exit_flag):
    global img_counter, remaining_images, taking_pictures
    remaining_images = how_many_img
    for _ in range(how_many_img):
        if exit_flag.is_set():
            break
        ret, frame = cam.read()
        if ret:
            img_name = f"{img_prefix}_{img_counter}.png"
            threading.Thread(target=capture_image, args=(directory, img_name, frame.copy(), remaining_images - 1, exit_flag)).start()
            img_counter += 1
            remaining_images -= 1
            time.sleep(1)
        else:
            print("failed to grab frame")
    taking_pictures = False
    exit_flag.set()

def main():
    global img_counter, remaining_images, taking_pictures
    img_counter = 0
    remaining_images = 0
    taking_pictures = False
    exit_flag = threading.Event()

    cam = cv2.VideoCapture(0)
    cv2.namedWindow("test")

    while True:
        if not taking_pictures:
            how_many_img = int(input("How many pictures do you want to take?\n"))
            directory = input("Enter the directory name (single letter) where images will be saved:\n")
            img_prefix = directory
            print("Press spacebar to start taking pictures")
            taking_pictures = False

        while True:
            ret, frame = cam.read()
            if not ret:
                print("failed to grab frame")
                break

            if taking_pictures:
                feedback_text = f"Taking picture... Remaining: {remaining_images}"
            else:
                feedback_text = "Press spacebar to start taking pictures"

            cv2.putText(frame, feedback_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow("test", frame)

            k = cv2.waitKey(1)
            if k % 256 == 27:
                # ESC pressed
                print("Escape hit, closing...")
                exit_flag.set()
                break
            if k % 256 == 32 and not taking_pictures:
                # SPACE pressed
                taking_pictures = True
                threading.Thread(target=take_pictures, args=(how_many_img, cam, directory, img_prefix, exit_flag)).start()
                break

        if exit_flag.is_set():
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
