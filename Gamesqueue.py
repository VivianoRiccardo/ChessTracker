from Chesscom import ChessCom
import datetime
import threading
import Globalvals

class GamesQueue:
    
    def __init__(self):
        self.chesscom_mutex = threading.Lock()
        self.chesscom_games_dictionary = {}#key is id, value is a list of moves + infos
        self.lichess_games_dictionary = {}#key is id, value is a list of moves + infos
        self.chesscom = ChessCom()
        
    def enter_chesscom_critical_section(self):
        self.chesscom_mutex.acquire()
    
    def exit_chesscom_critical_section(self):
        self.chesscom_mutex.release()
    
    def insert_chesscom_move(self, infos):
        Globalvals.games_queue.enter_chesscom_critical_section()
        if infos['id'] in Globalvals.games_queue.chesscom_games_dictionary:
            if len(Globalvals.games_queue.chesscom_games_dictionary[infos['id']]) > 0:
                if int(infos['seq']) > int(Globalvals.games_queue.chesscom_games_dictionary[infos['id']][0]['seq']):
                    Globalvals.games_queue.chesscom_games_dictionary[infos['id']] = [infos]
            else:
                    Globalvals.games_queue.chesscom_games_dictionary[infos['id']].append(infos)
        Globalvals.games_queue.exit_chesscom_critical_section()
