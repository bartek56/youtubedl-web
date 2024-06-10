import sqlite3


class YoutubeDatabase:

    def __init__(self):
        self.conn = sqlite3.connect('youtubeConfig.db')

    def createTable(self):

        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                url TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                parameter TEXT UNIQUE,
                value TEXT
            )
        ''')

        self.conn.commit()

    def executeMany(self, sqlCommand, data):
        cursor = self.conn.cursor()

        try:
            cursor.executemany(sqlCommand, data)
        except Exception as e:
            print("exception of command:", sqlCommand)
            print(str(e))

        self.conn.commit()

    def execute(self, sqlCommand):
        cursor = self.conn.cursor()
        cursor.execute(sqlCommand)

        return cursor.fetchall()

    def insertPlaylistsData(self, *playlists):
        self.executeMany('INSERT INTO playlists (name, url) VALUES (?, ?)', playlists)

    def insertSettingsData(self, *settings):
        self.executeMany('INSERT INTO settings (parameter, value) VALUES (?, ?)', settings)

    def getPlaylists(self):

        query = 'SELECT name, url FROM playlists'

        data = self.execute(query)

        print(data)

    def getSettings(self):
        query = 'SELECT parameter, value FROM settings'
        data = self.execute(query)
        print(data)

    def __del__(self):
        self.conn.close()

ytDatabase = YoutubeDatabase()
ytDatabase.createTable()
ytDatabase.insertSettingsData(("path", "/mnt/TOSHIBA EXT/music"), ("otherSetting","test"))
ytDatabase.getPlaylists()
ytDatabase.insertPlaylistsData(('test2','https://www.youtube.com/playlist?list=PL6uhlddQJkfh4YsbxgPE70a6KeFOCDgG_'))
ytDatabase.getSettings()
