"""A class to provide basic CRUD operations.
It takes in one argument for the __init__ method which is
the table name. The Keyspace and Conact Points are set as
environment variables.
"""

from cassandra.cluster import Cluster
from collections import OrderedDict
import os

class CassandraModules:
    def __init__(self): 
        try:
            self.__keyspace = os.environ['KEYSPACE']
            self.__contact_points =os.environ['CONTACT_POINTS'].split(",")
        except (KeyError) as err:
            print("KEY ERROR: ",err) 
        else:
            self.__cluster = Cluster(self.__contact_points)
            self.__session = self.__cluster.connect(self.__keyspace)
            
    def __del__(self):
        if CassandraModules:
            self.__cluster.shutdown()
    
    def select_table(name):
            """
                Get the column names from the table schema and
                check if table exists. If not then raise an error
            """
            try:
                table_columns = f"SELECT column_name FROM system_schema.columns WHERE keyspace_name='{self.__keyspace}' AND table_name='{self.__table}'"
                resultSet = self.__session.execute(table_columns)
                self.__table = table
                print("Connected") 
                if not resultSet.current_rows:
                    raise NameError(f"Table name: '{self.__table}' not found")
            except NameError as err:
                raise
    
   
    def closeConnection(self):
        self.__cluster.shutdown()

    def __create_query(self):
        table_columns = f"SELECT column_name FROM system_schema.columns WHERE keyspace_name='{self.__keyspace}' AND table_name='{self.__table}'"
        resultSet = self.__session.execute(table_columns)

        """
            Storing the column names in an ordered dictionary to preserve column positions
            when inserting data --> INSERT INTO table (col1, col2, ...) VALUES (?,?, ...)
        """ 
        column_names_dict = OrderedDict()
        for column in resultSet.current_rows:
            column_names_dict[column.column_name] = None

        column_names = ','.join(column_names_dict.keys())
        placeholder = ("?,"*len(column_names_dict))[:-1]

        query = f"INSERT INTO {self.__table} ({column_names}) VALUES({placeholder})"
        return column_names_dict, query

    
    #INSERTING DATA INTO TABLE
    def insert(self, data):
        print("INSERT")
        column_names_dict, query = self.__create_query()
        prepared = self.__session.prepare(query) 
        
        for key, values in data.items():
            if isinstance(key, str):
                key = key.lower()
            column_names_dict[key] = values
        print(column_names_dict)
        try:
            bound = prepared.bind(column_names_dict)
            self.__session.execute(bound)
        except Exception as err:
            print("ERROR INSERTING DATA : ",err)
    
    
    def update(self, data, partition_key):
            what = []
            where = []

            for key, val in data.items():
                if isinstance(val, int):
                    what.append(f"{key} = {val}")
                else:
                    what.append(f"{key} = '{val}'")

            for key, val in partition_key.items():
                if isinstance(val, int):
                    where.append(f"{key} = {val}")
                else:
                    where.append(f"{key} = '{val}'")

            query = f"UPDATE {self.__table} SET {','.join(what)} WHERE {','.join(where)}"
            try:
                self.__session.execute(query)
            except:
                print("ERROR UPDATING VALUES")
