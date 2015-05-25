import cx_Oracle
import datetime
import os


class DatabaseManager(object):
    def __init__(self, connection_string, tns=False):
        self.__tns_connection = tns

        if self.__tns_connection:
            db_user = connection_string.split('/')[0]
            db_pass = connection_string.split('/')[1].split('@')[0]
            db_ip = connection_string.split('@')[1].split(':')[0]
            db_port = connection_string.split(':')[1].split('/')[0]
            db_sid = connection_string.split(':')[1].split('/')[1]
            db_tns = cx_Oracle.makedsn(db_ip, db_port, db_sid)
            db_con = cx_Oracle.connect(db_user, db_pass, db_tns)
            self.__connection_string = db_con

        else:
            self.__connection_string = connection_string

        self.start_time = datetime.datetime.now()
        self.query_count = 0

    def __enter__(self):
        if self.__tns_connection:
            self.__db = self.__connection_string
        else:
            self.__db = cx_Oracle.Connection(self.__connection_string)

        self.__cursor = self.__db.cursor()
        return self

    def __exit__(self, type, value, traceback):
        done_time = datetime.datetime.now() - self.start_time

        print 'DatabaseManager: DONE'
        print 'Run %s queries in %s seconds [1/%s q/Msec]' % (self.query_count,
                                                                  done_time.total_seconds(),
                                                                  (done_time.total_seconds() * 100.0) / self.query_count
        )
        self.__db.close()

    def query_executor(self, query, logging=False, store_output=False):

        try:
            if logging:
                print 'Executing query: %s' % query
            self.__db.begin()
            self.store_execute_output = self.__cursor.execute(query)
            self.query_count += 1
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

    def store_cid_revision(self, revision_list):
        dictonary_output = dict()

        for each_cid in revision_list:
            select_sql = "select max(drevlabel) from revisions where DDOCNAME = '%s'" % each_cid
            self.query_executor(select_sql)

            for each_sql_output in self.cursor_output:
                dictonary_output[each_cid] = each_sql_output[0]

        return dictonary_output

if __name__ == "__main__":
    base_connection_string = "user/pass@db_hostname:port/SID"

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

    def analyze_tables():
        with DatabaseManager(secondary_connection_string) as db_instance:
            db_instance.recursive_database_search('t02',
                skip_tables_list=['ARCHIVEHISTORY', 'DELETEDROWS', 'DOCMETA', 'DOCUMENTHISTORY', 'DOCUMENTS',
                'IDCCOLL1', 'IDCCOLL2', 'INDEXERSTATE', 'REVISIONS', 'SCTACCESSLOG', 'WORKFLOWHISTORY'],
                skip_tables_regex='$'
            )

    def compare_cid_revs(revision_list):
        with DatabaseManager(secondary_connection_string) as db_instance:
            dev_revisions = db_instance.store_cid_revision(revision_list)

        with DatabaseManager(base_connection_string) as db_instance:
            test_revisions = db_instance.store_cid_revision(revision_list)

        for each_dev_cid, cid_dev_revision in dev_revisions.iteritems():
            test_cid_revision = test_revisions[each_dev_cid]
            if cid_dev_revision != test_cid_revision:
                print 'The following item revision does not match: %s' % each_dev_cid
                print 'In source: %s' % cid_dev_revision
                print 'In target: %s' % test_cid_revision

    with open('/home/user/list.txt') as file_content:
        revisions_from_txt = file_content.read().splitlines()

    compare_cid_revs(revisions_from_txt)
