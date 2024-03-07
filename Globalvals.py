#from Gamesqueue import GamesQueue
#from Chesscom import ChessCom
#from Gameschecker import GamesChecker

import Gameschecker
import Gamesqueue
import Framesqueue
import Chesscom
import Twitchbroadcast
import time
import warnings
import threading

games_queue = Gamesqueue.GamesQueue()
chesscom1 = Chesscom.ChessCom()
chesscom2 = Chesscom.ChessCom(phpsessid_id = 'socket2')
chesscom3 = Chesscom.ChessCom(phpsessid_id = 'socket3')
chesscom4 = Chesscom.ChessCom(phpsessid_id = 'socket4')
frames_queue = Framesqueue.FramesQueue()
twitch = Twitchbroadcast.TwitchBroadcast()
phpsessid_mutex = threading.Lock()
is_online = True
is_online_mutex = threading.Lock()
phpsessid = {'socket1':[None, False], 'socket2':[None,False], 'socket3':[None,False], 'socket4':[None,False]}
warnings.filterwarnings("ignore")

def main():
    game_checker = Gameschecker.GamesChecker()
    game_checker_thread = game_checker.run_batch()
    chesscom_thread1 = chesscom1.run_batch()
    chesscom_thread2 = chesscom2.run_batch()
    chesscom_thread3 = chesscom3.run_batch()
    chesscom_thread4 = chesscom4.run_batch()
    frames_queue_thread = frames_queue.run_batch()
    twitch_thread1, twitch_thread2 = twitch.run_batch()
    chesscom_thread1.join()
    chesscom_thread2.join()
    chesscom_thread3.join()
    chesscom_thread4.join()
    game_checker_thread.join()
    frames_queue_thread.join()
    twitch_thread1.join()
    twitch_thread2.join()

if __name__ == "__main__":
    main()
