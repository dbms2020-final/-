#all kivy funcitons
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen

import datetime
import time
import psycopg2
import re

CD_re = re.compile(r'cd\d{9}$')
book_re = re.compile(r'bid\d{8}$')
users_re = re.compile(r'[a-c]\d{6}$')
library_re = re.compile(r'lid\d{3}$')
room_re = re.compile(r'r\d{3}$')
'''
conn = psycopg2.connect(
    host="satao.db.elephantsql.com",
    dbname="rsgeauxw",
    user="rsgeauxw",
    password="ai7DZe4fX2OfyJ87wEgWwnh1DkrAgNT1"
)'''
conn = psycopg2.connect(
    dbname="Final_Project",
    user="postgres",
    password="102030520z"
)
cur = conn.cursor()

class MainScreen(Screen):
    pass

class ModeselecterScreen(Screen):
    pass

class BorrowScreen(Screen):
    pass

class UserinformationScreen(Screen):
    pass

class BookinformationScreen(Screen):
    pass

class LibinformationScreen(Screen):
    pass

class FinalApp(App):
    
    def build(self):
        
        sm = ScreenManager()
        mainscreen = MainScreen(name = "mainscreen")
        modeselect = ModeselecterScreen(name = 'modeselect')
        borrow = BorrowScreen(name = 'borrow')
        userinfo = UserinformationScreen(name = 'userinfo')
        bookinfo = BookinformationScreen(name = 'bookinfo')
        libinfo = LibinformationScreen(name = 'libinfo')
        sm.add_widget(mainscreen)
        sm.add_widget(modeselect)
        sm.add_widget(borrow)
        sm.add_widget(userinfo)
        sm.add_widget(bookinfo)
        sm.add_widget(libinfo)
        #variables
        self.library_number = ''
        self.find_item = 'book'
        self.manage_lib = 'book'
        self.borrow_item = 'book'
        return sm

    def change_lib(self,number):
        self.library_number = number
        self.library_number = 'lid' + self.library_number 
        print(self.library_number)

    def pattern(self,item_type, item_id):
        if item_type == "CD":
            result = CD_re.match(item_id)    
        elif item_type == "book":
            result = book_re.match(item_id)
        elif item_type == "library":
            result = library_re.match(item_id)
        elif item_type == "room":
            result = room_re.match(item_id)
        if result == None:
            return False 
        else:
            return True

    def exist(self,item_type, item_id):
        if item_type == "room":
            cur.execute("""
                SELECT room_id
                FROM room
                WHERE room_id = '{}' AND library_id = '{}'
            """.format(item_id,self.library_number))
            data = cur.fetchall()
        else:
            cur.execute("""
                SELECT {}_id
                FROM {}
                WHERE {}_id = '{}'
                """.format(item_type, item_type, item_type, item_id))
            data = cur.fetchall()

        return data
    
    def item_manage(self,button, item_type, item_id, item_name, floor, coordinate):
        if button == "create":
            cur.execute("""
                INSERT INTO {} ({}_id, name, state)
                VALUES('{}', '{}', '1');
            """.format(item_type, item_type, item_id, item_name))
            conn.commit()
            cur.execute("""
                INSERT INTO item_placed (library_id, item_type, item_id, floor, coordinate)
                VALUES('{}', '{}', '{}', {}, '{}');
            """.format(self.library_number, item_type, item_id, floor, coordinate))
            conn.commit()
        elif button == "delete":
            cur.execute("""
                DELETE FROM {}
                WHERE {}_id = '{}'
            """.format(item_type, item_type, item_id))
            conn.commit()
            cur.execute("""
                DELETE FROM item_placed
                WHERE item_id = '{}'
            """.format(item_id))
            conn.commit()

    def item_search(self,item_type , item_id):
        #id是否存在
        if(self.exist(item_type , item_id) == []):
            return []
        
        else:
            cur = conn.cursor()
            cur.execute("""
            SELECT * FROM {} WHERE {}_id = '{}'
            """
            .format(item_type , item_type , item_id)
            )

            data = cur.fetchall()

            if(data[0][2]):
                cur.execute("""
                SELECT library_id , floor , coordinate FROM item_placed WHERE item_id = '{}'
                """
                .format(item_id)
                )
                info = cur.fetchall()
                data[0] = data[0]+info[0]

        data[0] = tuple(list(data[0])[1:])

        return data
    def user_search(self,user_id):
    #[name,借閱中的book,借閱過的book,借閱中的cd,借閱過的cd]
        #id是否存在
        if self.user_check(user_id) == False:
            return []
        else:
            cur.execute("""
                SELECT name
                FROM users
                WHERE user_id = '{}'"""
                .format(user_id))
            data = cur.fetchall()

        for i in ["book" , "CD"]:
            cur.execute("""
            SELECT it.name , b.lend_date , b.estimated_return , b.state , b.exact_return
            FROM {}_borrow as b, {} as it
            WHERE b.user_id = '{}' AND it.{}_id = b.{}_id
            """
            .format(i , i , user_id , i , i))
            
            data2 = cur.fetchall()
            back = list()
            unback = list()

            for it in data2:
                if(it[3]):
                    back.append(it[0:2] + (it[4],))
                else:
                    unback.append(it[0:3])

            data.append(unback)
            data.append(back)

        return data

    def user_check(self,_id):
        result = users_re.match(_id)
        if result == None:
            print("error user_id input pattern!")
            return False
        else:
            cur.execute("""
            SELECT *
            FROM users
            WHERE user_id = '{}'
            """.format(_id))
            data = cur.fetchall()
            if data==[]:
                print("id not exist!")
                return False
            else:
                return True

    def find_switch(self,item):
        self.find_item = item

    def find(self,item_id):
        print(item_id)
        if self.find_item == 'book':
            item_id = 'bid' + item_id
        else: 
            item_id = 'cd' + item_id
        if self.pattern(self.find_item, item_id):
            data = self.exist(self.find_item, item_id)
            if data == []:
                print("id not exist!")
            else:
                temp = self.item_search(self.find_item, item_id)
                print(temp)
                return str(temp)
        else:
            print("error input pattern!")
        return ''

    def manage_switch(self,item):
        self.manage_lib = item
        print(self.manage_lib)

    #button, item_type, item_id, item_name, floor, coordinate
    def lib_manage_delete(self,item_id,item_name,floor,coordinate):
        print(item_id)
        if self.manage_lib == 'book':
            item_id = 'bid' + item_id
        else: 
            item_id = 'cd' + item_id
        if self.pattern(self.manage_lib, item_id):
            data = self.exist(self.manage_lib, item_id)
            if (data == []):
                return "no such item can delete!"
            else :
                self.item_manage('delete',self.manage_lib,item_id,item_name,floor,coordinate)
                conn.commit()
                return "done!"
        else:
            return "error input pattern!"
    
    def lib_manage_insert(self,item_id,item_name,floor,coordinate):
        print(item_id)
        if self.manage_lib == 'book':
            item_id = 'bid' + item_id
        else: 
            item_id = 'cd' + item_id
        if self.pattern(self.manage_lib, item_id):
            data = self.exist(self.manage_lib, item_id)
            if (data != []):
                return "the item id was exist!"
            else :
                self.item_manage('create',self.manage_lib,item_id,item_name,floor,coordinate)
                conn.commit()
                return "done!"
        else:
            return "error input pattern!"

    def search_user_information(self,user_id):
        data = self.user_search(user_id)
        temp = ''
        for item in data[1]:
            temp = temp + str(item) + '\n'
        for item in data[3]:
            temp = temp + str(item) + '\n'
        print(temp)
        if temp == '':
            temp = 'All item have been returned'
        return temp

    def button_pressed(self,user_id, item_id, item_type, day, button): 
        print(user_id)
        print(item_id)
        print(item_type)
        print(day)
        print(button)
        if item_type == 'book':
            item_id = 'bid' + item_id
        elif item_type == 'CD':
            item_id = 'cd' + item_id
        else :
            item_id = 'r' + item_id

        print(item_id)
        if self.user_check(user_id) == False:
            return
        if self.pattern(item_type, item_id):
            data = self.exist(item_type, item_id)
            if data == []:
                print("id not exist!")
                return
        else:
            print("error item_id input pattern!")
            return

        if button == 'return':
            if item_type == 'room':
                t = time.localtime()
                now_time = time.strftime("%H:%M", t)
                cur.execute("""
                    UPDATE room_borrow
                    SET end_time = '{}'
                    WHERE library_id = '{}' AND room_id = '{}' AND user_id = '{}'
                    """.format(now_time, self.library_number, item_id, user_id))
                conn.commit()
                cur.execute("""
                    UPDATE room
                    SET state = '1'
                    WHERE room_id = '{}' AND library_id = '{}'
                """.format(item_id, self.library_number))
                conn.commit()
            else:
                now_date = datetime.date.today().strftime('%Y-%m-%d')
                cur.execute("""
                    UPDATE {}_borrow
                    SET exact_return = '{}', state = '1'
                    WHERE user_id = '{}' AND {}_id = '{}' AND state = '0'
                    """.format(item_type, now_date, user_id, item_type, item_id))
                conn.commit()
                cur.execute("""
                    UPDATE {}
                    SET state = '1'
                    WHERE {}_id = '{}'
                """.format(item_type, item_type, item_id))
                conn.commit()
                cur.execute("""
                    UPDATE item_placed
                    SET library_id = '{}'
                    WHERE item_id = '{}'
                """.format(self.library_number, item_id))
                conn.commit()
            print("update done!")

        elif button == 'borrow':
            cur.execute("""
                SELECT state
                FROM {}
                WHERE {}_id = '{}'
            """.format(item_type , item_type , item_id))
        
            data = cur.fetchall()
            if not(data[0][0]):
                return False
        
            cur.execute("""
                UPDATE {}
                SET state = '0'
                WHERE {}_id = '{}' AND state = '1'
                """.format(item_type, item_type, item_id))
            conn.commit()

            if(item_type == "room"):
                now = time.strftime("%H:%M", time.localtime())
            
                cur.execute("""
                    INSERT INTO room_borrow (library_id , room_id, user_id , start_time)
                    VALUES('{}', '{}', '{}' , '{}');
                    """.format(self.library_number, item_id, user_id, now))
                conn.commit()

            else:
                toda = datetime.date.today()
                res = toda + datetime.timedelta(days=int(day))

                today = toda.strftime('%Y-%m-%d')
                est = res.strftime('%Y-%m-%d')

                cur.execute("""
                    INSERT INTO {}_borrow ({}_id, user_id , lend_date , estimated_return , state)
                    VALUES('{}', '{}', '{}' , '{}' , '0');
                    """.format(item_type , item_type , 
                        item_id, user_id, today , est))
                conn.commit()

            print("update done!")



            
if __name__ == "__main__":
    FinalApp().run()