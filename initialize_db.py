import mysql.connector
import sys

# 数据库连接配置
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'your_password',
    'database': 'clinic',
}

# SQL 操作
sql_create_tables = [
    """
    CREATE TABLE IF NOT EXISTS Department (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        code VARCHAR(255) UNIQUE NOT NULL,
        location VARCHAR(255),
        is_active BOOLEAN NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS Doctor (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        name VARCHAR(255) NOT NULL,
        department_id INT NOT NULL,
        title VARCHAR(255),
        phone VARCHAR(255) UNIQUE NOT NULL,
        available_slots_per_day INT NOT NULL,
        FOREIGN KEY (department_id) REFERENCES Department(id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS Patient (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        id_card VARCHAR(255) UNIQUE NOT NULL,
        phone VARCHAR(255) UNIQUE NOT NULL,
        dob DATE NOT NULL,
        gender VARCHAR(50),
        insurance_type VARCHAR(50),
        address VARCHAR(255)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS Schedule (
        id INT AUTO_INCREMENT PRIMARY KEY,
        doctor_id INT NOT NULL,
        date DATE NOT NULL,
        time_slot VARCHAR(50) NOT NULL,
        room_no VARCHAR(50),
        capacity INT NOT NULL,
        status VARCHAR(50),
        FOREIGN KEY (doctor_id) REFERENCES Doctor(id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS Appointment (
        id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id INT NOT NULL,
        schedule_id INT NOT NULL,
        status VARCHAR(50) NOT NULL,
        check_in_time DATETIME,
        assigned_room VARCHAR(50),
        created_at DATETIME NOT NULL,
        FOREIGN KEY (patient_id) REFERENCES Patient(id),
        FOREIGN KEY (schedule_id) REFERENCES Schedule(id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS MedicalRecord (
        id INT AUTO_INCREMENT PRIMARY KEY,
        appointment_id INT NOT NULL,
        doctor_id INT NOT NULL,
        diagnosis TEXT,
        treatment TEXT,
        prescription TEXT,
        visit_time DATETIME,
        FOREIGN KEY (appointment_id) REFERENCES Appointment(id),
        FOREIGN KEY (doctor_id) REFERENCES Doctor(id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS Billing (
        id INT AUTO_INCREMENT PRIMARY KEY,
        medical_record_id INT NOT NULL,
        total_amount DECIMAL(10, 2) NOT NULL,
        insurance_amount DECIMAL(10, 2),
        self_pay_amount DECIMAL(10, 2),
        status VARCHAR(50),
        paid_at DATETIME,
        payment_method VARCHAR(50),
        FOREIGN KEY (medical_record_id) REFERENCES MedicalRecord(id)
    );
    """
]

sql_drop_tables = [
    "DROP TABLE IF EXISTS Billing;",
    "DROP TABLE IF EXISTS MedicalRecord;",
    "DROP TABLE IF EXISTS Appointment;",
    "DROP TABLE IF EXISTS Schedule;",
    "DROP TABLE IF EXISTS Patient;",
    "DROP TABLE IF EXISTS Doctor;",
    "DROP TABLE IF EXISTS Department;",
]

sql_insert_data = [
    "INSERT INTO Department (name, code, location, is_active) VALUES ('内科', 'NK', '一楼', TRUE);",
    "INSERT INTO Department (name, code, location, is_active) VALUES ('外科', 'WK', '二楼', TRUE);",
    
]

sql_query_data = "SELECT * FROM Department;"

# 执行 SQL 脚本
def execute_sql(statements):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        for statement in statements:
            cursor.execute(statement)
            print(f"Executed: {statement.strip().splitlines()[0]}...")
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# 查询数据
def query_data(statement):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(statement)
        results = cursor.fetchall()
        for row in results:
            print(row)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# 主函数
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python initialize_db.py [create|drop|insert|query]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "create":
        execute_sql(sql_create_tables)
    elif command == "drop":
        execute_sql(sql_drop_tables)
    elif command == "insert":
        execute_sql(sql_insert_data)
    elif command == "query":
        query_data(sql_query_data)
    else:
        print("Invalid command. Use [create|drop|insert|query].")
