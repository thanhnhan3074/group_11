import mysql.connector

db = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password ="Minh_17102004",
    database = "usermanagement"
)
cursor = db.cursor()

def check_connection_db():
    try:
        if db.is_connected():
            return f"{db._host} is connected"
    except mysql.connector.errors as error:
        return f"Error - {error}"
    
def _create_user_tb():
    try:
        users ='''
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                email TEXT NOT NULL
            )
        '''
        cursor.execute(users)
        return "Set up table complete"
    except Exception as error:
        return f"error - {error}"
    
def _create_record_tb():
    try:
        params = [1,"thanhnhan","thanhnhan_123","admin","mtranquoc77@gmail.com"]
        users_record ='''
            INSERT INTO users (id,username,password,role,email) VALUES (%s,%s,%s,%s,%s)
        '''
        cursor.execute(users_record,params)
        db.commit()
        return "Set up record complete"
    except Exception as error:
        return f"error - {error}"
    
def _check_record_tb():
    try:
        cursor.execute("SELECT * FROM users")
        for obj in cursor.fetchall():
            return obj
    except Exception as error:
        return f"error - {error}"
            
def _clear_data():
    try:
        cursor.execute("DROP TABLE users")
        return f"Removed data"
    except Exception as error:
        return f"error - {error}"
if __name__ == "__main__":
    print(check_connection_db())
    print(_create_user_tb())
    print(_create_record_tb())
    print(_check_record_tb())
    # print(_clear_data())
    