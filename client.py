import socket
import cv2
import time
import threading
from audio_handler import *
import base64
import zmq
import numpy as np
from os import path
from encryption import *
import hashlib
from base64 import decodebytes
import pyaudio
import wave
import sys
import re
from moviepy.editor import VideoFileClip
import path_class

SERVER_IP = "127.0.0.1"  # the server ip
PATH = path_class.Path.get_project_path()  # the path of the main project Directory
rate_after_without_connection = False


class UdpClient(object):
    """
    This class is responsible for communicating with the GUI and the server, receives a video that sends with
    streaming and display it with Sync the video and audio, displaying a video found on the computer and Sync the video
     and audio, swapping encryption keys with the server,
     downloading a video, viewing from the last viewing point, registering and membership of a user,
    and taking pictures describing the videos that exist on the system
    """

    def __init__(self, video_port, audio_port, zmq_port, socket_c_sharp, my_client_socket, video_client_socket,
                 aes_encryption):
        self.send_ip = SERVER_IP
        self.video_port = int(video_port)
        self.audio_port = int(audio_port)
        self.audio_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.video_socket = video_client_socket
        self.c_sharp_socket = socket_c_sharp
        self.tcp_socket = my_client_socket
        self.context = zmq.Context()
        self.footage_socket = self.context.socket(zmq.SUB)
        self.footage_socket.connect('tcp://' + SERVER_IP + ':' + zmq_port)
        self.footage_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))
        self.current_time_video = 0.0
        self.current_position_audio_time = 0.2
        self.list_of_chunks = []
        self.list_of_frames = []
        self.video_lock = threading.Lock()
        self.audio_lock = threading.Lock()
        self.audio_buffer = 6000
        self.close = False
        self.stop = False
        self.mute = False
        self.first_frame = True
        self.minus = 0
        self.plus = False
        self.time_of_plus = 0.0
        self.aes = aes_encryption
        self.jump_counter = 0
        self.jump_time = 0
        self.show = True
        self.count = 0
        self.t_video_commands = threading.Thread(target=self.wait_for_commands)
        self.rate = False
        self.time_loading = 0
        self.file_name = ""
        self.play_after = False
        self.clip_duration = 0

    def receive_decrypted_message_tcp(self, buffer_size):
        """receive a message"""
        message_to_decrypt = self.tcp_socket.recv(buffer_size)
        return self.aes.decrypt_aes(message_to_decrypt)

    def send_encrypted_message_tcp(self, message_to_encrypt):
        """send a message"""
        message_to_send = self.aes.encrypt_aes(message_to_encrypt)
        self.tcp_socket.send(message_to_send)

    def wait_for_commands(self):
        """A function that waits for commands from the GUI and runs accordingly,
         for example- mute,stop,close,jump 10 sec and stop"""
        global rate_after_without_connection
        while not self.close:
            command = self.c_sharp_socket.recv(1024).decode()
            print(command)
            if rate_after_without_connection and command == "close":
                rate_after_without_connection = False
            elif command == "close the wait for commands thread in client":
                self.close = True
            elif command == "close":
                self.close = True
                self.c_sharp_socket.send("closing the thread in buttonsForm and open".encode())
                self.send_encrypted_message_tcp("stop_time " + str(int(self.current_position_audio_time)))
            elif command == "stop":
                self.stop = not self.stop
            elif command == "mute":
                self.mute = not self.mute
            elif command == "minus":
                self.minus -= 10
            elif command == "plus":  # when the user wants to jump 10 sec
                if not self.play_after:
                    if isinstance(self.list_of_frames[-1], float):
                        x = self.list_of_frames[-1]
                    else:
                        x = self.list_of_frames[-2]
                    if x - 10 > self.current_position_audio_time:
                        self.jump_counter += 73
                        self.jump_time += 73 * 0.1362
                        self.show = False
                        self.count = 44
                    else:
                        print("rejected plus")
                elif self.clip_duration - 12 > self.current_position_audio_time:
                    self.jump_counter += 73
                    self.jump_time += 73 * 0.1362
                    self.show = False
                    self.count = 44
                else:
                    print("rejected plus")

    def jump(self, time_audio):
        """
        A function responsible for calculating the amount of chunks and frames
        that need to be skipped to start from the last viewing point
        :param time_audio:
        :return:
        """
        self.jump_counter += int(time_audio / 0.1362)  # amount of chunks that need to be skipped
        self.jump_time += self.jump_counter * 0.1362
        self.show = False
        self.count = int(self.jump_counter * 0.7)  # amount of frames that need to be skipped
        if self.count % 2 != 0:
            self.count += 1
        self.time_loading = int(
            (time_audio / 3) + 1)  # The time it takes for the video to load until it reaches this point
        print(self.time_loading)

    def play_after_video(self):
        """
        A function that is responsible for displaying the video found on the computer
        And is responsible for audio and video synchronization
        :return:
        """
        cap = cv2.VideoCapture(PATH + "files\\" + self.file_name + ".avi")
        fps = cap.get(cv2.CAP_PROP_FPS)
        calc_timestamps = [0.0]
        cv2.namedWindow("frame", 0)
        cv2.resizeWindow("frame", 640, 360)
        self.t_video_commands.start()
        while cap.isOpened() and not self.close:
            ret, frame = cap.read()
            calc_timestamps.append(calc_timestamps[-1] + 1000 / fps)  # Calculate the time taken for each frame
            self.current_time_video = calc_timestamps[-1] / 1000
            while self.stop:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            delay = self.current_position_audio_time - self.current_time_video
            if delay > 0.05:
                print(str(self.current_position_audio_time) + "\t" + str(self.current_time_video) + "\t" + str(delay))
            else:
                print("sleep")
                time.sleep(1 / 25)
                self.show = True
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.close = True
                break
            if delay < 0.4:
                try:
                    cv2.imshow('frame', frame)
                except cv2.error:
                    break
            else:
                for i in range(25):
                    cap.read()
                    calc_timestamps.append(calc_timestamps[-1] + 1000 / fps)
                    self.current_time_video = calc_timestamps[-1] / 1000
        cap.release()
        cv2.destroyAllWindows()

    def play_after_audio(self):
        """A function responsible for playing the audio of the video found on the computer"""
        global rate_after_without_connection
        f = wave.open(PATH + "files\\" + self.file_name + '.wav', "rb")
        # instantiate PyAudio
        p = pyaudio.PyAudio()
        # open stream
        stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                        channels=f.getnchannels(),
                        rate=f.getframerate(),
                        output=True)
        chunk = 3000
        # read data
        data = f.readframes(chunk)
        start = time.time()
        stop = 0
        while data and not self.close:
            if self.stop:
                start_stop = time.time()
                while self.stop:
                    pass
                end_stop = time.time()
                stop += (end_stop - start_stop)
            end = time.time()
            self.current_position_audio_time = (end - start) - stop + self.jump_time
            if data == b'finish audio':
                self.close = True
                self.rate = True
                print("happen now")
                self.c_sharp_socket.send("close".encode())
            else:
                if not self.mute:
                    if self.jump_counter > 0:
                        self.jump_counter -= 1
                    else:
                        stream.write(data)
                else:
                    time.sleep(0.135)
                data = f.readframes(chunk)
        stream.stop_stream()
        stream.close()
        p.terminate()
        if not self.close:
            self.c_sharp_socket.send("finish and open rate".encode())
            rate_from_c_sharp = self.c_sharp_socket.recv(1024).decode()
            print(rate_from_c_sharp)
            self.send_encrypted_message_tcp(rate_from_c_sharp + "&")
            rate_after_without_connection = True

    def t_video(self):
        """
        A function responsible for turning on video streaming
        :return:
        """
        self.video_socket.send("startVideo".encode())
        t_receive = threading.Thread(target=self.receive_video_thread)
        t_receive.start()
        t_play = threading.Thread(target=self.play_video)
        t_play.start()

    def receive_video_thread(self):
        """
        Function is responsible for receiving the streaming frames
        :return:
        """
        while not self.close:
            video_time = self.video_socket.recv(17).decode()
            if video_time != "":
                video_time = float(video_time)
            frame = self.footage_socket.recv_string()
            img = base64.b64decode(frame)
            np_img = np.frombuffer(img, dtype=np.uint8)
            source = cv2.imdecode(np_img, 1)
            self.video_lock.acquire()
            self.list_of_frames.append(video_time)
            self.list_of_frames.append(source)
            self.video_lock.release()

    def play_video(self):
        """A function that is responsible for displaying the video that is being streamed
        and synchronizing it with the audio"""
        if self.time_loading != 0:
            time.sleep(self.time_loading)
        cv2.namedWindow("frame", 0)
        cv2.resizeWindow("frame", 640, 360)
        self.t_video_commands.start()
        while not self.close:
            if len(self.list_of_frames) > 1:
                self.video_lock.acquire()
                self.current_time_video = self.list_of_frames.pop(0)
                frame = self.list_of_frames.pop(0)
                self.video_lock.release()
                while self.stop:
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                delay = self.current_position_audio_time - self.current_time_video
                if delay > 0.05:
                    print(
                        str(self.current_position_audio_time) + "\t" + str(self.current_time_video) + "\t" + str(delay))
                else:
                    print("sleep")
                    time.sleep(1 / 25)
                    self.show = True
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.close = True
                    break
                if delay < 0.4:
                    cv2.imshow('frame', frame)
                else:
                    self.list_of_frames = self.list_of_frames[self.count:]
        cv2.destroyAllWindows()

    def audio(self):
        """
        A function responsible for turning on audio streaming
        :return:
        """
        self.audio_socket.sendto("startAudio".encode(), (self.send_ip, self.audio_port))
        py_audio_message = self.audio_socket.recvfrom(self.audio_buffer)[0].decode()
        py_audio_obj = Audio("", py_audio_message)
        t_receive = threading.Thread(target=self.receive_audio_thread)
        t_receive.start()
        t_play = threading.Thread(target=self.play_song, args=(py_audio_obj,))
        t_play.start()
        t_play.join()
        print("finish audio thread")

    def receive_audio_thread(self):
        """
        Function is responsible for receiving the streaming chunks
        :return:
        """
        while not self.close:
            data = self.audio_socket.recvfrom(self.audio_buffer)[0]
            self.audio_lock.acquire()
            self.list_of_chunks.append(data)
            self.audio_lock.release()

    def play_song(self, py_audio_obj):
        """
        A function that is responsible for playing the video audio
        :param py_audio_obj:
        :return:
        """
        if self.time_loading != 0:
            time.sleep(self.time_loading)
        start = time.time()
        stop = 0
        while not self.close:
            if self.stop:
                start_stop = time.time()
                while self.stop:
                    pass
                end_stop = time.time()
                stop += (end_stop - start_stop)
            if self.list_of_chunks:
                self.audio_lock.acquire()
                data = self.list_of_chunks.pop(0)
                self.audio_lock.release()
                end = time.time()
                self.current_position_audio_time = (end - start) - stop + self.jump_time
                if data == b'finish audio':
                    self.close = True
                    self.rate = True
                    self.c_sharp_socket.send("finish and open rate".encode())
                else:
                    if not self.mute:
                        if self.jump_counter > 0:
                            self.jump_counter -= 1
                        else:
                            py_audio_obj.write(data)
                    else:
                        time.sleep(0.135)
        py_audio_obj.close()
        if self.rate:
            rate_from_c_sharp = self.c_sharp_socket.recv(1024).decode()
            self.send_encrypted_message_tcp(rate_from_c_sharp + "&")
            self.rate = False

    def login_and_register(self):
        """A function responsible for checking whether the user information is correct or registering it to the system
         and checking that the password is strong enough with Authentication"""
        ok = True
        username = ""
        error_message = ""
        while ok:
            username_password = self.c_sharp_socket.recv(1024).decode()
            if "<%>" in username_password:
                username_password = username_password.split("<%>")
                username = username_password[0]
                password = username_password[1]
                hash_object = hashlib.md5(password.encode())
                hash_password = hash_object.hexdigest()
                self.send_encrypted_message_tcp(username + "<%>" + hash_password)
                message_from_server = self.receive_decrypted_message_tcp(1024)
                self.c_sharp_socket.send(message_from_server.encode())
                if message_from_server == "ok":
                    ok = False
            else:
                flag = 0
                if "<%>" in username_password and "<&>" in username_password:
                    flag = -1
                    error_message = "There are special characters in the password"
                username_password = username_password.split("<&>")
                username = username_password[0]
                password = username_password[1]
                if len(password) < 8:
                    flag = -1
                    error_message = "Password length is less than 8"
                elif not re.search("[a-z]", password):
                    flag = -1
                    error_message = "There are no lowercase letters in password"
                elif not re.search("[A-Z]", password):
                    flag = -1
                    error_message = "There are no capital letters in password"
                elif not re.search("[0-9]", password):
                    flag = -1
                    error_message = "There are no numbers in password"
                elif flag != -1:
                    hash_object = hashlib.md5(password.encode())
                    hash_password = hash_object.hexdigest()
                    self.send_encrypted_message_tcp(username + "<&>" + hash_password)
                if flag == -1:
                    self.c_sharp_socket.send(error_message.encode())
                else:
                    message_from_server = self.receive_decrypted_message_tcp(1024)
                    self.c_sharp_socket.send(message_from_server.encode())
                    if message_from_server == "ok":
                        ok = False
        return username

    def download_video(self):
        """A function that receives the content of the movie and downloads it to the computer"""
        data = b''
        filename_length_message = self.tcp_socket.recv(1024).decode().split("$")
        self.send_encrypted_message_tcp("finish")
        filename = filename_length_message[0]
        image_length = int(filename_length_message[1])
        while len(data) != image_length:
            data += self.tcp_socket.recv(image_length - len(data))
        data_str = aes.decrypt_aes(data)
        data = base64.b64decode(data_str)
        self.send_encrypted_message_tcp("finish")
        my_file = open(PATH + "files\\" + filename + ".avi", "wb")
        my_file.write(data)
        data = b''
        filename_length_message = self.tcp_socket.recv(1024).decode().split("$")
        self.send_encrypted_message_tcp("finish")
        filename = filename_length_message[0]
        image_length = int(filename_length_message[1])
        while len(data) != image_length:
            data += self.tcp_socket.recv(image_length - len(data))
        self.send_encrypted_message_tcp("finish")
        data_str = aes.decrypt_aes(data)
        data = base64.b64decode(data_str)
        my_file = open(PATH + "files\\" + filename + ".wav", "wb")
        my_file.write(data)
        self.c_sharp_socket.send("finish download".encode())
        print("finish downloading the video")


