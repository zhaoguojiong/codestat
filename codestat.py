# -*- coding: utf-8 -*-

__author__ = "Jason Zhao"

import os
import sys
import logging
import datetime

# 获得logger实例
logger = logging.getLogger()
# 设置日志格式
formatter = logging.Formatter("%(levelname)s %(asctime)s: %(message)s", "%Y-%m-%d %H:%M:%S")
# 设置文件日志处理器
file_handler = logging.FileHandler("codestat.log")
file_handler.setFormatter(formatter)
# 设置控制台日志处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
# 为logger添加日志处理器（同时console输出和文件输出）
logger.addHandler(file_handler)
logger.addHandler(console_handler)
# 设置日志级别
logger.setLevel(logging.INFO)

# git代码库的根目录
git_root = os.path.join(".", "git")
# output文件的根目录
output_root = os.path.join(".", "output")

# 要处理的git项目清单，dict结构，key为group名称，value为项目名称
git_proj = {
	"xueledata": [
		'treasury',
		'tracking-data-monitor',
		'testkit',
		'dataservice-teach',
		'question-data',
		'dataservice-competition',
		'dataservice-work',
		'dataservice-cwork',
		'dataservice-misc',
		'dataservice-login',
		'dataservice-tfb',
		'dataservice-common',
		'dataservice-exam',
		'content-analyzer',
		'XETL',
		'excercise',
		'kpdiag-stream',
		'act-stream',
		'XStreamCompute',
		'dataservice-kpdiag',
		'exam-flatten',
		'kpdiag-cache',
		'exam-stream',
		'recommend-data',
		'x-storm-kafka',
		'bigdata-xudf',
		'kpdiag-algorithm-kit',
		'xa-server',
		'kpdiag-stat-stream',
		'recommend',
		'xa-sdk-java',
		'log2json',
		'content-extract',
		'dataservice-teach-study',
		'dataservice-interactions',
		'x-zuul',
		'x-eureka',
		'dataservice-cloudteach',
		'KnowledgeGraph',
		'dataservice-users',
		'dataservice-orgs',
		'x-log-monitor',
		'dataservice-questions',
		'dataservice-clouddisk',
		'XAlert',
		'x-mongo-hadoop',
		'dataservice-actions',
		'dataservice-resources',
		'XScheduler',
		'XFlume',
		'question-sim'
	],
	"xueleapp": [
		'classroom',
		'smartclass-web-autotest',
		'smartclass-api',
		'py-convert-manager',
		'ppt-converter',
		'call-convert-machine-mfc'
	]
}

# 统计final lines的文件扩展名
# 每增加一个新的ext，需要：
# 1. print_final_lines_stat_oneline()中，增加一个"str(cols[xxx]).rjust(EXT_COL_WIDTH)"
code_file_ext = [
	# Java项目
	".java", 
	# 仓库项目
	".sh", ".sql", ".job", 
	# 前端项目
	".htm", ".html", ".css", ".less", ".js", ".ts", ".vue", 
	# Python项目
	".py", 
	#C/C++项目
	".c", ".cpp", ".h", 
	# Scala项目
	".scala", 
	# 配置及其它文件
	".properties", ".md", ".xml", ".yml", ".bat", ".json"]

# 统计final lines时要跳过的文件扩展名
skipped_file_ext = [
	# IDEA项目文件
	".iml", 
	# VC项目文件
	".vcxproj", 
	# 备份文件
	".bak", 
	# 二进制文件
	".jar", ".zip", ".gz", ".7z", ".tar", ".war", ".class", ".exe", ".dat",
	".png", ".gif", ".jpg", ".bmp", ".ico", ".cur", ".mp3", ".wav", ".m4a", ".flac", ".wma", ".wmv", ".mp4", ".flv",
	".otf", ".eot", ".ttf", ".woff", ".swf", ".crc", ".psd", ".ogg",
	".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".pages", ".numbers", ".key", ".vsd",
	# 其它数据文件
	".out", ".txt", ".log", ".dic", ".csv"]

# 统计final lines时要跳过的目录或文件
skipped_path = [
	# git目录
	".git", 
	# svn目录
	".svn", 	
	# IDEA目录
	".idea", 
	# Mac
	".DS_Store",
	# Java编译后输出
	"target"]

# 特殊author email的映射，dict结构，key为不规范的email，value为规范的email
author_mapping = {
	'xl123456': 'wenhuanhuan@xueleyun.com',
	'wenhuanhuan@task1-sandbox.xuele.net': 'wenhuanhuan@xueleyun.com',

	'chongfq@qq.com': 'chongfaqin@xueleyun.com',
	'pengxiuzhao@task1-sandbox.xuele.net': 'pengxiuzhao@xueleyun.com',
	'18210507492@126.com': 'qindongliang@xueleyun.com',

	'15901206690@139.com': 'lvnan@xueleyun.com',
	'lvnan@xuele.com': 'lvnan@xueleyun.com',

	'王子美@home': 'wangzimei@xueleyun.com',
	'王子美': 'wangzimei@xueleyun.com',

	'hwwweb@163.com': 'huoweiwei@xueleyun.com',
	'bigdata@task1-sandbox.xuele.net': 'bigdata',
	'yue': 'guiqiuyue@xueleyun.com',
	'lianxiaolei@hqyxjy.com': 'lianxiaolei@xueleyun.com',

	'476143560@qqcom': 'chenliang@xueleyun.com',
	'chenliang@xuele.com': 'chenliang@xueleyun.com'
}

# 命令行参数的name
P_PROJECT = "--project"
P_UPDATE_CODES = "--update_codes"
P_CREATE_LOG = "--create_log"
P_SINCE = "--since"
P_BEFORE = "--before"
P_ORIGINAL_AUTHOR = "--original_author"
P_SUBTOTAL = "--subtotal"
P_DEBUG = "--debug"
P_OUTPUT = "--output"
P_STAT_BY_MONTH = "--stat_by_month"

# 部分命令行参数的有效value
P_OUTPUT_CONSOLE = "console"
P_OUTPUT_FILE = "file"

# 分隔符
# proj_author_stat{}的key中的project与author之间的分隔符，例如：classroom:zhaoguojiong@xueleyun.com
SEP_PROJ_AUTHOR_KEY = ":"
# 各个***_stat_month{}中的key中的两个月份的分隔符，例如：2018-01-01:2018-02-01
SEP_STAT_MONTH_KEY = ":"
# 命令行参数--project的value中的group与project之间的分隔符，例如：xueleapp/classroom
SEP_CMD_PROJ = "/"
# author中name与email之间的分隔符，例如：zhaoguojiong <zhaoguojiong@xueleyun.com>
SEP_AUTHOR_NAME_EMAIL = " "
# author中email的开始、结束标志字符，例如：zhaoguojiong <zhaoguojiong@xueleyun.com>
SEP_AUTHOR_EMAIL_BEGIN = "<"
SEP_AUTHOR_EMAIL_END = ">"
# git log --pretty=tformat: 输出文件中各列之间的分隔符，例如：
# 04281db86b16393ceb3968219426189b9a30c007||霍伟伟 <huoweiwei@xueleyun.com>||2017-12-29T19:16:09+08:00
SEP_GIT_LOG_COLUMN = "||"
# 日期中年、月、日之间的分隔符，例如：2018-01-01
SEP_DATE = "-"
# 命令行参数中param和value的分隔符，例如：--output=file
SEP_CMD_PARAM_VALUE = "="
# output文件中各列之间的分隔符，例如：2018-01-01	2018-02-01	treasury	unknown	23459	25.4	350	25.5
SEP_OUTPUT_FILE_COLUMN = "\t"

