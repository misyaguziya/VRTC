import os
import ctypes
import time
from psutil import process_iter
from threading import Thread
import openvr
import numpy as np
from PIL import Image
try:
    from . import overlay_utils as utils
except ImportError:
    import overlay_utils as utils
from utils import printLog

def mat34Id(array):
    arr = openvr.HmdMatrix34_t()
    for i in range(3):
        for j in range(4):
            arr[i][j] = array[i][j]
    return arr

def getBaseMatrix(x_pos, y_pos, z_pos, x_rotation, y_rotation, z_rotation):
    arr = np.zeros((3, 4))
    rot = utils.euler_to_rotation_matrix((x_rotation, y_rotation, z_rotation))

    for i in range(3):
        for j in range(3):
            arr[i][j] = rot[i][j]

    arr[0][3] = x_pos * z_pos
    arr[1][3] = y_pos * z_pos
    arr[2][3] = - z_pos
    return arr

def getHMDBaseMatrix():
    x_pos = 0.0
    y_pos = -0.4
    z_pos = 1.0
    x_rotation = 0.0
    y_rotation = 0.0
    z_rotation = 0.0
    arr = getBaseMatrix(x_pos, y_pos, z_pos, x_rotation, y_rotation, z_rotation)
    return arr

def getLeftHandBaseMatrix():
    x_pos = 0.0
    y_pos = -0.06
    z_pos = -0.14
    x_rotation = -62.0
    y_rotation = 154.0
    z_rotation = 71.0
    arr = getBaseMatrix(x_pos, y_pos, z_pos, x_rotation, y_rotation, z_rotation)
    return arr

def getRightHandBaseMatrix():
    x_pos = 0.0
    y_pos = -0.06
    z_pos = -0.14
    x_rotation = -62.0
    y_rotation = -154.0
    z_rotation = -71.0
    arr = getBaseMatrix(x_pos, y_pos, z_pos, x_rotation, y_rotation, z_rotation)
    return arr

