#!/usr/bin/python2.7
# coding:utf-8

import time
import os
import sys
import codecs
import json
import sqlite3
import subprocess


class Database(object):
    def __init__(self, db_name):
        self.exam_out_split = u"{{::}}"
        self.exam_inner_split = u"{{##}}"
        self.connection = sqlite3.connect(db_name)
        command = u"chmod 755 %s" % db_name
        subprocess.call(command, shell=True)
        #create table and index
        self.cursor = self.connection.cursor()
        create_table_stmt = u"""
            CREATE TABLE IF NOT EXISTS pyhelp(
              id INTEGER AUTO_INCREMENT,
              category TEXT NOT NULL ,
              command TEXT NOT NULL ,
              brief TEXT NOT NULL ,
              detail TEXT,
              exam TEXT,
              PRIMARY KEY (id)
              UNIQUE (command, category)
            );
        """
        create_index_stmt = u"""
            CREATE INDEX IF NOT EXISTS idx_cmd ON pyhelp(command);
        """
        self.cursor.execute(create_table_stmt)
        self.cursor.execute(create_index_stmt)
        self.connection.commit()

    def __encode_exam(self, exam_list):
        if not exam_list:
            return u""
        result = []
        for elem in exam_list:
            exam = elem[0] + self.exam_inner_split + elem[1]
            result.append(exam)
        exam_str = self.exam_out_split.join(result)
        return exam_str

    def __decode_exam(self, exam_str):
        if not exam_str:
            return []
        result = exam_str.split(self.exam_out_split)
        exam_list = []
        for elem in result:
            exam_elem = elem.split(self.exam_inner_split)
            exam_list.append([exam_elem[0], exam_elem[1]])
        return exam_list

    def insert(self, category, command, brief, detail=u"", exam=[]):
        insert_stmt = u"""
                        INSERT INTO pyhelp (category, command, brief, detail, exam)
                        VALUES (?, ?, ?, ?, ?);
                        """
        exam = self.__encode_exam(exam)
        record = (category, command, brief, detail, exam)
        self.cursor.execute(insert_stmt, record)
        self.connection.commit()
        return self.cursor.rowcount

    def query(self, command=u"", category=u""):
        if not category and not command:
            query_stmt = u"""
                 SELECT category, command, brief, detail, exam FROM pyhelp
            """
            record = ()

        elif category and command:
            query_stmt = u"""
                SELECT category, command, brief, detail, exam FROM pyhelp WHERE command=? AND category=?;
            """
            record = (command, category)
        elif command:
            query_stmt = u"""
                SELECT category, command, brief, detail, exam FROM pyhelp WHERE command=?;
            """
            record = (command, )
        elif category:
            query_stmt = u"""
                SELECT category, command, brief, detail, exam FROM pyhelp WHERE category=?;
            """
            record = (category, )

        ret = self.cursor.execute(query_stmt, record)
        result = []
        for row in ret:
            exam_list = self.__decode_exam(row[4])
            result.append({u"category": row[0], u"command": row[1], u"brief": row[2], u"detail": row[3], u"exam": exam_list})
        return result

    def delete(self, command, category=u""):
        if category and command:
            delete_stmt = u"""
              DELETE  FROM pyhelp WHERE command=? AND category=?;
            """
            record = (command, category)
        elif command:
            delete_stmt = u"""
              DELETE  FROM pyhelp WHERE command=?;
            """
            record = (command, )
        else:
            return
        self.cursor.execute(delete_stmt, record)
        self.connection.commit()
        return self.cursor.rowcount

    def close(self):
        self.connection.close()


