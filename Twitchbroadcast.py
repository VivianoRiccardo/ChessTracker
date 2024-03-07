import subprocess
import Logwriter
import json
import threading
import Twitchapi
import Globalvals
import time
import datetime

class TwitchBroadcast:
    
    def __init__(self, frame_height=720,frame_width=1280, json_path = './json/streaming_configuration.json'):
        
        self.log_file_name = './twitchbroadcast-{}.log'
        f = open(json_path,'r')
        self.is_online = True
        self.json_file = json.load(f)
        f.close()
        videosize = str(frame_width) + 'X' + str(frame_height)
        twitch_data = self.json_file['streaming_services']['twitch']
        rtmp_server = twitch_data['servers'][0]['url']
        twitch_stream_key = twitch_data['streaming_key']
        CBR = '8000k'
        self.ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'rawvideo',
            '-pix_fmt', 'rgb24', 
            '-framerate', '30',  # Adjusted to 30 fps (or 60 fps if applicable)
            '-video_size', videosize,
            '-i', '-',  # Input from pipe
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-tune', 'zerolatency',  # Optimize for low latency
            '-f', 'flv',
            '-b:v', CBR,
            '-maxrate', CBR,
            '-bufsize', CBR,  # Adjusted bufsize to 8000k (you can experiment with this value)
            '-pix_fmt', 'yuv420p',
            '-threads', '2',  # Reduced the number of threads to 2
            rtmp_server + twitch_stream_key
        ]
        self.s = threading.Lock()
        self.keep_going = False
        
        
        self.ffmpeg_process = subprocess.Popen(self.ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)

    
    def exit_critical_section(self):
        self.s.release()
        
    def enter_critical_section(self):
        self.s.acquire()
    
    def send_frames_to_twitch(self, list_of_frames):
        
        for frame in list_of_frames:
            try:

                self.ffmpeg_process.stdin.write(frame.tobytes())
            except:
                print("Error")
                self.ffmpeg_process.stdin.close()
                self.ffmpeg_process.wait()
                error_output = self.ffmpeg_process.stderr.read().decode()
                Logwriter.save_log(self.log_file_name,error_output)
                self.ffmpeg_process = subprocess.Popen(self.ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                return False
        return True 
    
    def close_process(self):
        self.ffmpeg_process.stdin.close()
        self.ffmpeg_process.wait()
    
    def handle_twitch(self):
        while True:
            date = datetime.datetime.now()
            last_frame = []
            Globalvals.is_online_mutex.acquire()

            while Globalvals.is_online:
                Globalvals.is_online_mutex.release()
                flag = True
                l = []
                Globalvals.frames_queue.enter_frames_critical_section()
                l = Globalvals.frames_queue.frames
                Globalvals.frames_queue.frames = []
                Globalvals.frames_queue.exit_frames_critical_section()
                
                if l != []:
                    flag = False
                    last_frame = [l[-1]]
                    Globalvals.twitch.send_frames_to_twitch(l)
                    date = datetime.datetime.now()
                if flag and len(last_frame) > 0:
                    date_new = datetime.datetime.now()
                    if (date_new - date).total_seconds() >= 0.07:
                        Globalvals.twitch.send_frames_to_twitch(last_frame)
                        date = date_new
                Globalvals.is_online_mutex.acquire()
            Globalvals.is_online_mutex.release()    
            self.close_process()
            self.ffmpeg_process = subprocess.Popen(self.ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            Globalvals.is_online_mutex.acquire()
            self.is_online = True
            Globalvals.is_online_mutex.release()
        
    def check_streaming_status(self):
        twitch_api = Twitchapi.TwitchApi()
        date = datetime.datetime.now()
        while True:
            is_empty = True
            Globalvals.frames_queue.enter_dict_critical_section()
            if len(list(Globalvals.frames_queue.dictionary.keys())) > 0:
                is_empty = False
            Globalvals.frames_queue.exit_dict_critical_section()
            new_date = datetime.datetime.now()
            if not is_empty:
                twitch_api.set_access_token()
                ret = None
                while ret == None:
                    time.sleep(0.1)
                    ret = twitch_api.is_streaming('chesstracker')
                is_empty = (not ret)
            if is_empty and (new_date-date).total_seconds() >= 85:
                Globalvals.is_online_mutex.acquire()
                Globalvals.is_online = False
                while not self.is_online:
                    Globalvals.is_online_mutex.release()
                    time.sleep(1)
                    Globalvals.is_online_mutex.acquire()
                Globalvals.is_online_mutex.release()
                date = datetime.datetime.now()
            elif not is_empty:
                date = datetime.datetime.now()
            time.sleep(0.1)
        
    def run_batch(self):
        thread1 = threading.Thread(target=self.handle_twitch)
        thread1.start()
        thread2 = threading.Thread(target=self.check_streaming_status)
        thread2.start()
        return thread1, thread2    