class Overlay:
    def __init__(self, settings_dict):
        self.system = None
        self.overlay = None
        self.handle = None
        self.initialized = False
        self.loop = True
        self.thread_overlay = None

        self.settings = {}
        self.lastUpdate = {}
        self.fadeRatio = {}
        for key, value in settings_dict.items():
                self.settings[key] = value
                self.lastUpdate[key] = time.monotonic()
                self.fadeRatio[key] = 1

    def init(self):
        try:
            self.system = openvr.init(openvr.VRApplication_Background)
            self.overlay = openvr.IVROverlay()
            self.overlay_system = openvr.IVRSystem()
            self.handle = {}
            for i, size in enumerate(self.settings.keys()):
                self.handle[size] = self.overlay.createOverlay(f"VRCT{i}", f"VRCT{i}")
                self.overlay.showOverlay(self.handle[size])
            self.initialized = True

            for size in self.settings.keys():
                self.updateImage(Image.new("RGBA", (1, 1), (0, 0, 0, 0)), size)
                self.updateColor([1, 1, 1], size)
                self.updateOpacity(self.settings[size]["opacity"], size, True)
                self.updateUiScaling(self.settings[size]["ui_scaling"], size, True)
                self.updatePosition(
                    self.settings[size]["x_pos"],
                    self.settings[size]["y_pos"],
                    self.settings[size]["z_pos"],
                    self.settings[size]["x_rotation"],
                    self.settings[size]["y_rotation"],
                    self.settings[size]["z_rotation"],
                    self.settings[size]["tracker"]
                )

        except Exception as e:
            printLog("error:Could not initialise OpenVR", e)

    def updateImage(self, img, size):
        if self.initialized is True:
            width, height = img.size
            img = img.tobytes()
            img = (ctypes.c_char * len(img)).from_buffer_copy(img)

            try:
                self.overlay.setOverlayRaw(self.handle[size], img, width, height, 4)
            except Exception as e:
                printLog("error:Could not update image", e)
                self.initialized = False
                self.reStartOverlay()
                while self.initialized is False:
                    time.sleep(0.1)
                self.overlay.setOverlayRaw(self.handle[size], img, width, height, 4)
            self.updateOpacity(self.settings[size]["opacity"], size, True)
            self.lastUpdate[size] = time.monotonic()

    def clearImage(self, size):
        if self.initialized is True:
            self.updateImage(Image.new("RGBA", (1, 1), (0, 0, 0, 0)), size)

    def updateColor(self, col, size):
        """
        col is a 3-tuple representing (r, g, b)
        """
        if self.initialized is True:
            r, g, b = col
            self.overlay.setOverlayColor(self.handle[size], r, g, b)

    def updateOpacity(self, opacity, size, with_fade=True):
        self.settings[size]["opacity"] = opacity

        if self.initialized is True:
            if with_fade is True:
                if self.fadeRatio[size] > 0:
                    self.overlay.setOverlayAlpha(self.handle[size], self.fadeRatio[size] * self.settings[size]["opacity"])
            else:
                self.overlay.setOverlayAlpha(self.handle[size], self.settings[size]["opacity"])

    def updateUiScaling(self, ui_scaling, size):
        self.settings[size]["ui_scaling"] = ui_scaling
        if self.initialized is True:
            self.overlay.setOverlayWidthInMeters(self.handle[size], self.settings[size]["ui_scaling"])

    def updatePosition(self, x_pos, y_pos, z_pos, x_rotation, y_rotation, z_rotation, tracker, size):
        """
        x_pos, y_pos, z_pos are floats representing the position of overlay
        x_rotation, y_rotation, z_rotation are floats representing the rotation of overlay
        tracker is a string representing the tracker to use ("HMD", "LeftHand", "RightHand")
        """

        self.settings[size]["x_pos"] = x_pos
        self.settings[size]["y_pos"] = y_pos
        self.settings[size]["z_pos"] = z_pos
        self.settings[size]["x_rotation"] = x_rotation
        self.settings[size]["y_rotation"] = y_rotation
        self.settings[size]["z_rotation"] = z_rotation
        self.settings[size]["tracker"] = tracker

        match tracker:
            case "HMD":
                base_matrix = getHMDBaseMatrix()
                trackerIndex = openvr.k_unTrackedDeviceIndex_Hmd
            case "LeftHand":
                base_matrix = getLeftHandBaseMatrix()
                trackerIndex = self.overlay_system.getTrackedDeviceIndexForControllerRole(openvr.TrackedControllerRole_LeftHand)
            case "RightHand":
                base_matrix = getRightHandBaseMatrix()
                trackerIndex = self.overlay_system.getTrackedDeviceIndexForControllerRole(openvr.TrackedControllerRole_RightHand)
            case _:
                base_matrix = getHMDBaseMatrix()
                trackerIndex = openvr.k_unTrackedDeviceIndex_Hmd

        translation = (self.settings[size]["x_pos"], self.settings[size]["y_pos"], - self.settings[size]["z_pos"])
        rotation = (self.settings[size]["x_rotation"], self.settings[size]["y_rotation"], self.settings[size]["z_rotation"])
        transform = utils.transform_matrix(base_matrix, translation, rotation)
        transform = mat34Id(transform)

        if self.initialized is True:
            self.overlay.setOverlayTransformTrackedDeviceRelative(
                self.handle[size],
                trackerIndex,
                transform
            )

    def updateDisplayDuration(self, display_duration, size):
        self.settings[size]["display_duration"] = display_duration

    def updateFadeoutDuration(self, fadeout_duration, size):
        self.settings[size]["fadeout_duration"] = fadeout_duration

    def checkActive(self):
        try:
            if self.system is not None and self.initialized is True:
                new_event = openvr.VREvent_t()
                while self.system.pollNextEvent(new_event):
                    if new_event.eventType == openvr.VREvent_Quit:
                        return False
            return True
        except Exception as e:
            printLog("error:Could not check SteamVR running", e)
            return False

    def evaluateOpacityFade(self, lastUpdate, currentTime, size):
        if (currentTime - lastUpdate) > self.settings[size]["display_duration"]:
            timeThroughInterval = currentTime - lastUpdate - self.settings[size]["display_duration"]
            self.fadeRatio[size] = 1 - timeThroughInterval / self.settings[size]["fadeout_duration"]
            if self.fadeRatio[size] < 0:
                self.fadeRatio[size] = 0
            self.overlay.setOverlayAlpha(self.handle[size], self.fadeRatio[size] * self.settings[size]["opacity"])

    def update(self, size):
        currTime = time.monotonic()
        if self.settings[size]["fadeout_duration"] != 0:
            self.evaluateOpacityFade(self.lastUpdate[size], currTime, size)
        else:
            self.updateOpacity(self.settings[size]["opacity"], size, True)

    def mainloop(self):
        self.loop = True
        while self.checkActive() is True and self.loop is True:
            startTime = time.monotonic()
            for size in self.settings.keys():
                self.update(size)
            sleepTime = (1 / 16) - (time.monotonic() - startTime)
            if sleepTime > 0:
                time.sleep(sleepTime)

    def main(self):
        self.init()
        if self.initialized is True:
            self.mainloop()

    def startOverlay(self):
        self.thread_overlay = Thread(target=self.main)
        self.thread_overlay.daemon = True
        self.thread_overlay.start()

    def shutdownOverlay(self):
        if isinstance(self.thread_overlay, Thread):
            self.loop = False
            self.thread_overlay.join()
            self.thread_overlay = None
        if isinstance(self.overlay, openvr.IVROverlay):
            for size in self.settings.keys():
                if isinstance(self.handle[size], int):
                    self.overlay.destroyOverlay(self.handle[size])
            self.overlay = None
        if isinstance(self.system, openvr.IVRSystem):
            openvr.shutdown()
            self.system = None
        self.initialized = False

    def reStartOverlay(self):
        self.shutdownOverlay()
        self.startOverlay()

    @staticmethod
    def checkSteamvrRunning() -> bool:
        _proc_name = "vrmonitor.exe" if os.name == "nt" else "vrmonitor"
        return _proc_name in (p.name() for p in process_iter())

if __name__ == "__main__":
    x_pos = 0
    y_pos = 0
    z_pos = 0
    x_rotation = 0
    y_rotation = 0
    z_rotation = 0

    base_matrix = getLeftHandBaseMatrix()
    translation = (x_pos * z_pos, y_pos * z_pos, z_pos)
    rotation = (x_rotation, y_rotation, z_rotation)
    transform = utils.transform_matrix(base_matrix, translation, rotation)
    transform = mat34Id(transform)
    print(transform)