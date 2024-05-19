import cv2
import time
import threading

#TODO 
#Użytkownik w trakcie działania programu powinien móc wielokrotnie wybierać to ile zdjęć chce wykonań
#Fajnie by było jakby na ekranie wyświetlał się jakiś feedback, że zdjęcie zostało wykonane/ile pozostało 
#do wykonania. 
#Potrzebna jest jakaś wyraźna przerwa, albokomunikat żeby przygotować się do kolejnego zdjęci, żeby foty nie 
#wychodziły rozmazane, bo jak na razie może ci w ruchu zrobić zdjęcie. (Będzie trzeba mniej czasu poświęcić na
# oczyszczanie danych)

def capture_image(img_name, frame):
    cv2.imwrite(img_name, frame)
    print(f"{img_name} written!")

def take_pictures(how_many_img, cam):
    global img_counter
    for _ in range(how_many_img):
        ret, frame = cam.read()
        if ret:
            img_name = f"opencv_frame_{img_counter}.png"
            threading.Thread(target=capture_image, args=(img_name, frame.copy())).start()
            img_counter += 1
            time.sleep(1)
        else:
            print("failed to grab frame")

cam = cv2.VideoCapture(0)
cv2.namedWindow("test")

img_counter = 0
how_many_img = int(input("How many pictures do you want to take?\n"))
taking_pictures = False

while True:
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("test", frame)

    k = cv2.waitKey(1)
    if k % 256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k % 256 == 32 and not taking_pictures:
        # SPACE pressed
        taking_pictures = True
        threading.Thread(target=take_pictures, args=(how_many_img, cam)).start()
        taking_pictures = False

cam.release()
cv2.destroyAllWindows()
