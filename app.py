from __future__ import annotations

import hashlib
import json
import random
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT_DIR = Path(__file__).resolve().parent
STATIC_DIR = ROOT_DIR / "static"
TEMPLATE_DIR = ROOT_DIR / "templates"


DISHES: list[dict[str, Any]] = [
    {
        "name": "桂花蜜汁小番茄",
        "course": "appetizer",
        "price": 48,
        "serves": (2, 10),
        "luxury": 1,
        "surprise": 1,
        "tags": {"fresh", "light", "vegetarian", "spring", "sweet"},
        "occasions": {"date", "family", "birthday"},
        "description": "冰镇番茄浸入桂花蜜露，酸甜开胃，适合作为晚宴的第一口。",
        "presentation": "盛在磨砂玻璃盏里，顶部点一朵桂花糖片，轻盈又清爽。",
    },
    {
        "name": "潮汕卤水双拼",
        "course": "appetizer",
        "price": 88,
        "serves": (3, 10),
        "luxury": 2,
        "surprise": 1,
        "tags": {"classic", "savory", "pork", "poultry"},
        "occasions": {"business", "family", "friends"},
        "description": "卤香温润，组合了卤水鹅片与慢卤豆干，是私房菜里很稳妥的迎宾冷盘。",
        "presentation": "扇形排盘配酸姜丝，颜色稳重，适合正式宴席。",
    },
    {
        "name": "低温葱油鸡卷",
        "course": "appetizer",
        "price": 78,
        "serves": (2, 8),
        "luxury": 2,
        "surprise": 2,
        "tags": {"fresh", "light", "cantonese", "poultry"},
        "occasions": {"date", "business", "family"},
        "description": "鸡腿肉低温处理后卷入葱姜冻，口感细嫩，香气克制而高级。",
        "presentation": "切成厚片配青葱油珠，像一道精致的西式前菜。",
    },
    {
        "name": "椒麻手撕杏鲍菇",
        "course": "appetizer",
        "price": 58,
        "serves": (2, 8),
        "luxury": 1,
        "surprise": 2,
        "tags": {"spicy", "vegetarian", "creative", "savory"},
        "occasions": {"friends", "birthday", "family"},
        "description": "以椒麻油拌入手撕杏鲍菇，香气直给，能很快把餐桌气氛带起来。",
        "presentation": "铺在黑石板上，边缘点少量青花椒油，层次鲜明。",
    },
    {
        "name": "黑松露脆皮豆腐",
        "course": "appetizer",
        "price": 72,
        "serves": (2, 10),
        "luxury": 2,
        "surprise": 2,
        "tags": {"creative", "vegetarian", "crispy", "savory"},
        "occasions": {"business", "date", "birthday"},
        "description": "外脆里嫩的豆腐带有轻微松露香，适合做一道人见人爱的过渡菜。",
        "presentation": "方块堆叠并撒上细碎香草，视觉简洁但有记忆点。",
    },
    {
        "name": "陈皮风干牛肉配酸梅番茄",
        "course": "appetizer",
        "price": 96,
        "serves": (2, 8),
        "luxury": 3,
        "surprise": 3,
        "tags": {"beef", "creative", "savory", "fragrant"},
        "occasions": {"business", "friends", "date"},
        "description": "陈皮香让牛肉更有回甘，和酸梅番茄搭配后酸、鲜、香层次丰富。",
        "presentation": "牛肉薄切卷成小花束，适合提升餐桌第一印象。",
    },
    {
        "name": "花胶瑶柱炖鸡汤",
        "course": "soup",
        "price": 188,
        "serves": (2, 10),
        "luxury": 4,
        "surprise": 1,
        "tags": {"seafood", "poultry", "classic", "light", "tonic"},
        "occasions": {"business", "family", "birthday"},
        "description": "汤底清亮但胶质丰润，兼顾体面与滋补，是私房宴的经典配置。",
        "presentation": "一人一盅更显仪式感，揭盖时香气会非常完整。",
    },
    {
        "name": "竹荪菌皇炖老鸡汤",
        "course": "soup",
        "price": 158,
        "serves": (2, 10),
        "luxury": 3,
        "surprise": 1,
        "tags": {"poultry", "light", "classic", "fresh"},
        "occasions": {"family", "date", "business"},
        "description": "竹荪和菌香让汤体更显干净鲜甜，适合偏清雅口味的人群。",
        "presentation": "白瓷盅上桌，汤色透亮，容易营造温润的第一段节奏。",
    },
    {
        "name": "松茸姬松茸清炖汤",
        "course": "soup",
        "price": 148,
        "serves": (2, 8),
        "luxury": 3,
        "surprise": 2,
        "tags": {"vegetarian", "light", "fresh", "tonic"},
        "occasions": {"date", "family", "birthday"},
        "description": "以菌香做主线，没有重油重盐，适合清淡或不吃海鲜的定制席面。",
        "presentation": "汤盅边缘点缀嫩芽，呈现山野感和季节感。",
    },
    {
        "name": "酸汤时蔬海鲜羹",
        "course": "soup",
        "price": 168,
        "serves": (3, 10),
        "luxury": 3,
        "surprise": 3,
        "tags": {"seafood", "spicy", "creative", "fresh"},
        "occasions": {"friends", "birthday", "business"},
        "description": "微酸的汤底配海鲜和时蔬，刺激食欲，适合想要一点新鲜感的餐桌。",
        "presentation": "金黄色汤面点红油珠，视觉上很有食欲。",
    },
    {
        "name": "清蒸东星斑佐豉油皇",
        "course": "seafood",
        "price": 368,
        "serves": (4, 10),
        "luxury": 5,
        "surprise": 1,
        "tags": {"seafood", "classic", "cantonese", "light", "fresh"},
        "occasions": {"business", "birthday", "family"},
        "description": "火候克制，鱼肉细嫩，是偏粤式审美里很稳的主角菜。",
        "presentation": "整鱼上桌配热油葱丝，仪式感和分享感都很强。",
    },
    {
        "name": "黄椒酱焗波士顿龙虾",
        "course": "seafood",
        "price": 428,
        "serves": (4, 10),
        "luxury": 5,
        "surprise": 3,
        "tags": {"seafood", "creative", "fragrant", "premium"},
        "occasions": {"business", "birthday", "date"},
        "description": "黄椒酱带出龙虾甜味，鲜中有一点轻微辛香，属于高识别度的招牌菜。",
        "presentation": "龙虾对半开边盛盘，视觉张力很足，适合作为菜单高潮。",
    },
    {
        "name": "杏香百合炒带子",
        "course": "seafood",
        "price": 238,
        "serves": (2, 8),
        "luxury": 4,
        "surprise": 2,
        "tags": {"seafood", "light", "fresh", "spring"},
        "occasions": {"date", "family", "business"},
        "description": "带子鲜甜，百合和杏仁片让香气更轻盈，是很讨喜的一道清鲜主菜。",
        "presentation": "白盘留白感强，适合做菜单中段的清雅亮点。",
    },
    {
        "name": "香辣脆皮大虾球",
        "course": "seafood",
        "price": 258,
        "serves": (3, 10),
        "luxury": 3,
        "surprise": 2,
        "tags": {"seafood", "spicy", "crispy", "savory"},
        "occasions": {"friends", "birthday", "family"},
        "description": "外皮酥脆、虾肉弹牙，偏热闹型餐桌会很喜欢这类有冲击力的口感。",
        "presentation": "高脚盘堆叠出高度，适合作为中段气氛菜。",
    },
    {
        "name": "金蒜银丝蒸扇贝",
        "course": "seafood",
        "price": 198,
        "serves": (2, 8),
        "luxury": 3,
        "surprise": 1,
        "tags": {"seafood", "classic", "fresh", "cantonese"},
        "occasions": {"family", "business", "birthday"},
        "description": "蒜香和粉丝的接受度非常高，作为共享型海鲜菜很稳。",
        "presentation": "扇贝逐只摆放，适合多人分享，也能照顾视觉完整度。",
    },
    {
        "name": "脆皮沙姜鸡",
        "course": "poultry",
        "price": 188,
        "serves": (3, 10),
        "luxury": 2,
        "surprise": 1,
        "tags": {"poultry", "classic", "fragrant", "crispy"},
        "occasions": {"family", "friends", "business"},
        "description": "皮脆肉嫩，沙姜香突出，是南方私房宴里很受欢迎的压轴鸡菜。",
        "presentation": "整鸡斩件后错落堆叠，配热油香葱，香气直接。",
    },
    {
        "name": "花雕熟醉鸡",
        "course": "poultry",
        "price": 168,
        "serves": (2, 8),
        "luxury": 3,
        "surprise": 2,
        "tags": {"poultry", "light", "fresh", "fragrant"},
        "occasions": {"date", "business", "family"},
        "description": "酒香温和、肉质细嫩，适合偏精致和清雅路线的餐桌。",
        "presentation": "冷食切片配酒冻，能让整套菜单更显细腻。",
    },
    {
        "name": "松露葱烧走地鸡",
        "course": "poultry",
        "price": 228,
        "serves": (3, 10),
        "luxury": 4,
        "surprise": 3,
        "tags": {"poultry", "creative", "fragrant", "premium"},
        "occasions": {"business", "birthday", "date"},
        "description": "私房做法把葱香和松露香融合得更柔和，适合想要一点高级变化的菜单。",
        "presentation": "鸡块覆上浅棕色酱汁，盘边配炭烤葱段，层次比较完整。",
    },
    {
        "name": "陈皮黑豚叉烧",
        "course": "meat",
        "price": 198,
        "serves": (3, 10),
        "luxury": 3,
        "surprise": 2,
        "tags": {"pork", "classic", "cantonese", "sweet", "fragrant"},
        "occasions": {"business", "family", "birthday"},
        "description": "甜润中带陈皮回香，是很有粤式私房气质的一道肉菜。",
        "presentation": "长条厚切并刷亮面酱汁，适合做菜单后段的稳定收束。",
    },
    {
        "name": "梅子酱慢烤和牛粒",
        "course": "meat",
        "price": 328,
        "serves": (2, 8),
        "luxury": 5,
        "surprise": 3,
        "tags": {"beef", "creative", "premium", "savory"},
        "occasions": {"business", "date", "birthday"},
        "description": "和牛粒油香明显，以梅子酱提味后更显平衡，适合高预算菜单。",
        "presentation": "深色石板盘搭配烤时蔬，现代感较强。",
    },
    {
        "name": "紫苏藤椒小羊排",
        "course": "meat",
        "price": 288,
        "serves": (3, 8),
        "luxury": 4,
        "surprise": 3,
        "tags": {"spicy", "creative", "premium", "savory"},
        "occasions": {"friends", "birthday", "business"},
        "description": "紫苏香和藤椒麻感叠在一起，适合想把菜单做得更有记忆点的场景。",
        "presentation": "羊排立式摆盘，张力强，很适合做视觉主菜。",
    },
    {
        "name": "冰烧脆梅肉",
        "course": "meat",
        "price": 178,
        "serves": (3, 10),
        "luxury": 2,
        "surprise": 1,
        "tags": {"pork", "classic", "crispy", "savory"},
        "occasions": {"family", "friends", "birthday"},
        "description": "表皮酥香、肉层分明，是聚餐时非常容易被快速吃完的一道肉菜。",
        "presentation": "脆皮切块后搭配酸梅酱，适合热闹氛围。",
    },
    {
        "name": "金汤竹笙浸菜苗",
        "course": "vegetable",
        "price": 86,
        "serves": (2, 10),
        "luxury": 2,
        "surprise": 1,
        "tags": {"vegetarian", "light", "fresh", "spring"},
        "occasions": {"date", "family", "business"},
        "description": "菜苗和竹笙的口感清脆，能让整套餐更透气，避免后段发腻。",
        "presentation": "浅金色汤底衬托嫩绿色菜苗，视觉上很干净。",
    },
    {
        "name": "炭烤有机茄子配芝麻酱",
        "course": "vegetable",
        "price": 92,
        "serves": (2, 8),
        "luxury": 2,
        "surprise": 2,
        "tags": {"vegetarian", "creative", "savory", "fragrant"},
        "occasions": {"friends", "date", "birthday"},
        "description": "烤香和芝麻酱的坚果香很突出，适合让菜单有一点当代私房菜气质。",
        "presentation": "长条茄子刷酱后加芝麻碎，深浅对比明显。",
    },
    {
        "name": "清炒山苏配橄榄菜",
        "course": "vegetable",
        "price": 78,
        "serves": (2, 10),
        "luxury": 1,
        "surprise": 1,
        "tags": {"vegetarian", "classic", "light", "fresh"},
        "occasions": {"family", "business", "friends"},
        "description": "山苏爽脆，橄榄菜咸香提味，是一道人群接受度很高的时蔬。",
        "presentation": "简单清亮，适合作为餐桌的换气点。",
    },
    {
        "name": "蟹粉扒时蔬",
        "course": "vegetable",
        "price": 128,
        "serves": (3, 10),
        "luxury": 4,
        "surprise": 2,
        "tags": {"seafood", "fresh", "premium", "cantonese"},
        "occasions": {"business", "birthday", "family"},
        "description": "以蟹粉裹住脆嫩时蔬，鲜味浓度更高，适合高预算席面。",
        "presentation": "金黄酱汁覆在青绿时蔬上，色彩对比很抓眼。",
    },
    {
        "name": "鲍汁菌菇焖伊面",
        "course": "staple",
        "price": 98,
        "serves": (2, 10),
        "luxury": 2,
        "surprise": 1,
        "tags": {"classic", "savory", "fragrant"},
        "occasions": {"family", "business", "birthday"},
        "description": "伊面吸满酱汁，适合做整套菜单的收尾主食，稳妥又有宴席感。",
        "presentation": "砂锅上桌会更有温度，也方便多人分食。",
    },
    {
        "name": "松露野菌炒饭",
        "course": "staple",
        "price": 108,
        "serves": (2, 10),
        "luxury": 3,
        "surprise": 2,
        "tags": {"vegetarian", "creative", "fragrant"},
        "occasions": {"date", "business", "friends"},
        "description": "松露香气明显，搭配野菌能让主食也保持高级感，不会显得只是填饱肚子。",
        "presentation": "压模成圆塔状，适合精致路线菜单。",
    },
    {
        "name": "海鲜脆米泡饭",
        "course": "staple",
        "price": 138,
        "serves": (3, 10),
        "luxury": 3,
        "surprise": 3,
        "tags": {"seafood", "creative", "fresh"},
        "occasions": {"birthday", "friends", "business"},
        "description": "桌边冲入热汤，脆米声响会带来不错的互动感，适合做一桌饭局里的记忆点。",
        "presentation": "适合安排桌边服务，是菜单里很好的记忆点。",
    },
    {
        "name": "腊味荷叶饭",
        "course": "staple",
        "price": 96,
        "serves": (3, 10),
        "luxury": 2,
        "surprise": 1,
        "tags": {"pork", "classic", "savory"},
        "occasions": {"family", "friends", "birthday"},
        "description": "荷叶香气温和，偏传统宴席的收尾方式，很适合家宴或朋友聚餐。",
        "presentation": "拆开荷叶时香气会一下子出来，氛围感不错。",
    },
    {
        "name": "桂花酒酿小圆子",
        "course": "dessert",
        "price": 56,
        "serves": (2, 10),
        "luxury": 1,
        "surprise": 1,
        "tags": {"classic", "light", "sweet"},
        "occasions": {"family", "date", "birthday"},
        "description": "酒酿香轻柔，适合做温和的收尾，不会压住整餐回味。",
        "presentation": "白瓷小盅单人份更显精致。",
    },
    {
        "name": "茉莉奶冻配龙井蜜桃",
        "course": "dessert",
        "price": 68,
        "serves": (2, 8),
        "luxury": 2,
        "surprise": 2,
        "tags": {"fresh", "light", "creative", "sweet"},
        "occasions": {"date", "business", "birthday"},
        "description": "茶香甜品比传统奶味更轻，能延续私房菜的细腻气质。",
        "presentation": "玻璃杯分层装盘，颜色柔和，很适合拍照展示。",
    },
    {
        "name": "杨枝甘露慕斯杯",
        "course": "dessert",
        "price": 72,
        "serves": (2, 10),
        "luxury": 2,
        "surprise": 2,
        "tags": {"fresh", "sweet", "creative"},
        "occasions": {"birthday", "friends", "family"},
        "description": "芒果和西柚风味很讨喜，作为聚餐尾声会让情绪比较明亮。",
        "presentation": "适合做成单杯甜点，层次清晰。",
    },
]