# 输出proj_stat{}时的表头列名
metrics = ["added lines", "lines%", "commits", "commits%"]
COLUMNS_PROJ_STAT = ["project", "branch"] + metrics
# 输出proj_author_stat{}时的表头列名
COLUMNS_PROJ_AUTHOR_STAT = ["project", "branch", "author"] + metrics
# 输出author_stat{}时的表头列名
COLUMNS_AUTHOR_STAT = ["author"] + metrics
# 输出final_lines_stat{}时的表头列名
# final_lines_stat{}中的特殊key
FINAL_LINES_TOTAL = "total"
FINAL_LINES_OTHERS = "others"
COLUMNS_FINAL_LINES_STAT = ["project", "final lines", "lines%"] + code_file_ext + [FINAL_LINES_OTHERS]

# 日期格式
DATE_FORMAT = "%Y" + SEP_DATE + "%m" + SEP_DATE + "%d"

# 克隆git项目
def git_clone(group_name, proj_name):
	# 先检查该git项目目录是否已经存在
	if proj_name in os.listdir(git_root):
		return

	logger.info("git cloning...")

	# 构建git命令行
	cmd_cd = 'cd %s' % git_root
	cmd_git_clone = 'git clone git@git.xuelebj.net:%s/%s.git' % (group_name, proj_name)
	cmd = '%s && %s' % (cmd_cd, cmd_git_clone) 
	logger.debug(cmd)
	# 执行git命令行
	os.system(cmd)

# git pull最新代码
def git_pull(path, branch):
	logger.info("git pulling...")

	# 构建git命令行
	cmd_cd = "cd %s" % path
	cmd_git_checkout = "git checkout %s" % branch
	cmd_git_pull = "git pull"
	cmd = "%s && %s && %s" % (cmd_cd, cmd_git_checkout, cmd_git_pull) 
	logger.debug(cmd)
	# 执行git命令行
	result = os.system(cmd)
	logger.debug("command return: %s", result)

# git fetch最新代码
def git_fetch(path):
	logger.info("git fetching...")

	# 构建git命令行
	cmd_cd = "cd %s" % path
	cmd_git_fetch = "git fetch origin"
	cmd = "%s && %s" % (cmd_cd, cmd_git_fetch) 
	logger.debug(cmd)
	# 执行git命令行
	result = os.system(cmd)
	logger.debug("command return: %s", result)

# 获取git_log_stat_***.txt文件名称（不含路径）
def get_git_log_stat_filename_without_path(since, before):
	# 构建git_log_stat_***.txt文件名称
	return "git_log_stat_%s_%s.txt" % (since, before)

# 获取git_log_stat_***.txt文件名称（含路径）
def get_git_log_stat_filename_with_path(path, since, before):
	# 获得git_log_stat_***.txt文件名称（不含路径）
	filename = get_git_log_stat_filename_without_path(since, before)
	# 返回文件名称（含路径）
	return os.path.join(path, filename)

# 执行git log --stat命令，生成commit统计文件，包含每一次commit的author、date、及代码行数统计
def create_git_log_stat_file(path, since, before):
	logger.info("git logging...")

	# 构建git_log_stat_***.txt文件名称
	filename = get_git_log_stat_filename_without_path(since, before)

	# 构建统计提交代码行数的git log --stat命令行
	cmd_cd = "cd %s" % path
	cmd_git_log = "git log --pretty=tformat:\"%%H%s%%an <%%ae>%s%%aI\" --stat --since=%s --before=%s --all > \"%s\"" % (SEP_GIT_LOG_COLUMN, SEP_GIT_LOG_COLUMN, since, before, filename)
	cmd = "%s && %s" % (cmd_cd, cmd_git_log) 
	logger.debug(cmd)
	# 执行git命令行
	result = os.system(cmd)
	logger.debug("command return: %s", result)
	
	# 返回生成的文件名称
	return get_git_log_stat_filename_with_path(path, since, before)

# 从author中解析出email，并转换为规范的email
# author格式为：zhaoguojiong <zhaoguojiong@xueleyun.com>
def normalize_author_email(author):
	# 截取出原始的email
	author_email = author.split(SEP_AUTHOR_EMAIL_BEGIN)[1].strip(SEP_AUTHOR_EMAIL_END)
	logger.debug("split email: %s.", author_email)

	if author_email in author_mapping:
		new_author = author_mapping.get(author_email)
		logger.debug("Notice: %s --> %s", author_email, new_author)
	else:
		new_author = author_email

	return new_author

# 获取最近更新的branch（暂时没有办法，返回"unknown"）
def get_latest_branch():
	return "unknown"

# 解析git_log_stat_***.txt文件，统计整个项目的lines、commits，输出到proj_stat{}中；同时统计每个人的lines、commits，输出到proj_author_stat{}中
# filename需包含完整路径
# original_author决定是将原始的author、还是规范化后的author email输出到proj_author_stat{}中
def parse_git_log_stat_file(proj_stat, proj_author_stat, author_stat, proj, filename, original_author: False):
	logger.debug("parsing %s", filename)
	total_lines = 0
	total_commits = 0

	# 读取git_log_stat_***.txt文件，一次commit记录的内容格式为：
	# c3c867c8a146d9c3fe1dfb3284c6fcb237f95467||zhouming <zhouming@xueleyun.com>||2017-12-28T18:22:28+08:00
	#
	#  .../dm_recomm_book_bottom_kp_schedule.sh           |  4 +-
	#  .../dm_recomm_book_bottom_kp_schedule.sql          | 94 +++++++++++++++++++++-
	#  .../dm_recomm_book_bottom_unit_schedule.sql        | 19 ++++-
	#  3 files changed, 108 insertions(+), 9 deletions(-)	
	with open(filename, "r", encoding="utf-8") as f:
		author = ""
		commit = ""

		try:
			for line in f:
				line = line.strip("\n")
				logger.debug("reading a line: %s.", line)
				
				# 处理commit行
				if SEP_GIT_LOG_COLUMN in line:
					# 截取出commit id和author
					commit = line.split(SEP_GIT_LOG_COLUMN)[0]
					author = line.split(SEP_GIT_LOG_COLUMN)[1]

					# 保留原样的author格式
					if original_author:
						new_author = author
					else:
						# 转换为规范的author email
						new_author = normalize_author_email(author)

					# 累加该项目中该人的commits，更新到proj_author_stat{}中
					key = proj + SEP_PROJ_AUTHOR_KEY + new_author
					if key in proj_author_stat:
						proj_author_stat[key][2] += 1
					else:
						branch = get_latest_branch()
						proj_author_stat[key] = [branch, 0, 1]

					# 累加该人的commits（不考虑项目），更新到author_stat{}中
					key = new_author
					if key in author_stat:
						author_stat[key][1] += 1
					else:
						author_stat[key] = [0, 1]

					# 累加该项目的commits
					total_commits += 1
				# 处理lines行
				elif "changed" in line and ("insertion" in line or "deletion" in line):
					logger.debug("parsing: %s.", line)
					# 可能有三种格式：
					# 1： 3 files changed, 39 insertions(+), 106 deletions(-)
					# 2： 1 file changed, 18 deletions(-)
					# 3： 1 file changed, 4 insertions(+)
					insertions = line.split(", ")[1]
					if "insertion" in insertions:
						insertions = insertions.split(" ")[0]
					else:
						insertions = 0
					logger.debug("split insertions: %s.", insertions)
					lines = int(insertions);

					# 累加该项目中该人的lines，更新到proj_author_stat{}中
					key = proj + SEP_PROJ_AUTHOR_KEY + new_author
					if key in proj_author_stat:
						proj_author_stat[key][1] += lines
					else:
						branch = get_latest_branch()
						proj_author_stat[key] = [branch, lines, 1]

					# 累加该人的lines（不考虑项目），更新到author_stat{}中
					key = new_author
					if key in author_stat:
						author_stat[key][0] += lines
					else:
						author_stat[key] = [lines, 1]

					# 累加该项目的lines
					total_lines += lines
		except Exception as e:
			logger.error(e)

	# 将该项目的统计结果添加到proj_stat{}中
	if total_commits > 0:
		branch = get_latest_branch()
		proj_stat[proj] = [branch, total_lines, total_commits]

	logger.debug("proj_stat{} total: %s, proj_author_stat{} total: %s, author_stat{} total: %s",
		len(proj_stat), len(proj_author_stat), len(author_stat))

