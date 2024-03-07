import Globalvals
import Logwriter
import threading
import datetime
import time
import json

class GamesChecker:
    
    def __init__(self, filename = './json/players.json'):
        self.filename = filename
        self.log_file_name = './gameschecker-{}.log'
    def run_chesscom_matches(self):
        phpsessid = None
        previous_phpsessid = None
        stringa = 'socket1'
        while True:
            f = open(self.filename, 'r')
            d = json.load(f)
            f.close()
            sorted_keys = sorted(d['players'], key=lambda k: d['players'][k]['priority'])
            sorted_keys.reverse()
            for i in sorted_keys:
                for j in d['players'][i]['chesscom']['profiles']:
                    priority = d['players'][i]['priority']
                    username = j.strip()
                    Logwriter.save_log(self.log_file_name,"checking if the player '"+username+"' is playing")
                    print("checking if the player '"+username+"' is playing")
                    match_id = Globalvals.chesscom1.is_player_playing(username)
                    if match_id != None:
                        Logwriter.save_log(self.log_file_name,"The player '"+username+"' is playing")
                        print("The player '"+username+"' is playing")
                        Globalvals.games_queue.enter_chesscom_critical_section()
                        visit = False
                        if match_id != None and match_id not in Globalvals.games_queue.chesscom_games_dictionary:
                            visit = True
                        Globalvals.games_queue.exit_chesscom_critical_section()
                        if visit:
                            chesscom = Globalvals.chesscom1
                            Globalvals.games_queue.enter_chesscom_critical_section()
                            Globalvals.games_queue.chesscom_games_dictionary[match_id] = []
                            Globalvals.games_queue.exit_chesscom_critical_section()
                            chesscom.save_player_image(username)
                            Globalvals.frames_queue.enter_dict_critical_section()
                            Globalvals.frames_queue.dictionary['chesscom/'+match_id] = {'player':i,'username':username, 'priority_match_id':priority}
                            Globalvals.frames_queue.exit_dict_critical_section()
                            Globalvals.frames_queue.enter_json_critical_section()
                            Globalvals.frames_queue.json = d
                            Globalvals.frames_queue.exit_json_critical_section()
                            Logwriter.save_log(self.log_file_name,"visiting match: "+match_id+" of player "+username+" with browser")
                            print("visiting match: "+match_id+" of player "+username+" with browser")
                            Globalvals.phpsessid_mutex.acquire()
                            #Globalvals.phpsessid[stringa][0] = 'purcudiu'
                            while Globalvals.phpsessid[stringa][1]:
                                Globalvals.phpsessid_mutex.release()
                                time.sleep(1)
                                Globalvals.phpsessid_mutex.acquire()
                            Globalvals.phpsessid_mutex.release()
                            chesscom.visit_match_with_browser(match_id, stringa)
                            number = int(stringa[len('socket'):])
                            number +=1
                            if number >= 5:
                                number = 1
                            stringa = 'socket'+str(number)
     
    def run_batch(self):
        thread = threading.Thread(target=self.run_chesscom_matches)
        thread.start()
        return thread
