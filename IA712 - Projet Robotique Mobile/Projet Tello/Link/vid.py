#!/usr/bin/env python3

##############################################################################
#
# Allows experimenting with video stream in OpenCV under temperature control
# and battery monitoring.
#
# Adapted from: https://github.com/robagar/tello-asyncio/blob/main/examples/video_opencv.py
# Modified by Helge Hackbarth and provided under the same conditions as the
# original file.
#
# The OpenCV UI must run in the main thread, so the drone control runs in a
# worker thread with its own asyncio event loop.
#
# Please note:
#   - If OpenCV fails to capture any video it gives up without showing the
#     window
#   - The video may lag a few seconds behind the live action, but it should
#     keep up with the live stream after some seconds
#
##############################################################################

import asyncio
import time
from threading import Thread

import cv2  # requires python-opencv

from tello_asyncio import Tello, VIDEO_URL

# constants
TEMP_THRESHOLD = 85
BATTERY_CRITICAL_PERCENT = 20
# global vars
video_started = False
battery_critical = False

print("[main thread] START")

##############################################################################
# drone control in worker thread


def fly():
    print("[fly thread] START")

    async def main():
        global video_started, battery_critical, TEMP_THRESHOLD, BATTERY_CRITICAL_PERCENT
        drone = Tello()
        motors_running = False
        try:
            await asyncio.sleep(1)
            await drone.wifi_wait_for_network(prompt=True)
            await drone.connect()
            await drone.start_video(connect=False)
            video_started = True
            while video_started and not battery_critical:
                if int(drone.temperature.high) >= TEMP_THRESHOLD and not motors_running:
                    # cool down by activating motors
                    try:
                        await drone.motor_on()
                        motors_running = True
                    except:
                        # motors were propably already on
                        pass
                if int(drone.temperature.high) < TEMP_THRESHOLD and motors_running:
                    # turn off motors
                    try:
                        await drone.motor_off()
                        motors_running = False
                    except:
                        # motors were propably already on
                        pass
                if video_started:
                    await asyncio.sleep(10)
                battery = await drone.query_battery()
                print(f"battery: {battery}%")
                battery_critical = int(battery) < BATTERY_CRITICAL_PERCENT
                print(
                    f"temperature: {drone.temperature.low}-{drone.temperature.high}°C"
                )
        finally:
            await drone.stop_video()
            video_started = False
            try:
                if motors_running:
                    await drone.motor_off()
                    motors_running = False
            except:
                # motors were propably already on
                pass
            await drone.disconnect()

    # Python 3.7+
    asyncio.run(main())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

    print("[fly thread] END")


# needed for drone.wifi_wait_for_network() in worker thread in Python < 3.8
try:
    asyncio.get_child_watcher()
except NotImplementedError:
    pass

fly_thread = Thread(target=fly, daemon=True)
fly_thread.start()

##############################################################################
# Video capture and GUI in main thread


capture = None
try:
    while not video_started and fly_thread.is_alive():
        time.sleep(0.1)
    print(f"[main thread] OpenCV capturing video from {VIDEO_URL}")
    print(
        f"[main thread] Press Ctrl-C or any key with the OpenCV window focussed to exit (the OpenCV window may take some time to close)"
    )
    capture = cv2.VideoCapture(VIDEO_URL)
    # capture.open(VIDEO_URL)

    while not battery_critical:
        # grab and show video frame in OpenCV window
        grabbed, frame = capture.read()
        if grabbed:
            cv2.imshow("tello-asyncio", frame)

        # process OpenCV events and exit if any key is pressed
        if cv2.waitKey(1) != -1:
            video_started = False
            if not fly_thread is None and fly_thread.is_alive():
                # wait for fly thread to finish
                print("[main thread] waiting for fly_thread to finish...")
                fly_thread.join()
            break
except KeyboardInterrupt:
    pass
finally:
    # tidy up
    if capture:
        capture.release()
    cv2.destroyAllWindows()

print("[main thread] END")