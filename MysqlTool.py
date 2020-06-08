import pymysql



def get_db(host,username,password,db_name):
    db = pymysql.connect(host, username, password, db_name)
    return db

# 执行新增语句
def insert(db,sql):
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    db.close()

# 执行修改语句
def delete(db,sql):
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    db.close()

# 执行修改语句
def update(db,sql):
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    db.close()


# 查询语句
def select(db,sql):
    cursor = db.cursor()
    results = None
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
    except:
        print("查询语句执行异常")
    db.close()
    return results