# A class to provide basic CRUD operations.
# It takes in one argument for the __init__ method which is
# the table name. The Keyspace and Conact Points are set as
# environment variables.

import os
from collections import OrderedDict

from cassandra.cluster import Cluster, ExecutionProfile
from cassandra.policies import DCAwareRoundRobinPolicy
from cassandra.query import dict_factory, named_tuple_factory


class CassandraModules:
    def __init__(self, TESTING=None):
        self.table = None
        profiles = None
        try:
            # Set the environment variables within your virtual environment
            # having the following names:
            # For production:
            #               KEYSPACE='key1'
            #               CONTACT_POINTS='127.0.1'
            #
            # For testing:
            #               TEST_KEYSPACE='key2'
            #               TEST_CONTACT_POINTS='127.0.1'
            # Activate the environment variable based on weather TESTING is
            # True or False
            if TESTING is None:
                self._keyspace = os.environ['KEYSPACE']
                self._contact_points = os.environ['CONTACT_POINTS'].split(",")
            else:
                self._keyspace = os.environ['TEST_KEYSPACE']
                self._contact_points = os.environ['TEST_CONTACT_POINTS'].split(",")
        except (KeyError) as err:
            print("KEY ERROR: ", err)
        else:
            policy = ExecutionProfile(load_balancing_policy=DCAwareRoundRobinPolicy())
            self._cluster = Cluster(self._contact_points,
                                    execution_profiles=profiles
                                    )
            self._session = self._cluster.connect(self._keyspace)

    def __call__(self, table):
        try:
            table_columns = f"SELECT column_name FROM system_schema.columns WHERE keyspace_name='{self._keyspace}' AND table_name='{table}'"
            resultSet = self._session.execute(table_columns)

            if not resultSet.current_rows:
                raise NameError(f"Table name: '{self.table}' not found")

            self.table = table
        except NameError as err:
            raise

        return 

    def closeConnection(self):
        self._cluster.shutdown()

    def _create_query(self):
        table_columns = f"SELECT column_name FROM system_schema.columns WHERE keyspace_name='{self._keyspace}' AND table_name='{self.table}'"
        self._session.row_factory = named_tuple_factory
        resultSet = self._session.execute(table_columns)

        """Storing the column names in an ordered dictionary to preserve column positions
        when inserting data --> INSERT INTO table (col1, col2, ...) VALUES (?, ?, ...)
        """
        column_names_dict = OrderedDict()
        for column in resultSet.current_rows:
            print(type(column))
            column_names_dict[column.column_name] = None

        # column_names :: col1, col2, col3, ...
        # placeholder  ::   ?,    ?,    ?,  ...
        column_names = ','.join(column_names_dict.keys())
        placeholder = ("?,"*len(column_names_dict))[:-1]

        # final query to be used for insertion
        query = f"INSERT INTO {self.table} ({column_names}) VALUES({placeholder})"
        return column_names_dict, query

    # INSERTING DATA INTO TABLE
    def insert(self, data):
        column_names_dict, query = self._create_query()
        prepared = self._session.prepare(query) 

        for key, values in data.items():
            if isinstance(key, str):
                key = key.lower()
            column_names_dict[key] = values
        try:
            bound = prepared.bind(column_names_dict)
            self._session.execute(bound)
        except Exception as err:
            print("ERROR INSERTING DATA : ",err)

    def execute_query(self, query):
        """Execute the given query"""
        resultSet = None
        self._session.row_factory = dict_factory
        try:
            resultSet = self._session.execute(query)
        except:
            print("Error executing query ", query)

        return resultSet

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

            query = f"UPDATE {self.table} SET {','.join(what)} WHERE {','.join(where)}"
            try:
                self._session.execute(query)
            except:
                print("ERROR UPDATING VALUES")
