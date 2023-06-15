import json
import datetime
import threading

def save_json(path, key, value):
    with open(path, "r") as fp:
        json_data = json.load(fp)
    json_data[key] = value
    with open(path, "w") as fp:
        json.dump(json_data, fp, indent=4)

def print_textbox(textbox, message):
    now = datetime.datetime.now()
    now = now.strftime('%H:%M:%S')
    textbox.configure(state='normal')
    textbox.insert("end", f"[{now}]{message}\n")
    textbox.configure(state='disabled')
    textbox.see("end")

class thread_fnc(threading.Thread):
    def __init__(self, fnc, *args, **kwargs):
        super(thread_fnc, self).__init__(*args, **kwargs)
        self.fnc = fnc
        self._stop = threading.Event()
    def stop(self):
        self._stop.set()
    def stopped(self):
        return self._stop.isSet()
    def run(self):
        while True:
            if self.stopped():
                return
            self.fnc()