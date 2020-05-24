PROJECT_DIRECTORY = "C:\\tomer_python\\work_project\\work\\last_work2\\"  # the path of the main project Directory


class Path(object):
    """The server class is responsible for exchanging encryption keys with the client,
     sending communications ports, and creating the thread for each client that connects. """

    def __init__(self):
        pass

    @staticmethod
    def get_project_path():
        return PROJECT_DIRECTORY
