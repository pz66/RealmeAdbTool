import json
import re
import time
from urllib import request

HEADERS = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36'}
HEADERS_wandoujia = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36',"cookie": "_uab_collina=169323554989581412030976; _ga=GA1.2.1305880941.1693234928; _gid=GA1.2.1556665379.1693234928; track_id=aligames_platform_ug_1693234933098_b93857d8-9e73-4995-bd76-4ebc1527a9a9; x5sec=7b22617365727665723b32223a223038386237306136396139626135323264333065366264396262306662366166434c487973716347454b4f4e755045464d4d534e332b774251414d3d222c22733b32223a2238303239333364653966373439396339227d; ctoken=F7SeXa54HYnIBhwf33bdDjyf; sid=83626570169323551073020801867673; sid.sig=xwl5YSFUm4t13c8YAx74-L6xIcVw29gf2ENMDCZ3Zyw; _gat=1; _bl_uid=Lplw9lw9vz1083qL87szz690U5R4; _pwid=53129500169323555000727502699123; wdj_source=direct; uuid=2c7a2765-76f0-4032-9bb7-54f0c4fa948e; _uToken=T2gAssAMuSOY3HYwIb_hY1rb8uDHkJa5EI_VQHl7Yx3v_iVbWQI2BD6PdD3MrZo65ds%3D; isg=BG5utWJGhrXN_fLRflEnSfXAv8QwbzJpYY1BcJg34HEsew7VAfqFeSRpNeGXuCqB"}

NAMES = {
    "com.coloros.onekeylockscreen": "一键锁屏",
    "com.ccb.longjiLife": "建行生活",
    "com.duolabao.customer": "京东收银",
    "com.yitong.mbank.psbc": "邮储银行",
    "com.coloros.backuprestore": "备份与恢复",
    "com.unionpay.tsmservice": "兴业银行",
    "com.teslacoilsw.launcher": "Nova桌面",
    "com.android.bankabc": "农行掌上银行",
    "com.lerist.fakelocation": "Fake Location",
    "com.android.email": "邮箱",
    "com.kingsoft.moffice_pro": "WPS Office",
    "cn.wps.moffice.lite": "WPS Office",
    "com.huawei.genexcloud.speedtest": "花瓣测速",
    "com.citibank.mobile.cn": "花旗银行",
    "org.zwanoo.android.speedtest": "SpeedTest",

}

def get_name_from_qq(item):
    try:
        url = f"https://sj.qq.com/appdetail/{item}"
        req = request.Request(url=url, headers=HEADERS)
        res = request.urlopen(req).read().decode('utf-8')
        find_name = re.search(r"<title>(.*?)官方新版本", res, re.I)
        if find_name:
            return find_name.group(1)
    except:
        pass

def get_name_from_wandoujia(item):
    try:
        url = f"https://www.wandoujia.com/apps/{item}"
        req = request.Request(url=url, headers=HEADERS_wandoujia)
        res = request.urlopen(req).read().decode('utf-8')
        find_name = re.search(r"<title>(.*?)(下载|相似)", res, re.I)
        if find_name:
            return find_name.group(1)
    except:
        pass

def main():
    try:
        result = json.load(open("_app_names.json", 'r', encoding='utf-8'))
    except:
        result = dict()
    try:
        packages = json.load(open("_my_installed_apps.json", 'r', encoding='utf-8'))
    except:
        return

    for each in packages:
        if each not in result:
            print(each, )
            # pass
            # app_name = get_name_from_qq(each)
            # print(app_name, each)
            # if app_name:
            #     result[each] = app_name
            # time.sleep(1)
        continue
        url = f"https://www.coolapk.com/apk/{each}"
        req = request.Request(url=url, headers=HEADERS)
        try:
            res = request.urlopen(req).read().decode('utf-8')
            find_name = re.search(r"<title>(.*?)\(", res, re.I)

            if find_name:
                app_name = find_name.group(1)
                # print(each, app_name)
                result[each] = app_name
        except Exception as e:
            print(each, "Not Found")
            continue
    result.update(NAMES)
    json.dump(result, open("_app_names.json", 'w', encoding='utf-8'), indent=4)
    print("finish")


if __name__ == "__main__":
    main()
    # print(get_name_from_qq("com.qiyi.video"))
