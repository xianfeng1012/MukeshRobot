import flag
from countryinfo import CountryInfo

from MukeshRobot import BOT_USERNAME
from MukeshRobot import telethn as borg
from MukeshRobot.events import register


@register(pattern="^/country (.*)")
async def msg(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    lol = input_str
    country = CountryInfo(lol)
    try:
        a = country.info()
    except:
        await event.reply("暂时无法获取该国家的信息。")
    name = a.get("name")
    bb = a.get("altSpellings")
    hu = ""
    for p in bb:
        hu += p + ",  "

    area = a.get("area")
    borders = ""
    hell = a.get("borders")
    for fk in hell:
        borders += fk + ",  "

    call = ""
    WhAt = a.get("callingCodes")
    for what in WhAt:
        call += what + "  "

    capital = a.get("capital")
    currencies = ""
    fker = a.get("currencies")
    for FKer in fker:
        currencies += FKer + ",  "

    HmM = a.get("demonym")
    geo = a.get("geoJSON")
    pablo = geo.get("features")
    Pablo = pablo[0]
    PAblo = Pablo.get("geometry")
    EsCoBaR = PAblo.get("type")
    iso = ""
    iSo = a.get("ISO")
    for hitler in iSo:
        po = iSo.get(hitler)
        iso += po + ",  "
    fla = iSo.get("alpha2")
    nox = fla.upper()
    okie = flag.flag(nox)

    languages = a.get("languages")
    lMAO = ""
    for lmao in languages:
        lMAO += lmao + ",  "

    nonive = a.get("nativeName")
    waste = a.get("population")
    reg = a.get("region")
    sub = a.get("subregion")
    tik = a.get("timezones")
    tom = ""
    for jerry in tik:
        tom += jerry + ",   "

    GOT = a.get("tld")
    lanester = ""
    for targaryen in GOT:
        lanester += targaryen + ",   "

    wiki = a.get("wiki")

    caption = f"""<b><u>国家信息查询成功</b></u>

<b>国家名称：</b> {name}
<b>别名拼写：</b> {hu}
<b>国土面积：</b> {area} 平方公里
<b>接壤国家：</b> {borders}
<b>国际拨号码：</b> {call}
<b>首都：</b> {capital}
<b>货币：</b> {currencies}
<b>国旗：</b> {okie}
<b>国民名称：</b> {HmM}
<b>国家类型：</b> {EsCoBaR}
<b>ISO 代码：</b> {iso}
<b>官方语言：</b> {lMAO}
<b>本地名称：</b> {nonive}
<b>人口：</b> {waste}
<b>所属地区：</b> {reg}
<b>次级地区：</b> {sub}
<b>时区：</b> {tom}
<b>顶级域名：</b> {lanester}
<b>维基百科：</b> {wiki}

<u>信息由 @{BOT_USERNAME} 提供</u>
"""

    await borg.send_message(
        event.chat_id,
        caption,
        parse_mode="HTML",
        link_preview=None,
    )


__help__ = """
查询指定国家的详细信息

 ❍ /country <国家名称> *:* 查询指定国家的详细信息
"""

__mod_name__ = "国家信息"