# 计算proj_stat{}的lines和commits的总数
def proj_stat_sum(stat):
	total_lines = 0
	total_commits = 0
	for p in stat:
		total_lines += stat[p][1]
		total_commits += stat[p][2]
	return total_lines, total_commits

# 准备要写入文件的一行数据
# cols是一个数组
def prepare_to_write(cols):
	# 拼接一行数据，列之间以\t分隔
	line = ""
	for c in cols:
		line += SEP_OUTPUT_FILE_COLUMN + str(c)
	# 去掉行首第一个列分隔符
	line = line.strip(SEP_OUTPUT_FILE_COLUMN)
	logger.debug("prepare to write: %s", line)
	return line + "\n"

# 将proj_stat_month{}写入到文件中
# whole_since, whole_before为命令行参数中的整体的since、before，不是按月统计时的每一个月的since、before
# stat_by_month决定输出的文件是按月统计的***_month.ext文件，还是整体上一个统计时间段的文件
def write_proj_stat(stat_month, whole_since, whole_before, stat_by_month: False):
	if len(stat_month) == 0:
		return

	# 构建输出文件名称
	if stat_by_month:
		filename = os.path.join(output_root, "proj_stat_%s_%s_month.txt" % (whole_since, whole_before))
	else:
		filename = os.path.join(output_root, "proj_stat_%s_%s.txt" % (whole_since, whole_before))
	logger.info("writing to %s", filename)
	with open(filename, "w", encoding="utf-8") as f:
		# 写入表头
		line = prepare_to_write(["since", "before"] + COLUMNS_PROJ_STAT)
		f.write(line)

		for sm in stat_month:
			# 取出这个月的since、before和proj_stat{}
			since = sm.split(SEP_STAT_MONTH_KEY)[0]
			before = sm.split(SEP_STAT_MONTH_KEY)[1]
			stat = stat_month[sm]

			# 先统计总数，因为要计算百分比
			total_lines, total_commits = proj_stat_sum(stat)

			# 写入每一行数据
			for p in stat:
				lines_percent = "%.1f" % (stat[p][1] / total_lines * 100)
				commits_percent = "%.1f" % (stat[p][2] / total_commits * 100)
				line = prepare_to_write([since, before, p, stat[p][0], stat[p][1], lines_percent, stat[p][2], commits_percent])
				f.write(line)

# 格式化打印输出proj_stat{}的一行
def print_proj_stat_oneline(cols):
	# 设置各列的宽度
	PROJECT_COL_WIDTH = 30
	BRANCH_COL_WIDTH = 20
	LINES_COL_WIDTH = 20
	COMMITS_COL_WIDTH = 20
	PERCENT_COL_WIDTH = 10

	logger.info("%s%s%s%s%s%s",
		str(cols[0]).rjust(PROJECT_COL_WIDTH), 
		str(cols[1]).rjust(BRANCH_COL_WIDTH), 
		str(cols[2]).rjust(LINES_COL_WIDTH), 
		str(cols[3]).rjust(PERCENT_COL_WIDTH), 
		str(cols[4]).rjust(COMMITS_COL_WIDTH),
		str(cols[5]).rjust(PERCENT_COL_WIDTH))

# 格式化打印输出proj_stat{}，返回lines和commits的总数
def print_proj_stat(stat):
	# 打印表头
	print_proj_stat_oneline(COLUMNS_PROJ_STAT)

	# 先统计总数，因为要计算百分比
	total_lines, total_commits = proj_stat_sum(stat)

	# 打印每一行数据
	total_projects = 0
	for p in stat:
		total_projects += 1
		lines_percent = "%.1f" % (stat[p][1] / total_lines * 100)
		commits_percent = "%.1f" % (stat[p][2] / total_commits * 100)
		print_proj_stat_oneline([p, stat[p][0], stat[p][1], lines_percent, stat[p][2], commits_percent])

	# 打印最后的总计行
	logger.info("")
	print_proj_stat_oneline(["total %d projects" % total_projects, "", total_lines, "", total_commits, ""])
	logger.info("")

	return total_lines, total_commits

# 格式化打印输出proj_author_stat{}的一行
def print_proj_author_stat_oneline(cols, author_width: 30):
	# 设置各列的宽度
	PROJECT_COL_WIDTH = 30
	BRANCH_COL_WIDTH = 20
	AUTHOR_COL_WIDTH = author_width
	LINES_COL_WIDTH = 15
	COMMITS_COL_WIDTH = 15
	PERCENT_COL_WIDTH = 15

	logger.info("%s%s%s%s%s%s%s" % (
		str(cols[0]).rjust(PROJECT_COL_WIDTH), 
		str(cols[1]).rjust(BRANCH_COL_WIDTH), 
		str(cols[2]).rjust(AUTHOR_COL_WIDTH), 
		str(cols[3]).rjust(LINES_COL_WIDTH), 
		str(cols[4]).rjust(PERCENT_COL_WIDTH), 
		str(cols[5]).rjust(COMMITS_COL_WIDTH),
		str(cols[6]).rjust(PERCENT_COL_WIDTH)))	