COURSE_LABELS = {
    "appetizer": "开胃前菜",
    "soup": "汤品",
    "seafood": "海鲜主菜",
    "poultry": "鸡鸭禽类",
    "meat": "肉类热菜",
    "vegetable": "时蔬",
    "staple": "主食",
    "dessert": "甜品",
}


COURSE_BUDGET_WEIGHTS = {
    "appetizer": 0.08,
    "soup": 0.14,
    "seafood": 0.18,
    "poultry": 0.14,
    "meat": 0.16,
    "vegetable": 0.08,
    "staple": 0.08,
    "dessert": 0.06,
}


BUDGET_PROFILES = {
    "comfort": {"label": "舒心私宴", "per_person": 220, "luxury": 2},
    "signature": {"label": "招牌体验", "per_person": 320, "luxury": 3},
    "premium": {"label": "雅宴款待", "per_person": 460, "luxury": 4},
    "chef": {"label": "主厨定制", "per_person": 620, "luxury": 5},
}


OCCASION_PROFILES = {
    "family": {"label": "家宴", "tone": "温润、照顾长幼口味", "words": ["温润", "舒服", "家常但有体面"]},
    "business": {"label": "商务宴请", "tone": "体面、节奏稳、上桌有记忆点", "words": ["体面", "稳妥", "层次完整"]},
    "date": {"label": "纪念日晚餐", "tone": "轻盈、精致、适合慢慢吃", "words": ["精致", "清雅", "有氛围"]},
    "birthday": {"label": "庆生聚餐", "tone": "热闹、适合分享、视觉张力强", "words": ["热闹", "分享感强", "仪式感"]},
    "friends": {"label": "朋友聚会", "tone": "香气张扬、互动感强、容易带动气氛", "words": ["有话题", "下酒感", "记忆点足"]},
}


