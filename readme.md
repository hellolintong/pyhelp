#  ph.py是一款帮助您解决在linux下反复记忆命令的软件。

ph.py是一款帮助您记住日常命令的工具。我们经常会反复的查找资料看一个命令如何使用，ph.py就是帮助您解决这方面的困扰.<br>

##   说明：
①：第一次使用该软件，请将ph.py文件拷贝到/usr/bin/目录下，并设置文件权限为755
②：中括号中的文件表示可选输入。
③：每个命令有如下相关信息：
1：category：该命令所属于的范围，比如linux命令，或者是git命令等。
2：command: 命令名称。
3：brief：命令的简要说明（在默认情况下只显示命令的简要说明信息）。
4：detail：命令的详细说明。

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

7：寻求帮助: 在终端中输入ph.py -h，会显示详细的帮助信息, -h 是help的缩写。
