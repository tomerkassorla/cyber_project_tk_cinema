import sqlite3
import os.path
import threading


class Database(object):
    """
    A class that takes care of creating a DATABASE if there is no data entry from DATABASE and reading data from it
    """

    def __init__(self):
        db_name = 'Database.db'
        self.result = ""
        self.result_dict = {}
        self.db_lock = threading.Lock()
        is_db_file_created = False
        if os.path.isfile(db_name):
            is_db_file_created = True
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.id_cursor = self.conn.cursor()
        if not is_db_file_created:
            self.id_cursor.execute(
                'CREATE TABLE users (username TEXT PRIMARY KEY, password TEXT,movie_time_list TEXT,'
                ' download_videos TEXT)')
            self.id_cursor.execute(
                'CREATE TABLE movie_info (movie_name TEXT PRIMARY KEY, rate TEXT,  count INT)')
            # Updates the database
            self.conn.commit()

    def add_new_user(self, username, hash_password):
        """
        Function that add a new user to the database
        :param username:
        :param hash_password:
        :return:
        """
        # Adds a row to the cursor
        self.db_lock.acquire()
        try:
            self.id_cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (username, hash_password, "", ""))
            self.conn.commit()
            self.db_lock.release()
            return "ok"
        except sqlite3.IntegrityError:
            self.db_lock.release()
            return "The user name already taken"

    def check_user_login(self, username, hash_password):
        """
        Function that check if the username and the password are okay
        :param username:
        :param hash_password:
        :return:
        """
        for db_row in self.id_cursor.execute("SELECT * FROM users"):
            if db_row[0] == username and db_row[1] == hash_password:
                return "ok"
        return "The user name or the password is incorrect"

    def add_new_movie(self, movie_name):
        """
        Function that add a new movie to the database
        :param movie_name:
        :return:
        """
        # Adds a row to the cursor
        self.db_lock.acquire()
        try:
            self.id_cursor.execute("INSERT INTO movie_info VALUES (?, ?, ?)", (movie_name, 0, 0))
            self.conn.commit()
            self.db_lock.release()
            return "ok"
        except sqlite3.IntegrityError:
            self.db_lock.release()
            return "The movie name already taken"

    def check_movie_exists(self, movie_name):
        """
        Function that check if the movie exist
        :param movie_name:
        :return:
        """
        for db_row in self.id_cursor.execute("SELECT * FROM movie_info"):
            if db_row[0] == movie_name:
                return True
        return False

    def get_list_of_videos_names(self):
        """
        Function that return list of the videos names
        :return:
        """
        videos_names_list = []
        for db_row in self.id_cursor.execute("SELECT * FROM movie_info"):
            videos_names_list.append(db_row[0])
        return videos_names_list

    def get_rate(self, movie_name):
        """
        Function that return the rate
        :param movie_name:
        :return:
        """
        for db_row in self.id_cursor.execute("SELECT * FROM movie_info"):
            if db_row[0] == movie_name:
                return float(db_row[1]), int(db_row[2])
        return 0, 0

    def get_movies_rates_str(self):
        """
        Function that return string of the movies rates
        :return:
        """
        movie_rate_str = ""
        for db_row in self.id_cursor.execute("SELECT * FROM movie_info"):
            movie_rate_str += db_row[0] + "%" + db_row[1] + "*"
        return movie_rate_str

    def convert_movie_time_dict_to_str(self, movie_time_dict):
        """
        function that convert dictionary to string
        :param movie_time_dict:
        :return:
        """
        self.result = ""
        for movie_name in movie_time_dict.keys():
            self.result = self.result + movie_name + "@" + str(movie_time_dict[movie_name]) + ";"
        return self.result

    def convert_movie_time_str_to_dict(self, movie_time_str):
        """
        function that convert string to dictionary
        :param movie_time_str:
        :return:
        """
        self.result_dict = {}
        if movie_time_str == "":
            return self.result_dict
        movie_time_str = movie_time_str.split(";")[:-1]
        for movie_data in movie_time_str:
            movie_name = movie_data.split("@")[0]
            movie_time = int(movie_data.split("@")[1])
            self.result_dict[movie_name] = movie_time
        return self.result_dict

    def update_rate(self, movie_name, rate):
        """
        function that update the video rate
        :param movie_name:
        :param rate:
        :return:
        """
        is_exists = self.check_movie_exists(movie_name)
        if not is_exists:
            # Adds a row to the cursor
            return False
        else:
            self.db_lock.acquire()
            old_rate, old_count = self.get_rate(movie_name)
            new_count = old_count + 1
            new_rate = (old_rate * old_count + rate) / new_count
            sql_cmd = "UPDATE movie_info SET rate = '" + str(new_rate) + "', count = " + str(
                new_count) + " WHERE movie_name= '" + str(movie_name) + "'"
            self.id_cursor.execute(sql_cmd)
            self.conn.commit()
            self.db_lock.release()

    def update_movie_time_for_user(self, username, movie_name, movie_time):
        """function that update the video time for user
        function that convert dictionary to string
        :param username:
        :param movie_name:
        :param movie_time:
        :return:
        """
        for db_row in self.id_cursor.execute("SELECT * FROM users"):
            if db_row[0] == username:
                movie_dict = self.convert_movie_time_str_to_dict(db_row[2])
                movie_dict[movie_name] = movie_time
                new_movie_time_list_str = self.convert_movie_time_dict_to_str(movie_dict)
                self.db_lock.acquire()
                sql_cmd = "UPDATE users SET movie_time_list = '" + new_movie_time_list_str + "' WHERE username = '" \
                          + str(username) + "'"
                self.id_cursor.execute(sql_cmd)
                self.conn.commit()
                self.db_lock.release()
                return "ok"
        return "The user name is incorrect"

    def get_movie_time_for_user(self, username):
        """
        function that return the video time for user
        :param username:
        :return:
        """
        for db_row in self.id_cursor.execute("SELECT * FROM users"):
            if db_row[0] == username:
                movie_dict = self.convert_movie_time_str_to_dict(db_row[2])
                return movie_dict
        return {}

    def update_download_videos(self, username, movie_name):
        """
        function that update the download videos
        :param username:
        :param movie_name:
        :return:
        """
        for db_row in self.id_cursor.execute("SELECT * FROM users"):
            if db_row[0] == username:
                self.db_lock.acquire()
                download_videos = self.get_download_videos(username) + movie_name + "&"
                sql_cmd = "UPDATE users SET download_videos = '" + download_videos + "' WHERE username = '" + str(
                    username) + "'"
                self.id_cursor.execute(sql_cmd)
                self.conn.commit()
                self.db_lock.release()
                return "ok"
        return "The user is incorrect"

    def get_download_videos(self, username):
        """
        Function that return the download videos of the user
        :param username:
        :return:
        """
        for db_row in self.id_cursor.execute("SELECT * FROM users"):
            if db_row[0] == username:
                return db_row[3]
        return ""


def main():
    d = Database()
    print(d.add_new_user("tom", "11"))
    d.update_download_videos("tom", "yos")
    print(d.get_download_videos("tom"))

# main()