PREFERENCE_PROFILES = {
    "fresh": {"label": "鲜香清雅", "tags": {"fresh", "light", "cantonese", "spring"}, "accent": "藏鲜"},
    "spicy": {"label": "香辣过瘾", "tags": {"spicy", "crispy", "savory"}, "accent": "辛香"},
    "cantonese": {"label": "粤式经典", "tags": {"classic", "cantonese", "fragrant"}, "accent": "粤韵"},
    "creative": {"label": "创意融合", "tags": {"creative", "premium", "fragrant"}, "accent": "新私房"},
}


RESTRICTION_LABELS = {
    "no_spicy": "不吃辣",
    "no_seafood": "不要海鲜",
    "no_beef": "不吃牛肉",
    "light": "少油清淡",
}


RESTRICTION_BLOCKERS = {
    "no_spicy": {"spicy"},
    "no_seafood": {"seafood"},
    "no_beef": {"beef"},
}


SEASON_LABELS = {
    1: "冬藏",
    2: "冬藏",
    3: "春宴",
    4: "春宴",
    5: "春宴",
    6: "夏味",
    7: "夏味",
    8: "夏味",
    9: "秋馔",
    10: "秋馔",
    11: "秋馔",
    12: "冬藏",
}


DISH_INDEX = {dish["name"]: dish for dish in DISHES}


STATION_LABELS = {
    "cold": "冷菜台",
    "hot": "热菜灶",
    "soup": "炖煮炉",
    "steam": "蒸箱",
}


