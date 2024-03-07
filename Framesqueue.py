import threading
import Globalvals
import Chessdrawing
import datetime
import chess
import time
from PIL import Image
import numpy as np

class FramesQueue:
    
    def __init__(self, background_image_path = './images/backgrounds/fire2_background_1280x720.jpg'):
        self.im = Image.open(background_image_path) 
        self.frames_mutex = threading.Lock()
        self.dict_mutex = threading.Lock()
        self.json_mutex = threading.Lock()
        self.frames = []
        self.boards = {}
        self.dictionary = {}
        self.json = {}
        self.draw = Chessdrawing.ChessDrawing()#init
        self.board = chess.Board()

    def enter_frames_critical_section(self):
        self.frames_mutex.acquire()
    
    def exit_frames_critical_section(self):
        self.frames_mutex.release()
        
    def enter_dict_critical_section(self):
        self.dict_mutex.acquire()
    
    def exit_dict_critical_section(self):
        self.dict_mutex.release()
        
    def enter_json_critical_section(self):
        self.json_mutex.acquire()
    
    def exit_json_critical_section(self):
        self.json_mutex.release()
    
    def generate_frames(self):
        pass
    
    def run_batch(self):
        thread = threading.Thread(target=self.generate_boards)
        thread.start()
        return thread
    
    
    def get_image_from_info(self,date, previous_image, previous_size, ids, info, chess_size = 400):
        if previous_image == None or previous_size == None or previous_size != chess_size:
            fen = info['fen']
            white_time = info['white_time']
            black_time = info['black_time']
            image_white = info['image_white']
            image_black = info['image_black']
            white_player = info['white_player']
            black_player = info['black_player']
            white_rating = info['white_rating']
            black_rating = info['black_rating']
            self.draw.set_chess_size(chess_size)
            self.draw.set_padding(int(chess_size/8), (55,6,23))
            self.draw.set_fen(fen)
            self.draw.get_engine_eval()#eval the pos
            self.draw.get_score_in_percentage()# get the percentage for bar
            self.draw.get_png_board()#draw the board
            self.draw.add_padding()#padd the board
            self.draw.add_timer_to_image(str(white_time), str(black_time))#add the timer
            self.draw.add_bar_to_image()#add the evaluation bar
            self.draw.add_players_info(image_white,image_black,white_player,black_player, white_rating,black_rating)# draw user infos
            image = self.draw.image_with_user_infos
            if info['remove']:
                image = self.draw.add_game_ended(image, self.draw.padding_color)
            return image
        else:
            self.draw.set_chess_size(chess_size)
            self.draw.set_padding(int(chess_size/8), (55,6,23))
            white_time = info['white_time']
            black_time = info['black_time']
            if info['remove']:
                image = self.draw.add_game_ended(image, self.draw.padding_color)
            return self.draw.add_timer_to_image2(previous_image,white_time,black_time) 
            
        
    def generate_boards(self):
        while True:
            # generating the boards
            boards = {}
            games_to_remove = []
            
            date = datetime.datetime.now()
            
            Globalvals.games_queue.enter_chesscom_critical_section()
            games = Globalvals.games_queue.chesscom_games_dictionary.copy()
            
            for i in Globalvals.games_queue.chesscom_games_dictionary:
                Globalvals.games_queue.chesscom_games_dictionary[i] = []
            Globalvals.games_queue.exit_chesscom_critical_section()
            Globalvals.frames_queue.enter_dict_critical_section()
            d = Globalvals.frames_queue.dictionary
            for i in games:
                try:
                    # controlliamo che siano segnate dentro d
                    i_d = 'chesscom/'+i
                    if i_d in d:
                        # se la lunghezza è 0 o non abbiamo ancora ottenuto nulla
                        # o abbiamo poppato tutto il possibile
                        # nel primo caso non abbiamo alcune info in d
                        if len(games[i]) == 0:
                            
                            # non abbiamo l'info turn per esempio
                            # se ce l'abbiamo ok allora dobbiamo prendere
                            # l'ultima posizione che è salvata in d
                            # diminuire il tempo
                            if 'turn' in d[i_d]:
                                
                                white_date = d[i_d]['white_date']
                                white_time = d[i_d]['white_time']
                                black_date = d[i_d]['black_date']
                                black_time = d[i_d]['black_time']
                                if not d[i_d]['remove']:
                                    if d[i_d]['turn'] == 'white':
                                        diff = (white_date-date).total_seconds()
                                        white_time+=diff
                                        if white_time < 0:
                                            white_time = 0
                                    else:
                                        diff = (black_date-date).total_seconds()
                                        black_time+=diff
                                        if black_time < 0:
                                            black_time = 0
                                else:
                                    d[i_d]['delete'] = True
                                    
                                fen = d[i_d]['fen']
                                temp_d = {}
                                temp_d['fen'] = fen
                                temp_d['white_time'] = str(white_time)
                                temp_d['black_time'] = str(black_time)
                                temp_d['image_white'] = str(d[i_d]['image_white'])
                                temp_d['image_black'] = str(d[i_d]['image_black'])
                                temp_d['white_player'] = str(d[i_d]['white_player'])
                                temp_d['black_player'] = str(d[i_d]['black_player'])
                                temp_d['white_rating'] = str(d[i_d]['white_rating'])
                                temp_d['black_rating'] = str(d[i_d]['black_rating'])
                                temp_d['remove'] = False
                                board_size = None
                                image = None
                                if 'board_size' in d[i_d]:
                                    board_size = d[i_d]['board_size']
                                if 'image' in d[i_d]:
                                    image = d[i_d]['image']
                                boards[i_d] = {'remove':False,'image': image, 'i_d': i_d, 'id':i, 'white_player' : d[i_d]['white_player'], 'black_player':d[i_d]['black_player'], 'priority':0, 'info':temp_d, 'board_size':board_size}
                        else:
                            remove = False
                            for game in games[i]:
                                fen = game['fen']
                                white_date = date
                                black_date = date
                                try:
                                    white_time = int(game['WhiteClock'][:-1])
                                except:
                                    white_time = 0
                                try:
                                    black_time = int(game['BlackClock'][:-1])
                                except:
                                    black_time = 0
                                self.board.set_fen(fen)
                                turn = 'black'
                                if self.board.turn:
                                    turn = 'white'
                                if not 'turn' in d[i_d]:
                                    white_player = game['WhitePlayer']
                                    black_player = game['BlackPlayer']
                                    image_white = Globalvals.chesscom2.save_player_image(white_player)
                                    image_black = Globalvals.chesscom2.save_player_image(black_player)
                                    white_rating_rapid, white_rating_blitz, white_rating_bullet = Globalvals.chesscom2.get_player_ratings(white_player)
                                    black_rating_rapid, black_rating_blitz, black_rating_bullet = Globalvals.chesscom2.get_player_ratings(black_player)
                                    white_rating = 'Rp('+str(white_rating_rapid)+')Bz('+str(white_rating_blitz)+')Bt('+str(white_rating_bullet)+')'
                                    black_rating = 'Rp('+str(black_rating_rapid)+')Bz('+str(black_rating_blitz)+')Bt('+str(black_rating_bullet)+')'
                                    d[i_d]['white_player'] = white_player
                                    d[i_d]['black_player'] = black_player
                                    d[i_d]['image_white'] = image_white
                                    d[i_d]['image_black'] = image_black
                                    d[i_d]['white_rating'] = white_rating
                                    d[i_d]['black_rating'] = black_rating
                                d[i_d]['turn'] = turn
                                d[i_d]['fen'] = fen
                                d[i_d]['black_date'] = black_date
                                d[i_d]['white_date'] = white_date
                                d[i_d]['white_time'] = white_time
                                d[i_d]['black_time'] = black_time
                                d[i_d]['remove'] = remove
                                if game['results'] != []:
                                    print(game)
                                    fen = d[i_d]['fen']
                                    remove = True
                                d[i_d]['remove'] = remove
                                temp_d = {}
                                temp_d['fen'] = fen
                                temp_d['white_time'] = str(white_time)
                                temp_d['black_time'] = str(black_time)
                                temp_d['image_white'] = str(d[i_d]['image_white'])
                                temp_d['image_black'] = str(d[i_d]['image_black'])
                                temp_d['white_player'] = str(d[i_d]['white_player'])
                                temp_d['black_player'] = str(d[i_d]['black_player'])
                                temp_d['white_rating'] = str(d[i_d]['white_rating'])
                                temp_d['black_rating'] = str(d[i_d]['black_rating'])
                                temp_d['remove'] = remove
                                boards[i_d] = {'image': None, 'i_d': i_d, 'id':i, 'white_player' : d[i_d]['white_player'], 'black_player':d[i_d]['black_player'], 'priority':0, 'info':temp_d, 'board_size':None}
                            #if remove:
                            #    games_to_remove.append(i)
                except:
                    i_d = 'chesscom/'+i
                    if i_d in d:
                        d[i_d]['delete'] = True
            '''
            if len(games_to_remove) > 0:
                Globalvals.games_queue.enter_chesscom_critical_section()
                for i in games_to_remove:
                    games.pop(i,None)
                Globalvals.games_queue.exit_chesscom_critical_section()
            '''
            Globalvals.frames_queue.exit_dict_critical_section()
            
            
            
            # generating the image
            
            if boards == {}:
                continue
            Globalvals.frames_queue.enter_json_critical_section()
            for i in boards:
                for player in Globalvals.frames_queue.json['players']:
                    for user in Globalvals.frames_queue.json['players'][player]["chesscom"]["profiles"]:
                        if boards[i]['white_player'] == user:
                            boards[i]['priority']+=Globalvals.frames_queue.json['players'][player]['priority']
            Globalvals.frames_queue.exit_json_critical_section()
            priorities = []
            
            for i in boards:
                priorities.append(boards[i]['priority'])
            priorities.sort()
            priorities.reverse()
            
            first_board = None
            first_board_size = None
            first_board_id = None
            first_board_image = None
            second_board = None
            second_board_size = None
            second_board_id = None
            second_board_image = None
            third_board = None
            third_board_size = None
            third_board_id = None
            third_board_image = None
            fourth_board = None
            fourth_board_size = None
            fourth_board_id = None
            fourth_board_image = None
            fifth_board = None
            fifth_board_size = None
            fifth_board_id = None
            fifth_board_image = None
            
            break_flag = False
            for i in priorities:
                index = None
                for j in boards:
                    if boards[j]['priority'] == i:
                        if first_board == None:
                            first_board = boards[j]['info']
                            first_board_size = boards[j]['board_size']
                            first_board_id = boards[j]['i_d']
                            first_board_image = boards[j]['image']
                        elif second_board == None:
                            second_board = boards[j]['info']
                            second_board_size = boards[j]['board_size']
                            second_board_id = boards[j]['i_d']
                            second_board_image = boards[j]['image']
                        elif third_board == None:
                            third_board = boards[j]['info']
                            third_board_size = boards[j]['board_size']
                            third_board_id = boards[j]['i_d']
                            third_board_image = boards[j]['image']
                        elif fourth_board == None:
                            fourth_board = boards[j]['info']
                            fourth_board_size = boards[j]['board_size']
                            fourth_board_id = boards[j]['i_d']
                            fourth_board_image = boards[j]['image']
                        
                        else:
                            break_flag = True
                        
                        '''    
                        elif fifth_board == None:
                            fifth_board = boards[j]['info']
                            fifth_board_size = boards[j]['board_size']
                            fifth_board_id = boards[j]['i_d']
                            fifth_board_image = boards[j]['image']
                            break_flag = True
                        '''
                        index = j
                        break
                if index != None:
                    boards.pop(index,None)
                if break_flag:
                    break
            im = self.im.copy()
            size_1 = None
            size_other = None
            
            '''
            if fifth_board != None:
                size_1 = 700.0
                size_other = 250.0
                size_1*= 4/5
                size_other*= 4/5
                size_1 = int(size_1)
                size_other = int(size_other)
                
                fifth_board = self.get_image_from_info(date,fifth_board_image, fifth_board_size, fifth_board_id, fifth_board,size_other)
                fourth_board = self.get_image_from_info(date,fourth_board_image, fourth_board_size, fourth_board_id, fourth_board,size_other)
                third_board = self.get_image_from_info(date,third_board_image, third_board_size, third_board_id, third_board,size_other)
                second_board = self.get_image_from_info(date,second_board_image, second_board_size, second_board_id, second_board,size_other)
                first_board = self.get_image_from_info(date,first_board_image, first_board_size, first_board_id, first_board,size_1)

                
                im.paste(first_board, (40, 10))
                im.paste(second_board, (40+700, 110))
                im.paste(third_board, (40+700+250, 110))
                im.paste(fourth_board, (40+700, 250+110))
                im.paste(fifth_board, (40+700+250, 250+110))
            
            
            #elif fourth_board != None:
            if fourth_board != None:
                
                size_1 = 700.0
                size_other = 233.0
                size_1*= 4/5
                size_other*= 4/5
                size_1 = int(size_1)
                size_other = int(size_other)
                
                fourth_board = self.get_image_from_info(date,fourth_board_image, fourth_board_size, fourth_board_id, fourth_board,size_other)
                third_board = self.get_image_from_info(date,third_board_image, third_board_size, third_board_id, third_board,size_other)
                second_board = self.get_image_from_info(date,second_board_image, second_board_size, second_board_id, second_board,size_other)
                first_board = self.get_image_from_info(date,first_board_image, first_board_size, first_board_id, first_board,size_1)

                
                im.paste(first_board, (130, 10))
                im.paste(second_board, (130+700 + 60, 10))
                im.paste(third_board, (130+700 + 60, 10+233))
                im.paste(fourth_board, (130+700 + 60, 10+233+233))
            elif third_board != None:
                
                size_1 = 700.0
                size_other = 350.0
                size_1*= 4/5
                size_other*= 4/5
                size_1 = int(size_1)
                size_other = int(size_other)
                
                third_board = self.get_image_from_info(date,third_board_image, third_board_size, third_board_id, third_board,size_other)
                second_board = self.get_image_from_info(date,second_board_image, second_board_size, second_board_id, second_board,size_other)
                first_board = self.get_image_from_info(date,first_board_image, first_board_size, first_board_id, first_board,size_1)

                
                im.paste(first_board, (130, 10))
                im.paste(second_board, (130+700, 10))
                im.paste(third_board, (130+700, 10+350))
            '''
            if second_board != None:
                
                size_1 = 600.0
                size_other = 600.0
                size_1*= 4/5
                size_other*= 4/5
                size_1 = int(size_1)
                size_other = int(size_other)
                
                second_board = self.get_image_from_info(date,second_board_image, second_board_size, second_board_id, second_board,size_other)
                first_board = self.get_image_from_info(date,first_board_image, first_board_size, first_board_id, first_board,size_1)

                im.paste(first_board, (40, 60))
                im.paste(second_board, (40+600, 60))
            elif first_board != None:
                size_1 = 700.0
                size_other = 600.0
                size_1*= 4/5
                size_other*= 4/5
                size_1 = int(size_1)
                size_other = int(size_other)
                first_board = self.get_image_from_info(date,first_board_image, first_board_size, first_board_id, first_board,size_1)
                im.paste(first_board, (290, 10))
            
            Globalvals.frames_queue.enter_dict_critical_section()
            d = Globalvals.frames_queue.dictionary
            if fifth_board != None and fifth_board_id in d:
                d[fifth_board_id]['image'] = fifth_board
                d[fifth_board_id]['board_size'] = size_other
            if fourth_board != None and fourth_board_id in d:
                d[fourth_board_id]['image'] = fourth_board
                d[fourth_board_id]['board_size'] = size_other
            if third_board != None and third_board_id in d:
                d[third_board_id]['image'] = third_board
                d[third_board_id]['board_size'] = size_other
            if second_board != None and second_board_id in d:
                d[second_board_id]['image'] = second_board
                d[second_board_id]['board_size'] = size_other
            if first_board != None and first_board_id in d:
                d[first_board_id]['image'] = first_board
                d[first_board_id]['board_size'] = size_1
            Globalvals.frames_queue.exit_dict_critical_section()
            frame = np.asarray(im)
            frame = frame.astype(np.uint8)
            Globalvals.frames_queue.enter_frames_critical_section()
            Globalvals.frames_queue.frames=[frame]
            Globalvals.frames_queue.exit_frames_critical_section()
            
                            
