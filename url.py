import re


def a_html(matchobj: re.Match):
    url = matchobj.group(0)

    return f"""<a href="{url}" target="_blank" >{url}</a>"""


def beautiful_url(s):
    return re.sub(r'https?://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]', repl=a_html, string=s)
