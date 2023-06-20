#import psycopg2.extras
import psycopg2
import common_methods
from api import reliefweb_api_calls as relif_web
from api import gdacs_api_calls as gdacs_api


def insertDataToDb(conn):
    with conn.cursor() as cursor: 
        data_gdacs = gdacs_api()
        data_reliefweb = relif_web()

        data = data_gdacs + data_reliefweb
        print(data)
        
        try:
            for disaster in data:
                loop_dis_id=disaster['dis_id']
                
                # Check if the record already exists in the database
                select_query = 'SELECT COUNT(*) FROM disaster_table WHERE disaster_id = %s'
                cursor.execute(select_query, (loop_dis_id,))
                record_count = cursor.fetchone()[0]

                if record_count == 0:
                    counter=0
                    # Insert the data into the PostgreSQL table
                    insert_query = 'INSERT INTO disaster_table (disaster_id, dis_name, dis_source_url, dis_country, disaster_type, dis_date, dis_status, dis_category) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
                    data_values = (loop_dis_id, disaster['dis_name'], disaster['dis_source_url'], disaster['dis_country'], disaster['dis_type'], disaster['dis_date'], disaster['dis_status'], disaster['dis_category'])
                    cursor.execute(insert_query, data_values)
                    insert_query_clickcount = 'INSERT INTO link_click_count (disaster_id, click_count) values(%s, %s)'
                    data_values_clickcount = (loop_dis_id,counter)
                    cursor.execute(insert_query_clickcount,data_values_clickcount)
                    print(f"Data inserted for disaster_id: {loop_dis_id}")
                    print("Data inserted into PostgreSQL successfully.")
                else:
                    print(f"Record already exists for disaster_id: {loop_dis_id}")
            
                
                conn.commit()
        except Exception as error:
            print(data)
            print(error)
        finally:
           # Commit the changes and close the cursor and connection
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()


#Calling the method
connection=common_methods.establish_connection()
if(connection == ""):
    print("Error in Connecting to database")
else:
    insertDataToDb(connection)