def receive_photos(my_socket, aes_encryption):
    """A function that receives the content of the movie and downloads it to the computer"""
    ok = True
    while ok:
        data = b''
        filename_length_message = aes_encryption.decrypt_aes(my_socket.recv(1024))
        if filename_length_message != "done":
            filename_length_message = filename_length_message.split("$")
            filename = filename_length_message[0]
            if path.exists(PATH + "files\\" + filename + ".bmp"):
                my_socket.send(aes_encryption.encrypt_aes("i have it"))
            else:
                my_socket.send(aes_encryption.encrypt_aes("send the photo"))
                image_length = int(filename_length_message[1])
                while len(data) != image_length:
                    data += my_socket.recv(image_length - len(data))
                data_str = aes_encryption.decrypt_aes(data)
                data = decodebytes(data_str.encode())
                my_socket.send(aes_encryption.encrypt_aes("ok"))
                my_file = open(PATH + "files\\" + filename + ".bmp", "wb")
                my_file.write(data)
        else:
            ok = False


def encryption_exchange_keys(sock):
    """
    Responsible for replacing encryption keys with the server
    :param sock:
    :return:
    """
    rsa = RSACrypt()
    aes_obj = AESEncryption()
    pickle_public_key = sock.recv(1024)
    rsa.public_key = rsa.unpack(pickle_public_key)
    aes_obj.create_key()
    sock.send(rsa.encrypt(aes_obj.key))
    return aes_obj