# 格式化打印输出proj_author_stat{}中的给定项目的总计行
def print_proj_author_stat_proj_total(proj_stat, proj, proj_lines, proj_commits, author_width: 30):
	# 如果proj_author_stat中的总计数值与proj_stat中的不同，则打印特殊标记
	if proj_lines != proj_stat[proj][1]:
		proj_lines = str(proj_lines) + "!=" + str(proj_stat[proj][1])
	if proj_commits != proj_stat[proj][2]:
		proj_commits = str(proj_commits) + "!=" + str(proj_stat[proj][2])
	print_proj_author_stat_oneline([proj, "", "total", proj_lines, "", proj_commits, ""], author_width)

# 计算proj_author_stat{}中各个project的lines和commits的总数，返回一个dict结构，key为project名称，value为统计结果数组
def proj_author_stat_sum_by_proj(stat):
	tmp_proj_stat = {}
	for pa in stat:
		proj = pa.split(SEP_PROJ_AUTHOR_KEY)[0]
		if proj in tmp_proj_stat:
			# 累计这个项目的lines
			tmp_proj_stat[proj][0] += stat[pa][1]
			# 累计这个项目的commits
			tmp_proj_stat[proj][1] += stat[pa][2]
		else:
			# 放入这个项目的第一行数据
			tmp_proj_stat[proj] = [stat[pa][1], stat[pa][2]]
	return tmp_proj_stat

# 获得proj_author_stat{}中author的最大长度
def get_max_author_len_in_proj_author_stat(stat):
	max_author_len = 0
	for pa in stat:
		a = pa.split(SEP_PROJ_AUTHOR_KEY)[1]
		if len(a) > max_author_len:
			max_author_len = len(a)
	max_author_len += 5
	return max_author_len

# 格式化打印输出proj_author_stat{}
def print_proj_author_stat(proj_stat, proj_author_stat, subtotal: False):
	# 获得author的最大长度
	max_author_len = get_max_author_len_in_proj_author_stat(proj_author_stat)

	# 打印表头
	print_proj_author_stat_oneline(COLUMNS_PROJ_AUTHOR_STAT, max_author_len)

	# 先统计每个项目的总数，因为要计算百分比
	tmp_proj_stat = proj_author_stat_sum_by_proj(proj_author_stat)

	# 打印每一行数据
	total_commits = 0
	total_lines = 0
	last_proj = ""
	for pa in proj_author_stat:
		proj =  pa.split(SEP_PROJ_AUTHOR_KEY)[0]
		author = pa.split(SEP_PROJ_AUTHOR_KEY)[1]
		# 可能存在有commit、但lines为0的情况
		if tmp_proj_stat[proj][0] == 0:
			lines_percent = "-"
		else:
			lines_percent = "%.1f" % (proj_author_stat[pa][1] / tmp_proj_stat[proj][0] * 100)
		commits_percent = "%.1f" % (proj_author_stat[pa][2] / tmp_proj_stat[proj][1] * 100)

		# 先打印上一个项目的总计行
		if subtotal and last_proj != "" and proj != last_proj:
			print_proj_author_stat_proj_total(proj_stat, last_proj, tmp_proj_stat[last_proj][0], tmp_proj_stat[last_proj][1], max_author_len)
		last_proj = proj

		print_proj_author_stat_oneline([proj, proj_author_stat[pa][0], author, proj_author_stat[pa][1], lines_percent, proj_author_stat[pa][2], commits_percent], max_author_len)

		# 累计所有项目的lines和commits
		total_lines += proj_author_stat[pa][1]
		total_commits += proj_author_stat[pa][2]

	# 打印最后一个项目的总计行
	if subtotal and len(proj_author_stat) > 0:
		print_proj_author_stat_proj_total(proj_stat, last_proj, tmp_proj_stat[last_proj][0], tmp_proj_stat[last_proj][1], max_author_len)

	# 打印最后的总计行
	logger.info("")
	print_proj_author_stat_oneline(["total %d projects" % len(tmp_proj_stat), "", "", total_lines, "", total_commits, ""], max_author_len)
	logger.info("")

	return total_lines, total_commits

# 将proj_author_stat_month{}写入到文件中
def write_proj_author_stat(stat_month, whole_since, whole_before, stat_by_month: False):
	if len(stat_month) == 0:
		return
	
	# 构建输出文件名称（位于当前目录下）
	if stat_by_month:
		filename = os.path.join(output_root, "proj_author_stat_%s_%s_month.txt" % (whole_since, whole_before))
	else:
		filename = os.path.join(output_root, "proj_author_stat_%s_%s.txt" % (whole_since, whole_before))
	logger.info("writing to %s", filename)
	with open(filename, 'w', encoding='utf-8') as f:
		# 写入表头
		line = prepare_to_write(['since', 'before'] + COLUMNS_PROJ_AUTHOR_STAT)
		f.write(line)

		for sm in stat_month:
			since = sm.split(SEP_STAT_MONTH_KEY)[0]
			before = sm.split(SEP_STAT_MONTH_KEY)[1]
			stat = stat_month[sm]

			# 先统计每个项目的总数，因为要计算百分比
			tmp_proj_stat = proj_author_stat_sum_by_proj(stat)

			# 写入每一行数据
			for pa in stat:
				proj =  pa.split(SEP_PROJ_AUTHOR_KEY)[0]
				author = pa.split(SEP_PROJ_AUTHOR_KEY)[1]
				# 可能存在有commit、但lines为0的情况
				if tmp_proj_stat[proj][0] == 0:
					lines_percent = "-"
				else:
					lines_percent = "%.1f" % (stat[pa][1] / tmp_proj_stat[proj][0] * 100)
				commits_percent = "%.1f" % (stat[pa][2] / tmp_proj_stat[proj][1] * 100)

				line = prepare_to_write([since, before, proj, stat[pa][0], author, stat[pa][1], lines_percent, stat[pa][2], commits_percent])
				f.write(line)

# 格式化打印输出author_stat{}的一行
def print_author_stat_oneline(cols, author_width: 30):
	# 设置各列的宽度
	AUTHOR_COL_WIDTH = author_width
	LINES_COL_WIDTH = 15
	COMMITS_COL_WIDTH = 15
	PERCENT_COL_WIDTH = 15

	logger.info("%s%s%s%s%s",
		str(cols[0]).rjust(AUTHOR_COL_WIDTH), 
		str(cols[1]).rjust(LINES_COL_WIDTH), 
		str(cols[2]).rjust(PERCENT_COL_WIDTH), 
		str(cols[3]).rjust(COMMITS_COL_WIDTH),
		str(cols[4]).rjust(PERCENT_COL_WIDTH))

# 计算author_stat{}中的lines和commits的总数
def author_stat_sum(stat):
	total_commits = 0
	total_lines = 0
	for a in stat:
		# 累计所有人的lines和commits
		total_lines += int(stat[a][0])
		total_commits += int(stat[a][1])
	return total_lines, total_commits

# 获得author_stat{}中author的最大长度
def get_max_author_len_in_author_stat(stat):
	max_author_len = 0
	for a in stat:
		if len(a) > max_author_len:
			max_author_len = len(a)
	max_author_len += 5
	return max_author_len