class PyHelp(object):
    def __init__(self):
        with open(u"/usr/bin/ph_config.ini", u"r") as f:
            self.home_dir = f.readline()
            self.home_dir = self.home_dir.strip()
            if self.home_dir.endswith(u"/"):
                self.home_dir = self.home_dir[:-1]
        self.data_dir = self.home_dir + os.sep + u"pyhelp"
        self.database = Database(self.home_dir + os.sep + u"pyhelp.db")

    def __find_avail_filename(self):
        count = 1
        base_name = self.data_dir + os.sep + unicode(time.strftime(u"%Y-%m-%d", time.localtime(time.time())))
        filename = base_name + unicode(count) + u".json"
        #找到不冲突的文件
        while os.path.exists(filename):
            count += 1
            filename = base_name + unicode(count) + u".json"
        return filename

    def __create_file(self, filename):
        create_command = u"touch %s" % filename
        chmod_command = u"chmod 755 %s" % filename
        edit_command = u"vim %s" % filename
        commands = [create_command, chmod_command, edit_command]
        for command in commands:
            subprocess.call(command, shell=True)

    @staticmethod
    def help():
        print u"""
            ph.py是一款帮助您记住日常命令的工具。我们经常会反复的查找资料看一个命令如何使用，ph.py就是帮助您解决这方面的困扰.
            说明：
            ①：第一次使用该软件，请将ph.py文件拷贝到/usr/bin/目录下，并设置文件权限为755
            ②：中括号中的文件表示任选输入。
            ③：每个命令有如下相关信息：
            1：category：该命令所属于的范围，比如linux命令，或者是git命令等。
            2：command: 命令名称。
            3：brief：命令的简要说明（在默认情况下只显示命令的简要说明信息）。
            4：detail：命令的详细说明。
            5: exam: 考查内容。以数组的形式，每个数组元素代表一个测试单元，测试单元的第一项表示：question，第二项表示: answer

            用法：
            1:插入命令：在终端输入ph.py -i [需要记录的命令的数量]。
              然后会打开相应的编辑文件，您只要在文件中填入相关的信息即可。-i是insert的缩写。

            2:刷新文件：在终端输入ph.py -c。该命令会检查pyhelp文件夹下的所有文件，
              并将其数据导入数据库中，并删除文件。-c 是clean的缩写。

            3:编辑命令: 在终端输入ph.py -e filename [-category category_name]。
              该命令将重新编辑记录的命令。-e 是edit的缩写。

            4:删除命令: 在终端输入ph.py -d filename [-category category_name]。
              该命令将删除制定的文件。-d是delete的缩写。

            5:导出到文件: 在终端输入ph.py -o [filename]。该命令会将数据库中的数据导出到文件中。
              注意：如果加上filename，则会导出到指定文件中，否则导出到随机生成的文件中.-o是output的缩写。

            6:查看命令: 在终端输入ph.py command [-category category_name] [-detail]。该命令会显示相关命令的信息
              添加-detail参数表示是否详细显示命令。

            7:测试命令: 在终端输入ph.py -t category。该命令会显示category下的所有命令的测试内容，用户根据提示信息，输入相应的命令，直到输入全部的命令为止。
              如果你不知道答案，输入tell me会提示你答案。如果你想退出，输入i quit

            8：寻求帮助: 在终端中输入ph.py -h，会显示详细的帮助信息, -h 是help的缩写。
        """

    def __strip_blank(self, data):
        return u"".join(data.split(u" "))

    def exam(self, category):
        result_list = self.database.query(command=u"", category=category)
        self.database.close()
        subprocess.call(u"clear", shell=True)
        index = 0
        while result_list:
            result = result_list[index]
            if not result[u"exam"]:
                print result[u"brief"]
                input_command = raw_input(u":")
                input_command = self.__strip_blank(input_command)
                result_command = result[u"command"]
                result_command = self.__strip_blank(result_command)
                if input_command == result_command:
                    del result_list[index]
            else:
                exam_index = 0
                exam_list = result[u"exam"]
                while exam_list:
                    exam = exam_list[exam_index]
                    print exam[0]
                    input_command = raw_input(u":")
                    input_command = self.__strip_blank(input_command)
                    result_command = exam[1]
                    result_command = self.__strip_blank(result_command)
                    if input_command == u"iquit":
                        return
                    if input_command == u"tellme":
                        print exam[1]
                    elif input_command == result_command:
                        del exam_list[exam_index]
                    if not exam_list:
                        del result_list[index]
                        break
                    exam_index = (exam_index + 1) % len(exam_list)
            subprocess.call(u"clear", shell=True)
            if not result_list:
                break
            index = (index + 1) % len(result_list)

    def query(self, command=u"", category=u"", detail_flag=False):
        if not command and not category:
            detail_flag = True
        result_list = self.database.query(command, category)
        for result in result_list:
            if not detail_flag:
                if category:
                    print result[u"command"] + u"\t" + result[u"brief"]
                    print u"\n"
                else:
                    print result[u"brief"]
                    print u"\n"
                for elem in result[u"exam"]:
                    print elem[0]
                    print elem[1]
                    print u"==="
                print u"\n"
            else:
                print u"category: " + result[u"category"]
                #print u"\n"
                print u"command: " + result[u"command"]
                #print u"\n"
                print u"brief: " + result[u"brief"]
                #print u"\n"
                print u"detail: " + result[u"detail"]

                for elem in result[u"exam"]:
                    print elem[0]
                    print elem[1]
                    print u"==="

                print u"\n"
                #print u"\n"
        self.database.close()

    def edit(self, command, category=u""):
        result = self.database.query(command, category)

        filename = self.__find_avail_filename()
        with codecs.open(filename, u"w", encoding=u"utf-8") as outfile:
            json.dump(result, outfile, ensure_ascii=False, indent=4)
        self.database.delete(command=command, category=category)
        self.database.close()

        self.__create_file(filename)

    def delete(self, command, category=u""):
        self.database.delete(command=command, category=category)
        self.database.close()

    def output(self, filename=u"", category=u""):
        if filename:
            if os.path.exists(filename):
                print u"该文件已经存在，请输入一个新的文件名"
        else:
            filename = self.__find_avail_filename()
            print u"随机生成文件名 %s" % filename

        result = self.database.query(command=u"", category=category)

        with codecs.open(filename, u"w", encoding=u"utf-8") as outfile:
            json.dump(result, outfile, ensure_ascii=False, indent=4)
        self.database.close()

    def create_data_file(self, number):
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)

        json_data = {u"category": u"", u"command": u"", u"brief": u"", u"detail": u"", u"exam": []}
        file_content = []
        for i in xrange(number):
            file_content.append(json_data)

        filename = self.__find_avail_filename()
        with codecs.open(filename, u"w", u"utf-8") as outfile:
            json.dump(file_content, outfile, ensure_ascii=False, indent=4)

        self.__create_file(filename)

    def clean_dir(self):
        files = os.listdir(self.data_dir)
        files = [self.data_dir + os.sep + filename for filename in files]
        file_list = [data_file for data_file in files if os.path.isfile(data_file)]

        for filename in file_list:
            with codecs.open(filename, u"r", u"utf-8") as infile:
                try:
                    json_data = json.load(infile)
                except Exception, e:
                    print e
                    return
                for elem in json_data:
                    try:
                        command = elem[u"command"].split(u" ")
                        elem[u"command"] = u" ".join([n for n in command if n])

                        category = elem[u"category"].split(u" ")
                        elem[u"category"] = u" ".join([n for n in category if n])

                        self.database.insert(elem[u"category"], elem[u"command"], elem[u"brief"], elem[u"detail"], elem[u"exam"])
                    except Exception, e:
                        print e
            os.remove(filename)
        self.database.close()