COURSE_START_OFFSETS = {
    "appetizer": 0,
    "soup": 0,
    "seafood": 8,
    "poultry": 10,
    "meat": 12,
    "vegetable": 18,
    "staple": 26,
    "dessert": 42,
}


COURSE_TARGET_OFFSETS = {
    "appetizer": 12,
    "soup": 22,
    "seafood": 32,
    "poultry": 36,
    "meat": 40,
    "vegetable": 48,
    "staple": 58,
    "dessert": 72,
}


SIMULATION_OCCASIONS = ["family", "business", "date", "birthday", "friends"]
SIMULATION_BUDGETS = ["comfort", "signature", "premium", "signature", "premium", "chef"]
SIMULATION_PREFERENCES = ["fresh", "cantonese", "spicy", "creative"]
SIMULATION_RESTRICTIONS = ["no_spicy", "no_seafood", "no_beef", "light"]


def stable_rng(payload: dict[str, Any]) -> random.Random:
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    digest = hashlib.md5(serialized.encode("utf-8")).hexdigest()
    return random.Random(int(digest[:8], 16))


def scaled_price(dish: dict[str, Any], diners: int) -> int:
    factor = min(2.3, 0.66 + diners * 0.13)
    return int(round(dish["price"] * factor / 10.0) * 10)


def normalize_request(payload: dict[str, Any]) -> dict[str, Any]:
    diners = max(2, min(int(payload.get("diners", 4)), 12))
    occasion = payload.get("occasion", "family")
    if occasion not in OCCASION_PROFILES:
        occasion = "family"

    budget = payload.get("budget", "signature")
    if budget not in BUDGET_PROFILES:
        budget = "signature"

    surprise = payload.get("surprise", "balanced")
    if surprise not in {"classic", "balanced", "adventurous"}:
        surprise = "balanced"

    preferences = [item for item in payload.get("preferences", []) if item in PREFERENCE_PROFILES]
    if not preferences:
        preferences = ["fresh", "cantonese"]

    restrictions = [item for item in payload.get("restrictions", []) if item in RESTRICTION_LABELS]
    notes = str(payload.get("notes", "")).strip()[:120]

    return {
        "diners": diners,
        "occasion": occasion,
        "budget": budget,
        "surprise": surprise,
        "preferences": preferences,
        "restrictions": restrictions,
        "notes": notes,
    }


def build_course_plan(request_data: dict[str, Any]) -> list[str]:
    diners = request_data["diners"]
    budget = request_data["budget"]
    restrictions = set(request_data["restrictions"])
    preferences = set(request_data["preferences"])

    appetizer_count = 1 if diners <= 3 else 2
    plan = ["appetizer"] * appetizer_count + ["soup"]

    if "no_seafood" not in restrictions:
        if diners <= 3:
            main_sequence = ["seafood", "poultry"]
        elif diners <= 5:
            main_sequence = ["seafood", "poultry", "meat"]
        elif diners <= 8:
            main_sequence = ["seafood", "poultry", "meat", "seafood" if budget in {"premium", "chef"} else "poultry"]
        else:
            main_sequence = ["seafood", "poultry", "meat", "seafood", "poultry"]
    else:
        main_sequence = ["poultry", "meat"]
        if diners >= 4:
            main_sequence.append("poultry")
        if diners >= 7:
            main_sequence.append("meat")

    if "spicy" in preferences and "no_spicy" not in restrictions and "meat" in main_sequence:
        main_sequence.sort(key=lambda item: 0 if item == "meat" else 1)
    if "fresh" in preferences and "no_seafood" not in restrictions and "seafood" in main_sequence:
        main_sequence.sort(key=lambda item: 0 if item == "seafood" else 1)

    plan.extend(main_sequence)
    plan.extend(["vegetable", "staple", "dessert"])

    if budget == "chef":
        plan.insert(2, "appetizer")
    return plan


def dish_is_allowed(dish: dict[str, Any], request_data: dict[str, Any]) -> bool:
    diners = request_data["diners"]
    serves_min, serves_max = dish["serves"]
    if diners < serves_min and serves_min - diners >= 3:
        return False

    blocked_tags: set[str] = set()
    for restriction in request_data["restrictions"]:
        blocked_tags |= RESTRICTION_BLOCKERS.get(restriction, set())
    if blocked_tags & dish["tags"]:
        return False

    return not (diners > serves_max and diners - serves_max >= 5)


def preference_bonus(dish: dict[str, Any], request_data: dict[str, Any]) -> float:
    bonus = 0.0
    for preference in request_data["preferences"]:
        bonus += len(dish["tags"] & PREFERENCE_PROFILES[preference]["tags"]) * 1.1
    return bonus


def occasion_bonus(dish: dict[str, Any], request_data: dict[str, Any]) -> float:
    occasion = request_data["occasion"]
    bonus = 2.2 if occasion in dish["occasions"] else 0.4
    if occasion == "business" and dish["luxury"] >= 4:
        bonus += 0.8
    if occasion == "date" and {"light", "fresh"} & dish["tags"]:
        bonus += 0.8
    if occasion in {"birthday", "friends"} and {"spicy", "crispy", "creative"} & dish["tags"]:
        bonus += 0.7
    return bonus


def surprise_bonus(dish: dict[str, Any], request_data: dict[str, Any]) -> float:
    desired = {"classic": 1, "balanced": 2, "adventurous": 3}[request_data["surprise"]]
    diff = abs(desired - int(dish["surprise"]))
    return 2.0 - diff * 0.8


def budget_bonus(dish: dict[str, Any], request_data: dict[str, Any], course: str) -> float:
    budget_profile = BUDGET_PROFILES[request_data["budget"]]
    target_luxury = budget_profile["luxury"]
    luxury_fit = 1.8 - abs(target_luxury - int(dish["luxury"])) * 0.6

    target_total = budget_profile["per_person"] * request_data["diners"]
    desired_price = max(50, target_total * COURSE_BUDGET_WEIGHTS.get(course, 0.1))
    price_fit = 1.4 - abs(scaled_price(dish, request_data["diners"]) - desired_price) / max(desired_price, 1) * 0.9
    return luxury_fit + price_fit


def health_bonus(dish: dict[str, Any], request_data: dict[str, Any]) -> float:
    if "light" not in request_data["restrictions"]:
        return 0.0
    if {"light", "fresh", "vegetarian"} & dish["tags"]:
        return 1.4
    if {"crispy", "premium"} & dish["tags"]:
        return -0.9
    return 0.0


