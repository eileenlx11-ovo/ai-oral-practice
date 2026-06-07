"""
Scenario learning guide — vocabulary, expressions, tips, and dialogue examples.
Provides pre-practice study materials for each scenario.
"""
import json
import os
from pathlib import Path

CACHE_DIR = Path(__file__).parent / "data" / "guides"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

SCENARIO_GUIDES = {
    "coffee_shop": {
        "title": "Coffee Shop",
        "vocabulary": [
            {"word": "latte", "phonetic": "/ˈlɑːteɪ/", "meaning": "拿铁咖啡", "example": "I'd like a medium latte, please."},
            {"word": "espresso", "phonetic": "/eˈspresəʊ/", "meaning": "浓缩咖啡", "example": "Can I get a double espresso?"},
            {"word": "oat milk", "phonetic": "/əʊt mɪlk/", "meaning": "燕麦奶", "example": "Could I have that with oat milk?"},
            {"word": "pastry", "phonetic": "/ˈpeɪstri/", "meaning": "糕点", "example": "What pastries do you have today?"},
            {"word": "to-go", "phonetic": "/tə ɡəʊ/", "meaning": "外带", "example": "I'll have that to-go, please."},
        ],
        "expressions": [
            {"phrase": "What can I get you?", "phonetic": "/wɒt kæn aɪ ɡet juː/", "meaning": "您要点什么？（店员用语）", "example": "Hi there! What can I get you today?"},
            {"phrase": "for here or to go", "phonetic": "/fɔːr hɪər ɔːr tə ɡəʊ/", "meaning": "堂食还是外带", "example": "Is that for here or to go?"},
            {"phrase": "Can I get a...", "phonetic": "/kæn aɪ ɡet ə/", "meaning": "我要一个...（点单常用）", "example": "Can I get a large iced americano?"},
        ],
        "tips": [
            {"title": "用 Could I have 代替 I want", "description": "点单时用 Could I have... 或 Can I get... 比直接说 I want 更礼貌自然", "example": "Could I have a medium latte with oat milk?", "note": "英语母语者几乎从不在点餐时说 I want"},
            {"title": "尺寸表达", "description": "美式咖啡店通常用 small/medium/large，星巴克用 tall/grande/venti", "example": "I'll take a grande cappuccino.", "note": "如果不确定尺寸叫法，直接说 medium 最安全"},
        ],
        "dialogue": [
            {"speaker": "A", "text": "Hey there! Welcome to Bean & Brew. What can I get started for you?", "translation": "嘿！欢迎来到 Bean & Brew。想喝点什么？", "notes": [{"term": "get started for you", "explanation": "咖啡店常用开场，比 What do you want 更热情"}]},
            {"speaker": "B", "text": "Hi! Could I get a medium oat milk latte? And maybe a blueberry muffin to go.", "translation": "嗨！我要一杯中杯燕麦拿铁，再来一个蓝莓松饼外带。", "notes": [{"term": "to go", "explanation": "外带；反义词 for here 堂食"}]},
            {"speaker": "A", "text": "Sure thing! Hot or iced for the latte?", "translation": "没问题！拿铁要热的还是冰的？", "notes": [{"term": "Sure thing", "explanation": "口语化的 'no problem'，比 OK 更热情"}]},
            {"speaker": "B", "text": "Iced, please. Oh, and could you make it with an extra shot?", "translation": "冰的。哦对了，能多加一份浓缩吗？", "notes": [{"term": "extra shot", "explanation": "多加一份浓缩咖啡；shot = 一份 espresso"}]},
        ],
    },
    "restaurant": {
        "title": "Restaurant",
        "vocabulary": [
            {"word": "appetizer", "phonetic": "/ˈæpɪtaɪzər/", "meaning": "开胃菜/前菜", "example": "Would you like to start with an appetizer?"},
            {"word": "entrée", "phonetic": "/ˈɒntreɪ/", "meaning": "主菜（美式英语）", "example": "For my entrée, I'll have the salmon."},
            {"word": "allergies", "phonetic": "/ˈælədʒiz/", "meaning": "过敏", "example": "Do you have any food allergies?"},
            {"word": "specials", "phonetic": "/ˈspeʃəlz/", "meaning": "今日特供", "example": "What are today's specials?"},
            {"word": "check/bill", "phonetic": "/tʃek/ /bɪl/", "meaning": "账单", "example": "Could we get the check, please?"},
        ],
        "expressions": [
            {"phrase": "table for two", "phonetic": "/ˈteɪbəl fɔːr tuː/", "meaning": "两位用餐", "example": "Hi, table for two, please."},
            {"phrase": "I'll have the...", "phonetic": "/aɪl hæv ðə/", "meaning": "我要...（点餐）", "example": "I'll have the grilled chicken, please."},
            {"phrase": "on the side", "phonetic": "/ɒn ðə saɪd/", "meaning": "酱料/配菜另放", "example": "Could I get the dressing on the side?"},
        ],
        "tips": [
            {"title": "点餐时用 I'll have 而非 I want", "description": "I'll have the... 是最自然的点餐表达，I want 显得生硬", "example": "I'll have the steak, medium rare, please.", "note": "加 please 是基本礼貌"},
            {"title": "询问推荐", "description": "不确定点什么时问 What do you recommend? 比盯着菜单更自然", "example": "What would you recommend for a first-timer here?", "note": "也可以说 What's good here?"},
        ],
        "dialogue": [
            {"speaker": "A", "text": "Good evening! Welcome to The Garden Bistro. Do you have a reservation?", "translation": "晚上好！欢迎来到花园小酒馆。请问有预订吗？", "notes": [{"term": "reservation", "explanation": "餐厅预订；动词 reserve 或 book"}]},
            {"speaker": "B", "text": "Yes, under the name Chen. Table for two.", "translation": "有的，姓陈。两位。", "notes": [{"term": "under the name", "explanation": "以...的名字（预订的）；比 my name is 更地道"}]},
            {"speaker": "A", "text": "Right this way. Can I start you off with something to drink?", "translation": "这边请。先来点喝的吗？", "notes": [{"term": "start you off with", "explanation": "先来...；餐厅服务员的标准开场"}]},
        ],
    },
    "airport": {
        "title": "Airport Check-in",
        "vocabulary": [
            {"word": "boarding pass", "phonetic": "/ˈbɔːrdɪŋ pæs/", "meaning": "登机牌", "example": "Here's your boarding pass. Gate B12."},
            {"word": "carry-on", "phonetic": "/ˈkæri ɒn/", "meaning": "随身行李", "example": "Is this your only carry-on?"},
            {"word": "aisle/window", "phonetic": "/aɪl/ /ˈwɪndəʊ/", "meaning": "靠走道/靠窗", "example": "Would you prefer an aisle or window seat?"},
            {"word": "layover", "phonetic": "/ˈleɪəʊvər/", "meaning": "转机停留", "example": "I have a two-hour layover in Dubai."},
            {"word": "turbulence", "phonetic": "/ˈtɜːrbjələns/", "meaning": "气流颠簸", "example": "Please fasten your seatbelt during turbulence."},
        ],
        "expressions": [
            {"phrase": "check in a bag", "phonetic": "/tʃek ɪn ə bæɡ/", "meaning": "托运行李", "example": "I'd like to check in one bag, please."},
            {"phrase": "What gate is it?", "phonetic": "/wɒt ɡeɪt ɪz ɪt/", "meaning": "在几号登机口？", "example": "What gate is my flight departing from?"},
            {"phrase": "Is my flight on time?", "phonetic": "/ɪz maɪ flaɪt ɒn taɪm/", "meaning": "我的航班准时吗？", "example": "Excuse me, is flight BA215 on time?"},
        ],
        "tips": [
            {"title": "用 I'd like to 表达需求", "description": "机场场景用 I'd like to... 表达请求比 I want to 更得体", "example": "I'd like to check in for my flight to London.", "note": "机场工作人员习惯了礼貌表达"},
            {"title": "座位偏好的表达", "description": "不要只说 window，完整说 Could I get a window seat? 或 I'd prefer an aisle seat.", "example": "If possible, could I get a window seat near the front?", "note": "加 if possible 显得更通情达理"},
        ],
        "dialogue": [
            {"speaker": "A", "text": "Good morning! Passport and booking reference, please.", "translation": "早上好！请出示护照和预订号。", "notes": [{"term": "booking reference", "explanation": "预订确认号；也叫 confirmation number 或 PNR"}]},
            {"speaker": "B", "text": "Here you go. I'd like to check in one suitcase and keep my backpack as carry-on.", "translation": "给您。我想托运一个行李箱，背包随身带。", "notes": [{"term": "Here you go", "explanation": "递东西时的口语，比 Here it is 更日常"}]},
        ],
    },
    "interview": {
        "title": "Job Interview",
        "vocabulary": [
            {"word": "strengths", "phonetic": "/streŋθs/", "meaning": "优势/强项", "example": "My biggest strength is problem-solving."},
            {"word": "collaborative", "phonetic": "/kəˈlæbərətɪv/", "meaning": "协作的", "example": "I'm a collaborative team player."},
            {"word": "initiative", "phonetic": "/ɪˈnɪʃətɪv/", "meaning": "主动性", "example": "I take initiative on projects."},
            {"word": "deadline", "phonetic": "/ˈdedlaɪn/", "meaning": "截止日期", "example": "I always deliver before the deadline."},
            {"word": "accomplishment", "phonetic": "/əˈkʌmplɪʃmənt/", "meaning": "成就", "example": "My biggest accomplishment was leading the migration."},
        ],
        "expressions": [
            {"phrase": "Tell me about a time when...", "phonetic": "/tel mi əˈbaʊt ə taɪm wen/", "meaning": "跟我说一个...的经历（行为面试题）", "example": "Tell me about a time when you handled a conflict."},
            {"phrase": "I'd say my strength is...", "phonetic": "/aɪd seɪ maɪ streŋθ ɪz/", "meaning": "我认为我的优势是...", "example": "I'd say my strength is attention to detail."},
            {"phrase": "In my previous role", "phonetic": "/ɪn maɪ ˈpriːviəs rəʊl/", "meaning": "在我上一份工作中", "example": "In my previous role, I managed a team of five."},
        ],
        "tips": [
            {"title": "STAR 法则回答行为面试题", "description": "Situation(背景) → Task(任务) → Action(行动) → Result(结果)，结构清晰让面试官容易跟随", "example": "In my last role (S), I was asked to reduce load times (T). I profiled the app and optimized the database queries (A), which improved performance by 40% (R).", "note": "每个部分 1-2 句就够，不要讲太长"},
            {"title": "避免 I think，用 I believe/I'd say", "description": "面试中 I think 显得不够自信，用 I believe 或 I'd say 更有说服力", "example": "I believe my experience in full-stack development makes me a strong fit.", "note": "也可以用 I'm confident that..."},
        ],
        "dialogue": [
            {"speaker": "A", "text": "Thanks for coming in. Could you start by telling me a bit about yourself?", "translation": "感谢你来面试。能先简单介绍一下自己吗？", "notes": [{"term": "tell me about yourself", "explanation": "面试最经典开场；准备 60-90 秒的 elevator pitch"}]},
            {"speaker": "B", "text": "Sure! I'm a software engineer with three years of experience, mainly in backend development with Python and Go.", "translation": "好的！我是一名有三年经验的软件工程师，主要做 Python 和 Go 后端开发。", "notes": [{"term": "mainly in", "explanation": "主要在...领域；简洁表达专长方向"}]},
        ],
    },
    "roommate": {
        "title": "Meeting Your Roommate",
        "vocabulary": [
            {"word": "settle in", "phonetic": "/ˈsetl ɪn/", "meaning": "安顿下来", "example": "Are you settling in OK?"},
            {"word": "night owl", "phonetic": "/naɪt aʊl/", "meaning": "夜猫子", "example": "I'm a bit of a night owl."},
            {"word": "early bird", "phonetic": "/ˈɜːrli bɜːrd/", "meaning": "早起的人", "example": "I'm more of an early bird—up by 6am."},
            {"word": "ground rules", "phonetic": "/ɡraʊnd ruːlz/", "meaning": "基本规则", "example": "Should we set some ground rules?"},
            {"word": "heads up", "phonetic": "/hedz ʌp/", "meaning": "提前通知", "example": "Just give me a heads up if you're having friends over."},
        ],
        "expressions": [
            {"phrase": "Do you mind if...", "phonetic": "/duː juː maɪnd ɪf/", "meaning": "你介意...吗", "example": "Do you mind if I play music while studying?"},
            {"phrase": "I'm cool with that", "phonetic": "/aɪm kuːl wɪð ðæt/", "meaning": "我没问题/可以", "example": "You want to split groceries? I'm cool with that."},
            {"phrase": "What's your schedule like?", "phonetic": "/wɒts jɔːr ˈʃedjuːl laɪk/", "meaning": "你的作息是什么样的？", "example": "What's your schedule like? I have 8am classes."},
        ],
        "tips": [
            {"title": "用 Do you mind if... 而非 Can I...", "description": "和室友协商时 Do you mind if... 比 Can I... 更尊重对方感受", "example": "Do you mind if I keep the light on till midnight?", "note": "注意：回答 No 表示不介意（= 可以）"},
            {"title": "表达偏好用 I tend to / I'm more of a...", "description": "描述自己习惯时用这些表达比直接说 I always 更柔和", "example": "I tend to study with music on. I'm more of a night owl.", "note": "给室友留有协商空间"},
        ],
        "dialogue": [
            {"speaker": "A", "text": "Hey! You must be my new roommate! I'm Chris, from Portland.", "translation": "嘿！你一定是我的新室友吧！我是 Chris，来自波特兰。", "notes": [{"term": "You must be", "explanation": "初次见面的猜测用语，比 Are you...? 更热情"}]},
            {"speaker": "B", "text": "Hi Chris! Nice to meet you. I'm still unpacking—this room's bigger than I expected!", "translation": "嗨 Chris！很高兴认识你。我还在收拾东西——这房间比我想的大！", "notes": [{"term": "bigger than I expected", "explanation": "比较级 + than I expected 是表达惊喜的常用句式"}]},
        ],
    },
    "hotel": {
        "title": "Hotel Check-in",
        "vocabulary": [
            {"word": "reservation", "phonetic": "/ˌrezərˈveɪʃən/", "meaning": "预订", "example": "I have a reservation under the name Li."},
            {"word": "complimentary", "phonetic": "/ˌkɒmplɪˈmentəri/", "meaning": "免费赠送的", "example": "Breakfast is complimentary for all guests."},
            {"word": "amenities", "phonetic": "/əˈmenɪtiz/", "meaning": "设施/便利设施", "example": "What amenities does the hotel offer?"},
            {"word": "checkout", "phonetic": "/ˈtʃekaʊt/", "meaning": "退房", "example": "What time is checkout?"},
            {"word": "upgrade", "phonetic": "/ʌpˈɡreɪd/", "meaning": "升级", "example": "Is there a room upgrade available?"},
        ],
        "expressions": [
            {"phrase": "under the name...", "phonetic": "/ˈʌndər ðə neɪm/", "meaning": "以...的名字（预订）", "example": "I have a reservation under the name Wang."},
            {"phrase": "Is breakfast included?", "phonetic": "/ɪz ˈbrekfəst ɪnˈkluːdɪd/", "meaning": "含早餐吗？", "example": "Quick question—is breakfast included in the rate?"},
            {"phrase": "Could I get a late checkout?", "phonetic": "/kʊd aɪ ɡet ə leɪt ˈtʃekaʊt/", "meaning": "能晚退房吗？", "example": "Would it be possible to get a late checkout tomorrow?"},
        ],
        "tips": [
            {"title": "用 Would it be possible to... 提出特殊要求", "description": "比 Can I... 更礼貌，适合向酒店提出升级/延迟退房等请求", "example": "Would it be possible to move to a higher floor?", "note": "就算被拒绝也不会尴尬"},
        ],
        "dialogue": [
            {"speaker": "A", "text": "Welcome to The Grand! Do you have a reservation with us?", "translation": "欢迎来到格兰酒店！请问有预订吗？", "notes": [{"term": "with us", "explanation": "加 with us 让语气更亲切，是酒店行业用语"}]},
            {"speaker": "B", "text": "Yes, under Li. I booked a deluxe room for three nights.", "translation": "有的，姓李。我订了一间豪华房住三晚。", "notes": [{"term": "deluxe room", "explanation": "豪华房；酒店房型从低到高：standard → superior → deluxe → suite"}]},
        ],
    },
    "renting": {
        "title": "Renting an Apartment",
        "vocabulary": [
            {"word": "lease", "phonetic": "/liːs/", "meaning": "租约/租赁合同", "example": "The lease is for twelve months."},
            {"word": "deposit", "phonetic": "/dɪˈpɒzɪt/", "meaning": "押金", "example": "The security deposit is one month's rent."},
            {"word": "utilities", "phonetic": "/juːˈtɪlɪtiz/", "meaning": "水电煤等费用", "example": "Are utilities included in the rent?"},
            {"word": "landlord", "phonetic": "/ˈlændlɔːrd/", "meaning": "房东", "example": "The landlord lives upstairs."},
            {"word": "furnished", "phonetic": "/ˈfɜːrnɪʃt/", "meaning": "带家具的", "example": "Is the apartment fully furnished?"},
        ],
        "expressions": [
            {"phrase": "What's included in the rent?", "phonetic": "/wɒts ɪnˈkluːdɪd ɪn ðə rent/", "meaning": "房租包含哪些？", "example": "Just to clarify — what's included in the rent?"},
            {"phrase": "Is there a minimum lease term?",  "phonetic": "/ɪz ðeər ə ˈmɪnɪməm liːs tɜːrm/", "meaning": "有最短租期吗？", "example": "Is there a minimum lease term, or is it month-to-month?"},
            {"phrase": "When would I be able to move in?", "phonetic": "/wen wʊd aɪ biː ˈeɪbəl tə muːv ɪn/", "meaning": "什么时候能入住？", "example": "If I decide today, when would I be able to move in?"},
        ],
        "tips": [
            {"title": "用 Just to clarify 开头提问", "description": "看房时确认细节用 Just to clarify... 比直接问更自然，表示你在认真考虑", "example": "Just to clarify — does the rent include internet?", "note": "房东会觉得你是认真的租客"},
            {"title": "表达顾虑用 My only concern is...", "description": "委婉表达不满意的地方，比直接说 I don't like 更成熟", "example": "My only concern is the noise from the street. Is it usually this loud?", "note": "给房东回应的空间，可能有解决方案"},
        ],
        "dialogue": [
            {"speaker": "A", "text": "So, this is the one-bedroom. The rent is $1,200 a month, utilities not included.", "translation": "这就是一居室。月租1200美元，不含水电。", "notes": [{"term": "utilities not included", "explanation": "水电煤气等不包含在房租内，需要另付"}]},
            {"speaker": "B", "text": "It's nice and bright. Just to clarify — is there a parking spot included?", "translation": "挺明亮的。确认一下——含车位吗？", "notes": [{"term": "Just to clarify", "explanation": "确认细节的礼貌开场，比 Does it have... 更成熟"}]},
            {"speaker": "A", "text": "There's street parking, but we do have a garage spot available for an extra $50 a month.", "translation": "有路边停车位，不过车库车位每月另加50美元。", "notes": [{"term": "available for an extra", "explanation": "可以额外付费获得；available = 有的/可用的"}]},
            {"speaker": "B", "text": "Got it. And what's the policy on pets? I have a small dog.", "translation": "明白了。养宠物的政策是什么？我有一只小狗。", "notes": [{"term": "policy on", "explanation": "关于...的政策/规定；租房常问问题"}]},
        ],
    },
    "counseling": {
        "title": "Counseling Session",
        "vocabulary": [
            {"word": "overwhelmed", "phonetic": "/ˌəʊvərˈwelmd/", "meaning": "不堪重负的", "example": "I've been feeling really overwhelmed lately."},
            {"word": "cope", "phonetic": "/kəʊp/", "meaning": "应对/处理", "example": "How do you usually cope with stress?"},
            {"word": "anxious", "phonetic": "/ˈæŋkʃəs/", "meaning": "焦虑的", "example": "I get anxious before presentations."},
            {"word": "boundary", "phonetic": "/ˈbaʊndəri/", "meaning": "界限/边界", "example": "Setting boundaries is important for mental health."},
            {"word": "burnout", "phonetic": "/ˈbɜːrnaʊt/", "meaning": "倦怠/精疲力竭", "example": "I think I'm experiencing burnout from work."},
        ],
        "expressions": [
            {"phrase": "I've been feeling...", "phonetic": "/aɪv biːn ˈfiːlɪŋ/", "meaning": "我最近一直感觉...", "example": "I've been feeling really stressed about work."},
            {"phrase": "It's hard to put into words", "phonetic": "/ɪts hɑːrd tə pʊt ˈɪntə wɜːrdz/", "meaning": "很难用语言表达", "example": "It's hard to put into words, but I just feel stuck."},
            {"phrase": "What do you suggest?", "phonetic": "/wɒt duː juː səˈdʒest/", "meaning": "你有什么建议？", "example": "I want to improve things. What do you suggest?"},
        ],
        "tips": [
            {"title": "用 I've been feeling + 形容词 表达情绪", "description": "现在完成进行时表示持续状态，比 I feel 更强调'一直以来'的感受", "example": "I've been feeling anxious about the future.", "note": "咨询师会根据这个了解持续时间"},
            {"title": "表达不确定用 I'm not sure if/why...", "description": "表达自己也说不清楚的情绪，在心理咨询中很正常", "example": "I'm not sure why, but I've been losing motivation.", "note": "承认不确定比假装了解自己更有帮助"},
        ],
        "dialogue": [
            {"speaker": "A", "text": "Hi, welcome back. How have things been since we last talked?", "translation": "嗨，欢迎回来。上次聊完之后感觉怎么样？", "notes": [{"term": "since we last talked", "explanation": "自从上次谈话以来；咨询师的标准回访开场"}]},
            {"speaker": "B", "text": "Honestly, it's been a rough week. I've been feeling overwhelmed with everything.", "translation": "说实话，这周挺难熬的。我一直感觉压力很大。", "notes": [{"term": "a rough week", "explanation": "艰难的一周；rough = 困难的/不顺的"}]},
            {"speaker": "A", "text": "I'm sorry to hear that. Can you tell me more about what's been weighing on you?", "translation": "很遗憾听到这些。能具体说说什么让你感到压力吗？", "notes": [{"term": "weighing on you", "explanation": "压在心头的；weigh on = 使感到沉重/烦心"}]},
            {"speaker": "B", "text": "It's mainly work. The deadlines keep piling up and I can't seem to say no to new tasks.", "translation": "主要是工作。截止日期不断堆积，我好像没法拒绝新任务。", "notes": [{"term": "piling up", "explanation": "堆积；pile up = 越积越多"}]},
        ],
    },
    "family": {
        "title": "Family Gathering",
        "vocabulary": [
            {"word": "catch up", "phonetic": "/kætʃ ʌp/", "meaning": "叙旧/了解近况", "example": "It's so nice to catch up with everyone!"},
            {"word": "settle down", "phonetic": "/ˈsetl daʊn/", "meaning": "安定下来（结婚成家）", "example": "Are you thinking about settling down soon?"},
            {"word": "reunion", "phonetic": "/riːˈjuːniən/", "meaning": "团聚/重聚", "example": "The family reunion is next month."},
            {"word": "in-laws", "phonetic": "/ɪn lɔːz/", "meaning": "姻亲/公婆/岳父母", "example": "My in-laws are coming for dinner."},
            {"word": "get-together", "phonetic": "/ˈɡet təˌɡeðər/", "meaning": "聚会/小型聚会", "example": "We should have a get-together more often."},
        ],
        "expressions": [
            {"phrase": "Long time no see!", "phonetic": "/lɒŋ taɪm nəʊ siː/", "meaning": "好久不见！", "example": "Hey! Long time no see! You look great!"},
            {"phrase": "How's everything going?", "phonetic": "/haʊz ˈevriθɪŋ ˈɡəʊɪŋ/", "meaning": "一切都好吗？", "example": "So, how's everything going? Still at the same company?"},
            {"phrase": "You haven't changed a bit!", "phonetic": "/juː ˈhævnt tʃeɪndʒd ə bɪt/", "meaning": "你一点都没变！", "example": "Wow, you haven't changed a bit! Still look the same."},
        ],
        "tips": [
            {"title": "回答 How are you 不要只说 Fine", "description": "家庭聚会中亲戚真的想知道你的近况，多说几句", "example": "I'm doing well! Actually, I just got promoted last month, so that's been exciting.", "note": "给对方接话的机会"},
            {"title": "用 Actually / To be honest 引入真实想法", "description": "家人问起敏感话题（工作、恋爱）时，用这些可以诚实但不尴尬", "example": "To be honest, I'm taking a break from dating right now. Focusing on myself.", "note": "诚实但设了界限"},
        ],
        "dialogue": [
            {"speaker": "A", "text": "There you are! We haven't seen you since Christmas! How's the new job going?", "translation": "你来了！圣诞节之后就没见了！新工作怎么样？", "notes": [{"term": "There you are!", "explanation": "终于见到你了！带有惊喜和开心的语气"}]},
            {"speaker": "B", "text": "Hey Uncle Frank! It's going great, actually. I just finished a big project.", "translation": "嘿 Frank 叔叔！其实挺好的。我刚完成了一个大项目。", "notes": [{"term": "actually", "explanation": "加 actually 暗示'比预期的好'，增加真实感"}]},
            {"speaker": "A", "text": "That's wonderful! Your mom was telling me about it. So, anyone special in your life?", "translation": "太好了！你妈跟我说了。那，有没有特别的人啊？", "notes": [{"term": "anyone special", "explanation": "委婉问'有没有对象'；家庭聚会经典问题"}]},
            {"speaker": "B", "text": "Ha, you sound just like Mom! I'm keeping my options open for now.", "translation": "哈，你跟我妈一样！我目前保持开放态度。", "notes": [{"term": "keeping my options open", "explanation": "保持开放态度；委婉回避'没有'的说法"}]},
        ],
    },
    "fitness": {
        "title": "Sports & Exercise",
        "vocabulary": [
            {"word": "warm up", "phonetic": "/wɔːrm ʌp/", "meaning": "热身", "example": "Always warm up before lifting heavy."},
            {"word": "rep", "phonetic": "/rep/", "meaning": "重复次数（一组中）", "example": "I usually do 3 sets of 12 reps."},
            {"word": "cardio", "phonetic": "/ˈkɑːrdiəʊ/", "meaning": "有氧运动", "example": "I do 30 minutes of cardio before weights."},
            {"word": "pace", "phonetic": "/peɪs/", "meaning": "配速/节奏", "example": "What's your usual running pace?"},
            {"word": "recovery", "phonetic": "/rɪˈkʌvəri/", "meaning": "恢复", "example": "Rest days are important for recovery."},
        ],
        "expressions": [
            {"phrase": "How often do you work out?", "phonetic": "/haʊ ˈɒfən duː juː wɜːrk aʊt/", "meaning": "你多久锻炼一次？", "example": "How often do you work out? I try to go four times a week."},
            {"phrase": "I've been getting into...", "phonetic": "/aɪv biːn ˈɡetɪŋ ˈɪntə/", "meaning": "我最近开始喜欢上...", "example": "I've been getting into swimming lately."},
            {"phrase": "Do you have any tips for...?", "phonetic": "/duː juː hæv ˈeni tɪps fɔːr/", "meaning": "你有...方面的建议吗？", "example": "Do you have any tips for improving my form?"},
        ],
        "tips": [
            {"title": "描述频率用 I try to + 动词", "description": "比 I always 更真实，表达努力但不一定每次做到", "example": "I try to run three times a week, but sometimes life gets in the way.", "note": "更自然，也更容易引起共鸣"},
            {"title": "用 I've been... + -ing 描述新习惯", "description": "表达最近开始做某事，暗示在持续中", "example": "I've been doing yoga in the mornings. It really helps with flexibility.", "note": "现在完成进行时表示'到目前为止一直在做'"},
        ],
        "dialogue": [
            {"speaker": "A", "text": "Hey! I just signed up for a 5K next month. Have you ever done a race before?", "translation": "嘿！我刚报了下个月的5公里跑。你以前跑过比赛吗？", "notes": [{"term": "signed up for", "explanation": "报名参加；sign up = 注册/报名"}]},
            {"speaker": "B", "text": "I did a 10K last year, actually! It was tough but so rewarding. What's your training plan?", "translation": "我去年跑了个10公里！挺累但很有成就感。你训练计划是什么？", "notes": [{"term": "rewarding", "explanation": "有回报的/值得的；比 good 更精确地表达成就感"}]},
            {"speaker": "A", "text": "I'm doing Couch to 5K — basically building up from walking to running over 8 weeks.", "translation": "我在用 Couch to 5K 计划——大概8周从走路到跑步逐步提升。", "notes": [{"term": "building up from... to...", "explanation": "从...逐步提升到...；描述渐进过程"}]},
            {"speaker": "B", "text": "That's smart! Don't push too hard too fast. And make sure you get good running shoes.", "translation": "聪明！别急着加量。还有一定要买双好跑鞋。", "notes": [{"term": "push too hard", "explanation": "过度逼自己；运动场景常用表达"}]},
        ],
    },
}


