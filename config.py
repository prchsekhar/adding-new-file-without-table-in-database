import mysql.connector
import psycopg2
import pyodbc
import streamlit as st
import pandas as pd

# Function to establish a MySQL connection
def connect_mysql(host, port, db_name, username, password):
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            database=db_name,
            user=username,
            password=password,
        )
        if connection.is_connected():
            return connection, "Successfully connected to MySQL!"
    except Exception as e:
        return None, str(e)

# Function to establish a PostgreSQL connection
def connect_postgres(host, port, db_name, username, password):
    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=db_name,
            user=username,
            password=password,
        )
        if connection:
            return connection, "Successfully connected to PostgreSQL!"
    except Exception as e:
        return None, str(e)

# Function to establish a MSSQL connection
def connect_mssql(host, port, db_name, username, password):
    try:
        connection = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={host},{port};"
            f"DATABASE={db_name};"
            f"UID={username};"
            f"PWD={password};"
        )
        if connection:
            return connection, "Successfully connected to MSSQL!"
    except Exception as e:
        return None, str(e)
    

def show_tables(connection,message,selected_db):
    if connection:
        st.success(message)
        cursor = connection.cursor()
        if selected_db == "MySQL":
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
        elif selected_db == "PostgreSQL":
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            tables = [table[0] for table in cursor.fetchall()]
        elif selected_db == "MSSQL":
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
            tables = [table[0] for table in cursor.fetchall()]
        elif selected_db=="Excel":
            cursor.execute("""SELECT name FROM sqlite_master WHERE type='table';""")
            tables = [table[0] for table in cursor.fetchall()]
        return cursor,tables
    else:
        st.warning(message)
    

def show_data(cursor,selected_table,tables):
    if selected_table in tables:
        cursor.execute(f"SELECT * FROM {selected_table} LIMIT 10;")
        st.code(f'SELECT * FROM {selected_table};',language='sql')
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        st.write(pd.DataFrame(rows, columns=col_names).head())
    return col_names

def create_function(cursor,connection,table_name,output,df):
    query=f'''create table {table_name}({output});'''
    cursor.execute(query)
    values = [tuple(x) for x in df.to_numpy()]
    for value in values:
        try:
            query=f'''INSERT INTO {table_name} VALUES {value};'''
            print(query)
            cursor.execute(query)
        except Exception as e :
            cursor.execute("ROLLBACK")
            print(e)
        connection.commit()
    st.write('table created and inserted the data')

def insert_function(cursor,connection,selected_table,df):
    values = [tuple(x) for x in df.to_numpy()]
    for value in values:
        try:
            query=f'''INSERT INTO {selected_table} VALUES {value};'''
            print(query)
            cursor.execute(query)
        except Exception as e :
            cursor.execute("ROLLBACK")
            print(e)
        connection.commit()
    st.write('inserted the data')

def alter_function(cursor,connection,table_name,output):
    query=f'''alter table {table_name} {output};'''    
    cursor.execute(query)
    connection.commit()