# 格式化打印输出author_stat{}
def print_author_stat(stat):
	# 获得author的最大长度
	max_author_len = get_max_author_len_in_author_stat(stat)

	# 打印表头
	print_author_stat_oneline(COLUMNS_AUTHOR_STAT, max_author_len)

	# 先统计所有author的总数，因为要计算百分比
	total_lines, total_commits = author_stat_sum(stat)

	# 打印每一行数据
	for author in stat:
		lines_percent = "%.1f" % (stat[author][0] / total_lines * 100)
		commits_percent = "%.1f" % (stat[author][1] / total_commits * 100)

		print_author_stat_oneline([author, stat[author][0], lines_percent, stat[author][1], commits_percent], max_author_len)

	# 打印最后的总计行
	logger.info("")
	print_author_stat_oneline(["total %d authors" % len(stat), total_lines, "", total_commits, ""], max_author_len)
	logger.info("")

	return total_lines, total_commits

# 将author_stat{}写入到文件中
def write_author_stat(stat_month, whole_since, whole_before, stat_by_month: False):
	if len(stat_month) == 0:
		return

	# 构建输出文件名称（位于当前目录下）
	if stat_by_month:
		filename = os.path.join(output_root, "author_stat_%s_%s_month.txt" % (whole_since, whole_before))
	else:
		filename = os.path.join(output_root, "author_stat_%s_%s.txt" % (whole_since, whole_before))
	logger.info("writing to %s", filename)
	with open(filename, "w", encoding="utf-8") as f:
		# 写入表头
		line = prepare_to_write(["since", "before"] + COLUMNS_AUTHOR_STAT)
		f.write(line)

		for sm in stat_month:
			since = sm.split(SEP_STAT_MONTH_KEY)[0]
			before = sm.split(SEP_STAT_MONTH_KEY)[1]
			stat = stat_month[sm]

			# 先统计所有author的总数，因为要计算百分比
			total_lines, total_commits = author_stat_sum(stat)

			# 打印每一行数据
			for author in stat:
				lines_percent = "%.1f" % (stat[author][0] / total_lines * 100)
				commits_percent = "%.1f" % (stat[author][1] / total_commits * 100)

				line = prepare_to_write([since, before, author, stat[author][0], lines_percent, stat[author][1], commits_percent])
				f.write(line)

# 格式化打印输出final_lines_stat{}的一行
def print_final_lines_stat_oneline(cols):
	# 设置各列的宽度
	PROJECT_COL_WIDTH = 30
	LINES_COL_WIDTH = 20
	PERCENT_COL_WIDTH = 10
	EXT_COL_WIDTH = 10

	# 头三列：project, total lines, percentage
	fmt = "%s%s%s"
	# 中间的ext列
	for e in code_file_ext:
		fmt += "%s"
	# 最后的others列
	fmt += "%s"

	logger.info(fmt,
		str(cols[0]).rjust(PROJECT_COL_WIDTH), 
		str(cols[1]).rjust(LINES_COL_WIDTH), 
		str(cols[2]).rjust(PERCENT_COL_WIDTH), 
		str(cols[3]).rjust(EXT_COL_WIDTH), 
		str(cols[4]).rjust(EXT_COL_WIDTH),
		str(cols[5]).rjust(EXT_COL_WIDTH),
		str(cols[6]).rjust(EXT_COL_WIDTH),
		str(cols[7]).rjust(EXT_COL_WIDTH),
		str(cols[8]).rjust(EXT_COL_WIDTH),
		str(cols[9]).rjust(EXT_COL_WIDTH),
		str(cols[10]).rjust(EXT_COL_WIDTH),
		str(cols[11]).rjust(EXT_COL_WIDTH),
		str(cols[12]).rjust(EXT_COL_WIDTH),
		str(cols[13]).rjust(EXT_COL_WIDTH),
		str(cols[14]).rjust(EXT_COL_WIDTH),
		str(cols[15]).rjust(EXT_COL_WIDTH),
		str(cols[16]).rjust(EXT_COL_WIDTH),
		str(cols[17]).rjust(EXT_COL_WIDTH),
		str(cols[18]).rjust(EXT_COL_WIDTH),
		str(cols[19]).rjust(EXT_COL_WIDTH),
		str(cols[20]).rjust(EXT_COL_WIDTH),
		str(cols[21]).rjust(EXT_COL_WIDTH),
		str(cols[22]).rjust(EXT_COL_WIDTH),
		str(cols[23]).rjust(EXT_COL_WIDTH),
		str(cols[24]).rjust(EXT_COL_WIDTH),
		str(cols[25]).rjust(EXT_COL_WIDTH))

# 计算final_lines_stat{}中的final lines的总数
def final_lines_stat_sum(stat):
	total_lines = 0
	for p in stat:
		# 累计所有项目的final lines
		total_lines += int(stat[p][FINAL_LINES_TOTAL])

	return total_lines

# 格式化打印输出final_lines_stat{}
def print_final_lines_stat(stat):
	# 打印表头
	print_final_lines_stat_oneline(COLUMNS_FINAL_LINES_STAT)

	# 先统计所有项目的总数，因为要计算百分比
	total_lines = final_lines_stat_sum(stat)

	# 打印每一行数据
	for p in stat:
		lines_percent = "%.1f" % (stat[p][FINAL_LINES_TOTAL] / total_lines * 100)

		# 前三列：project, total lines, percent
		row = [p, stat[p][FINAL_LINES_TOTAL], lines_percent]
		# 中间的ext列
		for e in code_file_ext:
			row += [stat[p][e]]
		# 最后的others列
		row += [stat[p][FINAL_LINES_OTHERS]]
		print_final_lines_stat_oneline(row)

	# 打印最后的总计行
	logger.info("")
	# 前三列：project, total lines, percent
	last_row = ["total %d projects" % len(stat), total_lines, ""]
	# 中间的ext列
	for e in code_file_ext:
		last_row += [""]
	# 最后的others列
	last_row += [""]
	print_final_lines_stat_oneline(last_row)
	logger.info("")

# 将final_lines_stat{}写入到文件中
def write_final_lines_stat(stat):
	if len(stat) == 0:
		return

	# 构建输出文件名称（位于当前目录下）
	today = datetime.datetime.now().strftime(DATE_FORMAT)
	filename = os.path.join(output_root, "final_lines_stat_%s.txt" % today)

	logger.info("writing to %s", filename)
	with open(filename, "w", encoding="utf-8") as f:
		# 写入表头
		line = prepare_to_write(["til"] + COLUMNS_FINAL_LINES_STAT)
		f.write(line)

		# 先统计所有项目的总数，因为要计算百分比
		total_lines = final_lines_stat_sum(stat)

		for p in stat:
			# 打印每一行数据
			lines_percent = "%.1f" % (stat[p][FINAL_LINES_TOTAL] / total_lines * 100)

			# 前四列：date, project, total lines, percent
			row = [today, p, stat[p][FINAL_LINES_TOTAL], lines_percent]
			# 中间的ext列
			for e in code_file_ext:
				row += [stat[p][e]]
			# 最后的others列
			row += [stat[p][FINAL_LINES_OTHERS]]

			line = prepare_to_write(row)
			f.write(line)

# 获取给定项目的完整路径
def get_proj_path(proj):
	return os.path.join(git_root, proj)

