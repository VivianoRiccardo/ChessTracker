import chess
import cairosvg
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import chess.svg
import chess.engine
import datetime
import math
import pyvips

class ChessDrawing:
    
    fen = ''
    has_fen_changed = False
    history = []
    board = ''
    engine = None
    engine_time = 0.1
    last_move = None
    white_perspective = True
    engine_analysis = None
    want_suggestion = True
    want_bar = True
    want_timer = True
    want_profile_pictures = True
    current_board = None
    padded_board = None
    image_with_user_infos = None
    padding = 200
    font = None
    font_size = 36
    font_color = (255, 0, 0)
    paddding_color = "black"
    image_with_bar = None
    image_with_timer = None
    chess_size = 400
    score = 0
    players_text_color = (0,0,0)
    
    def __init__(self, engine_time = 0.1, engine_filename = './exec/stockfish', white_perspective = True,
                 font_path = './fonts/monofonto rg.otf', font_size = 36, font_color = (255, 255, 255), padding = 50,
                 padding_color = (55,6,23), chess_size = 400, players_text_color = (255,255,255)):
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_filename)
        self.engine_time = engine_time
        self.white_perspective = white_perspective
        self.font = font_path
        self.font_size = font_size
        self.font_color = font_color
        self.padding = padding
        self.padding_color = padding_color
        self.chess_size = chess_size
        self.players_text_color = players_text_color
    
    def set_players_color(self, colpyvipsor):
        self.players_text_color = color
    
    def set_chess_size(self,size):
        self.chess_size = size
    def generate_png_image_from_svg_string(self,svg_string):
        image = pyvips.Image.svgload_buffer(svg_string.encode())

        pil_image = Image.fromarray(image.numpy())
        return pil_image
    def textsize(self, text, font=None):
        im = Image.new(mode="P", size=(0, 0))
        draw = ImageDraw.Draw(im)
        _, _, width, height = draw.textbbox((0, 0), text=text, font=font)
        return width, height
    '''   
    def generate_png_image_from_svg_string(self,svg_string):
        # Convert SVG to PNG in memory
        svg_bytes = svg_string.encode('utf-8')
        png_bytes = cairosvg.svg2png(bytestring=svg_bytes)

        # Create PIL Image object from PNG bytes
        image = Image.open(io.BytesIO(png_bytes))

        return image
    '''
    def set_font(self, font, font_size, font_color):
        self.font = font
        self.font_size = font_size
        self.font_color = font_color
    
    def set_padding(self, padding, padding_color):
        self.padding = padding
        self.padding_color = padding_color
        
    def set_fen(self,fen):
        if fen != self.fen:
            self.has_fen_changed = True
            self.history.append(fen)
            board2 = chess.Board()
            board2.set_fen(fen)
            # Generate a list of all moves in board1
            moves = [move for move in self.board.legal_moves]

            # Find the last move by comparing the two boards
            last_move = None
            for move in moves:
                # Make the move on board1
                self.board.push(move)
                ChessDrawing
                # Compare the resulting FEN position with board2
                if self.board.fen() == board2.fen():
                    last_move = move
                    break
                
                # Undo the move for the next iteration
                self.board.pop()
            self.last_move = last_move#could be None if we have lost some positions
            self.board.set_fen(fen)
        fen = self.fen = fen
    
    def get_engine_eval(self):
        self.engine_analysis = self.engine.analyse(self.board, chess.engine.Limit(time=self.engine_time))
    
    def fen_changed(self):
        ret = self.has_fen_changed
        self.has_fen_changed = False
        return ret
    
    def show_image(self, image):
        image.show()
        
    def set_suggestion(self, suggestion):
        self.want_suggestion = suggestion
    
    
    
    def get_score_in_percentage(self):
        score = self.engine_analysis['score']
        white = score.white()
        stringa = str(white)
        mate = False
        if '#' in stringa:
            mate = True
            stringa = stringa.replace("#","")
        if mate:
            if int(stringa) < 0:
                score = -1
            else:
                score = 1
        else:
            stringa = int(stringa)
            multiplyer = 1
            if stringa < 0:
                multiplyer = -1
                stringa*=-1
            x = stringa
            score = self.normalize_score(x)*multiplyer
        self.score = score
            
    
    def normalize_score(self, cp):
        if cp <= 100:
            return 0.5 + float(cp)*0.1/100.0
        elif cp <= 200:
            return 0.6 + float(200-cp)*0.08/100.0
        elif cp <= 300:
            return 0.68 + float(300-cp)*0.08/100.0
        elif cp <= 400:
            return 0.76 + float(400-cp)*0.07/100.0
        elif cp <= 500:
            return 0.83 + float(500-cp)*0.05/100.0
        elif cp <= 600:
            return 0.88 + float(600-cp)*0.04/100.0
        elif cp <= 700:
            return 0.92 + float(700-cp)*0.03/100.0
        elif cp <= 800:
            return 0.95 + float(800-cp)*0.01/100.0
        elif cp <= 900:
            return 0.96 + float(900-cp)*0.01/100.0
        elif cp <= 1000:
            return 0.97 + float(1000-cp)*0.01/100.0
        elif cp <= 1100:
            return 0.98 + float(1100-cp)*0.01/100.0
        elif cp <= 1200:
            return 0.99 + float(1200-cp)*0.01/100.0
        else:
            return 1
                
    def get_png_board(self):
        # get perspective
        perspective = chess.BLACK
        if self.white_perspective:
            perspective = chess.WHITE
        # if there is a check get the position of the check
        king_square = None
        is_check = self.board.is_check()
        if is_check:
            king_square = self.board.king(chess.WHITE) if self.board.turn == chess.WHITE else self.board.king(chess.BLACK)
        # draw the first best move of the engine
        arrow = None
        if self.engine_analysis != None and self.want_suggestion and 'pv' in self.engine_analysis:
            if len(self.engine_analysis['pv']) > 0:
                move_from, move_to = self.map_moves(self.engine_analysis['pv'][0].uci())
                if move_from != None and move_to != None:
                    arrow = [(move_from, move_to)]
        if arrow != None:
            self.current_board = self.generate_png_image_from_svg_string(chess.svg.board(self.board, size = self.chess_size, orientation = perspective, lastmove = self.last_move, check = king_square, arrows = arrow))
        else:
            self.current_board = self.generate_png_image_from_svg_string(chess.svg.board(self.board, size = self.chess_size, orientation = perspective, lastmove = self.last_move, check = king_square))
        self.padded_board = self.current_board
        self.image_with_timer = self.current_board
        self.image_with_bar = self.current_board
        self.image_with_user_infos = self.current_board
    
    def add_padding(self):
        new_width = self.current_board.width + 2 * self.padding
        new_height = self.current_board.height + 2 * self.padding

        self.padded_board = ImageOps.expand(self.current_board, border=self.padding, fill=self.padding_color)
        self.image_with_timer = self.padded_board
        self.image_with_bar = self.padded_board
        self.image_with_user_infos = self.padded_board
        
    def add_bar_to_image(self):
        
        bar_width = self.chess_size
        x_start = self.padding - int(self.current_board.height/12)
        y_start = self.padding
        width = int(self.current_board.height/15)
        image = self.image_with_timer
        image_height = image.height
        # Define the percentage value (between 0 and 100 for the white)
        if self.score > 0:
            percentage = self.score*100
        else:
            percentage = 100+self.score*100

        # Calculate the height of the bar based on the percentage
        bar_height = int((percentage / 100) * self.chess_size)

        # Create a drawing object
        draw = ImageDraw.Draw(image)
        
        fill1 = "white"
        fill2 = "black"
        if self.white_perspective:
            fill2 = "white"
            fill1 = "black"
            percentage = bar_height = self.chess_size-bar_height
        # Draw the background rectangle
        draw.rectangle([(x_start, y_start), (x_start+width, y_start+self.chess_size)], fill=fill2)

        # Draw the filled bar
        draw.rectangle([(x_start, y_start),
                        (x_start+width, y_start+bar_height)],
                       fill=fill1)
        # Save the image
        self.image_with_bar = image
        self.image_with_user_infos = image
    
    def add_players_info(self, image_white_path, image_black_path, name_white, name_black, elo_white, elo_black):
        elo_white = str(elo_white)
        elo_black = str(elo_black)
        image = self.image_with_bar
        white_image = Image.open(image_white_path)
        black_image = Image.open(image_black_path)
        size_images = int(self.chess_size/10)
        image1 = white_image.resize((size_images,size_images))
        image2 = black_image.resize((size_images,size_images))
        if self.white_perspective:
            image3 = image2
            image2 = image1
            image1 = image3
        position1x = (self.padding + self.chess_size - size_images)
        position1y = (self.padding - size_images)
        position2x = (self.padding + self.chess_size - size_images)
        position2y = (self.padding + self.chess_size)
        image.paste(image1, (position1x,position1y))
        image.paste(image2, (position2x,position2y))
        
        font_size = int(self.chess_size/25)
        font_color = self.players_text_color # RGB color value
        font_path = self.font  # Replace with the path to your font file

        # Load the font
        font = ImageFont.truetype(font_path, font_size)
        
        draw = ImageDraw.Draw(image)
        
        if self.white_perspective:
            name = name_white
            name_white = name_black
            name_black = name
            elo = elo_white
            elo_white = elo_black
            elo_black = elo
        
        # Write the text on the image
        text_width, text_height = self.textsize(name_white, font=font)
        draw.text((self.padding + self.chess_size - size_images - text_width, self.padding - size_images), name_white, font=font, fill=font_color)
        text_width, _ = self.textsize(elo_white, font=font)
        draw.text((self.padding + self.chess_size - size_images - text_width, self.padding - size_images + text_height), elo_white, font=font, fill=font_color)
        # Write the text on the image
        text_width, text_height = self.textsize(name_black, font=font)
        draw.text((self.padding + self.chess_size - size_images - text_width, self.padding + self.chess_size), name_black, font=font, fill=font_color)
        text_width, _ = self.textsize(elo_black, font=font)
        draw.text((self.padding + self.chess_size - size_images - text_width, self.padding + self.chess_size + text_height), elo_black, font=font, fill=font_color)
        self.image_with_user_infos = image
        
    def add_timer_to_image(self, white_time_seconds, black_time_seconds):
        # Load the image
        image = self.padded_board
        white_time_seconds = int(float(white_time_seconds))
        black_time_seconds = int(float(black_time_seconds))
        # Define the font properties
        font_path = self.font  # Path to the font file (.ttf)
        font_size = int(self.current_board.height/10)
        font_color1 = self.font_color  # Font color in RGB format
        font_color2 = self.font_color  # Font color in RGB format
        
        
        # Define the position of the timers (top left and top right)
        timer1_pos = (self.padding, self.padding-font_size-10)  # Top left position
        timer2_pos = (self.padding, self.padding+self.current_board.height)  # Top right position

        # Define the start time
        start_time = datetime.datetime.now()

        # Create a draw object
        draw = ImageDraw.Draw(image)

        # Load the font
        font = ImageFont.truetype(font_path, font_size)

        # Iterate over the timer duration


        # Format the remaining time as HH:MM:SS
        formatted_time_white = str(datetime.timedelta(seconds=int(white_time_seconds)))
        formatted_time_black = str(datetime.timedelta(seconds=int(black_time_seconds)))
        
        if white_time_seconds <= 10:
            font_color1 = (255,0,0)
        if black_time_seconds <= 10:
            font_color2 = (255,0,0)
        # Clear the previous text by filling a rectangle
        draw.rectangle([timer1_pos, (int(timer1_pos[0] + font_size*3.7), timer1_pos[1] + font_size + 10)], fill=(0, 0, 0))
        draw.rectangle([timer2_pos, (int(timer2_pos[0] + font_size*3.7), timer2_pos[1] + font_size + 10)], fill=(0, 0, 0))

        # Draw the timer text
        if self.white_perspective:
            timer3_pos = timer2_pos
            timer2_pos = timer1_pos
            timer1_pos = timer3_pos
        
        draw.text(timer1_pos, formatted_time_white, font=font, fill=font_color1)
        draw.text(timer2_pos, formatted_time_black, font=font, fill=font_color2)

        # Save the image with the timer
        self.image_with_timer = image
        self.image_with_bar = image
        self.image_with_user_infos = image
    
    def add_game_ended(self, image, color):
        image_size = image.size

        # Print the width and height of the image
        width, height = image_size
        chess_size = int(float(width*4.0/5.0))
        font_size = int(chess_size/10)
        font_color = color # RGB color value
        font_path = self.font  # Replace with the path to your font file

        # Load the font
        font = ImageFont.truetype(font_path, font_size)
        
        draw = ImageDraw.Draw(image)
        text = "Game Ended!"
        text_width, text_height = self.textsize(text, font=font)

        # Calculate the position to center the text
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2

        # Draw the text on the image
        draw.text((text_x, text_y), text, font=font, fill=font_color)  # Replace fill color with desired RGB values

        return image
        
    def add_timer_to_image2(self,image,white_time_seconds, black_time_seconds):
        # Load the image
        white_time_seconds = int(float(white_time_seconds))
        black_time_seconds = int(float(black_time_seconds))
        # Define the font properties
        font_path = self.font  # Path to the font file (.ttf)
        font_size = int(self.current_board.height/10)
        font_color1 = self.font_color  # Font color in RGB format
        font_color2 = self.font_color  # Font color in RGB format
        
        
        # Define the position of the timers (top left and top right)
        timer1_pos = (self.padding, self.padding-font_size-10)  # Top left position
        timer2_pos = (self.padding, self.padding+self.current_board.height)  # Top right position

        # Define the start time
        start_time = datetime.datetime.now()

        # Create a draw object
        draw = ImageDraw.Draw(image)

        # Load the font
        font = ImageFont.truetype(font_path, font_size)

        # Iterate over the timer duration


        # Format the remaining time as HH:MM:SS
        formatted_time_white = str(datetime.timedelta(seconds=int(white_time_seconds)))
        formatted_time_black = str(datetime.timedelta(seconds=int(black_time_seconds)))
        
        if white_time_seconds <= 10:
            font_color1 = (255,0,0)
        if black_time_seconds <= 10:
            font_color2 = (255,0,0)
        # Clear the previous text by filling a rectangle
        draw.rectangle([timer1_pos, (int(timer1_pos[0] + font_size*3.7), timer1_pos[1] + font_size + 10)], fill=(0, 0, 0))
        draw.rectangle([timer2_pos, (int(timer2_pos[0] + font_size*3.7), timer2_pos[1] + font_size + 10)], fill=(0, 0, 0))

        # Draw the timer text
        if self.white_perspective:
            timer3_pos = timer2_pos
            timer2_pos = timer1_pos
            timer1_pos = timer3_pos
        
        draw.text(timer1_pos, formatted_time_white, font=font, fill=font_color1)
        draw.text(timer2_pos, formatted_time_black, font=font, fill=font_color2)

        # Save the image with the timer
        return image
        
    
    def map_moves(self, move_string):
        move_from = move_string[:2]
        move_to = move_string[2:]
        if move_from == 'a1':
            move_from = chess.A1
        elif move_from == 'a2':
            move_from = chess.A2
        elif move_from == 'a3':
            move_from = chess.A3
        elif move_from == 'a4':
            move_from = chess.A4
        elif move_from == 'a5':
            move_from = chess.A5
        elif move_from == 'a6':
            move_from = chess.A6
        elif move_from == 'a7':
            move_from = chess.A7
        elif move_from == 'a8':
            move_from = chess.A8
        elif move_from == 'b1':
            move_from = chess.B1
        elif move_from == 'b2':
            move_from = chess.B2
        elif move_from == 'b3':
            move_from = chess.B3
        elif move_from == 'b4':
            move_from = chess.B4
        elif move_from == 'b5':
            move_from = chess.B5
        elif move_from == 'b6':
            move_from = chess.B6
        elif move_from == 'b7':
            move_from = chess.B7
        elif move_from == 'b8':
            move_from = chess.B8
        elif move_from == 'c1':
            move_from = chess.C1
        elif move_from == 'c2':
            move_from = chess.C2
        elif move_from == 'c3':
            move_from = chess.C3
        elif move_from == 'c4':
            move_from = chess.C4
        elif move_from == 'c5':
            move_from = chess.C5
        elif move_from == 'c6':
            move_from = chess.C6
        elif move_from == 'c7':
            move_from = chess.C7
        elif move_from == 'c8':
            move_from = chess.C8
        elif move_from == 'd1':
            move_from = chess.D1
        elif move_from == 'd2':
            move_from = chess.D2
        elif move_from == 'd3':
            move_from = chess.D3
        elif move_from == 'd4':
            move_from = chess.D4
        elif move_from == 'd5':
            move_from = chess.D5
        elif move_from == 'd6':
            move_from = chess.D6
        elif move_from == 'd7':
            move_from = chess.D7
        elif move_from == 'd8':
            move_from = chess.D8
        elif move_from == 'e1':
            move_from = chess.E1
        elif move_from == 'e2':
            move_from = chess.E2
        elif move_from == 'e3':
            move_from = chess.E3
        elif move_from == 'e4':
            move_from = chess.E4
        elif move_from == 'e5':
            move_from = chess.E5
        elif move_from == 'e6':
            move_from = chess.E6
        elif move_from == 'e7':
            move_from = chess.E7
        elif move_from == 'e8':
            move_from = chess.E8
        elif move_from == 'f1':
            move_from = chess.F1
        elif move_from == 'f2':
            move_from = chess.F2
        elif move_from == 'f3':
            move_from = chess.F3
        elif move_from == 'f4':
            move_from = chess.F4
        elif move_from == 'f5':
            move_from = chess.F5
        elif move_from == 'f6':
            move_from = chess.F6
        elif move_from == 'f7':
            move_from = chess.F7
        elif move_from == 'f8':
            move_from = chess.F8
        elif move_from == 'g1':
            move_from = chess.G1
        elif move_from == 'g2':
            move_from = chess.G2
        elif move_from == 'g3':
            move_from = chess.G3
        elif move_from == 'g4':
            move_from = chess.G4
        elif move_from == 'g5':
            move_from = chess.G5
        elif move_from == 'g6':
            move_from = chess.G6
        elif move_from == 'g7':
            move_from = chess.G7
        elif move_from == 'g8':
            move_from = chess.G8
        elif move_from == 'h1':
            move_from = chess.H1
        elif move_from == 'h2':
            move_from = chess.H2
        elif move_from == 'h3':
            move_from = chess.H3
        elif move_from == 'h4':
            move_from = chess.H4
        elif move_from == 'h5':
            move_from = chess.H5
        elif move_from == 'h6':
            move_from = chess.H6
        elif move_from == 'h7':
            move_from = chess.H7
        elif move_from == 'h8':
            move_from = chess.H8
        else:
            move_from = None
        if move_to == 'a1':
            move_to = chess.A1
        elif move_to == 'a2':
            move_to = chess.A2
        elif move_to == 'a3':
            move_to = chess.A3
        elif move_to == 'a4':
            move_to = chess.A4
        elif move_to == 'a5':
            move_to = chess.A5
        elif move_to == 'a6':
            move_to = chess.A6
        elif move_to == 'a7':
            move_to = chess.A7
        elif move_to == 'a8':
            move_to = chess.A8
        elif move_to == 'b1':
            move_to = chess.B1
        elif move_to == 'b2':
            move_to = chess.B2
        elif move_to == 'b3':
            move_to = chess.B3
        elif move_to == 'b4':
            move_to = chess.B4
        elif move_to == 'b5':
            move_to = chess.B5
        elif move_to == 'b6':
            move_to = chess.B6
        elif move_to == 'b7':
            move_to = chess.B7
        elif move_to == 'b8':
            move_to = chess.B8
        elif move_to == 'c1':
            move_to = chess.C1
        elif move_to == 'c2':
            move_to = chess.C2
        elif move_to == 'c3':
            move_to = chess.C3
        elif move_to == 'c4':
            move_to = chess.C4
        elif move_to == 'c5':
            move_to = chess.C5
        elif move_to == 'c6':
            move_to = chess.C6
        elif move_to == 'c7':
            move_to = chess.C7
        elif move_to == 'c8':
            move_to = chess.C8
        elif move_to == 'd1':
            move_to = chess.D1
        elif move_to == 'd2':
            move_to = chess.D2
        elif move_to == 'd3':
            move_to = chess.D3
        elif move_to == 'd4':
            move_to = chess.D4
        elif move_to == 'd5':
            move_to = chess.D5
        elif move_to == 'd6':
            move_to = chess.D6
        elif move_to == 'd7':
            move_to = chess.D7
        elif move_to == 'd8':
            move_to = chess.D8
        elif move_to == 'e1':
            move_to = chess.E1
        elif move_to == 'e2':
            move_to = chess.E2
        elif move_to == 'e3':
            move_to = chess.E3
        elif move_to == 'e4':
            move_to = chess.E4
        elif move_to == 'e5':
            move_to = chess.E5
        elif move_to == 'e6':
            move_to = chess.E6
        elif move_to == 'e7':
            move_to = chess.E7
        elif move_to == 'e8':
            move_to = chess.E8
        elif move_to == 'f1':
            move_to = chess.F1
        elif move_to == 'f2':
            move_to = chess.F2
        elif move_to == 'f3':
            move_to = chess.F3
        elif move_to == 'f4':
            move_to = chess.F4
        elif move_to == 'f5':
            move_to = chess.F5
        elif move_to == 'f6':
            move_to = chess.F6
        elif move_to == 'f7':
            move_to = chess.F7
        elif move_to == 'f8':
            move_to = chess.F8
        elif move_to == 'g1':
            move_to = chess.G1
        elif move_to == 'g2':
            move_to = chess.G2
        elif move_to == 'g3':
            move_to = chess.G3
        elif move_to == 'g4':
            move_to = chess.G4
        elif move_to == 'g5':
            move_to = chess.G5
        elif move_to == 'g6':
            move_to = chess.G6
        elif move_to == 'g7':
            move_to = chess.G7
        elif move_to == 'g8':
            move_to = chess.G8
        elif move_to == 'h1':
            move_to = chess.H1
        elif move_to == 'h2':
            move_to = chess.H2
        elif move_to == 'h3':
            move_to = chess.H3
        elif move_to == 'h4':
            move_to = chess.H4
        elif move_to == 'h5':
            move_to = chess.H5
        elif move_to == 'h6':
            move_to = chess.H6
        elif move_to == 'h7':
            move_to = chess.H7
        elif move_to == 'h8':
            move_to = chess.H8
        else:
            move_to = None
        return move_from, move_to
    
    


    