def score_dish(dish: dict[str, Any], request_data: dict[str, Any], course: str, rng: random.Random) -> float:
    if dish["course"] != course:
        return -999.0

    base = 10.0
    base += preference_bonus(dish, request_data)
    base += occasion_bonus(dish, request_data)
    base += surprise_bonus(dish, request_data)
    base += budget_bonus(dish, request_data, course)
    base += health_bonus(dish, request_data)

    serves_min, serves_max = dish["serves"]
    diners = request_data["diners"]
    if diners < serves_min or diners > serves_max:
        base -= 1.4
    else:
        base += 0.8

    base += rng.uniform(0.0, 1.2)
    return base


def choose_from_top(candidates: list[tuple[float, dict[str, Any]]], rng: random.Random) -> dict[str, Any]:
    top_choices = sorted(candidates, key=lambda item: item[0], reverse=True)[:3]
    weights = [max(0.1, score) for score, _ in top_choices]
    picked = rng.choices(top_choices, weights=weights, k=1)[0]
    return picked[1]


def build_reason(dish: dict[str, Any], request_data: dict[str, Any]) -> str:
    snippets: list[str] = []
    preferences = set(request_data["preferences"])
    tags = dish["tags"]

    if "fresh" in preferences and {"fresh", "light", "spring"} & tags:
        snippets.append("保留了清鲜和季节感")
    if "spicy" in preferences and "spicy" in tags:
        snippets.append("辛香层次能把聚餐气氛拉起来")
    if "cantonese" in preferences and {"classic", "cantonese"} & tags:
        snippets.append("有比较稳的粤式私房菜底色")
    if "creative" in preferences and "creative" in tags:
        snippets.append("能给整套菜单增加一点新鲜感")
    if request_data["occasion"] == "business" and dish["luxury"] >= 4:
        snippets.append("上桌体面，适合宴请")
    if request_data["occasion"] == "date" and {"light", "fresh"} & tags:
        snippets.append("节奏轻盈，适合慢慢吃")
    if request_data["occasion"] in {"birthday", "friends"} and {"crispy", "creative", "spicy"} & tags:
        snippets.append("适合分享，也更容易成为话题菜")
    if "light" in request_data["restrictions"] and {"light", "vegetarian"} & tags:
        snippets.append("做法相对清爽，不会让后段太腻")

    if not snippets:
        snippets.append("能和整套席面的口味节奏自然衔接")

    return "，".join(snippets[:2]) + "。"


def build_title(request_data: dict[str, Any]) -> tuple[str, str]:
    import datetime as _dt

    season = SEASON_LABELS[_dt.date.today().month]
    accents = [PREFERENCE_PROFILES[item]["accent"] for item in request_data["preferences"][:2]]
    accent = " / ".join(accents)
    occasion_label = OCCASION_PROFILES[request_data["occasion"]]["label"]
    title = f"{season} {accent} · {request_data['diners']}人{occasion_label}"

    preference_labels = [PREFERENCE_PROFILES[item]["label"] for item in request_data["preferences"]]
    subtitle = (
        f"根据 {request_data['diners']} 位客人、{occasion_label}场景、"
        f"{' / '.join(preference_labels)}的偏好生成，整体走 {OCCASION_PROFILES[request_data['occasion']]['tone']} 的路线。"
    )
    return title, subtitle


def build_menu_summary(request_data: dict[str, Any], courses: list[dict[str, Any]], total_price: int) -> str:
    profile = BUDGET_PROFILES[request_data["budget"]]
    occasion = OCCASION_PROFILES[request_data["occasion"]]
    restrictions = [RESTRICTION_LABELS[item] for item in request_data["restrictions"]]
    restriction_text = "，并照顾到" + "、".join(restrictions) if restrictions else ""

    course_names = "、".join(COURSE_LABELS[item["course"]] for item in courses[:4])
    return (
        f"这套菜单以 {occasion['words'][0]} 为主轴，前段从 {course_names} 逐步打开味觉，"
        f"中段用主菜拉满私房菜记忆点，后段以主食和甜品收束。"
        f" 预计整桌约 ¥{total_price}，人均约 ¥{round(total_price / request_data['diners'])}，"
        f"风格接近“{profile['label']}”的真实私房菜体验{restriction_text}。"
    )


def build_chef_notes(request_data: dict[str, Any], courses: list[dict[str, Any]]) -> list[str]:
    mains = [item for item in courses if item["course"] in {"seafood", "poultry", "meat"}]
    notes = [
        "建议上菜节奏为：前菜 2 道并行，汤品单独上，再进入 2 到 3 道主菜高潮，最后用主食和甜品收尾。",
        f"本次主菜重点放在“{mains[0]['name']}”这类高识别度热菜上，适合作为整桌席面的味觉重心。",
        "整套餐单会尽量兼顾开场、高潮和收尾，让味型和上桌节奏更完整。",
    ]
    if request_data["notes"]:
        notes.insert(1, f"已吸收备注“{request_data['notes']}”，并在选菜时尽量往相近风格靠拢。")
    return notes


def generate_menu(payload: dict[str, Any]) -> dict[str, Any]:
    request_data = normalize_request(payload)
    rng = stable_rng(request_data)
    plan = build_course_plan(request_data)
    selected: list[dict[str, Any]] = []
    used_names: set[str] = set()

    for course in plan:
        scored_candidates: list[tuple[float, dict[str, Any]]] = []
        for dish in DISHES:
            if dish["name"] in used_names:
                continue
            if not dish_is_allowed(dish, request_data):
                continue
            score = score_dish(dish, request_data, course, rng)
            if score > 0:
                scored_candidates.append((score, dish))

        if not scored_candidates:
            continue

        picked = choose_from_top(scored_candidates, rng)
        used_names.add(picked["name"])
        selected.append(
            {
                "course": picked["course"],
                "course_label": COURSE_LABELS[picked["course"]],
                "name": picked["name"],
                "description": picked["description"],
                "presentation": picked["presentation"],
                "reason": build_reason(picked, request_data),
                "price": scaled_price(picked, request_data["diners"]),
            }
        )

    total_price = sum(item["price"] for item in selected)
    title, subtitle = build_title(request_data)
    summary = build_menu_summary(request_data, selected, total_price)

    highlights = [
        "会根据人数和预算控制出菜数量，让整桌份量和席面结构更协调。",
        "会结合口味偏好、用餐场景和忌口做安排，让整套餐单更贴近真实待客体验。"
    ]

    return {
        "request": {
            "diners": request_data["diners"],
            "occasion": OCCASION_PROFILES[request_data["occasion"]]["label"],
            "budget": BUDGET_PROFILES[request_data["budget"]]["label"],
            "preferences": [PREFERENCE_PROFILES[item]["label"] for item in request_data["preferences"]],
            "restrictions": [RESTRICTION_LABELS[item] for item in request_data["restrictions"]] or ["无特别忌口"],
        },
        "title": title,
        "subtitle": subtitle,
        "summary": summary,
        "estimated_total": total_price,
        "per_person": round(total_price / request_data["diners"]),
        "courses": selected,
        "chef_notes": build_chef_notes(request_data, selected),
        "highlights": highlights,
    }