# 递归统计给定目录下的文件行数，返回predefined_ext和undefined_ext。
# predefined_ext为一个dict结构，key为预定义的文件扩展名（即存在于code_file_ext中的扩展名），value为final lines。
#   但是，所有的未定义的扩展名，也会作为一个统一的“others”扩展名（一个key），也计入到此dict中
# undefined_ext为一个dict结构，key为未定义的文件扩展名，value为final lines
# skipped_files为一个数组结构，保存跳过的文件列表
# error_files为一个数组结构，保存read文件有异常的文件列表
def count_lines(path, predefined_ext, undefined_ext, skipped_files, error_files):
	for file in os.listdir(path):
		# 获得完整路径
		file_path = os.path.join(path, file)

		# 跳过一些目录或文件
		if file in skipped_path:
			skipped_files += [file_path]
			logger.debug("%s is skipped.", file)
			continue

		# 如果是目录，则继续递归
		if os.path.isdir(file_path):
			count_lines(file_path, predefined_ext, undefined_ext, skipped_files, error_files)
			continue

		# 获取文件扩展名（转换为小写）
		ext = os.path.splitext(file)[1].lower()

		# 跳过一些扩展名（精确匹配）
		if ext in skipped_file_ext:
			skipped_files += [file_path]
			logger.debug("%s is skipped, because ext: %s", file, ext)
			continue

		# 统计文件行数
		file_lines = 0
		read_error = False
		# 先尝试以utf-8读取
		try:
			with open(file_path, "r", encoding = "utf-8") as f:
				for l in f:
					file_lines += 1
			read_error = False
			logger.debug("%s: %d final lines.", file_path, file_lines)
		except Exception as e:
			read_error = True
			utf_error = e
			logger.debug(e)

		# 再尝试以gbk读取
		if read_error:
			try:
				with open(file_path, "r", encoding = "gbk") as f:
					for l in f:
						file_lines += 1
				read_error = False
				logger.debug("%s: %d final lines.", file_path, file_lines)
			except Exception as e:
				read_error = True
				gbk_error = e
				logger.debug(e)

		# 再尝试以utl-16读取
		if read_error:
			try:
				with open(file_path, "r", encoding = "utf-16") as f:
					for l in f:
						file_lines += 1
				read_error = False
				logger.debug("%s: %d final lines.", file_path, file_lines)
			except Exception as e:
				# 认为不是一个文本文件，不统计lines
				read_error = True
				error_files += [file_path + (" (%s; %s; %s)" % (utf_error, gbk_error, e))]
				logger.debug(e)
				logger.debug("%s is not a text file? just skipped.", file_path)
				continue

		# 如果扩展名是预定义的，则按原扩展名分类统计；否则，统一计入到“others”类别中
		if not (ext in code_file_ext):
			if not (ext in undefined_ext):
				undefined_ext[ext] = file_lines
			else:
				undefined_ext[ext] += file_lines
			logger.debug("undefined ext: %s, file: %s", ext, file_path)
			ext = FINAL_LINES_OTHERS

		predefined_ext[ext] += file_lines

# 递归项目的代码目录，统计final lines，保存到final_lines_stat{}中
def stat_final_lines(stat, proj):
	# 获取该项目的完整路径
	projdir = get_proj_path(proj)

	# 初始化要返回的predefined_ext{}、undefined_ext{}和skipped_file[]
	predefined_ext = {FINAL_LINES_TOTAL: 0, FINAL_LINES_OTHERS: 0}
	for e in code_file_ext:
		predefined_ext[e] = 0
	undefined_ext = {}
	skipped_files = []
	error_files = []

	# 统计该项目下的final lines
	count_lines(projdir, predefined_ext, undefined_ext, skipped_files, error_files)

	# 计算所有ext的lines的总和（不包含未定义扩展名的lines）
	for e in predefined_ext:
		if not (e in [FINAL_LINES_TOTAL, FINAL_LINES_OTHERS]):
			predefined_ext[FINAL_LINES_TOTAL] += predefined_ext[e]

	# 添加到final_lines_stat{}中
	stat[proj] = predefined_ext

	# 打印undefined_ext{}
	if len(undefined_ext) > 0:
		logger.info("final lines of undefined ext: %s", undefined_ext)
	# 打印跳过的文件列表
	# if len(skipped_files) > 0:
	# 	logger.info("skipped %d files:", len(skipped_files))
	# 	for f in skipped_files:
	# 		logger.info(f)
	# 打印read异常的文件列表
	if len(error_files) > 0:
		logger.info("%d error files:", len(error_files))
		for f in error_files:
			logger.info(f)

# 生成给定项目的统计数据，保存到proj_stat{}、proj_author_stat{}、author_stat{}中
def stat_commits(proj_stat, proj_author_stat, author_stat, proj, since, before, create_log_needed: False, original_author: False):
	# 获取该项目的完整路径
	projdir = get_proj_path(proj)

	# 如果需要重新生成log文件，则重新执行git log操作
	if create_log_needed:
		filename = create_git_log_stat_file(projdir, since, before)
	else:
		filename = get_git_log_stat_filename_with_path(projdir, since, before)
	if not os.path.exists(filename):
		logger.error("%s is not existed", filename)
		logger.error("please run again with --create_log option")
		return

	# 统计该项目的commits和added lines
	parse_git_log_stat_file(proj_stat, proj_author_stat, author_stat, proj, filename, original_author)

# 处理给定的git项目的commits和added lines
def process_proj_commits(proj_stat, proj_author_stat, author_stat, proj_group, proj, since, before, update_codes_needed: False, create_log_needed: False, original_author: False):
	# 先检查该git项目是否已经存在，如果不存在，则先克隆项目
	if not (proj in os.listdir(git_root)):
		git_clone(proj_group, proj)
		# 如果克隆了新项目，则必须更新代码，生成log文件
		update_codes_needed = True
		create_log_needed = True

	# 获取该项目的完整路径
	projdir = get_proj_path(proj)
	if not os.path.exists(projdir):
		logger.error("%s is not existed" % projdir)
		return

	# 如果需要更新代码，先执行git fetch操作
	if update_codes_needed:
		# 执行git fetch，用于后续的统计所有分支的commits和added lines
		git_fetch(projdir)

	# 统计该项目的commits和lines
	stat_commits(proj_stat, proj_author_stat, author_stat, proj, since, before, create_log_needed, original_author)

# 处理给定的git项目的final lines
def process_proj_final_lines(final_lines_stat, proj_group, proj, update_codes_needed: False):
	# 先检查该git项目是否已经存在，如果不存在，则先克隆项目
	if not (proj in os.listdir(git_root)):
		git_clone(proj_group, proj)
		# 如果克隆了新项目，则必须更新代码
		update_codes_needed = True

	# 获取该项目的完整路径
	projdir = get_proj_path(proj)
	if not os.path.exists(projdir):
		logger.error("%s is not existed" % projdir)
		return

	# 如果需要更新代码，先执行git pull操作
	if update_codes_needed:
		# 执行git pull，用于后续的统计master分支中的final lines
		git_pull(projdir, "master")

	# 统计该项目的final lines
	stat_final_lines(final_lines_stat, proj)