def get_guide(scenario_id: str) -> dict | None:
    """Get learning guide for a scenario. Returns static data or cached LLM result."""
    if scenario_id in SCENARIO_GUIDES:
        return SCENARIO_GUIDES[scenario_id]

    # Check cache
    cache_path = CACHE_DIR / f"{scenario_id}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))

    return None  # LLM generation handled at API layer


async def generate_guide(scenario_id: str, scenario_name: str, llm_client, model: str) -> dict:
    """Generate a learning guide via LLM and cache it."""
    cache_path = CACHE_DIR / f"{scenario_id}.json"

    prompt = f"""Generate a learning guide for an English oral practice scenario: "{scenario_name}".
Return a JSON object with these fields:
- "title": scenario name
- "vocabulary": array of 5 objects, each with "word", "phonetic" (IPA), "meaning" (Chinese), "example" (English sentence)
- "expressions": array of 3 objects, each with "phrase", "phonetic", "meaning" (Chinese), "example"
- "tips": array of 2 objects, each with "title" (Chinese), "description" (Chinese), "example" (English), "note" (Chinese)
- "dialogue": array of 4 objects (alternating speakers A/B), each with "speaker", "text" (English), "translation" (Chinese), "notes" (array of {{"term", "explanation" in Chinese}})

Make it practical and natural. Use common real-life expressions. Return ONLY valid JSON."""

    try:
        resp = await llm_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000,
        )
        text = resp.choices[0].message.content.strip()
        # Parse JSON
        import re
        if text.startswith("```"):
            text = re.sub(r"^```\w*\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
        guide = json.loads(text)
        # Cache
        cache_path.write_text(json.dumps(guide, ensure_ascii=False, indent=2), encoding="utf-8")
        return guide
    except Exception:
        return None
