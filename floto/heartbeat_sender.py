import ctypes
import multiprocessing as mp
import time

import floto.api


class HeartbeatSender:
    def __init__(self):
        self.swf = floto.api.Swf()
        self.is_send_heartbeat = mp.Value(ctypes.c_bool, True)
        self.process = None
        self.request_cancel = mp.Value(ctypes.c_bool, False)

    def cancel_requested(self):
        return self.request_cancel.value

    def send_heartbeats(self, timeout, task_token):
        self.is_send_heartbeat.value = True
        self.process = mp.Process(target=self._send_heartbeat, args=(timeout, task_token))
        self.process.start()

    def stop_heartbeats(self):
        self.is_send_heartbeat.value = False

    def _send_heartbeat(self, timeout, task_token):
        while self.is_send_heartbeat.value:
            t = time.time()
            response = None
            try:
                response = self.swf.record_activity_task_heartbeat(task_token=task_token, details=None)
            except Exception:
                pass
            if response:
                self.request_cancel.value = response.get("cancelRequested", False)
            time.sleep(timeout - (time.time() - t))