# 判断一个字符串是否为有效的日期
def is_valid_date(date_str):
	try:
		date = datetime.datetime.strptime(date_str, DATE_FORMAT)
		return True
	except Exception as e:
		return False

# 标准化日期字符串，变为：yyyy-mm-dd
def normalize_date(date_str):
	# 通过日期格式化方法，比较笨
	# 先转换为日期
	date = datetime.datetime.strptime(date_str, DATE_FORMAT)
	# 然后再对日期进行格式化：yyyy-mm-dd
	return date.strftime(DATE_FORMAT)	

# 返回下一个月份，格式为：yyyy-mm-dd
def get_next_month(date_str):
	year = int(date_str.split(SEP_DATE)[0])
	month = int(date_str.split(SEP_DATE)[1])
	if month == 12:
		month = 1
		year += 1
	else:
		month += 1
	next_month = str(year) + SEP_DATE + str(month) + SEP_DATE + "01"

	# 对next_month进行格式规范化
	return normalize_date(next_month)

# 获取一个命令行参数的value
def get_param_value(pv):
	v = pv.split(SEP_CMD_PARAM_VALUE)
	if len(v) > 1:
		return v[1]
	else:
		return ""

# 获取命令行参数
def get_cmd_params():
	logger.info("cmd: %s", sys.argv)

	# usage提示信息中，各命令行参数的value
	cmd_param = {
		P_PROJECT: "group/project",
		P_UPDATE_CODES: "",
		P_CREATE_LOG: "",
		P_SINCE: "yyyy-mm-dd",
		P_BEFORE: "yyyy-mm-dd",
		P_ORIGINAL_AUTHOR: "",
		P_SUBTOTAL: "",
		P_DEBUG: "",
		P_OUTPUT: P_OUTPUT_CONSOLE + "/" + P_OUTPUT_FILE,
		P_STAT_BY_MONTH: ""
	}

	# 构造usage提示信息
	usage = "Usage: python " + sys.argv[0]
	for p in cmd_param:
		if cmd_param[p] != "":
			usage += " [" + p + SEP_CMD_PARAM_VALUE + cmd_param[p] + "]"
		else:
			usage += " [" + p + "]"

	# 设置各命令行参数的默认值
	cmd_pv = {
		P_PROJECT: "",
		P_UPDATE_CODES: False,
		P_CREATE_LOG: False,
		P_SINCE: "",
		P_BEFORE: "",
		P_ORIGINAL_AUTHOR: False,
		P_SUBTOTAL: False,
		P_DEBUG: False,
		P_OUTPUT: P_OUTPUT_CONSOLE,
		P_STAT_BY_MONTH: False
	}

	group = ""
	proj = ""
	since = ""
	before = ""
	i = 0
	for a in sys.argv:
		# 跳过第一个参数，即脚本名称自身
		if i == 0:
			i += 1
			continue

		if P_PROJECT in a:
			project = get_param_value(a)
			if project == "":
				logger.error("project is null")
				logger.error(usage)
				exit()
			elif not (SEP_CMD_PROJ in project):
				logger.error("%s format: %s", P_PROJECT, cmd_param[P_PROJECT])
				exit()
			else:
				group = project.split(SEP_CMD_PROJ)[0]
				proj = project.split(SEP_CMD_PROJ)[1]
				if group == "" or proj == "":
					logger.error("%s: group or project is null", a)
					exit()
			cmd_pv[P_PROJECT] = project
		elif P_UPDATE_CODES == a:
			cmd_pv[P_UPDATE_CODES] = True
		elif P_CREATE_LOG == a:
			cmd_pv[P_CREATE_LOG] = True			
		elif P_SINCE in a:
			since = get_param_value(a)
		elif P_BEFORE in a:
			before = get_param_value(a)
		elif P_ORIGINAL_AUTHOR == a:
			cmd_pv[P_ORIGINAL_AUTHOR] = True
		elif P_SUBTOTAL == a:
			cmd_pv[P_SUBTOTAL] = True
		elif P_DEBUG == a:
			cmd_pv[P_DEBUG] = True
		elif P_OUTPUT in a:
			output = get_param_value(a)
			if output == "":
				logger.error("output is null")
				logger.error(usage)
				exit()
			elif not (output in [P_OUTPUT_CONSOLE, P_OUTPUT_FILE]):
				logger.error("%s format: %s", P_OUTPUT, cmd_param[P_OUTPUT])
				exit()
			cmd_pv[P_OUTPUT] = output
		elif P_STAT_BY_MONTH == a:
			cmd_pv[P_STAT_BY_MONTH] = True
		else:
			logger.error("%s is invalid", a)
			logger.error(usage)
			exit()

	if since == "" and before == "":
		logger.error("since or before is missed")
		logger.info(usage)
		exit()

	if not (since == "") and not is_valid_date(since):
		logger.error("since is not a valid date. format: yyyy-mm-dd")
		logger.info(usage)
		exit()
	if not (before == "") and not is_valid_date(before):
		logger.error("before is not a valid date. format: yyyy-mm-dd")
		logger.info(usage)
		exit()

	# 对日期格式进行标准化
	since = normalize_date(since)
	before = normalize_date(before)

	if not (since == "") and not (before == "") and before <= since:
		logger.error("before must > since")
		logger.info(usage)
		exit()

	cmd_pv[P_SINCE] = since
	cmd_pv[P_BEFORE] = before

	# 如果需要更新代码，则必须重新生成log文件，此时忽略命令行参数
	if cmd_pv[P_UPDATE_CODES]:
		cmd_pv[P_CREATE_LOG] = True

	# 打印命令行参数值
	for pv in cmd_pv:
		logger.info("%s: %s", pv, cmd_pv[pv])
	logger.info("")

	return cmd_pv

