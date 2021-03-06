#!/usr/bin/env python

import argparse
import time

import numpy
from CVBackwardCompat import cv2

import CameraCommander


def main():

    parser = argparse.ArgumentParser(
        description='This script detects motion using an '
                    'attached webcam. When it detects '
                    'motion, it captures photos on an '
                    'attached gPhoto2-compatible photo '
                    'camera.')

    parser.add_argument(
        '--debug', type=bool, default=False,
        help='print debugging information')

    parser.add_argument(
        '--cam-index', type=int, default=-1,
        help='device index for detection camera '
             '(default=0)')
    parser.add_argument(
        '--width', type=int, default=320,
        help='capture width for detection camera '
             '(default=320)')
    parser.add_argument(
        '--height', type=int, default=240,
        help='capture height for detection camera '
             '(default=240)')
    parser.add_argument(
        '--detection-interval', type=float, default=0.25,
        help='interval between detection frames, in seconds '
             '(default=0.25)')

    parser.add_argument(
        '--learning-rate', type=float, default=0.008,
        help='learning rate for background subtractor, which '
             'is used in motion detection (default=0.008)')
    parser.add_argument(
        '--min-motion', type=float, default=0.15,
        help='proportion of frame that must be classified as '
             'foreground to trigger motion event '
             '(default=0.15, valid_range=[0.0, 1.0])')

    parser.add_argument(
        '--photo-count', type=int, default=1,
        help='number of photo frames per motion event '
             '(default=1)')
    parser.add_argument(
        '--photo-interval', type=float, default=3.0,
        help='interval between photo frames, in seconds '
             '(default=3.0)')
    parser.add_argument(
        '--photo-ev-step', type=float, default=None,
        help='exposure step between photo frames, in EV. If '
             'this is specified, --photo-interval is ignored '
             'and --photo-count refers to the length of an '
             'exposure bracketing sequence, not a time-lapse '
             'sequence.')

    args = parser.parse_args()

    debug = args.debug

    cam_index = args.cam_index
    w, h = args.width, args.height
    detection_interval = args.detection_interval

    learning_rate = args.learning_rate
    min_motion = args.min_motion

    photo_count = args.photo_count
    photo_interval = args.photo_interval
    photo_ev_step = args.photo_ev_step

    cap = cv2.VideoCapture(cam_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

    bgr = None
    gray = None
    fg_mask = None

    bg_sub = cv2.createBackgroundSubtractorMOG2()

    cc = CameraCommander.CameraCommander()

    while True:
        time.sleep(detection_interval)
        success, bgr = cap.read(bgr)
        if success:
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY, gray)
            gray = cv2.equalizeHist(gray, gray)
            fg_mask = bg_sub.apply(gray, fg_mask,
                                   learning_rate)
            h, w = fg_mask.shape
            motion = numpy.sum(numpy.where(
                fg_mask == 255, 1, 0))
            motion /= float(h * w)
            if debug:
                print('motion=%f' % motion)
            if motion >= min_motion and not cc.capturing:
                if photo_ev_step is not None:
                    cc.capture_exposure_bracket(
                        photo_ev_step, photo_count)
                else:
                    cc.capture_time_lapse(
                        photo_interval, photo_count)


if __name__ == '__main__':
    main()
