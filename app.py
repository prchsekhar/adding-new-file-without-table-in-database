import streamlit as st
import pandas as pd
from config import *
import base64
from PIL import Image

im = Image.open(r'D:\Raja\POC_1\3IINFOLTD.NS_BIG.png')
st.set_page_config(page_title='3i future tech', layout='centered', page_icon =im , initial_sidebar_state = 'auto')

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)
# set_background(r'D:\Raja\POC_1\back3.jpg')

Image = Image.open(r'D:\Raja\POC_1\3i-logo-black-bkg-1.png')
st.image(Image)

column_type_list=['bigint','binary','bit','char','date','datetime','datetime2','datetimeoffset','decimal','float','geography','geometry','hierarchyid','image','int','money','nchar','ntext','numeric','nvarchar','real','smalldatetime','smallint','smallmoney','sql_variant','sysname','text','time','timestamp','tinyint','uniqueidentifier','varbinary','varchar','xml']

input_values={}

# Main function to run the Streamlit app
def main():
    # Create a dictionary to map the database options to their corresponding connection functions
    db_options = {
        "MySQL": connect_mysql,
        "PostgreSQL": connect_postgres,
        "MSSQL": connect_mssql,
    }
       
    # Create the Streamlit app layout
    st.title(":blue[Welcome to Data Engineer's world]:sunglasses:")
    selected_db = st.selectbox(":red[Select a database]", ["Select a database","MySQL", "PostgreSQL", "MSSQL"])
    if selected_db in ["MySQL", "PostgreSQL", "MSSQL"]:
        host = st.text_input(":red[Host name]")
        port = st.text_input(":red[Port number]")
        db_name = st.text_input(":red[Database name]")
        username = st.text_input(":red[Username]")
        password = st.text_input(":red[Password]", type="password")
        if host=='' or port=='' or db_name=='' or username=='' or password=='' :
            st.write(":red[Pleace fill the details]")
        else:
            connect_func = db_options[selected_db]
            connection, message = connect_func(host, port, db_name, username, password)
            cursor,tables = show_tables(connection,message,selected_db)
            selected_table = st.selectbox(":red[Select a table]",tables+['select upload your own table'])  
            if selected_table in tables:
                show_data(cursor,selected_table,tables)
                upload_file=st.file_uploader("upload")
                try:
                    df=pd.read_csv(upload_file)
                except:
                    df=pd.read_excel(upload_file)
                st.write(df.head())
                insert,edit=st.columns(2)
                with insert:
                    insert = st.button("upload the new data")
                    if insert:
                        insert_function(cursor,connection,selected_table,df)
                with edit:
                    edit= st.button("add new columns")
                    if edit:
                        n = st.number_input("Enter the number of columns to create:", min_value=1, step=1)
                        col1,col2=st.columns(2)
                        for i in range(n):
                            with col1:
                                input_values[f"column_name_{i+1}"] =st.text_input(f"Input for column {i+1} ")
                            with col2:
                                input_values[f"column_type_{i+1}"]=st.selectbox(f"Input for column  type {i+1} ",['select column type']+column_type_list)
                        output = ", ".join([f"ADD COLUMN {input_values[f'column_name_{i}']} {input_values[f'column_type_{i}']}" for i in range(1, len(input_values)//2 + 1)])
                        alter=st.button('alter the table')
                        if alter:
                            alter_function(cursor,connection,selected_table,output)
            else:
                upload_file=st.file_uploader("upload")
                try:
                    df=pd.read_csv(upload_file)
                except:
                    df=pd.read_excel(upload_file)                
                st.write(df.head())
                table_name=st.text_input("table name")
                col1,col2=st.columns(2)
                for i in range(len(df.columns)):
                    with col1:
                        input_values[f"column_name_{i+1}"] = st.text_input(f"Input for column {i+1}")
                    with col2:
                        input_values[f"column_type_{i+1}"] = st.selectbox(f"Input for column type {i+1}",['select column type']+column_type_list)
                output = ", ".join([f"{input_values[f'column_name_{i}']} {input_values[f'column_type_{i}']}" for i in range(1, len(input_values)//2 + 1)])
                upload=st.button('upload')
                if upload:
                    create_function(cursor,connection,table_name,output,df)
            
    else:
        st.write(':red[select database]')
                

if __name__ == "__main__":
    main()


