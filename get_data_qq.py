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

url = "https://view.inews.qq.com/g2/getOnsInfo?name=disease_other&callback=jQuery341048941168800821044_1583926995704&_=1583926995705"
# 实时消息推送reg
reg = r'\(\{\"ret\":0,\"data\":\"(.*)\"\}\)'
# 统计数据reg
# [确诊， 疑似， 治愈， 死亡， 重症， 疑似较昨日新增， 确诊较昨日新增， 治愈较昨日新增， 死亡较昨日新增， 重症较昨日新增]
data_reg = r'confirmedCount":(\d+),"suspectedCount":(\d+),"curedCount":(\d+),"deadCount":(\d+),"seriousCount":(\d+),"suspectedIncr":(\d+),"confirmedIncr":(\d+),"curedIncr":(\d+),"deadIncr":(\d+),"seriousIncr":(\d+),"virus'


def get_data(urlx, regx):
    article_data = {}
    re_format = re.compile(regx)
    try:
        param = {
            "name": "disease_other",
            "callback": "jQuery341048941168800821044",
            "_": round(time.time())
        }
        webdata = requests.get(urlx, params=json.dumps(param))
        assert webdata.status_code == 200
    except AssertionError as e:
        logger.error(e)
        pass
    web_page = webdata.content.decode()
    logger.info(web_page)
    data = re_format.findall(webdata.content.decode())
    # logger.info(data)
    if data:
        data = data[0].replace("\\", "")
        data = json.loads(data)
        # logger.info(data)
        for item in data["articleList"]:
            data_id = item["cmsId"]
            article_data[data_id] = item
            # if data_id not in json_data["news"]:
            #     json_data["news"][data_id] = item
        return data, article_data, data['chinaDayAddList']
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
    qq_url = "https://news.qq.com/zt2020/page/feiyan.htm#/"
    for secret_key in secret_key_list:
        address = "https://sc.ftqq.com/%s.send" % secret_key.strip()
        if len(kwargs) > 5:
            data = {"text": "%s" % kwargs["title"],
                    "desp": "####%s  \n#####新增数据：确诊新增:%s例，疑似新增:%s例，死亡新增:%s例，治愈新增:%s例  \n#####消息来源：%s  \n######消息链接：%s  \n#####消息获取时间：%s  \n######腾讯新闻：%s  \n" % (
                        kwargs["summary"], kwargs["confirmed_inc"], kwargs["suspected_inc"],  kwargs["dead_inc"],
                        kwargs["cured_inc"], kwargs["info_source"], kwargs["source_url"], kwargs["pub_date_str"], qq_url)
                    }
        else:
            data = {"text": "%s" % kwargs["title"],
                    "desp": "####%s  \n#####消息获取时间：%s  \n#####消息来源：%s  \n######消息链接：%s  \n" % (
                        kwargs["summary"], kwargs["pub_date_str"], kwargs["info_source"], kwargs["source_url"],)
                    }
        try:
            resp = requests.post(address, data=data)
            assert resp.status_code == 200
            logger.info("send %s to %s success" % (kwargs["title"], secret_key))
        except AssertionError:
            logger.error("send %s to %s failed" % (kwargs["title"], secret_key))


def parse_num_data(num_date):
    if num_date:
        item = num_date[-1]
        confirm = item['confirm']
        suspect = item['suspect']
        dead = item['dead']
        heal = item['heal']
        importedCase = item['importedCase']
        return confirm, suspect, dead, heal, importedCase
    else:
        return 0, 0, 0, 0, 0


def main(backup_file, sckey_list):
    # 从丁香园得到数据，更新到json_data
    data = get_data(url, reg)
    if data:
        all_data, article_data, add_num_data = data
        # 和backup文件对比，确认是否有数据更新, 推送出最新的数据
        # 如果backup文件不存在则将所有数据写入文件，不推送消息
        latest_data = check_latest_data(backup_file, article_data)
        old_data = read_data_from_file(backup_file)
        num_data = parse_num_data(add_num_data)
        if latest_data and all_data:
            for item in latest_data:
                id_num = item["cmsId"]
                pub_date_str = item["publish_time"]
                title = item["title"]
                summary = item["desc"]
                info_source = item["media"]
                source_url = item["url"]
                try:
                    confirm_inc, suspect_inc, dead_inc, heal_inc, importedCase_inc = num_data
                    post_data(sckey_list, title=title, pub_date_str=pub_date_str, summary=summary, info_source=info_source,
                              source_url=source_url, confirmed_inc=confirm_inc, suspected_inc=suspect_inc,
                              cured_inc=heal_inc, dead_inc=dead_inc, importedCase=importedCase_inc)
                except Exception as err:
                    logging.error(err)
                    # logging.debug(num_data)
                    post_data(sckey_list, title=title, pub_date_str=pub_date_str, summary=summary, info_source=info_source,
                              source_url=source_url)
                old_data[id_num] = item
                write_data_to_file(backup_file, old_data)

            logger.info(latest_data)
        logger.info("no new item")
    logger.warning("no data get")


def get_key_list(file):
    with open(file, "r") as f:
        lines = f.readlines()
    f.close()
    return lines


if __name__ == "__main__":
    sckey_file = "sckey_file"
    data_back_file = "nCoV_data_backup_qq.json"
    sckey_list = get_key_list(sckey_file)
    while True:
        main(data_back_file, sckey_list=sckey_list)
        time.sleep(6)
    # post_data(sckey)
