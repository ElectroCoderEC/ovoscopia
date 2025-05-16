import cv2


class VideoCamera:
    def __init__(self):
        self.cap = None
        self.active = False

    def start(self):
        if not self.active:
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            self.active = True

    def stop(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        self.active = False
        print("Cámara detenida")

    def state(self):
        return self.active

    def get_frame(self):
        if self.cap is None:
            return None
        success, frame = self.cap.read()
        if not success:
            return None
        ret, jpeg = cv2.imencode(".jpg", frame)
        return jpeg.tobytes()