def normalize_kitchen_request(payload: dict[str, Any]) -> dict[str, Any]:
    tables = max(2, min(int(payload.get("tables", 3)), 8))
    chefs = max(2, min(int(payload.get("chefs", 4)), 10))
    hot_stations = max(1, min(int(payload.get("hot_stations", 2)), 6))
    cold_stations = max(1, min(int(payload.get("cold_stations", 2)), 4))
    soup_stations = max(1, min(int(payload.get("soup_stations", 2)), 3))
    steamers = max(1, min(int(payload.get("steamers", 1)), 3))
    arrival_window = max(10, min(int(payload.get("arrival_window", 30)), 90))
    start_time = str(payload.get("start_time", "18:00")).strip() or "18:00"
    seed_hint = str(payload.get("seed_hint", "kitchen")).strip()[:40]

    return {
        "tables": tables,
        "chefs": chefs,
        "hot_stations": hot_stations,
        "cold_stations": cold_stations,
        "soup_stations": soup_stations,
        "steamers": steamers,
        "arrival_window": arrival_window,
        "start_time": start_time,
        "seed_hint": seed_hint,
    }


def build_random_request_payload(rng: random.Random) -> dict[str, Any]:
    preference_count = 2 if rng.random() < 0.8 else 1
    preferences = rng.sample(SIMULATION_PREFERENCES, k=preference_count)
    restrictions: list[str] = []
    if rng.random() < 0.28:
        restriction = rng.choice(SIMULATION_RESTRICTIONS)
        if restriction == "no_spicy" and "spicy" in preferences and rng.random() < 0.8:
            preferences = [item for item in preferences if item != "spicy"] or ["fresh"]
        restrictions.append(restriction)

    return {
        "diners": rng.choice([2, 2, 4, 4, 6, 6, 8]),
        "occasion": rng.choice(SIMULATION_OCCASIONS),
        "budget": rng.choice(SIMULATION_BUDGETS),
        "surprise": rng.choice(["classic", "balanced", "balanced", "adventurous"]),
        "preferences": preferences,
        "restrictions": restrictions,
        "notes": rng.choice(
            [
                "",
                "希望整体节奏稳一点",
                "想要一道适合分享的主菜",
                "前段想清爽一些",
                "后段不要太厚重",
            ]
        ),
    }


def build_table_order(table_number: int, arrival_minute: int, request_payload: dict[str, Any]) -> dict[str, Any]:
    menu = generate_menu(request_payload)
    return {
        "table_id": f"T{table_number}",
        "table_name": f"{table_number}号桌",
        "arrival_minute": arrival_minute,
        "request_payload": request_payload,
        "menu": menu,
    }


def build_simulated_table_requests(config: dict[str, Any]) -> list[dict[str, Any]]:
    rng = stable_rng(config)
    arrivals = sorted(rng.randint(0, config["arrival_window"]) for _ in range(config["tables"]))
    requests: list[dict[str, Any]] = []

    for index in range(config["tables"]):
        request_payload = build_random_request_payload(rng)
        requests.append(build_table_order(index + 1, arrivals[index], request_payload))

    return requests


def get_cooking_profile(dish: dict[str, Any]) -> dict[str, Any]:
    name = dish["name"]
    course = dish["course"]
    tags = dish["tags"]

    if course == "appetizer":
        if {"fresh", "light"} & tags and "crispy" not in tags and "spicy" not in tags and "beef" not in tags:
            return {"station": "cold", "duration": 7, "chef_need": 1, "heat": "cold"}
        if "熟醉" in name:
            return {"station": "cold", "duration": 8, "chef_need": 1, "heat": "cold"}
        return {"station": "hot", "duration": 10, "chef_need": 1, "heat": "warm"}

    if course == "soup":
        if "酸汤" in name:
            return {"station": "soup", "duration": 24, "chef_need": 1, "heat": "hot"}
        return {"station": "soup", "duration": 32, "chef_need": 1, "heat": "hot"}

    if course == "seafood":
        if "蒸" in name or "清蒸" in name:
            return {"station": "steam", "duration": 16, "chef_need": 1, "heat": "hot"}
        if "龙虾" in name:
            return {"station": "hot", "duration": 22, "chef_need": 2, "heat": "hot"}
        return {"station": "hot", "duration": 15, "chef_need": 1, "heat": "hot"}

    if course == "poultry":
        if "熟醉" in name:
            return {"station": "cold", "duration": 8, "chef_need": 1, "heat": "cold"}
        if "脆皮" in name:
            return {"station": "hot", "duration": 18, "chef_need": 2, "heat": "hot"}
        return {"station": "hot", "duration": 16, "chef_need": 1, "heat": "hot"}

    if course == "meat":
        if "和牛" in name or "羊排" in name:
            return {"station": "hot", "duration": 20, "chef_need": 2, "heat": "hot"}
        return {"station": "hot", "duration": 16, "chef_need": 1, "heat": "hot"}

    if course == "vegetable":
        if "炭烤" in name:
            return {"station": "hot", "duration": 12, "chef_need": 1, "heat": "hot"}
        return {"station": "hot", "duration": 8, "chef_need": 1, "heat": "hot"}

    if course == "staple":
        if "泡饭" in name:
            return {"station": "hot", "duration": 14, "chef_need": 1, "heat": "hot"}
        return {"station": "hot", "duration": 11, "chef_need": 1, "heat": "hot"}

    return {"station": "cold", "duration": 6, "chef_need": 1, "heat": "cold"}


