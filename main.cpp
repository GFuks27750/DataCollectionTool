#include <opencv2/opencv.hpp>

#include <stdio.h>
#include <stdint.h>
#include <ctype.h>

#include <chrono>
#include <thread>
#include <mutex>

#include <filesystem>
namespace fs = std::filesystem;

using PhotoCount = uint32_t;

struct Context {
  bool running = true;
  PhotoCount photoCount = 0;
  PhotoCount remainingPhotos = 0;
  char directory = '\0';
};

PhotoCount getPhotoCount();
char getDirectory();
const char *numToString(uint64_t number, size_t &length);
void takePhotos();

Context gContext{};
std::mutex gContextMutex{};

bool gDone = false;
std::mutex gDoneMutex{};

cv::VideoCapture gCapture;
std::mutex gCaptureMutex{};

int main(void) {
  try {
    gCapture = cv::VideoCapture(0);
  } catch (cv::Exception &e) {
    fprintf(stderr, "Failed to open video capture!\n");
    return 1;
  }
  if (!gCapture.isOpened()) {
    fprintf(stderr, "Failed to open video capture!\n");
    return 1;
  }

  cv::namedWindow("Data collection");

  bool takingPhotos = false;
  std::thread thread;
  cv::Mat frame{};

  while (gContext.running) {
    if (!takingPhotos) {
      std::lock_guard<std::mutex> guard(gContextMutex);
      gContext.remainingPhotos = gContext.photoCount = getPhotoCount();
      gContext.directory = getDirectory();

      printf("Press space bar to begin!\n");

      char buf[2] = { gContext.directory, '\0' };
      fs::create_directory(buf);
    }

    while (1) {
      {
        std::lock_guard<std::mutex> guard(gCaptureMutex);
        if (!gCapture.read(frame)) {
          fprintf(stderr, "Failed to grab frame!\n");
          break;
        }
      }

      {
        std::lock_guard<std::mutex> guard(gDoneMutex);
        if (gDone) {
          takingPhotos = false;
          break;
        }
      }

      if (takingPhotos) {
        size_t numLength = 0;
        const char *numString = numToString(gContext.remainingPhotos, numLength);

        char buf[19+numLength] = {0};
        memcpy(&buf[ 0], "Remaining photos: ", 18);
        memcpy(&buf[18], numString, numLength);

        cv::putText(frame, buf, cv::Point(10, 30),
                    cv::FONT_HERSHEY_SIMPLEX, 1.0, CV_RGB(0, 255, 0), 2, cv::LINE_AA);
      } else {
        cv::putText(frame, "Press space bar to begin!", cv::Point(10, 30),
                    cv::FONT_HERSHEY_SIMPLEX, 1.0, CV_RGB(0, 255, 0), 2, cv::LINE_AA);
      }

      cv::imshow("Data collection", frame);

      int k = cv::waitKey(1);
      if (k == 27) {
        printf("Escaping...\n");
        gContext.running = false;
        break;
      } else if (k == 32 && !takingPhotos) {
        takingPhotos = true;
        thread = std::thread(takePhotos);
        break;
      }
    }
  }

  if (thread.joinable()) thread.join();

  gCapture.release();
  cv::destroyAllWindows();

  return 0;
}



static char sInputBuffer[32] = {0};

PhotoCount getPhotoCount() {
  while (1) {
    printf("Enter number of photos you wish to take: ");

    assert(fgets(sInputBuffer, 32, stdin));
    size_t len = strlen(sInputBuffer);
    if (sInputBuffer[len-1] == '\n') sInputBuffer[--len] = '\0';

    PhotoCount count = 0;
    const char *ptr = sInputBuffer;
    while (*ptr) {
      if (!isdigit(*ptr)) {
        fprintf(stderr, "Expected a number, got \"%s\"!\nRetrying...\n", sInputBuffer);
        break;
      }

      count *= 10;
      count += (*ptr)-'0';
      ++ptr;
    }

    if (!*ptr) return count;
  }
}

char getDirectory() {
  while (1) {
    printf("Enter a single letter for pictures to be stored at: ");

    assert(fgets(sInputBuffer, 32, stdin));
    size_t len = strlen(sInputBuffer);
    if (sInputBuffer[len-1] == '\n') sInputBuffer[--len] = '\0';

    if (len != 1 || !isalpha(sInputBuffer[0])) {
      fprintf(stderr, "Expected one letter, got: \"%s\"!\nRetrying...\n", sInputBuffer);
      continue;
    }

    return toupper(sInputBuffer[0]);
  }
}

const char *numToString(uint64_t number, size_t &length) {
  static constexpr size_t BUF_SIZE = 32;
  static char buf[BUF_SIZE] = {0};

  length = 0;
  while (number) {
    buf[BUF_SIZE-(++length)] = '0'+(number % 10);
    number /= 10;
  }

  return &buf[BUF_SIZE-length-1];
}

void takePhotos() {
  cv::Mat frame{};
  while (1) {
    {
      std::lock_guard<std::mutex> guard(gContextMutex);
      if (!gContext.running || !gContext.remainingPhotos) break;
    }

    {
      std::lock_guard<std::mutex> guard(gCaptureMutex);

      if (!gCapture.read(frame)) {
        fprintf(stderr, "Failed to grab frame!\n");
        break;
      }
    }

    {
      std::lock_guard<std::mutex> guard(gContextMutex);

      char dir[2] = { gContext.directory, 0 };

      size_t length = 0;

      std::stringstream filename{};
      filename << (gContext.remainingPhotos--) << ".png";

      fs::path path = dir;
      path /= filename.str();
      cv::imwrite(path.string(), frame);
    }

    std::this_thread::sleep_for(std::chrono::seconds(1));
  }
}