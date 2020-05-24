import socket
import threading
import time
import cv2
import zmq
import base64
import os
from audio_handler import *
from encryption import *
from base64 import b64encode
import path_class

PATH = path_class.Path.get_project_path()  # the path of the main project Directory


def number_to_be_17(number):
    """ כFunction that creates a 17-digit number """
    while len(number) < 17:
        number = "0" + number
    return number[:17]


class ClientHandler(threading.Thread):
    """This class is the server side for each client who joins,
     and is responsible for streaming the video,logging in and signing up
     a client with synchronization with the DATABASE and transferring videos and pictures that describe them."""

    def __init__(self, tcp_socket, video_port, audio_port, zmq_port, database, aes, first_time):
        super(ClientHandler, self).__init__()
        self.video_port = video_port
        self.audio_port = audio_port
        self.tcp_socket = tcp_socket
        self.database = database
        self.audio_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.server_video_socket = socket.socket()
        self.server_video_socket.bind(("0.0.0.0", video_port))
        self.server_video_socket.listen(1)
        self.video_socket = None
        self.audio_socket.bind(("0.0.0.0", self.audio_port))
        self.filename = "songs\\"
        self.context = zmq.Context()
        self.footage_socket = self.context.socket(zmq.PUB)
        self.footage_socket.bind('tcp://*:' + str(zmq_port))
        self.close_stream = False
        self.aes = aes
        self.first_time = first_time
        self.user_name = ""
        self.name = ""

    def get_the_names_of_files(self, message):
        """
        The function build a string that consists of all the video names corresponding to the input it received.
        :param message:
        :return:
        """
        new_message = ""
        videos_names_list = self.database.get_list_of_videos_names()
        for name in videos_names_list:
            if message in name:
                new_message += name + "#"
        if new_message == "":
            return "##"
        else:
            return new_message

    def run(self):
        """
        This function is the main function of the class and it runs automatically when the thread is started.
         She is responsible for sending the pictures describing the videos, transferring data from DATABASE,
         send video and audio with streaming and downloading a video.
        :return:
        """
        if self.first_time:
            self.send_video_files()  # send the photos to the client
            print(self.tcp_socket.recv(1024).decode())  # receive finish msg
        self.video_socket = self.server_video_socket.accept()[0]
        if self.first_time:
            self.login_and_register()
        self.user_name = self.receive_decrypted_message_tcp(1024)  # get the user name
        movie_time_dict = self.database.get_movie_time_for_user(self.user_name)
        movie_time_str = self.database.convert_movie_time_dict_to_str(movie_time_dict)
        self.send_encrypted_message_tcp(
            movie_time_str + "$" + self.database.get_movies_rates_str() + "$" + self.database.get_download_videos(
                self.user_name))  # send needed data from the database
        try:
            message = self.receive_decrypted_message_tcp(
                1024)  # receive the file name or what is written in the textbox
            if message == "":
                exit()
        except ConnectionResetError:
            message = ""
            self.tcp_socket.close()
            exit()
        while "%" in message:
            message = message[1:]
            new_message = self.get_the_names_of_files(message)
            self.send_encrypted_message_tcp(
                new_message)  # sends the names of the videos corresponding to the input it received
            message = self.receive_decrypted_message_tcp(
                1024)  # receive the file name or what is written in the textbox
            if message == "":
                exit()
        self.name = message
        if "play_without_connection!" in message:  # play without connection
            t3 = threading.Thread(target=self.wait_for_commands)
            t3.start()
            self.name = message.split("!")[1]
        elif "Download@" in self.name:  # send the data of the video
            name = self.name.split("@")[1]
            self.database.update_download_videos(self.user_name, name)  # update the downloaded videos
            t1 = threading.Thread(target=self.send_video_thread, args=(name,))
            t1.start()
        else:
            self.filename += self.name
            print(self.filename)
            # start streaming
            t1 = threading.Thread(target=self.handle_video)
            t1.start()
            t2 = threading.Thread(target=self.handle_audio)
            t2.start()
            t3 = threading.Thread(target=self.wait_for_commands)
            t3.start()

    def login_and_register(self):
        """
        A function that is responsible for checking that the user name
         and password are OK or register a new user for the system.
        :return:
        """
        ok = True
        while ok:
            username_password = self.receive_decrypted_message_tcp(1024)
            if "<%>" in username_password:
                username_password = username_password.split("<%>")
                user_name = username_password[0]
                self.user_name = user_name
                password = username_password[1]
                msg = self.database.check_user_login(user_name, password)
                self.send_encrypted_message_tcp(msg)
                if msg == "ok":
                    ok = False
            elif "<&>" in username_password:
                username_password = username_password.split("<&>")
                user_name = username_password[0]
                self.user_name = user_name
                password = username_password[1]
                msg = self.database.add_new_user(user_name, password)
                self.send_encrypted_message_tcp(msg)
                if msg == "ok":
                    ok = False

    def send_video_files(self):
        """
        The function is responsible for sending the pictures that describe the existing videos in the system.
        :return:
        """
        for file in os.listdir("songs"):
            if file.endswith(".bmp"):
                file_name = file[:-4]
                my_file = open("songs\\" + file_name + ".bmp", 'rb')
                data = my_file.read()
                base64_data = b64encode(data)
                data_str = str(base64_data)[2:-1]  # Makes the information a string to encrypt
                data = self.aes.encrypt_aes(data_str)
                self.send_encrypted_message_tcp(file_name + "$" + str(len(data)))
                msg = self.receive_decrypted_message_tcp(1024)
                if not self.database.check_movie_exists(file_name):
                    self.database.add_new_movie(file_name)
                    print("add new video " + file_name)
                if msg != "i have it":
                    self.tcp_socket.sendall(data)
                    self.receive_decrypted_message_tcp(1024)
        self.send_encrypted_message_tcp("done")

    def receive_decrypted_message_tcp(self, buffer_size):
        """receive a message"""
        message = self.tcp_socket.recv(buffer_size)
        return self.aes.decrypt_aes(message)

    def send_encrypted_message_tcp(self, message):
        """send a message"""
        message = self.aes.encrypt_aes(message)
        self.tcp_socket.send(message)

    def wait_for_commands(self):
        """
        A function that is responsible for entering the time the user left the video or rating it for the video.
        :return:
        """
        receive_msg = self.receive_decrypted_message_tcp(1024)
        print(receive_msg)
        if "stop_time" in receive_msg:
            self.close_stream = True
            time_stop = int(receive_msg.split(" ")[1])
            self.database.update_movie_time_for_user(self.user_name, self.name, time_stop)
        if "&" in receive_msg:
            self.database.update_rate(self.name, int(receive_msg[:-1]))
            print(self.database.get_rate(self.name)[0])

    def handle_audio(self):
        """
        A function that is responsible for streaming audio
        :return:
        """
        py_audio_obj = Audio(self.filename, "")
        receive_list = self.audio_socket.recvfrom(1024)
        msg = py_audio_obj.get_constants()
        self.audio_socket.sendto(msg.encode(), receive_list[1])
        address = receive_list[1]
        print(address)
        message = receive_list[0].decode()
        print(message)
        data = py_audio_obj.readframes()
        while data and not self.close_stream:
            self.audio_socket.sendto(data, address)
            data = py_audio_obj.readframes()
            time.sleep(0.002)
        self.audio_socket.sendto("finish audio".encode(), address)
        py_audio_obj.close()
        print("finish to send the audio")

    def handle_video(self):
        """
        A function responsible for streaming the video
        :return:
        """
        cap = cv2.VideoCapture(self.filename + '.avi')  # init the camera
        fps = cap.get(cv2.CAP_PROP_FPS)  # read from the file the fps => frames per sec
        calc_timestamps = [0.0]
        receive_message = self.video_socket.recv(1024)
        print(receive_message.decode())
        while cap.isOpened() and not self.close_stream:
            ret, frame = cap.read()
            calc_timestamps.append(calc_timestamps[-1] + 1000 / fps)
            current_time_video = calc_timestamps[-1] / 1000  # Calculate the time taken for each frame
            time_to_17 = number_to_be_17(str(current_time_video))
            try:
                encoded, buffer = cv2.imencode('.jpg', frame)
            except cv2.error:
                break
            jpg_as_text = base64.b64encode(buffer)
            self.video_socket.send(time_to_17.encode())
            self.footage_socket.send(jpg_as_text)  # sends tte data as string
            time.sleep(0.002)

        print("finish to send the video")

    def send_video_thread(self, name_of_video):
        """
        A function that sends the video information so that the user can download it
        :param name_of_video:
        :return:
        """
        my_file = open(PATH + "songs\\" + name_of_video + ".avi", 'rb')
        data = my_file.read()  # read the video file
        data_str = b64encode(data).decode('ascii')  # makes the data as string
        data = self.aes.encrypt_aes(data_str)
        self.tcp_socket.send((name_of_video + "$" + str(len(data))).encode())
        self.receive_decrypted_message_tcp(1024)
        self.tcp_socket.sendall(data)
        self.receive_decrypted_message_tcp(1024)
        my_file = open(PATH + "songs\\" + name_of_video + ".wav", 'rb')
        data = my_file.read()  # read the audio file
        data_str = b64encode(data).decode('ascii')  # makes the data as string
        data = self.aes.encrypt_aes(data_str)
        self.tcp_socket.send((name_of_video + "$" + str(len(data))).encode())
        self.receive_decrypted_message_tcp(1024)
        self.tcp_socket.sendall(data)
        self.receive_decrypted_message_tcp(1024)
        print("finish with transfer the video")