# Create a UDP socket at client side
# Send to server using created UDP socket
#
first_time = True
c_sharp_socket = None
user_name = ""
video_socket = None
while True:
    client_socket = socket.socket()
    client_socket.connect((SERVER_IP, 8077))  # connect to the server
    aes = encryption_exchange_keys(client_socket)
    msg = client_socket.recv(1024).decode()  # receive the list of ports
    if first_time:
        msg_if_first = "first"
    else:
        msg_if_first = "not first"
    client_socket.send(msg_if_first.encode())
    list_of_ports = msg.split("*")
    #
    if first_time:
        receive_photos(client_socket, aes)  # receive the photos of the videos
        client_socket.send("finish with the photos".encode())  # send finish
        #
        port = int(sys.argv[1])  # receive port as argument
        c_sharp_socket = socket.socket()
        c_sharp_socket.connect(("127.0.0.1", port))  # connect to the process in c#
    video_socket = socket.socket()
    video_socket.connect((SERVER_IP, int(list_of_ports[0])))  # connect to the server
    c = UdpClient(list_of_ports[0], list_of_ports[1], list_of_ports[2], c_sharp_socket, client_socket, video_socket,
                  aes)
    if first_time:
        user_name = c.login_and_register()
        first_time = False
    c.send_encrypted_message_tcp(user_name)
    movie_time_rate_download = c.receive_decrypted_message_tcp(1024)
    c_sharp_socket.send(movie_time_rate_download.encode())
    message = c_sharp_socket.recv(1024).decode()  # receive the file name from c# or what is written in the textbox
    print(message)
    if message == "":
        exit()
    elif message == "close":
        c.c_sharp_socket.send("closing the thread in buttonsForm and not open".encode())
        exit()
    while "%" in message:
        c.send_encrypted_message_tcp(message)  # send what is written in the textbox
        msg = c.receive_decrypted_message_tcp(1024)
        c_sharp_socket.send(msg.encode())
        message = c_sharp_socket.recv(1024).decode()  # receive the file name from c# or what is written in the textbox
        if message == "":
            exit()
    file_name = message
    if "play_without_connection!" in file_name:
        file_name = file_name.split("!")[1]
        c.file_name = file_name
        clip = VideoFileClip(PATH + "files\\" + c.file_name + ".avi")
        c.clip_duration = clip.duration
        c.play_after = True
        c.send_encrypted_message_tcp("play_without_connection!" + file_name)  # send to the server the file name
        t1 = threading.Thread(target=c.play_after_video)
        t1.start()
        t2 = threading.Thread(target=c.play_after_audio)
        t2.start()
        t2.join()
    else:
        if "#" in file_name:
            name_time = file_name
            file_name = name_time.split("#")[0]
            time_of_video = int(name_time.split("#")[1])
            c.jump(time_of_video)
        #
        c.send_encrypted_message_tcp(file_name)  # send to the server the file name
        #
        if "Download@" in file_name:
            t3 = threading.Thread(target=c.download_video)
            t3.start()
            t3.join()
        else:
            t1 = threading.Thread(target=c.t_video)
            t1.start()
            t2 = threading.Thread(target=c.audio)
            t2.start()
            t2.join()
        print("finish all")
