import cv2
import numpy as np
from imutils import contours, grab_contours
from skimage import measure
import os
import matplotlib.pyplot as plt
import multiprocessing as mp
import threading as tr
import time


class DataManager:
    def __init__(self, filename, res, roi, in_q, out_q):
        self.filename = filename
        self.in_q = in_q
        self.out_q = out_q
        self.shutdown_event = tr.Event()
        self.res = res
        self.roi = roi

    def start(self):
        self.t = tr.Thread(target=self.update, daemon=True)
        self.t.start()

    def stop(self):
        self.shutdown_event.set()

    def update(self):
        # Load the video
        cap = cv2.VideoCapture(path)
        ret, frame = cap.read()
        while not ret:
            ret, frame = cap.read()

        i = 0
        while cap.isOpened() and not self.shutdown_event.is_set():
            ret, frame = cap.read()
            if not ret:
                print('Got no image from the videostream')
                break

            # Crop the frame
            frame = cut_roi(self.roi, frame)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.in_q.put((i, gray))
            i += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
        cap.release()
        self.in_q.join()


def find_components(thresh_img, min_size=1000):
    """Find the components in the mask that are larger than min_size."""
    labels = measure.label(thresh_img, connectivity=2, background=0)
    mask = np.zeros(thresh_img.shape, dtype="uint8")

    for label in np.unique(labels):
        # If this is the background label, ignore it
        if label == 0:
            continue

        # Construct the label mask and count the pixels
        labelMask = np.zeros(thresh_img.shape, dtype="uint8")
        labelMask[labels == label] = 255
        numPixels = cv2.countNonZero(labelMask)

        # If the number of pixels in the object is large enough add it to
        # the valid objects list
        if numPixels >= min_size:
            mask = cv2.add(mask, labelMask)

    # Find the contours in the mask, then sort them from left to right
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    if len (cnts) == 0:
        return None
    cnts = grab_contours(cnts)
    return cnts


def find_center(cnts):
    """Find the center of the global bounding box"""
    if len(cnts) != 4:
        return None
    
    # Find the extremes of the bounding boxes
    bbox = [0, 0, 0, 0]
    for cnt in cnts:
        x, y, w, h = cv2.boundingRect(cnt)
        if bbox[0] == 0 or x < bbox[0]: bbox[0] = x
        if bbox[1] == 0 or y < bbox[1]: bbox[1] = y
        if x + w > bbox[2]: bbox[2] = x + w
        if y + h > bbox[3]: bbox[3] = y + h

    # Put back into the orignal x,y,w,h format
    bbox[3] -= bbox[1]
    bbox[2] -= bbox[0]
    return [bbox[0] + 1/2 * bbox[2], bbox[1] + 1/2 * bbox[3]]


def process_image(in_q, out_q):
    """
    Process the image and find the contours
    
    Puts the center point of the bounding box in the output queue
    format (x, y, w, h) in pixels.
    """
    if not in_q.empty():
        t, gray = in_q.get()
    else:
        return

    gray = cv2.GaussianBlur(gray, (5, 5), 0)  # Blur to remove noise
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    thresh = cv2.erode(thresh, None, iterations=2)
    # thresh = cv2.dilate(thresh, None, iterations=1)
    
    cnts = find_components(thresh, min_size=2000)
    if not cnts is None:
        center = find_center(cnts)
    else:
        center = None

    out_q.put((t, center))
    in_q.task_done()


def run_paralel(path, res, roi):
    """Run the image processing in parallel using multiprocessing."""
    # Create a threshold mask and find the contours in the frames
    in_q = mp.JoinableQueue()
    out_q = mp.Queue()
    source = DataManager(path, res, roi, in_q, out_q)

    # Start the source and the process pool
    source.start()
    pool = mp.Pool(mp.cpu_count(), process_image, (in_q, out_q))

    # Monitor the output queue
    data = []
    while source.t.is_alive or (not in_q.empty() and out_q.empty()):
        if not out_q.empty():
            t, center = out_q.get()
            if center is not None:
                data.append([t, center])
                print('got point {}'.format(t))
            else:
                print('No contours found in frame {}'.format(t))
        else:
            time.sleep(0.001)

    data = np.array(data)
    data.savetxt('data.csv', delimiter=',')

    # Stop the source and the process pool
    source.stop()
    pool.close()
    pool.join()


def cut_roi(roi, img):
    return img[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]


def run_single_thread(path, res, roi):
    """Run the image processing in a single thread."""
    in_q = mp.JoinableQueue()
    out_q = mp.Queue()

    cap = cv2.VideoCapture(path)
    ret, frame = cap.read()
    while not ret:
        ret, frame = cap.read()

    data = []
    i = 0
    while cap.isOpened() and i < 5:
        ret, frame = cap.read()
        if not ret:
            print('Got no image from the videostream')
            break

        # Crop the frame
        frame = cut_roi(roi, frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        in_q.put((i, gray))
        process_image(in_q, out_q)
        i += 1
        res = out_q.get()
        if not None in res:
            cv2.circle(frame, (int(res[1][0]), int(res[1][1])), 5, (0, 0, 255), -1)
            print('got point')
        else:
            print('No contours found in frame {}'.format(i))

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows
    cap.release()

    data = np.array(data)
    print(data)
    np.savetxt('data.csv', data, delimiter=',')


if __name__ == '__main__':
    path = 'C:/OLYMPUS Stream Start 2022-12-06 13-27-08.mp4'
    res = (2560, 1380)
    roi = (res[0] * 1/3, res[1] * 1/4, res[0] * 1/3, res[1] * 2.5/4)

    run_paralel(path, res, roi)