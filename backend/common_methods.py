import psycopg2 
import progressbar

#Establishing the connection
def establish_connection():
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="root",
        )
        connection.autocommit = True
        return connection
    except (Exception, psycopg2.DatabaseError) as error:
        print("Database connection error :- ",error)
        return ""
    
def progress_bar(len_list):
    widgets = [' [',
         progressbar.Timer(format= 'elapsed time: %(elapsed)s'),
         '] ',
           progressbar.Bar('*'),' (',
           progressbar.ETA(), ') ',
          ]
  
    bar = progressbar.ProgressBar(max_value=len_list+2, 
                              widgets=widgets).start()

    return bar

        