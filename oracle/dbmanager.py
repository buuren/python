import cx_Oracle
import collections

class DatabaseManager(object):
    def __init__(self, connection_string):
        self.__connection_string = connection_string

    def __enter__(self):
        self.__db = cx_Oracle.Connection(self.__connection_string)
        self.__cursor = self.__db.cursor()
        return self

    def __exit__(self, type, value, traceback):
        self.__db.close()

    def query_executor(self, query, logging=False, store_output=False):
        try:
            if logging:
                print 'Executing query: %s' % query
            self.__db.begin()

            #if store_output:
            self.store_execute_output = self.__cursor.execute(query)

            self.cursor_output = self.__cursor.fetchall()
            self.__db.commit()
            return self
        except Exception as ex:
            print "Failed to execute query: %s" % query
            print "Reason:", ex
            exit(1)

    def return_user_objects(self):
        """
        Returns dictionary of database objects within user tablepace
        dictionary format:
        {
            object_type1: [object_name1, object_name2, ... ],
            object_type2: [object_name1, object_name2, ... ],
            ...
        }
        """
        select_sql = """SELECT OBJECT_NAME, OBJECT_TYPE FROM USER_OBJECTS"""

        self.query_executor(select_sql)
        self.dictonary_output = dict()

        for each_sql_output in self.cursor_output:
            if each_sql_output[1] not in self.dictonary_output.keys():
                self.dictonary_output[each_sql_output[1]] = ''

        for each_key in self.dictonary_output.keys():
            values_array = []
            for each_sql_output in self.cursor_output:
                if each_key == each_sql_output[1]:
                    values_array.append(each_sql_output[0])
            self.dictonary_output[each_key] = values_array

    def recursive_database_search(self, string_to_search, skip_tables_list = list, skip_tables_regex = ''):

        print 'searcing string %s in database: %s' % (string_to_search, self.__connection_string)

        select_sql = "SELECT OBJECT_NAME from USER_OBJECTS where OBJECT_TYPE = 'TABLE'"

        if len(skip_tables_list) > 0:
            select_sql = select_sql + ' and OBJECT_NAME not in %s' % str(tuple(skip_tables_list))

        if len(skip_tables_regex) > 0:
            select_sql = select_sql + " and OBJECT_NAME not like '%s'" % ('%' + skip_tables_regex + '%')

        self.query_executor(select_sql)

        for each_sql_output in self.cursor_output:
            each_analyzie_table = each_sql_output[0]
            print 'Parsing table:', each_analyzie_table

            get_columns = """SELECT * FROM %s""" % each_analyzie_table
            self.query_executor(get_columns)

            table_values = [
                [col_name[0],
                    [first_value[0] for first_value in self.query_executor("select %s from %s" % (col_name[0], each_analyzie_table)).cursor_output]
                ]
                for col_name in self.store_execute_output.description
            ]

            for each_table_column_set in table_values:
                for each_table_column_value in each_table_column_set[1]:
                    if string_to_search in str(each_table_column_value):
                        print 'Found match at table: [%s], column: [%s], match: [%s]' % (each_analyzie_table, each_table_column_set[0], each_table_column_value)

if __name__ == "__main__":
    base_connection_string = "user/pass@hostname:port/sid"
    secondary_connection_string = "user/pass@hostname:port/sid"

    def compare_user_objects():
        with DatabaseManager(base_connection_string) as db_instance:
            db_instance.return_user_objects()
            base_results = db_instance.dictonary_output

        with DatabaseManager(secondary_connection_string) as db_instance:
            db_instance.return_user_objects()
            secondary_results = db_instance.dictonary_output

        print 'THE FOLLOWING DATA IS MISSING ON %s' % base_connection_string
        for key in secondary_results.keys():
            if key in base_results.keys():
                for each_value in secondary_results[key]:
                    if not each_value in [each_value_1 for each_value_1 in base_results[key]]:
                        print 'Could not find [Object type: %s][Object name: %s]' % (key, each_value)
            else:

                print 'Need to add: %s : %s' % (key, secondary_results[key])
    compare_user_objects()

    def analyze_tables():
        with DatabaseManager(secondary_connection_string) as db_instance:
            db_instance.recursive_database_search('t02',
                skip_tables_list=['ARCHIVEHISTORY', 'DELETEDROWS', 'DOCMETA', 'DOCUMENTHISTORY', 'DOCUMENTS',
                'IDCCOLL1', 'IDCCOLL2', 'INDEXERSTATE', 'REVISIONS', 'SCTACCESSLOG', 'WORKFLOWHISTORY'],
                skip_tables_regex='$'
            )

    analyze_tables()
