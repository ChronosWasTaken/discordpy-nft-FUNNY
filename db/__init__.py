import sqlite3
from os.path import isfile


class DB:
    def __init__(self, __DB_PATH, __BUILD_PATH):
        #sqlite3 by default doesn't support access from a different thread, so
        self.__conn = sqlite3.connect(__DB_PATH, check_same_thread=False)
        self.__cursor = self.__conn.cursor()

        if isfile(__BUILD_PATH):
            with open(__BUILD_PATH, 'r') as file:
                __plines = file.read().replace('\n', '').split(';')[:-1]
                for _ in __plines:
                    self.__cursor.execute(_)
                    self.__conn.commit()
    
    def __del__(self):
        self.__conn.close()

    def balanceof(self, discorduserid):
        #Try/Catch in here because it IS possible for someone to check their balance while having no entry.
        try:
            self.__cursor.execute(f"""
            SELECT Balance
            FROM storage
            WHERE UserID = {discorduserid};
            """)
            return self.__cursor.fetchall()[0][0]
        except:
            return None

    def delbalance(self, discorduserid):
        #Deletions in sqlite will always return 0
        self.__cursor.execute(f"""
        DELETE FROM storage 
        WHERE UserID = {discorduserid};
        """)
        self.__conn.commit()
        return 0

    def updbalance(self, discorduserid, newbalance):
        self.__cursor.execute(f"""
        INSERT INTO storage (UserID, Balance) 
        VALUES ({discorduserid}, {newbalance})
        ON CONFLICT(UserID) DO UPDATE SET Balance={newbalance};
        """)
        self.__conn.commit()
        return 0
    
    def mixbalance(self, discorduserid, addedbalance):
        if self.balanceof(discorduserid) is None:
            __finalbalance = addedbalance
        else:
            __finalbalance = self.balanceof(discorduserid) + addedbalance

        #UPSERT is kept because it is possible for someone to not have an entry in the db
        #and at the same time receive money
        #In other words, I am fucking stupid
        self.__cursor.execute(f"""
        INSERT INTO storage (UserID, Balance) 
        VALUES ({discorduserid}, {__finalbalance})
        ON CONFLICT(UserID) DO UPDATE SET Balance={__finalbalance};
        """)
        self.__conn.commit()
        return 0

    def top10(self):
        self.__cursor.execute("""
        SELECT UserID, Balance
        FROM storage
        ORDER BY Balance DESC
        LIMIT 10;
        """)
        return self.__cursor.fetchall()

    def addchannelwhitelist(self, channelid):
        try:
            self.__cursor.execute(f"""
            INSERT INTO channels (id)
            VALUES ({channelid});
            """)
            self.__conn.commit()
            return True
        except sqlite3.IntegrityError:
            return 'IE'
        except:
            return False

    def delchannelwhitelist(self, channelid):
        #Deletions in sqlite will always return 0
        self.__cursor.execute(f"""
        DELETE FROM channels 
        WHERE id = {channelid};
        """)
        self.__conn.commit()
        return True
    
    def channelwhitelist(self, channelid):
        try:
            self.__cursor.execute(f"""
            SELECT id
            FROM channels
            WHERE id = {channelid};
            """)
            #if nothing returned following return will throw IndexError
            #otherwise it will return the id
            return self.__cursor.fetchall()[0][0]
        except:
            return False

    def execute(self, arg, **kwargs):
        self.__cursor.execute(arg, kwargs)
        return self.__cursor

    def commit(self, *args, **kwargs):
        self.__conn.commit(args, kwargs)
        return 0

    def close(self):
        self.__conn.close()
        return 0