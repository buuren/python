try:
    method = ldap.AUTH_SIMPLE
    ldap_connect = ldap.initialize(server)
    ldap_connect.bind(rootdn, password, method)
except Exception:
    ldap_connect.unbind_s()
    print Exception
    exit("No connection")

class LdapManager():
    def __init__(self, user_name=None, group_name=None, search_results=False, metadata=None,
                metadata_group=None, custom_dn='o=4.se', custom_filter='uid=', skip_error = False):
        self.search_results = search_results
        self.metadata = metadata
        self.metadata_group = metadata_group
        self.custom_dn = custom_dn
        self.skip_error = skip_error
        self.user_name = user_name

    def find_user(self, user_name, is_main=True):
        try:
            self.user_name = user_name
            self.custom_filter = 'uid=%s' % self.user_name
            find_user_name = ldap_connect.search_s(self.custom_dn, ldap.SCOPE_SUBTREE, self.custom_filter)
        except Exception:
            print 'Error occured for -> \nuser: %s; \nfilter: %s; \ndn: %s; ' % (self.user_name, self.custom_filter, self.custom_dn)
            print sys.exc_info()[0]
            exit('find_user')
        else:
            if find_user_name:
                if is_main:
                    for each_atr in find_user_name:
                        for each_tuple in each_atr:
                            if type(each_tuple) is dict:
                                for key, value in sorted(each_tuple.items()):
                                    print '%s: %s' % (key, value[0])
                return find_user_name
            else:
                print 'Error: User: %s is not found.' % self.user_name


    def find_users_groups(self, user_name, is_main=True):
        if self.find_user(user_name, is_main=False):
           #print 'hello world'
            user_groups = []
            try:
                self.custom_filter = '(uniqueMember=uid=%s*)' % self.user_name
                custom_query = ldap_connect.search_s(self.custom_dn, ldap.SCOPE_SUBTREE, self.custom_filter)
            except Exception:
                print Exception
                exit()
            else:
                try:
                    for each_group in custom_query:
                        user_groups.append(each_group[0])
                except KeyError:
                    print "No groups for user:", self.user_name
                    exit("find_users_groups")

                if len(user_groups) != 0:
                    if is_main:
                        print "User %s belongs to:" % self.user_name
                        for each_group in user_groups:
                            print each_group
                    else:
                        return user_groups
                else:
                    print 'User %s does not belong to any group.' % self.user_name


    def find_group(self, group_name, is_main=True):
        try:
            self.group_name = group_name
            find_group_name = ldap_connect.search_s(self.group_name, ldap.SCOPE_BASE)
        except ldap.NO_SUCH_OBJECT:
            print 'Error occured for -> \ngroup name: %s; \ndn: %s; ' % (self.user_name,  self.custom_dn)
            print 'No such group'
        else:
            if is_main:
                for each_entry in find_group_name[0]:
                    if type(each_entry) is dict:
                        for key, value in each_entry.items():
                            print '%s = %s' % (key, value)
                    else:
                        print each_entry
            return find_group_name


    def find_users_in_group(self, group_name):
        if self.find_group(group_name, is_main=False):
            #print 'ok '
            users_in_group = []
            for each_entry in self.find_group(group_name, is_main=False)[0]:
                if type(each_entry) is dict:
                    for key, value in each_entry.items():
                        if key == 'uniqueMember':
                            for each_value in value:
                                users_in_group.append(each_value)

            if len(users_in_group) != 0:
                print 'Found users in group %s:' % self.group_name
                for each_user in users_in_group:
                    print each_user
            else:
                print 'No users in group:', self.group_name


    def find_subgroups(self, group_name):
        self.group_name = group_name
        try:
            find_subgroups = ldap_connect.search_s(self.group_name, ldap.SCOPE_ONELEVEL)
        except ldap.NO_SUCH_OBJECT:
            print 'Error occured for -> \ngroup name: %s; \ndn: %s; ' % (self.user_name,  self.custom_dn)
            print 'No such group'
        else:
            print 'Groups in %s:' % self.group_name
            for each_subgroup in find_subgroups:
                print each_subgroup[0].split(',')[0]


    def find_all_subgroups(self, group_name):
        self.group_name = group_name
        try:
            find_all_subgroups = ldap_connect.search_s(self.group_name, ldap.SCOPE_SUBTREE)
        except ldap.NO_SUCH_OBJECT:
            print 'Error occured for -> \ngroup name: %s; \ndn: %s; ' % (self.user_name,  self.custom_dn)
            print 'No such group'
        else:

            if find_all_subgroups:

                main_dict = {}
                to_delete = []

                for x in find_all_subgroups:
                    fixed_x = str(x[0]).replace(' ', '')
                    his = [str(group[0]).replace(' ', '') for group in ldap_connect.search_s(x[0], ldap.SCOPE_ONELEVEL)]
                    main_dict[fixed_x] = his

                lowest = min(len(x.split(',')) for x in main_dict)
                maxest = max(len(x.split(',')) for x in main_dict)

                for i in reversed(range(lowest, maxest+1)):
                    for indexer in range(len(main_dict)):
                        try:
                            each_z = main_dict.keys()[indexer]
                            if len(each_z.split(',')) == i:
                                for p, v in main_dict.items():
                                    if each_z in v:
                                        if len(main_dict[p]) != 0:
                                            v[v.index(each_z)] = [each_z, [main_dict[each_z]]]
                                        to_delete.append(each_z)
                        except IndexError:
                            pass

                for each_to_delete in to_delete:
                    main_dict.pop(each_to_delete, None)

                dict_with_indexes = OrderedDict()
                def traverse(o, tree_types=(list)):
                    i = 0
                    if isinstance(o, tree_types):
                        for value in o:
                            i = i + 1
                            if len(value) != 0:
                                if isinstance(value, str):
                                    dict_with_indexes[value] = i
                                for subvalue in traverse(value):
                                    i = i + 1
                                    if dict_with_indexes.has_key(subvalue):
                                        new_i = dict_with_indexes[subvalue] + 1
                                        dict_with_indexes[subvalue] = new_i
                                    yield subvalue
                    else:
                        yield o

                list(traverse(main_dict.values()[0]))
                print self.group_name
                for k, v in dict_with_indexes.items():
                    print '%s%s -> (%s)' % ((' ' * v), k.split(',')[0], k)


    def add_user_to_group(self, user_name, group_name):
        if self.find_group(group_name, is_main=False):
            if self.find_user(user_name, is_main=False):

                self.user_name = user_name
                self.group_name = group_name

                old_metadata = {'uniqueMember': ''}
                new_metadata = {'uniqueMember': 'uid=%s, ou=people, o=123.se' % self.user_name}

                ldif = modlist.modifyModlist(old_metadata, new_metadata)

                try:
                    if self.find_users_groups(self.user_name, is_main=False):
                        cc = 1
                        print 'Current user %s groups:' % (self.user_name)
                        for each_group in (self.find_users_groups(self.user_name, is_main=False)):
                            print "%s) %s" % (cc, each_group)
                            cc += 1

                    print '\nAdding %s to group %s...\n' % (self.user_name, self.group_name)

                    ldap_connect.modify_s(self.group_name, ldif)

                    print 'Success. New user groups:'

                    if self.find_users_groups(self.user_name, is_main=False):
                        cc = 1
                        print 'User: %s belongs to:' % (self.user_name)
                        for each_group in (self.find_users_groups(self.user_name, is_main=False)):
                            print "%s) %s" % (cc, each_group)
                            cc += 1

                except ldap.TYPE_OR_VALUE_EXISTS:
                        print 'Error - unable to add user %s to group %s. \nReason: User already exists in this group' % (self.user_name, self.group_name)


LdapManager(custom_dn='ou=people,o=123.se').find_user(user_name='55')
print '----------------------------------------------'
LdapManager().find_users_groups(user_name='1')
print '----------------------------------------------'
LdapManager().find_group(group_name='2=AaaaaBB_r,ou=55,ou=1a,o=sd.3')
#print '----------------------------------------------'
LdapManager().find_users_in_group(group_name='5123e')
print '----------------------------------------------'
LdapManager().find_subgroups(group_name='3.se')
print '----------------------------------------------'
LdapManager().find_all_subgroups(group_name='5551z.se')
print '----------------------------------------------'
LdapManager().add_user_to_group(user_name='123', group_name='o3ken.e')


ldap_connect.unbind_s()

time.sleep(0.1)
exit('done')
