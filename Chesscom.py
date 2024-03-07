import requests
import json
import datetime
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
import time
import warnings
import chess
import chess.svg
import asyncio
import websockets
import threading
import Globalvals
import Logwriter
import logging

warnings.filterwarnings("ignore")

class ChessCom:
    BASE_URL = 'https://api.chess.com'
    player_url = '/pub/player/{}'
    player_current_game = 'https://www.chess.com/member/{}'
    game_live = 'https://www.chess.com/game/live/{}'
    player_current_stats = '/pub/player/{}/stats'
    player_archive = 'https://api.chess.com/pub/player/{}/games/{}/{}'
    current_game = None
    phpsessid = None
    driver = None
    temporary_phpsessid_for_requests = None

    def __init__(self, phpsessid = None, phpsessid_id = "socket1",profile_path="./profiles/profile11072023", json_path = './json/firefox_profile.json'):
        f = open(json_path,'r')
        self.json_file = json.load(f)
        f.close()
        self.profile_path = self.json_file['profile_path']
        self.phpsessid = phpsessid
        self.phpsessid_id = phpsessid_id
        self.log_file_name = './chesscom-{}.log'
    
        pass        
        
    def is_player_playing(self,username):
        try:    
            if self.driver == None:
                self.driver = self.setup_driver()
            driver = self.driver
            driver.get(self.player_current_game.format(username))
            time.sleep(1)
            txt = driver.page_source
            string_to_search = '<div class="presence-button-component presence-button-visible"><a href="/game/live/'
            if string_to_search in txt:
                txt = txt[txt.find(string_to_search)+len(string_to_search):]
                txt = txt[:txt.find('"')]
                if '?' in txt:
                    txt = txt[:txt.find('?')]
                self.current_game = txt
            else:
                self.current_game = None
        except:
            self.current_game = None
        return self.current_game
    def visit_match_with_browser(self, current_game, stringa):
        url = 'https://www.chess.com/game/live/'+current_game
        if self.driver == None:
            self.driver = self.setup_driver()
        driver = self.driver
        self.driver.get(url)
        time.sleep(5)
        cookies = driver.get_cookies()
        # Print the cookies
        Logwriter.save_log(self.log_file_name,"browsing phpsessid with socket: "+stringa)
        print("browsing phpsessid with socket: "+stringa)

        for cookie in cookies:
            if cookie['name'] == 'PHPSESSID':
                phpsessid = cookie['value']
                Globalvals.phpsessid_mutex.acquire()
                Globalvals.phpsessid[stringa][0] = phpsessid
                Globalvals.phpsessid[stringa][1] = True
                Globalvals.phpsessid_mutex.release()
        
    def save_player_image(self, username, path_to_save = './images/chesscom/'):
        username = username.lower()
        # make the request
        try:
            headers = {'User-Agent': 'curl/7.68.0'}
            ret = requests.get(self.BASE_URL+self.player_url.format(username),headers=headers)
            # load the body 
            ret = json.loads(ret.content)
            # get the unix timestamp
            avatar_url = ret['avatar']
            extensions = ".jpg"
            if avatar_url.endswith(".png"):
                extension = ".png"
            elif avatar_url.endswith(".gif"):
                extension = ".gif"
            elif avatar_url.endswith(".svg"):
                extension = ".svg"
            elif avatar_url.endswith(".jpeg"):
                extension = ".jpeg"
            else:
                return path_to_save+'unknown.png'
            
            filename = path_to_save+username+extensions
            
            # Send a GET request to the URL
            response = requests.get(avatar_url)
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Open a file in binary mode and write the image content
                with open(filename, 'wb') as file:
                    file.write(response.content)
                return filename
            else:
                return path_to_save+'unknown.png'
        except:
            return path_to_save+'unknown.png'
      
    
    def decode_moves(self, n):
        T = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?{~}(^)[]@#$,./&-*++="
        w = len(n)
        C = []
        i = 0
        
        while i < w:
            c = {}
            o = T.index(n[i])
            s = T.index(n[i + 1])
            
            if s > 63:
                c["promotion"] = "qnrbkp"[((s - 64) // 3)]
                s = o + (o < 16 and -8 or 8) + ((s - 1) % 3) - 1
            
            if o > 75:
                c["drop"] = "qnrbkp"[o - 79]
            else:
                c["from"] = T[o % 8] + str((o // 8) + 1)
            c["to"] = T[s % 8] + str((s // 8) + 1)
            C.append(c)
            
            i += 2
        
        return C
    
    
    def setup_driver(self):
        logging.basicConfig(level=logging.WARNING)
        firefox_options = Options()
        firefox_options.add_argument("-profile")
        firefox_options.add_argument(self.profile_path)
        firefox_options.add_argument('-headless')
        driver = webdriver.Firefox(options=firefox_options)
        self.driver = driver
        return driver
        
    
    
    def get_player_ratings(self, username):
        username = username.lower()
        try:
            headers = {'User-Agent': 'curl/7.68.0'}
            # make the request
            ret = requests.get(self.BASE_URL+self.player_current_stats.format(username),headers=headers)
            # load the body 
            ret = json.loads(ret.content)
            print(ret)
            # get the games list
            rapid = '?'
            try:
                rapid = ret['chess_rapid']['last']['rating']
            except:
                rapid = '?'
            blitz = '?'
            bullet = '?'
            try:
                blitz = ret['chess_blitz']['last']['rating']
            except:
                blitz = '?'
            try:
                bullet = ret['chess_bullet']['last']['rating']
            except:
                bullet = '?'
            return rapid, blitz, bullet
        except:
            return None, None, None
     
    def get_fen_from_moves(self, moves):
        if moves == []:
            return ""
        board = chess.Board()
        count = 0
        for i in moves:
            move = i['from']+i['to']
            if 'promotion' in i:
                n = i['promotion'].lower()
                if n == 'k':
                    n = 'n'
                move+=n
            move = chess.Move.from_uci(move)
            board.push(move)
            count+=1
        return board.fen()
    
    def get_finished_match_winner_info(self, username, match_id, yyyy, mm):
        
        ret = requests.get(self.player_archive.format(username, yyyy, mm))
        ret = json.loads(ret.content)['games']
        ret.reverse()
        for i in ret:
            url = i['url']
            m_id = url[url.find('game/live/')+len('game/live/'):]
            if m_id == match_id:
                pgn = i['pgn']
                info = pgn.split('\n')
                for element in info:
                    if 'Result' in element:
                        v = element
                        if '1-0' in v:
                            return 'w'
                        elif '0-1' in v:
                            return 'b'
                        return 'd'
        return None
                
            
    async def socket(self, socket_url = 'wss://live2.chess.com/cometd'):
        match_id = None
        list_match_ids = []
        while True:
           
            Globalvals.phpsessid_mutex.acquire()
            phpsessid = Globalvals.phpsessid[self.phpsessid_id][0]
            Globalvals.phpsessid_mutex.release()
            
            if phpsessid != None:
                self.temporary_phpsessid_for_requests = phpsessid
                async with websockets.connect(uri=socket_url, extra_headers= {'Cookie':'PHPSESSID='+phpsessid+';'}) as websocket:
                    try:
                        message1 = '[{"version":"1.0","minimumVersion":"1.0","channel":"/meta/handshake","supportedConnectionTypes":["ssl-websocket"],"advice":{"timeout":60000,"interval":0},"clientFeatures":{"protocolversion":"2.1","clientname":"LC6;chrome/111.0.0;Linux;11queo5;48.2.0","skiphandshakeratings":true,"adminservice":true,"announceservice":true,"arenas":true,"chessgroups":true,"clientstate":true,"events":true,"gameobserve":true,"genericchatsupport":true,"genericgamesupport":true,"guessthemove":true,"multiplegames":true,"multiplegamesobserve":true,"offlinechallenges":true,"pingservice":true,"playbughouse":true,"playchess":true,"playchess960":true,"playcrazyhouse":true,"playkingofthehill":true,"playoddschess":true,"playthreecheck":true,"privatechats":true,"stillthere":true,"teammatches":true,"tournaments":true,"userservice":true},"serviceChannels":["/service/user"],"ext":{"ack":true,"timesync":{"tc":1688569933697,"l":0,"o":0}},"id":"1","clientId":null}]'
                        message2_1 = '[{"channel":"/meta/connect","connectionType":"ssl-websocket","ext":{"ack":'
                        message2_2 = ',"timesync":{"tc":1688571086925,"l":60,"o":6}},"id":"'
                        message2_3 = '","clientId":"'
                        closure_message2 = '"}]'
                        ack = 1
                        id = 2
                        await websocket.send(message1) # AWS.APIGateway style for example
                        message = await websocket.recv()
                        Logwriter.save_log(self.log_file_name,message+", ID IS: "+self.phpsessid_id)
                        print(message+", ID IS: "+self.phpsessid_id)
                        l = json.loads(message)
                        try:
                            client_id = l[0]['clientId']
                        except:
                            phpsessid = None
                            Globalvals.phpsessid_mutex.acquire()
                            Globalvals.phpsessid[self.phpsessid_id][1] = False
                            Globalvals.phpsessid_mutex.release()
                            await websocket.close()
                            continue
                        message2 = message2_1+str(ack)+message2_2+str(id)+message2_3+client_id+closure_message2
                        while True:
                            await websocket.send(message2)
                            message = await websocket.recv()
                            match_id = self.queue_message(message)# queue the message
                            Globalvals.frames_queue.enter_dict_critical_section()
                            # if the game ended
                            if match_id != None and match_id not in list_match_ids:
                                list_match_ids.append(match_id)
                            elem_list_to_remove = []
                            flag = True
                            for match_id in list_match_ids:
                                if match_id != None and match_id in Globalvals.frames_queue.dictionary and 'delete' in Globalvals.frames_queue.dictionary[match_id]:
                                    elem_list_to_remove.append(match_id)
                                    Logwriter.save_log(self.log_file_name,"socket number: "+str(self.phpsessid_id)+" is removing match id: "+match_id)
                                    print("socket number: "+str(self.phpsessid_id)+" is removing match id: "+match_id)
                                    if match_id in Globalvals.frames_queue.dictionary:# pop it from here
                                        Globalvals.frames_queue.dictionary.pop(match_id,None)
                                    Globalvals.frames_queue.exit_dict_critical_section()
                                    flag = False
                                    id_c = match_id[len("chesscom/"):]
                                    Globalvals.games_queue.enter_chesscom_critical_section()
                                    n_games = len(list(Globalvals.games_queue.chesscom_games_dictionary.keys()))
                                    if id_c in Globalvals.games_queue.chesscom_games_dictionary:# pop it from here
                                        Globalvals.games_queue.chesscom_games_dictionary.pop(id_c,None)
                                    Globalvals.games_queue.exit_chesscom_critical_section()
                                    '''
                                    if n_games <= 1:# if was the last game, close the socket
                                        phpsessid = None
                                        list_match_ids = []
                                        await websocket.close()
                                        break
                                    '''
                            for elem in elem_list_to_remove:
                                list_match_ids.remove(elem)
                            if flag:
                                Globalvals.frames_queue.exit_dict_critical_section()
                            ack+=1
                            id+=1
                            message2 = message2_1+str(ack)+message2_2+str(id)+message2_3+client_id+closure_message2
                            Globalvals.phpsessid_mutex.acquire()
                            if Globalvals.phpsessid[self.phpsessid_id][0] != phpsessid:
                                Globalvals.phpsessid_mutex.release()
                                phpsessid = None
                                await websocket.close()
                                Globalvals.phpsessid_mutex.acquire()
                                Globalvals.phpsessid[self.phpsessid_id][1] = False
                                Globalvals.phpsessid_mutex.release()
                                break
                            Globalvals.phpsessid_mutex.release()
                            time.sleep(0.001)
                    except:
                        Globalvals.phpsessid_mutex.acquire()
                        Globalvals.phpsessid[self.phpsessid_id][1] = False
                        Globalvals.phpsessid_mutex.release()
                        await websocket.close()
                        continue
    def run_batch(self):
        thread = threading.Thread(target=self.run_socket)
        thread.start()
        return thread
    
    def run_socket(self):
        asyncio.run(self.socket())
    
    def queue_message(self, message):    
        try:
            message = json.loads(message)
            if type(message) == type([]):
                for i in message:
                    try:
                        if 'data' in i and 'game' in i['data']:
                            game = i['data']['game']
                            game_id = game['id']
                            moves = game['moves']
                            seq = game['seq']
                            WhitePlayer = game['players'][0]['uid']
                            BlackPlayer = game['players'][1]['uid']
                            clock_white = game['clocks'][0]
                            clock_black = game['clocks'][1]
                            status = game['status']
                            results = []
                            if 'results' in game:
                                results = game['results']
                            win = None
                            d = {}
                            d['id'] = str(game_id)
                            d['moves'] = self.decode_moves(moves)
                            d['fen'] = self.get_fen_from_moves(d['moves'])
                            d['seq'] = str(seq)
                            d['WhitePlayer'] = WhitePlayer
                            d['BlackPlayer'] = BlackPlayer
                            d['WhiteClock'] = str(clock_white)
                            d['BlackClock'] = str(clock_black)
                            d['status'] = status
                            d['results'] = results
                            Logwriter.save_log(self.log_file_name,"insert chess move, match_id: "+str(game_id))
                            print("insert chess move, match_id: "+str(game_id))
                            Globalvals.games_queue.insert_chesscom_move(d)
                            return 'chesscom/'+d['id']
                    except:
                        return None
        except:
            return None