# 入口函数
def start_stat():
	# 每个项目的统计结果，dict类型，key为project名称，value为统计结果数组[branch, lines, commits]
	proj_stat = {}
	# 每个项目、每个人的统计结果，dict类型，key为"project名称:author"，value为统计结果数组[branch, lines, commits]
	# key中的author可能为原始的author格式，即“name <email>”；也可能为规范的email。由命令行参数--original_author决定”
	proj_author_stat = {}
	# 每个人的统计结果（不区分项目），dict类型，key为"author"，value为统计结果数组[lines, commits]
	# author的格式同proj_author_stat的key中的author
	author_stat = {}

	# 每个月的proj_stat统计结果，dict类型，key为"this_month:next_month"，value为proj_stat{}
	# key中的this_month为统计月份的1日的日期，格式为yyyy-mm-dd，如2018-01-01；next_month为统计月份的下一个月的1日的日期，格式同this_month。
	# 例如，存放2018年1月的统计数据，则key为"2018-01-01:2018-02-01"
	proj_stat_month = {}
	# 每个月的proj_author_stat统计结果，dict类型，key同proj_stat_month，value为proj_author_stat{}
	proj_author_stat_month = {}
	# 每个月的author_stat统计结果，dict类型，key同proj_stat_month，value为author_stat{}
	author_stat_month = {}

	# 每个项目的final lines统计结果，dict类型，key为project名称，value为final lines的一个dict类型，其中key为扩展名，value为final lines
	final_lines_stat = {}

	# 读取命令行参数
	cmd_param_value = get_cmd_params()

	# 此处修改日志级别无效，不知为啥
	# if cmd_param_value[P_DEBUG]:
	# 	logger.basicConfig(level=logger.DEBUG)
	# else:
	# 	logger.basicConfig(level=logger.INFO)

	# 如果git目录和output目录不存在， 则先创建目录
	if not os.path.exists(git_root):
		os.mkdir(git_root)
	if not os.path.exists(output_root):
		os.mkdir(output_root)

	# 先统计commits和added lines，涉及到多个月份的拆分问题
	logger.info("processing commits and added lines...")
	# 如果按月统计，则先生成月份列表
	since_before = {}
	if cmd_param_value[P_STAT_BY_MONTH]:
		# 截止到今天的下一个月
		max_before = get_next_month(datetime.datetime.now().strftime(DATE_FORMAT))
		logger.debug("max before: %s", max_before)

		# 获得起始日期
		since = cmd_param_value[P_SINCE]
		# 获得下一个月的日期
		next_month = get_next_month(since)
		# 将字符串转换为日期进行比较
		while datetime.datetime.strptime(next_month, DATE_FORMAT) < datetime.datetime.strptime(cmd_param_value[P_BEFORE], DATE_FORMAT):
			# 截止到当前日期的下一个月
			logger.debug("next month: %s, max month: %s", next_month, max_before)
			if next_month >= max_before:
				logger.debug("max before occured")
				break

			# 添加到列表中
			since_before[since] = next_month
			since = next_month
			next_month = get_next_month(since)

		# 将最后一个月加入到列表中
		since_before[since] = cmd_param_value[P_BEFORE]
		logger.debug(since_before)
	else:
		since_before[cmd_param_value[P_SINCE]] = cmd_param_value[P_BEFORE]

	n = 1
	total_sb = len(since_before)
	for sb in since_before:
		since = sb
		before = since_before[sb]
		logger.info("%s %s", ("processing [since, before]: " + since + ", " + before).ljust(70), (str(n) + "/" + str(total_sb)).rjust(10))

		# 每个新的时间周期处理之前，先清空三个***_stat{}
		proj_stat = {}
		proj_author_stat = {}
		author_stat = {}

		# 连续生成多个月的统计结果时，只有第一个月时才更新代码（假如命令行参数指定了要更新代码），后面的不再重复更新代码
		update_codes = cmd_param_value[P_UPDATE_CODES]
		if update_codes:
			if n >= 2:
				update_codes = False	

		# 如果命令行参数中指定了project，则只统计这个project
		if cmd_param_value[P_PROJECT] != "":
			group = cmd_param_value[P_PROJECT].split(SEP_CMD_PROJ)[0]
			proj = cmd_param_value[P_PROJECT].split(SEP_CMD_PROJ)[1]
			logger.info("processing %s/%s", group, proj)
			process_proj_commits(proj_stat, proj_author_stat, author_stat,
				group, proj, since, before, update_codes, cmd_param_value[P_CREATE_LOG], cmd_param_value[P_ORIGINAL_AUTHOR])				
		# 否则，循环处理git_proj{}中指定的每一个git项目
		else:
			for group in git_proj:
				logger.info("processing group: %s", group)
				num = 1
				total = len(git_proj[group])
				for proj in git_proj[group]:
					logger.info("%s %s", ("processing project: " + proj).ljust(70), (str(num) + "/" + str(total)).rjust(10))
					process_proj_commits(proj_stat, proj_author_stat, author_stat,
						group, proj, since, before, update_codes, cmd_param_value[P_CREATE_LOG], cmd_param_value[P_ORIGINAL_AUTHOR])
					num += 1
				logger.info("")

			# 输出未变更的项目清单
			logger.info("projects not changed:")
			for group in git_proj:
				for proj in git_proj[group]:
					if not (proj in proj_stat):
						logger.info(proj)
			logger.info("")

		# 将这次since-before周期内的统计结果保存到***_month{}中
		key = since + SEP_STAT_MONTH_KEY + before
		proj_stat_month[key] = proj_stat
		proj_author_stat_month[key] = proj_author_stat
		author_stat_month[key] = author_stat

		# 将统计结果打印到标准输出终端上
		if cmd_param_value[P_OUTPUT] == P_OUTPUT_CONSOLE:
			logger.info("since=%s, before=%s", since, before)
			# 格式化打印proj_stat{}
			l1, c1 = print_proj_stat(proj_stat)
			# 格式化打印proj_author_stat{}
			l2, c2 = print_proj_author_stat(proj_stat, proj_author_stat, cmd_param_value[P_SUBTOTAL])
			# 格式化打印author_stat{}
			l3, c3 = print_author_stat(author_stat)

			# 如果三个矩阵统计数据不一致，则打印警告信息
			if [l2, c2] != [l1, c1] or [l3, c3] != [l2, c2]:
				logger.warn("")
				logger.warn("total number in 3 tables is not equal. ")

		n += 1

	# 然后统计final lines，不管是否指定了--stat_by_month，只统计一次
	logger.info("processing final lines...")
	# 如果命令行参数中指定了project，则只统计这个project
	if cmd_param_value[P_PROJECT] != "":
		group = cmd_param_value[P_PROJECT].split(SEP_CMD_PROJ)[0]
		proj = cmd_param_value[P_PROJECT].split(SEP_CMD_PROJ)[1]
		logger.info("processing %s/%s", group, proj)
		# 统计该项目的final lines
		process_proj_final_lines(final_lines_stat, group, proj, cmd_param_value[P_UPDATE_CODES])
	# 否则，循环处理git_proj{}中指定的每一个git项目
	else:
		for group in git_proj:
			logger.info("processing group: %s", group)
			num = 1
			total = len(git_proj[group])
			for proj in git_proj[group]:
				logger.info("%s %s", ("processing project: " + proj).ljust(70), (str(num) + "/" + str(total)).rjust(10))
				# 统计该项目的final lines
				process_proj_final_lines(final_lines_stat, group, proj, cmd_param_value[P_UPDATE_CODES])
				num += 1
			logger.info("")

	if cmd_param_value[P_OUTPUT] == P_OUTPUT_CONSOLE:
		# 格式化打印final_lines_stat{}
		print_final_lines_stat(final_lines_stat)

	# 将统计结果输出到文件中
	if cmd_param_value[P_OUTPUT] == P_OUTPUT_FILE:
		write_proj_stat(proj_stat_month, cmd_param_value[P_SINCE], cmd_param_value[P_BEFORE], cmd_param_value[P_STAT_BY_MONTH])
		write_proj_author_stat(proj_author_stat_month, cmd_param_value[P_SINCE], cmd_param_value[P_BEFORE], cmd_param_value[P_STAT_BY_MONTH])
		write_author_stat(author_stat_month, cmd_param_value[P_SINCE], cmd_param_value[P_BEFORE], cmd_param_value[P_STAT_BY_MONTH])
		write_final_lines_stat(final_lines_stat)

if __name__ == "__main__":
	start_stat()