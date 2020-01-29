import os
import re
import json
import time
import logging
import requests

logging.basicConfig(level=logging.INFO,
                    format='%(levelname)-7s: %(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='Runlog.log',
                    filemode='w')

console = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s|%(levelname)-7s: %(message)s')
logger = logging.getLogger('')
console.setLevel(logging.DEBUG)
console.setFormatter(formatter)
logger.addHandler(console)

url = "https://3g.dxy.cn/newh5/view/pneumonia"
# 实时消息推送reg
reg = r'<script id="getTimelineService">.+?window.getTimelineService\s=\s(.*?\])}catch\(e\){}<\/script>'
# 统计数据reg
data_reg = r'[0-9]\);">(\d+)<\/span> 例'
data_reg= r'confirmedCount":(\d+),"suspectedCount":(\d+),"curedCount":(\d+),"deadCount":(\d+),"virus"'


def get_data(urlx, regx):
    all_data = {}
    re_format = re.compile(regx)
    try:
        webdata = requests.get(urlx)
        assert webdata.status_code == 200
    except AssertionError:
        pass
    web_page = webdata.content.decode()
    data = re_format.findall(webdata.content.decode())
    # logger.info(data)
    if data:
        data = eval(data[0])
        # logger.info(data)
        for item in data:
            data_id = item["id"]
            all_data[data_id] = item
            # if data_id not in json_data["news"]:
            #     json_data["news"][data_id] = item
        return all_data, web_page
    else:
        return False


def write_data_to_file(file, content):
    with open(file, 'w+') as f:
        json.dump(content, f, indent=4)
    f.close()


def read_data_from_file(file):
    with open(file, 'r+') as f:
        data = json.load(f)
    f.close()
    return data


def check_latest_data(backup_file, new_data):
    latest_data_list = []
    if os.path.exists(backup_file):
        backup_data = read_data_from_file(backup_file)
        for key, values in new_data.items():
            if str(key) not in backup_data.keys():
                latest_data_list.append(values)
        return latest_data_list
    else:
        logger.info(backup_file + " not exists, init env, will not send the msg this time")
        write_data_to_file(backup_file, new_data)
        return


def post_data(secret_key_list, **kwargs):
    for secret_key in secret_key_list:
        address = "https://sc.ftqq.com/%s.send" % secret_key.strip()
        data = {"text": "%s" % kwargs["title"],
                "desp": "####%s  \n#####确诊:%s例，疑似:%s例，死亡:%s例，治愈:%s例  \n#####消息获取时间：%s  \n#####消息来源：%s  \n######消息链接：%s  \n######丁香园链接：%s  \n" % (
                    kwargs["summary"], kwargs["confirmed_count"], kwargs["suspected_count"], kwargs["dead_count"],
                    kwargs["cured_count"], kwargs["pub_date_str"], kwargs["info_source"], kwargs["source_url"], url)
                }
        try:
            resp = requests.post(address, data=data)
            assert resp.status_code == 200
            logger.info("send %s to %s success" % (kwargs["title"], secret_key))
        except AssertionError:
            logger.error("send %s to %s failed" % (kwargs["title"], secret_key))


def parse_num_data(web_page, regx):
    re_format = re.compile(regx)
    data = re_format.findall(web_page)
    if data:
        return data[0]
    else:
        return 0, 0, 0, 0


def main(backup_file, sckey_list):
    # 从丁香园得到数据，更新到json_data
    new_data, web_page = get_data(url, reg)
    old_data = read_data_from_file(backup_file)
    # 和backup文件对比，确认是否有数据更新, 推送出最新的数据
    # 如果backup文件不存在则将所有数据写入文件，不推送消息
    latest_data = check_latest_data(backup_file, new_data)
    num_data = parse_num_data(web_page, regx=data_reg)
    if latest_data and new_data:
        for item in latest_data:
            id_num = item["id"]
            pub_date_str = item["pubDateStr"]
            title = item["title"]
            summary = item["summary"]
            info_source = item["infoSource"]
            source_url = item["sourceUrl"]
            confirmed_count = num_data[0]
            suspected_count = num_data[1]
            cured_count = num_data[2]
            dead_count = num_data[3]
            # post_data(sckey_list, title=title, pub_date_str=pub_date_str, summary=summary, info_source=info_source,
            #           source_url=source_url, confirmed_count=confirmed_count, suspected_count=suspected_count,
            #           cured_count=cured_count, dead_count=dead_count)
            old_data[id_num] = item
            write_data_to_file(backup_file, old_data)

        logger.info(latest_data)
    logger.info("no new item")


def get_key_list(file):
    with open(file, "r") as f:
        lines = f.readlines()
    f.close()
    return lines


if __name__ == "__main__":
    sckey_file = "sckeys"
    data_back_file = "nCoV_data_backup.json"
    sckey_list = get_key_list(sckey_file)
    while True:
        main(data_back_file, sckey_list=sckey_list)
        time.sleep(60)
    # post_data(sckey)