def parse_args(args):
    category = []
    command = []

    if u"-category" in args:
        index = args.index(u"-category")
        category_args = args[index + 1:]
        args = args[:index]
        for elem in category_args:
            category.append(elem)
        category = u" ".join(category)
    else:
        category = u""

    for elem in args:
        command.append(elem)
    command = u" ".join(command)

    return command, category


def main():
    pyhelp = PyHelp()
    args = sys.argv[1:]

    if len(args) == 0:
        pyhelp.query()
    elif args[0] == u"-h":
        pyhelp.help()

    elif args[0] == u"-i":
        if len(args) == 1:
            pyhelp.create_data_file(1)
        else:
            try:
                number = int(args[1])
            except Exception:
                print u"请输入数字"
                return
            pyhelp.create_data_file(number)
    elif args[0] == u"-c":
        pyhelp.clean_dir()

    elif args[0] == u"-e":
        command, category = parse_args(args[1:])
        pyhelp.edit(command=command, category=category)

    elif args[0] == u"-d":
        command, category = parse_args(args[1:])
        pyhelp.delete(command=command, category=category)

    elif args[0] == u"-o":
        filename, category = parse_args(args[1:])
        pyhelp.output(filename=filename, category=category)

    elif args[0] == u"-t":
        category, empty = parse_args(args[1:])
        pyhelp.exam(category)

    else:
        command, category = parse_args(args)
        pyhelp.query(command=command, category=category)


if __name__ == u"__main__":
    main()
