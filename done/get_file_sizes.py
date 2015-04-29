#!/path/to/your/python
import os
import sys
import datetime

if len(sys.argv) >= 2:
    path = sys.argv[1]
    print path

    if os.path.isdir(path):
        total_size = []
        folder_sizes = []
        dict_to_sort = {}

        d = datetime.datetime.now() - datetime.timedelta(hours=1)
        current_date_time = d.strftime("%Y%m%d%H%M%S")
        log_name = 'sizes_%s.txt' % current_date_time

        for dirpath, dirname, filename in os.walk(path):

            for each_filename in os.listdir(dirpath):
                each_filename = os.path.join(dirpath, each_filename)

                if os.path.isfile(each_filename):
                    file_size = (os.path.getsize(each_filename) / 1024.0) / 1024.0
                    file_size_rounded = '%.2f' % round(file_size, 2)
                    total_size.append(float(file_size_rounded))

            folder_size = sum(total_size)

            if folder_size == 0:
                pass
            else:
                folder_sizes.append(folder_size)
                if len(folder_sizes) == 1:
                    pass
                else:
                    folder_size = folder_sizes[len(folder_sizes) - 1] - folder_sizes[len(folder_sizes) - 2]

                dict_to_sort[dirpath] = folder_size

        total_path_size =  sum(total_size)

        with open(log_name, "ab") as my_log_file:
            for dict_key, dict_value in sorted(dict_to_sort.iteritems(), key=lambda (k,v): (v,k)):
                my_log_file.write("\n%s MB\t %s" % (dict_to_sort[dict_key], dict_key))

            my_log_file.write("\n\nTotal size of %s: %s MB\n\n" % (path, total_path_size))
            my_log_file.close()
    else:
        print "%s is not a directory" % sys.argv[1]

else:
    print 'Missing argument: full path to directory'
    print 'Usage: ./%s /path/to/dir' % sys.argv[0]
    sys.exit(0)
