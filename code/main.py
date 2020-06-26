#%% #initial
import psycopg2
import re
import datetime
import time
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
)
'''
conn = psycopg2.connect(
    dbname="Final_Project",
    user="postgres",
    password="102030520z"
)
cur = conn.cursor()

#%%
def pattern(item_type, item_id):
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

#%%
def exist(item_type, item_id):
    if item_type == "room":
        cur.execute("""
            SELECT room_id
            FROM room
            WHERE room_id = '{}' AND library_id = '{}'
        """.format(item_id, library_id))
        data = cur.fetchall()
    else:
        cur.execute("""
            SELECT {}_id
            FROM {}
            WHERE {}_id = '{}'
            """.format(item_type, item_type, item_type, item_id))
        data = cur.fetchall()

    return data

#%%
def item_manage(button, item_type, item_id, item_name, floor, coordinate):
    if button == "create":
        cur.execute("""
            INSERT INTO {} ({}_id, name, state)
            VALUES('{}', '{}', '1');
        """.format(item_type, item_type, item_id, item_name))
        conn.commit()
        cur.execute("""
            INSERT INTO item_placed (library_id, item_type, item_id, floor, coordinate)
            VALUES('{}', '{}', '{}', {}, '{}');
        """.format(library_id, item_type, item_id, floor, coordinate))
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

#%%   #館藏查詢,[]代表ID錯誤
def item_search(item_type , item_id):
    #id是否存在
    if(exist(item_type , item_id) == []):
        return []
    
    else:
        
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

#%%
def user_search(user_id):
#[name,借閱中的book,借閱過的book,借閱中的cd,借閱過的cd]
    #id是否存在
    if user_check(user_id) == False:
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

#%%
def user_check(_id):
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



#%%  1. 借閲界面
def button_pressed(user_id, item_id, item_type, button):
    if user_check(user_id) == False:
        return
    if pattern(item_type, item_id):
        data = exist(item_type, item_id)
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
                """.format(now_time, library_id, item_id, user_id))
            conn.commit()
            cur.execute("""
                UPDATE room
                SET state = '1'
                WHERE room_id = '{}' AND library_id = '{}'
            """.format(item_id, library_id))
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
                WHERE {}_id = '{}'
            """.format(library_id, item_type, item_id))
            conn.commit()
        print("update done!")

    elif button == 'borrow':
        cur.execute("""
            SELECT state
            FROM {}
            WHERE {}_id = '{}'
        """.format(item_type , item_type , item_id))
    
        data = cur.fetchall()
        if(data[0][0]):
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
                """.format(library_id, item_id, user_id, now))
            conn.commit()

        else:
            toda = datetime.date.today()
            res = toda + datetime.timedelta(days=day)

            today = toda.strftime('%Y-%m-%d')
            est = res.strftime('%Y-%m-%d')

            cur.execute("""
                INSERT INTO {}_borrow ({}_id, user_id , lend_date , estimated_return , state)
                VALUES('{}', '{}', '{}' , '{}' , '0');
                """.format(item_type , item_type , 
                    item_id, user_id, today , est))
            conn.commit()

        print("update done!")

library_id = 'lid102'
user_id = 'b434612'
item_id = 'bid10000654'
item_type = 'book'
button = 'borrow'
day = 5
button_pressed(user_id, item_id, item_type, button)


#%%  2. 調閲使用者資料
index = ['NAME:','借閱中的book:','借閱過的book:','借閱中的CD:','借閱過的CD:']
user_id = 'b196785'     # get input from kv
data = user_search(user_id)
j=0
for i in data:
    print(index[j])
    print(i)
    j+=1

#%%  3. 館藏查詢
item_type = "book"
item_id = "bid10000001"
if pattern(item_type, item_id):
    data = exist(item_type, item_id)
    if data == []:
        print("id not exist!")
    else:
        print(item_search(item_type, item_id))
else:
    print("error input pattern!")

#%%  4. 館藏管理
library_id = 'lid101'
button = 'create'
item_type = 'book'
name = 'night light'
item_id = 'bid10000654'  #get all this input from kv
floor = 2
coordinate = '2,3'

if pattern(item_type, item_id):
    data = exist(item_type, item_id)
    if (data == []) and (button == 'delete'):
        print("no such item can delete!")
    elif (data != []) and (button == 'insert'):
        print("the item id was exist!")
    else :
        item_manage(button, item_type, item_id, name, floor, coordinate)
        print("done!")
else:
    print("error input pattern!")


#%%
cur.close()
conn.close()

#%%