def build_kitchen_tasks(table_orders: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    tasks: list[dict[str, Any]] = []
    table_states: dict[str, dict[str, Any]] = {}

    for table in table_orders:
        table_id = table["table_id"]
        menu = table["menu"]
        courses = menu["courses"]
        table_states[table_id] = {
            "table_id": table_id,
            "table_name": table["table_name"],
            "arrival_minute": table["arrival_minute"],
            "diners": menu["request"]["diners"],
            "occasion": menu["request"]["occasion"],
            "budget": menu["request"]["budget"],
            "preferences": menu["request"]["preferences"],
            "restrictions": menu["request"]["restrictions"],
            "courses_total": len(courses),
            "served_count": 0,
            "running_count": 0,
            "last_served_at": None,
            "first_served_at": None,
            "served_times": [],
        }

        for index, course in enumerate(courses):
            source = DISH_INDEX[course["name"]]
            profile = get_cooking_profile(source)
            task_id = f"{table_id}-D{index + 1}"
            tasks.append(
                {
                    "task_id": task_id,
                    "table_id": table_id,
                    "table_name": table["table_name"],
                    "arrival_minute": table["arrival_minute"],
                    "dish_index": index,
                    "name": course["name"],
                    "course": course["course"],
                    "course_label": course["course_label"],
                    "price": course["price"],
                    "description": course["description"],
                    "station": profile["station"],
                    "station_label": STATION_LABELS[profile["station"]],
                    "duration": profile["duration"],
                    "chef_need": profile["chef_need"],
                    "heat": profile["heat"],
                    "target_offset": COURSE_TARGET_OFFSETS[course["course"]] + index * 2,
                    "earliest_start": table["arrival_minute"] + COURSE_START_OFFSETS[course["course"]],
                    "status": "queued",
                }
            )

    return tasks, table_states


def compute_task_priority(
    task: dict[str, Any],
    minute: int,
    table_state: dict[str, Any],
    min_served_count: int,
) -> float:
    wait_anchor = table_state["last_served_at"] if table_state["last_served_at"] is not None else table_state["arrival_minute"]
    wait_since_last = minute - wait_anchor
    target_time = task["arrival_minute"] + task["target_offset"]
    lateness = minute - target_time
    served_gap = table_state["served_count"] - min_served_count
    first_round_bonus = 14 if table_state["served_count"] == 0 else 0
    running_penalty = table_state["running_count"] * 3.2
    course_bias = {
        "appetizer": 6.0,
        "soup": 5.0,
        "seafood": 4.2,
        "poultry": 3.8,
        "meat": 3.6,
        "vegetable": 2.8,
        "staple": 2.0,
        "dessert": 1.0,
    }[task["course"]]
    return (
        lateness * 1.8
        + wait_since_last * 1.25
        + first_round_bonus
        + course_bias
        - served_gap * 12.0
        - running_penalty
        - task["duration"] * 0.08
    )


def build_station_state(config: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return {
        "cold": [{"slot_id": f"cold-{idx + 1}", "busy_until": 0, "current_task_id": None} for idx in range(config["cold_stations"])],
        "hot": [{"slot_id": f"hot-{idx + 1}", "busy_until": 0, "current_task_id": None} for idx in range(config["hot_stations"])],
        "soup": [{"slot_id": f"soup-{idx + 1}", "busy_until": 0, "current_task_id": None} for idx in range(config["soup_stations"])],
        "steam": [{"slot_id": f"steam-{idx + 1}", "busy_until": 0, "current_task_id": None} for idx in range(config["steamers"])],
    }


def select_free_slot(slots: list[dict[str, Any]], minute: int) -> dict[str, Any] | None:
    for slot in slots:
        if slot["busy_until"] <= minute:
            return slot
    return None


def build_recent_events(events: list[dict[str, Any]], current_minute: int) -> list[dict[str, Any]]:
    recent = [event for event in events if event["minute"] <= current_minute]
    return recent[-10:]


def serialize_table_order_for_live(order: dict[str, Any]) -> dict[str, Any]:
    tasks, table_states = build_kitchen_tasks([order])
    tasks.sort(key=lambda item: item["dish_index"])
    state = table_states[order["table_id"]]
    return {
        "table_id": order["table_id"],
        "table_name": order["table_name"],
        "arrival_minute": order["arrival_minute"],
        "diners": state["diners"],
        "occasion": state["occasion"],
        "budget": state["budget"],
        "preferences": state["preferences"],
        "restrictions": state["restrictions"],
        "menu_title": order["menu"]["title"],
        "summary": order["menu"]["summary"],
        "courses": [
            {
                "task_id": task["task_id"],
                "name": task["name"],
                "course": task["course"],
                "course_label": task["course_label"],
                "station": task["station"],
                "station_label": task["station_label"],
                "duration": task["duration"],
                "chef_need": task["chef_need"],
                "earliest_start": task["earliest_start"],
                "target_offset": task["target_offset"],
                "description": task["description"],
            }
            for task in tasks
        ],
    }


def generate_live_kitchen_order(payload: dict[str, Any]) -> dict[str, Any]:
    table_number = max(1, min(int(payload.get("table_number", 1)), 99))
    arrival_minute = max(0, int(payload.get("arrival_minute", 0)))
    seed_hint = str(payload.get("seed_hint", "live")).strip()[:40]
    rng = stable_rng(
        {
            "table_number": table_number,
            "arrival_minute": arrival_minute,
            "seed_hint": seed_hint,
        }
    )
    request_payload = build_random_request_payload(rng)
    order = build_table_order(table_number, arrival_minute, request_payload)
    return serialize_table_order_for_live(order)


def summarize_kitchen_metrics(table_states: dict[str, dict[str, Any]], schedule: list[dict[str, Any]]) -> dict[str, Any]:
    first_waits: list[int] = []
    longest_gap = 0

    for table in table_states.values():
        served_times = table["served_times"]
        if table["first_served_at"] is not None:
            first_waits.append(table["first_served_at"] - table["arrival_minute"])
        checkpoints = [table["arrival_minute"], *served_times]
        gaps = [checkpoints[index + 1] - checkpoints[index] for index in range(len(checkpoints) - 1)]
        if gaps:
            longest_gap = max(longest_gap, max(gaps))

    finish_time = max((item["end_minute"] for item in schedule), default=0)
    average_first_wait = round(sum(first_waits) / len(first_waits)) if first_waits else 0
    return {
        "average_first_wait": average_first_wait,
        "longest_gap": longest_gap,
        "finish_minute": finish_time,
        "served_dishes": len(schedule),
        "tables": len(table_states),
    }


def simulate_kitchen_service(payload: dict[str, Any]) -> dict[str, Any]:
    config = normalize_kitchen_request(payload)
    table_orders = build_simulated_table_requests(config)
    tasks, table_states = build_kitchen_tasks(table_orders)
    slots_by_station = build_station_state(config)
    task_lookup = {task["task_id"]: task for task in tasks}
    running_tasks: list[dict[str, Any]] = []
    schedule: list[dict[str, Any]] = []
    service_events: list[dict[str, Any]] = []
    minute = 0
    max_horizon = config["arrival_window"] + 180

    while minute <= max_horizon:
        finished = [item for item in running_tasks if item["end_minute"] <= minute]
        for item in finished:
            task = task_lookup[item["task_id"]]
            table_state = table_states[task["table_id"]]
            table_state["served_count"] += 1
            table_state["running_count"] = max(0, table_state["running_count"] - 1)
            table_state["last_served_at"] = item["end_minute"]
            table_state["served_times"].append(item["end_minute"])
            if table_state["first_served_at"] is None:
                table_state["first_served_at"] = item["end_minute"]
            task["status"] = "served"
            service_events.append(
                {
                    "minute": item["end_minute"],
                    "table_id": task["table_id"],
                    "table_name": task["table_name"],
                    "dish": task["name"],
                    "course_label": task["course_label"],
                    "station_label": task["station_label"],
                }
            )
        running_tasks = [item for item in running_tasks if item["end_minute"] > minute]

        current_chef_load = sum(item["chef_need"] for item in running_tasks)
        active_tables = [
            table
            for table in table_states.values()
            if table["arrival_minute"] <= minute and table["served_count"] < table["courses_total"]
        ]
        min_served_count = min((table["served_count"] for table in active_tables), default=0)

        while True:
            chefs_available = config["chefs"] - current_chef_load
            candidates: list[tuple[float, dict[str, Any], dict[str, Any]]] = []

            for task in tasks:
                if task["status"] != "queued":
                    continue
                if minute < task["arrival_minute"] or minute < task["earliest_start"]:
                    continue

                table_state = table_states[task["table_id"]]
                if table_state["running_count"] >= 2:
                    continue
                if task["chef_need"] > chefs_available:
                    continue

                slot = select_free_slot(slots_by_station[task["station"]], minute)
                if slot is None:
                    continue

                priority = compute_task_priority(task, minute, table_state, min_served_count)
                candidates.append((priority, task, slot))

            if not candidates:
                break

            candidates.sort(key=lambda item: (item[0], -item[1]["duration"]), reverse=True)
            _, chosen_task, chosen_slot = candidates[0]
            start_minute = minute
            end_minute = minute + chosen_task["duration"]

            chosen_task["status"] = "cooking"
            chosen_task["start_minute"] = start_minute
            chosen_task["end_minute"] = end_minute
            chosen_task["slot_id"] = chosen_slot["slot_id"]
            chosen_slot["busy_until"] = end_minute
            chosen_slot["current_task_id"] = chosen_task["task_id"]
            current_chef_load += chosen_task["chef_need"]
            table_states[chosen_task["table_id"]]["running_count"] += 1

            record = {
                "task_id": chosen_task["task_id"],
                "table_id": chosen_task["table_id"],
                "table_name": chosen_task["table_name"],
                "dish": chosen_task["name"],
                "course": chosen_task["course"],
                "course_label": chosen_task["course_label"],
                "station": chosen_task["station"],
                "station_label": chosen_task["station_label"],
                "slot_id": chosen_slot["slot_id"],
                "chef_need": chosen_task["chef_need"],
                "duration": chosen_task["duration"],
                "start_minute": start_minute,
                "end_minute": end_minute,
                "arrival_minute": chosen_task["arrival_minute"],
                "target_time": chosen_task["arrival_minute"] + chosen_task["target_offset"],
                "description": chosen_task["description"],
            }
            schedule.append(record)
            running_tasks.append(record)

        if all(task["status"] == "served" for task in tasks):
            break

        minute += 1

    tasks_by_table: dict[str, list[dict[str, Any]]] = {}
    for task in tasks:
        tasks_by_table.setdefault(task["table_id"], []).append(task)
    for value in tasks_by_table.values():
        value.sort(key=lambda item: item["dish_index"])

    tables_payload = []
    for order in table_orders:
        table_id = order["table_id"]
        state = table_states[table_id]
        tables_payload.append(
            {
                "table_id": table_id,
                "table_name": order["table_name"],
                "arrival_minute": order["arrival_minute"],
                "diners": state["diners"],
                "occasion": state["occasion"],
                "budget": state["budget"],
                "preferences": state["preferences"],
                "restrictions": state["restrictions"],
                "menu_title": order["menu"]["title"],
                "summary": order["menu"]["summary"],
                "courses": [
                    {
                        "task_id": task["task_id"],
                        "name": task["name"],
                        "course_label": task["course_label"],
                        "station_label": task["station_label"],
                        "duration": task["duration"],
                        "start_minute": task.get("start_minute"),
                        "end_minute": task.get("end_minute"),
                    }
                    for task in tasks_by_table[table_id]
                ],
            }
        )

    station_summary = [
        {"key": "cold", "label": STATION_LABELS["cold"], "count": config["cold_stations"]},
        {"key": "hot", "label": STATION_LABELS["hot"], "count": config["hot_stations"]},
        {"key": "soup", "label": STATION_LABELS["soup"], "count": config["soup_stations"]},
        {"key": "steam", "label": STATION_LABELS["steam"], "count": config["steamers"]},
    ]

    metrics = summarize_kitchen_metrics(table_states, schedule)
    return {
        "config": config,
        "start_time": config["start_time"],
        "stations": station_summary,
        "metrics": metrics,
        "tables": tables_payload,
        "schedule": sorted(schedule, key=lambda item: (item["start_minute"], item["table_id"])),
        "events": sorted(service_events, key=lambda item: item["minute"]),
        "total_minutes": metrics["finish_minute"] + 8,
        "recent_preview": build_recent_events(service_events, metrics["finish_minute"]),
    }


def guess_content_type(path: Path) -> str:
    suffix_map = {
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".svg": "image/svg+xml",
    }
    return suffix_map.get(path.suffix.lower(), "application/octet-stream")


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.serve_file(TEMPLATE_DIR / "index.html")
            return
        if parsed.path == "/kitchen":
            self.serve_file(TEMPLATE_DIR / "kitchen.html")
            return
        if parsed.path == "/api/health":
            self.send_json({"status": "ok"})
            return
        if parsed.path.startswith("/static/"):
            relative = parsed.path.removeprefix("/static/")
            target = (STATIC_DIR / relative).resolve()
            if STATIC_DIR.resolve() not in target.parents and target != STATIC_DIR.resolve():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            if not target.exists() or not target.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            self.serve_file(target)
            return

        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path not in {"/api/generate-menu", "/api/kitchen-simulate", "/api/kitchen-order"}:
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(length)
            payload = json.loads(raw_body.decode("utf-8") or "{}")
            if parsed.path == "/api/generate-menu":
                result = generate_menu(payload)
            elif parsed.path == "/api/kitchen-order":
                result = generate_live_kitchen_order(payload)
            else:
                result = simulate_kitchen_service(payload)
        except json.JSONDecodeError:
            self.send_json({"error": "请求体不是有效的 JSON。"}, status=HTTPStatus.BAD_REQUEST)
            return
        except Exception as exc:  # pragma: no cover
            self.send_json({"error": f"处理请求时出现异常：{exc}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self.send_json(result)

    def serve_file(self, file_path: Path) -> None:
        content = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", guess_content_type(file_path))
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        return


def run() -> None:
    host = "127.0.0.1"
    port = 8000
    server = ThreadingHTTPServer((host, port), DemoHandler)
    print(f"Private dining demo is running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
