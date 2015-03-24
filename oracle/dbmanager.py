import cx_Oracle

class DatabaseManager(object):
    def __init__(self, connection_string):
        self.__connection_string = connection_string

    def __enter__(self):
        self.__db = cx_Oracle.Connection(self.__connection_string)
        self.__cursor = self.__db.cursor()
        return self

    def __exit__(self, type, value, traceback):
        self.__db.close()

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

        self.__db.begin()
        self.__cursor.execute(select_sql)
        self.cursor_output = self.__cursor.fetchall()

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

if __name__ == "__main__":
    base_connection_string = "user/pass@hostname:port/sid"
    secondary_connection_string = "user/pass@hostname:port/sid"

    with DatabaseManager(base_connection_string) as db_instance:
        db_instance.return_user_objects()
        base_results = db_instance.dictonary_output

    with DatabaseManager(secondary_connection_string) as db_instance:
        db_instance.return_user_objects()
        secondary_results = db_instance.dictonary_output

    for key in secondary_results.keys():
        if key in base_results.keys():
            for each_value in secondary_results[key]:
                if not each_value in [each_value_1 for each_value_1 in base_results[key]]:
                    print 'Could not find [Object type: %s][Object name: %s]' % (key, each_value)
        else:

            print 'Need to add: %s : %s' % (key, secondary_results[key])

