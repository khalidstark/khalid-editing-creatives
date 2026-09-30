# -*- coding: utf-8 -*-
"""مسارات المهارة وبيانات المستخدم — مكان واحد يعرّفها للكل.

SKILL : مجلد المهارة نفسه (للقراءة فقط — ما نكتب فيه شي).
HOME  : مجلد بيانات المستخدم. كل شي يخصّه ينحفظ هنا ويبقى بين المقاطع:
        profile.json (هويته) · voice.md (لغته) · mechanisms.json + LEDGER.md (سجل آلياته)
        dialect.json (لهجته) · sounds/ (مكتبة أصواته) · refs/ (مراجعه) · tools/ (أدوات منزّلة)
        الافتراضي: ~/Documents/khalid-editing-creatives — ويتغيّر بمتغيّر البيئة KEC_HOME (أو VEB_HOME القديم).
        لو عنده مجلد الاسم القديم (~/Documents/video-editor-bassam) ومافيه الجديد، نكمّل على القديم عشان مشاريعه ما تضيع.
"""
import os, json
SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DOCS = os.path.join(os.path.expanduser("~"), "Documents")
_NEW, _OLD = os.path.join(_DOCS, "khalid-editing-creatives"), os.path.join(_DOCS, "video-editor-bassam")
HOME = (os.environ.get("KEC_HOME") or os.environ.get("VEB_HOME")
        or (_OLD if os.path.isdir(_OLD) and not os.path.isdir(_NEW) else _NEW))

def ensure():
    for d in ("", "sounds", "refs", "tools"):
        os.makedirs(os.path.join(HOME, d), exist_ok=True)
    return HOME

def data(*p):
    return os.path.join(HOME, *p)

def load(name, default):
    p = data(name)
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as f:
        return json.load(f)

EMPTY_LEDGER = {"videos": [], "mechs": {}, "rejected": [], "sounds": {}}
