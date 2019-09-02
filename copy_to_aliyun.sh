SRC="./output/proj_author_stat_2019-01-01_2020-01-01_month.txt"
DEST="39.105.8.98:/home/project/pms/data_tools/data/"
echo "copying "${SRC}" to "${DEST}" ..."
scp ${SRC} root@${DEST}
