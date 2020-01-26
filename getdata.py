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
formatter = logging.Formatter('%(levelname)-7s: %(message)s')
logger = logging.getLogger('')
console.setLevel(logging.DEBUG)
console.setFormatter(formatter)
logger.addHandler(console)

url = "https://3g.dxy.cn/newh5/view/pneumonia"
reg = r'<script id="getTimelineService">.+?window.getTimelineService\s=\s(.*?\])}catch\(e\){}<\/script>'

json_data = {
    "news": {}
}


def get_data(urlx, regx):
    all_data = {}
    format = re.compile(regx)
    try:
        webdata = requests.get(urlx)
        assert webdata.status_code == 200
    except AssertionError:
        pass
    data = format.findall(webdata.content.decode())
    # logger.info(data)
    if data:
        data = eval(data[0])
        # logger.info(data)
        for item in data:
            data_id = item["id"]
            all_data[data_id] = item
            # if data_id not in json_data["news"]:
            #     json_data["news"][data_id] = item
        return all_data
    else:
        return False


def write_data_to_file(file, content):
    with open(file, 'w+') as f:
        json.dump(content, f, indent=4)


def read_data_from_file(file):
    with open(file, 'r+') as f:
        data = json.load(f)
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


def post_data(secret_key, **kwargs):
    address = "https://sc.ftqq.com/%s.send" % secret_key
    data = {"text": "%s" % kwargs["title"],
            "desp": "###%s  \n###%s  \n###%s  \n###%s  \n" % (
                kwargs["summary"], kwargs["pub_date_str"], kwargs["info_source"], kwargs["source_url"])
            }
    resp = requests.post(address, data=data)
    assert resp.status_code == 200
    logger.info(resp.content)


def main(backup_file, sckey):
    # 从丁香园得到数据，更新到json_data
    new_data = get_data(url, reg)
    old_data = read_data_from_file(backup_file)
    # 和backup文件对比，确认是否有数据更新, 推送出最新的数据
    # 如果backup文件不存在则将所有数据写入文件，不推送消息
    latest_data = check_latest_data(backup_file, new_data)
    if latest_data and new_data:
        for item in latest_data:
            id_num = item["id"]
            pub_date_str = item["pubDateStr"]
            title = item["title"]
            summary = item["summary"]
            info_source = item["infoSource"]
            source_url = item["sourceUrl"]
            post_data(sckey, title=title, pub_date_str=pub_date_str, summary=summary, info_source=info_source,
                      source_url=source_url)
            old_data[id_num] = item
            write_data_to_file(backup_file, old_data)

        logger.info(latest_data)
    logger.info("nothing new items")


if __name__ == "__main__":
    sckey = "SCU77930T7c74bd2ae6168e9b00e6d30f75ccd6fd5e2110a3815d8"
    data_back_file = "nCoV_data_backup.json"
    while True:
        main(data_back_file, sckey=sckey)
        time.sleep(60)
    # post_data(sckey)
