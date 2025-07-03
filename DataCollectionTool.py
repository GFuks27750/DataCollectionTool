# 4. Powinno się dać wpisać tylko jedną literę

import cv2
import time
import threading
import os

def capture_image(directory, img_name, frame, remainingPictureCount, exitFlag):
	if exitFlag.is_set():
		return
	if not os.path.exists(directory):
		os.makedirs(directory)
	full_path = os.path.join(directory, img_name)
	cv2.imwrite(full_path, frame)

	if (remainingPictureCount % 10) == 0:
		print(f"{full_path} written! Remaining images: {remainingPictureCount}")

def take_pictures(pictureAmount, cam, directory, img_prefix, exitFlag):
	global imageCounter, remainingPictureCount, takingPictures
	remainingPictureCount = pictureAmount
	for _ in range(pictureAmount):
		if exitFlag.is_set():
			break
		ret, frame = cam.read()
		if ret:
			img_name = f"{img_prefix}_{imageCounter}.png"
			threading.Thread(target=capture_image, args=(directory, img_name, frame.copy(), remainingPictureCount - 1, exitFlag)).start()
			imageCounter += 1
			remainingPictureCount -= 1
			time.sleep(1)
		else:
			print("Failed to grab a frame!")
	takingPictures = False
	exitFlag.set()

def main():
	global imageCounter, remainingPictureCount, takingPictures
	imageCounter = 0
	remainingPictureCount = 0
	takingPictures = False
	exitFlag = threading.Event()

	cam = cv2.VideoCapture(0)
	if cam is None or not cam.isOpened():
		print("Failed to open video input!")
		exit(1)

	cv2.namedWindow("test")

	while True:
		if not takingPictures:
			while 1:
				pictureAmountString = input("How many pictures do you want to take? ")
				try:
					pictureAmount = int(pictureAmountString)
					break
				except ValueError:
					print(f"Expected a number, got: \"{pictureAmountString}\"")

			while 1:
				directory = input("Enter directory name (single letter) where pictures will be saved: ")
				if len(directory) != 1 or not directory.isalpha():
					print(f"Expected a single letter, got: \"{directory}\"")
				else:
					break

			directory = directory.upper()

			img_prefix = directory
			print("Press spacebar to start taking pictures")
			takingPictures = False

		while True:
			ret, frame = cam.read()
			if not ret:
				print("failed to grab frame")
				break

			feedbackText = "Press spacebar to start taking pictures"
			if takingPictures:
				feedbackText = f"Taking pictures... Remaining: {remainingPictureCount}"

			cv2.putText(frame, feedbackText, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
			cv2.imshow("test", frame)

			k = cv2.waitKey(1)
			if k % 256 == 27: # escape pressed
				print("Escaping...")
				exitFlag.set()
				break
			if k % 256 == 32 and not takingPictures: # space bar pressed
				takingPictures = True
				threading.Thread(target=take_pictures, args=(pictureAmount, cam, directory, img_prefix, exitFlag)).start()
				break

		if exitFlag.is_set():
			break

	cam.release()
	cv2.destroyAllWindows()

if __name__ == "__main__":
	main()