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
    "sightseeing": {
        "title": "Sightseeing — China Travel Edition",
        "vocabulary": [
            {"word": "itinerary", "phonetic": "/aɪˈtɪnəˌreri/", "meaning": "行程安排", "example": "Let me check my itinerary for today."},
            {"word": "blitz", "phonetic": "/blɪts/", "meaning": "闪电战；比喻紧凑的行程", "example": "We're doing a 144-hour Shanghai blitz."},
            {"word": "landmark", "phonetic": "/ˈlændmɑːrk/", "meaning": "地标", "example": "The Bund is Shanghai's most famous landmark."},
            {"word": "authentic", "phonetic": "/ɔːˈθentɪk/", "meaning": "正宗的/地道的", "example": "I want to find authentic street food."},
            {"word": "scenic", "phonetic": "/ˈsiːnɪk/", "meaning": "风景优美的", "example": "Let's take the scenic route along the river."},
            {"word": "visa-free", "phonetic": "/ˈviːzə friː/", "meaning": "免签", "example": "China offers 144-hour visa-free transit."},
        ],
        "expressions": [
            {"phrase": "hit the spots", "phonetic": "/hɪt ðə spɒts/", "meaning": "打卡热门地点", "example": "Let's hit the spots trending on Douyin!"},
            {"phrase": "whirlwind tour", "phonetic": "/ˈwɜːrlwɪnd tʊər/", "meaning": "旋风式旅行（行程紧凑）", "example": "It'll be a whirlwind tour — three cities in four days."},
            {"phrase": "off the beaten path", "phonetic": "/ɒf ðə ˈbiːtən pæθ/", "meaning": "小众/非游客路线", "example": "I prefer places off the beaten path."},
            {"phrase": "grab some...", "phonetic": "/ɡræb sʌm/", "meaning": "去吃/去买...（口语化）", "example": "Let's grab some xiaolongbao first!"},
        ],
        "tips": [
            {"title": "用 Let's 代替 You should 更友好", "description": "给旅行搭子建议时，Let's 后接动词原形，语气像朋友而非指导者", "example": "Let's grab some xiaolongbao first!", "note": "对比 You should try xiaolongbao — 像老师在教学生"},
            {"title": "用 How do I... 而非 How to...", "description": "口语中问方法用 How do I + 动词原形，不用 How to（那是标题写法）", "example": "How do I pay stuff without Alipay?", "note": "也可以说 How can I... 更正式一点"},
            {"title": "用 Sounds + 形容词 快速回应", "description": "对别人的提议表示态度：Sounds awesome / Sounds good / Sounds tricky", "example": "Sounds awesome~ But how do I pay stuff without Alipay?", "note": "比 That's a good idea 更口语化、更快"},
        ],
        "dialogue": [
            {"speaker": "A", "text": "Hey there! Ready for our 144-hour Shanghai blitz? Let's hit the spots trending on Douyin!", "translation": "嘿！准备好我们的 144 小时上海闪电游了吗？咱们去打卡抖音上热门的地方！", "notes": [{"term": "144-hour blitz", "explanation": "blitz 指闪电战，比喻紧凑旅行安排；可替换为 whirlwind tour"}, {"term": "hit the spots", "explanation": "打卡/去某些地点；spots = 地点（口语）"}]},
            {"speaker": "B", "text": "Sounds awesome~ But how do I pay stuff without Alipay?", "translation": "听起来太棒了～但没有支付宝我怎么付钱啊？", "notes": [{"term": "pay stuff", "explanation": "stuff = 东西（口语万能词）；正式说法 pay for things"}, {"term": "Sounds awesome", "explanation": "口语回应：听起来很棒；~ 表示语气轻松"}]},
            {"speaker": "A", "text": "No worries! Most places take WeChat Pay or even cash. I'll show you how to set it up.", "translation": "别担心！大部分地方接受微信支付甚至现金。我教你怎么设置。", "notes": [{"term": "No worries", "explanation": "别担心；比 Don't worry 更随意友好"}, {"term": "set it up", "explanation": "设置/搞定它；phrasal verb 常用于 app/账户设置"}]},
            {"speaker": "B", "text": "Sweet! So what's first on the itinerary? I'm dying to try those soup dumplings everyone raves about.", "translation": "太好了！那行程第一站是哪？我超想尝尝大家都夸的小笼包。", "notes": [{"term": "I'm dying to", "explanation": "我超想...；夸张表达强烈渴望"}, {"term": "raves about", "explanation": "狂赞/热烈推荐；rave = 极度热情地说"}]},
        ],
    },
    "public_transport": {
        "title": "Public Transport",
        "vocabulary": [
            {"word": "transfer", "phonetic": "/ˈtrænsfɜːr/", "meaning": "换乘", "example": "You need to transfer at the next station."},
            {"word": "platform", "phonetic": "/ˈplætfɔːrm/", "meaning": "站台", "example": "The train departs from platform 3."},
            {"word": "commute", "phonetic": "/kəˈmjuːt/", "meaning": "通勤", "example": "My daily commute takes about 40 minutes."},
            {"word": "fare", "phonetic": "/feər/", "meaning": "车费", "example": "The fare is $2.75 per ride."},
            {"word": "peak hours", "phonetic": "/piːk aʊərz/", "meaning": "高峰时段", "example": "Avoid the subway during peak hours."},
        ],
        "expressions": [
            {"phrase": "Which line do I take?", "phonetic": "/wɪtʃ laɪn duː aɪ teɪk/", "meaning": "我坐几号线？", "example": "Excuse me, which line do I take to get to the museum?"},
            {"phrase": "Does this go to...?", "phonetic": "/dʌz ðɪs ɡəʊ tuː/", "meaning": "这趟车去...吗？", "example": "Does this bus go to the city center?"},
            {"phrase": "How many stops is it?", "phonetic": "/haʊ ˈmeni stɒps ɪz ɪt/", "meaning": "还有几站？", "example": "How many stops is it to Central Park?"},
        ],
        "tips": [
            {"title": "问路用 Excuse me 开头", "description": "地铁里问陌生人用 Excuse me 是基本礼貌，直接问 Where is... 会显得唐突", "example": "Excuse me, does this train go to Brooklyn?", "note": "即使很急也别省略，一个词换来对方的配合"},
            {"title": "确认信息用 So I need to...?", "description": "复述对方指示来确认，用 So + 自己的理解 + 升调，表示求确认", "example": "So I need to take Line 2 and transfer at People's Square?", "note": "比 OK 有效率——对方会纠正任何错误"},
        ],
        "dialogue": [
            {"speaker": "A", "text": "Excuse me, I'm trying to get to the Oriental Pearl Tower. Which line should I take?", "translation": "打扰一下，我想去东方明珠塔。我应该坐几号线？", "notes": [{"term": "I'm trying to get to", "explanation": "我想去...；比 I want to go 更自然（暗示还在找路）"}]},
            {"speaker": "B", "text": "Sure! Take Line 2 heading east. It's about four stops from here. You can't miss it.", "translation": "没问题！坐 2 号线往东方向，从这里大概四站。不会错过的。", "notes": [{"term": "heading east", "explanation": "往东方向；heading + 方向 描述列车行驶方向"}, {"term": "You can't miss it", "explanation": "你不会错过的（很明显/很好找）"}]},
            {"speaker": "A", "text": "Got it. Do I need to transfer anywhere?", "translation": "明白了。我需要在哪里换乘吗？", "notes": [{"term": "Got it", "explanation": "明白了；比 I understand 更口语"}, {"term": "transfer anywhere", "explanation": "在任何地方换乘；anywhere 用于疑问句"}]},
            {"speaker": "B", "text": "Nope, it's a direct ride. Just make sure you exit from Exit 1 — it's closest to the tower.", "translation": "不用，直达的。记得从 1 号出口出来——离塔最近。", "notes": [{"term": "direct ride", "explanation": "直达（不用换乘）"}, {"term": "make sure you", "explanation": "确保你...；温馨提醒的常用句式"}]},
        ],
    },
    "debate": {
        "title": "Classroom Debate",
        "vocabulary": [
            {"word": "counterargument", "phonetic": "/ˈkaʊntərˌɑːrɡjumənt/", "meaning": "反驳论点", "example": "Let me address that counterargument."},
            {"word": "outweigh", "phonetic": "/ˌaʊtˈweɪ/", "meaning": "超过/大于", "example": "The benefits outweigh the risks."},
            {"word": "furthermore", "phonetic": "/ˌfɜːrðərˈmɔːr/", "meaning": "此外（正式）", "example": "Furthermore, studies have shown that..."},
            {"word": "concede", "phonetic": "/kənˈsiːd/", "meaning": "承认/让步", "example": "I concede that point, however..."},
            {"word": "compelling", "phonetic": "/kəmˈpelɪŋ/", "meaning": "令人信服的", "example": "That's a compelling argument."},
        ],
        "expressions": [
            {"phrase": "I'd argue that...", "phonetic": "/aɪd ˈɑːrɡjuː ðæt/", "meaning": "我认为...（辩论用）", "example": "I'd argue that social media does more harm than good."},
            {"phrase": "With all due respect...", "phonetic": "/wɪð ɔːl djuː rɪˈspekt/", "meaning": "恕我直言...", "example": "With all due respect, that evidence is outdated."},
            {"phrase": "The evidence suggests...", "phonetic": "/ðə ˈevɪdəns səˈdʒests/", "meaning": "证据表明...", "example": "The evidence suggests a clear correlation."},
        ],
        "tips": [
            {"title": "用 While I understand... 先肯定再反驳", "description": "辩论中直接说 You're wrong 太粗鲁。先承认对方有道理再转折，更有说服力", "example": "While I understand the convenience argument, the mental health data tells a different story.", "note": "这叫 concession-rebuttal 结构，学术辩论必备"},
            {"title": "用具体数据代替 many/a lot", "description": "辩论中模糊词汇削弱说服力，具体数据更有力", "example": "According to a 2024 study, 67% of teens reported increased anxiety from social media use.", "note": "即使记不清具体数字，说 nearly 70% 也比 many 有力"},
        ],
        "dialogue": [
            {"speaker": "A", "text": "I'd argue that social media has fundamentally damaged young people's mental health. Studies show anxiety rates have doubled since 2010.", "translation": "我认为社交媒体从根本上损害了年轻人的心理健康。研究显示 2010 年以来焦虑率翻了一倍。", "notes": [{"term": "fundamentally", "explanation": "从根本上；加强语气的副词，比 really 更学术"}, {"term": "rates have doubled", "explanation": "比率翻倍；用数据说话的模板句"}]},
            {"speaker": "B", "text": "With all due respect, correlation doesn't imply causation. Couldn't other factors explain that rise?", "translation": "恕我直言，相关性不等于因果关系。其他因素难道不能解释这种增长吗？", "notes": [{"term": "correlation doesn't imply causation", "explanation": "相关不等于因果；辩论/学术中经典反驳句"}, {"term": "Couldn't... explain", "explanation": "反问句式（难道不能...），比陈述更有辩论力度"}]},
        ],
    },
    "ielts_speaking": {
        "title": "IELTS Speaking Practice",
        "vocabulary": [
            {"word": "elaborate", "phonetic": "/ɪˈlæbəreɪt/", "meaning": "详细阐述", "example": "Could you elaborate on that point?"},
            {"word": "perspective", "phonetic": "/pərˈspektɪv/", "meaning": "观点/角度", "example": "From my perspective, education should be free."},
            {"word": "significant", "phonetic": "/sɪɡˈnɪfɪkənt/", "meaning": "重要的/显著的", "example": "Technology has had a significant impact on education."},
            {"word": "tend to", "phonetic": "/tend tuː/", "meaning": "倾向于", "example": "Young people tend to prefer online communication."},
            {"word": "drawback", "phonetic": "/ˈdrɔːbæk/", "meaning": "缺点/弊端", "example": "One major drawback is the cost."},
        ],
        "expressions": [
            {"phrase": "Speaking of which...", "phonetic": "/ˈspiːkɪŋ əv wɪtʃ/", "meaning": "说到这个...", "example": "Speaking of which, I actually had a similar experience."},
            {"phrase": "It depends on...", "phonetic": "/ɪt dɪˈpendz ɒn/", "meaning": "这取决于...", "example": "It depends on the context and the individual."},
            {"phrase": "In my experience...", "phonetic": "/ɪn maɪ ɪkˈspɪəriəns/", "meaning": "以我的经验来看...", "example": "In my experience, practice makes a huge difference."},
        ],
        "tips": [
            {"title": "IELTS Part 2 用 SPERM 结构", "description": "Situation(场景) + Person(人物) + Event(事件) + Reaction(反应) + Memory(为何记得)，确保说满 2 分钟", "example": "I'd like to talk about a trip to Beijing (S). I went with my best friend (P). We visited the Great Wall (E). I was blown away by how massive it was (R). It's memorable because... (M)", "note": "考官不打断你时答满 2 分钟是高分信号"},
            {"title": "用 I'd say... 和 I suppose... 替代 I think", "description": "整场只说 I think 显得词汇量小。交替使用同义表达提升 LR 分数", "example": "I'd say the biggest advantage is flexibility. I suppose it also saves time.", "note": "其他替换：In my view / As I see it / From my standpoint"},
        ],
        "dialogue": [
            {"speaker": "Examiner", "text": "Do you think technology has changed the way people communicate?", "translation": "你认为科技改变了人们的交流方式吗？", "notes": [{"term": "Do you think...", "explanation": "Part 3 常见开头；需要给出观点+原因+例子"}]},
            {"speaker": "Student", "text": "Absolutely. I'd say technology has transformed communication in both positive and negative ways. On the one hand, it's never been easier to stay in touch with people overseas. On the other hand, I suppose face-to-face interaction has suffered somewhat.", "translation": "确实如此。我认为科技从积极和消极两方面改变了交流。一方面，和海外的人保持联系从未如此容易。另一方面，我觉得面对面的互动多少受到了影响。", "notes": [{"term": "On the one hand... On the other hand", "explanation": "一方面...另一方面；展现辩证思维，IELTS 高分结构"}, {"term": "has suffered somewhat", "explanation": "受到了一定影响；somewhat 让表达更精准而非绝对化"}]},
        ],
    },
    "group_project": {
        "title": "Group Project",
        "vocabulary": [
            {"word": "delegate", "phonetic": "/ˈdelɪɡeɪt/", "meaning": "委派/分配任务", "example": "Let's delegate the tasks based on strengths."},
            {"word": "deadline", "phonetic": "/ˈdedlaɪn/", "meaning": "截止日期", "example": "The deadline is next Friday."},
            {"word": "feasible", "phonetic": "/ˈfiːzəbl/", "meaning": "可行的", "example": "Is this timeline feasible for everyone?"},
            {"word": "contribute", "phonetic": "/kənˈtrɪbjuːt/", "meaning": "贡献/出力", "example": "Everyone should contribute equally."},
            {"word": "draft", "phonetic": "/dræft/", "meaning": "草稿", "example": "I'll send a first draft by Wednesday."},
        ],
        "expressions": [
            {"phrase": "How about if I...?", "phonetic": "/haʊ əˈbaʊt ɪf aɪ/", "meaning": "我来...怎么样？（主动揽活）", "example": "How about if I handle the introduction?"},
            {"phrase": "Does that work for everyone?", "phonetic": "/dʌz ðæt wɜːrk fɔːr ˈevriwʌn/", "meaning": "大家都OK吗？", "example": "Let's meet Thursday at 3. Does that work for everyone?"},
            {"phrase": "I can take the lead on...", "phonetic": "/aɪ kæn teɪk ðə liːd ɒn/", "meaning": "...这块我来牵头", "example": "I can take the lead on the data analysis section."},
        ],
        "tips": [
            {"title": "主动揽活用 How about if I...?", "description": "比 I will do... 更合作化——你在征求团队同意而非单方面决定", "example": "How about if I put together the slides? I'm pretty good with design.", "note": "后面加上理由（I'm good with...）让提议更合理"},
            {"title": "委婉催进度用 How are things going with...?", "description": "组员没交作业时，比 Did you finish it? 更不伤面子", "example": "Hey, how are things going with the literature review? Need any help?", "note": "加 Need any help? 把催促包装成关心"},
        ],
        "dialogue": [
            {"speaker": "A", "text": "OK team, so we have this presentation due next Friday. How should we split it up?", "translation": "好的同学们，我们下周五要交 PPT。怎么分工？", "notes": [{"term": "split it up", "explanation": "分配/拆分；比 divide 更口语"}, {"term": "due next Friday", "explanation": "下周五到期；due = 应交/到期"}]},
            {"speaker": "B", "text": "How about if I handle the research section? I've already found some good sources.", "translation": "研究部分我来怎么样？我已经找到一些好的资料了。", "notes": [{"term": "How about if I handle", "explanation": "我来处理...如何？handle = 负责/处理"}, {"term": "sources", "explanation": "资料来源；学术语境指参考文献"}]},
            {"speaker": "A", "text": "Sounds good! I can take the lead on the slides. Does that work for everyone?", "translation": "好的！PPT 我来牵头做。大家都 OK 吗？", "notes": [{"term": "take the lead on", "explanation": "牵头做；lead 这里指主导责任"}, {"term": "Does that work for everyone?", "explanation": "小组协作万能确认句；显示你尊重每个人的意见"}]},
        ],
    },
    "study_abroad": {
        "title": "Study Abroad",
        "vocabulary": [
            {"word": "exchange program", "phonetic": "/ɪksˈtʃeɪndʒ ˈprəʊɡræm/", "meaning": "交换项目", "example": "I'm interested in the exchange program with UCL."},
            {"word": "scholarship", "phonetic": "/ˈskɒlərʃɪp/", "meaning": "奖学金", "example": "Are there any scholarships available?"},
            {"word": "prerequisite", "phonetic": "/priːˈrekwɪzɪt/", "meaning": "先决条件", "example": "What are the prerequisites for this program?"},
            {"word": "transcript", "phonetic": "/ˈtrænskrɪpt/", "meaning": "成绩单", "example": "I'll need to submit my official transcript."},
            {"word": "immersion", "phonetic": "/ɪˈmɜːrʒən/", "meaning": "沉浸式体验", "example": "Language immersion is the fastest way to improve."},
        ],
        "expressions": [
            {"phrase": "I'm considering...", "phonetic": "/aɪm kənˈsɪdərɪŋ/", "meaning": "我在考虑...", "example": "I'm considering applying for the spring semester."},
            {"phrase": "What would you recommend?", "phonetic": "/wɒt wʊd juː ˌrekəˈmend/", "meaning": "您推荐什么？", "example": "Given my major, what would you recommend?"},
            {"phrase": "Could you walk me through...?", "phonetic": "/kʊd juː wɔːk miː θruː/", "meaning": "能帮我梳理一下...流程吗？", "example": "Could you walk me through the application process?"},
        ],
        "tips": [
            {"title": "咨询时用 Could you walk me through...?", "description": "请人介绍流程时比 Tell me about... 更正式且具体——暗示你想要 step by step 的指导", "example": "Could you walk me through the visa application timeline?", "note": "walk through = 逐步引导，像散步一样带你过一遍"},
            {"title": "表达意向用 I'm considering/looking into", "description": "比 I want to 更成熟——显示你在认真思考而非冲动决定", "example": "I'm looking into programs in the UK or Netherlands for next fall.", "note": "look into = 了解/研究；比 think about 更行动导向"},
        ],
        "dialogue": [
            {"speaker": "A", "text": "Hi! I'm looking into exchange programs for next year. Could you walk me through what's available?", "translation": "嗨！我在了解明年的交换项目。能帮我介绍一下有哪些选择吗？", "notes": [{"term": "looking into", "explanation": "正在了解/研究；比 I want to know 更积极主动"}, {"term": "what's available", "explanation": "有哪些选择；简洁地问现有选项"}]},
            {"speaker": "B", "text": "Of course! We have partnerships with universities in 12 countries. What's your major, and is there a particular region you're drawn to?", "translation": "当然！我们和 12 个国家的大学有合作。你什么专业？有没有特别感兴趣的地区？", "notes": [{"term": "partnerships with", "explanation": "合作关系；正式用语"}, {"term": "drawn to", "explanation": "被...吸引；比 interested in 更文学化"}]},
        ],
    },
    "weather": {
        "title": "Weather Chat",
        "vocabulary": [
            {"word": "forecast", "phonetic": "/ˈfɔːrkæst/", "meaning": "天气预报", "example": "The forecast says it'll clear up by noon."},
            {"word": "humid", "phonetic": "/ˈhjuːmɪd/", "meaning": "潮湿的", "example": "It's so humid today — I'm already sweating."},
            {"word": "breeze", "phonetic": "/briːz/", "meaning": "微风", "example": "There's a nice breeze coming off the lake."},
            {"word": "pour", "phonetic": "/pɔːr/", "meaning": "倾盆大雨", "example": "It started to pour just as I left the house."},
            {"word": "chilly", "phonetic": "/ˈtʃɪli/", "meaning": "有点冷", "example": "It's getting chilly — I should've brought a jacket."},
        ],
        "expressions": [
            {"phrase": "Can you believe this weather?", "phonetic": "/kæn juː bɪˈliːv ðɪs ˈweðər/", "meaning": "这天气你敢信吗？（闲聊开场白）", "example": "Can you believe this weather? It was sunny an hour ago!"},
            {"phrase": "clear up", "phonetic": "/klɪər ʌp/", "meaning": "（天气）放晴", "example": "Hopefully it'll clear up this afternoon."},
            {"phrase": "under the weather", "phonetic": "/ˈʌndər ðə ˈweðər/", "meaning": "身体不舒服（idiom）", "example": "I've been feeling a bit under the weather lately."},
        ],
        "tips": [
            {"title": "天气是英语闲聊万能话题", "description": "在英国/澳洲，和陌生人、邻居、同事聊天几乎都从天气开始。不需要深入——3-4 个来回就自然过渡到其他话题", "example": "Lovely day, isn't it? → Yeah, finally! → Are you doing anything nice this weekend?", "note": "反问句 isn't it? / don't you think? 邀请对方参与对话"},
            {"title": "描述程度用 It's + 副词 + 形容词", "description": "比光说 It's hot 更生动：加 absolutely / incredibly / a bit 描述程度", "example": "It's absolutely scorching today. / It's a bit nippy this morning.", "note": "scorching = 酷热; nippy = 凉飕飕的（英式）"},
        ],
        "dialogue": [
            {"speaker": "A", "text": "Can you believe this weather? I heard it might rain all weekend.", "translation": "这天气你敢信吗？听说周末可能一直下雨。", "notes": [{"term": "Can you believe", "explanation": "你能相信吗——表达惊讶，万能闲聊开场"}, {"term": "I heard", "explanation": "我听说；引出未确认的信息"}]},
            {"speaker": "B", "text": "Ugh, seriously? I was planning a hike. Guess I'll have to play it by ear.", "translation": "啊，真的吗？我本来打算去徒步的。看来只能随机应变了。", "notes": [{"term": "play it by ear", "explanation": "随机应变/走一步看一步；来自音乐即兴演奏"}, {"term": "Guess I'll have to", "explanation": "看来我得...了；省略了 I 的口语表达"}]},
        ],
    },
    "books": {
        "title": "Book Discussion",
        "vocabulary": [
            {"word": "plot twist", "phonetic": "/plɒt twɪst/", "meaning": "情节反转", "example": "I did NOT see that plot twist coming!"},
            {"word": "protagonist", "phonetic": "/prəˈtæɡənɪst/", "meaning": "主角", "example": "The protagonist is really well-developed."},
            {"word": "page-turner", "phonetic": "/peɪdʒ ˈtɜːrnər/", "meaning": "引人入胜的书", "example": "It's a real page-turner — I finished it in two days."},
            {"word": "genre", "phonetic": "/ˈʒɒnrə/", "meaning": "体裁/类型", "example": "What genre do you usually read?"},
            {"word": "thought-provoking", "phonetic": "/θɔːt prəˈvəʊkɪŋ/", "meaning": "发人深省的", "example": "It's a really thought-provoking novel."},
        ],
        "expressions": [
            {"phrase": "I couldn't put it down", "phonetic": "/aɪ ˈkʊdnt pʊt ɪt daʊn/", "meaning": "放不下手（太好看了）", "example": "I couldn't put it down — stayed up until 3am!"},
            {"phrase": "It's a must-read", "phonetic": "/ɪts ə mʌst riːd/", "meaning": "必读之作", "example": "If you like sci-fi, it's an absolute must-read."},
            {"phrase": "I'm into...", "phonetic": "/aɪm ˈɪntə/", "meaning": "我喜欢/我对...感兴趣", "example": "I'm really into historical fiction lately."},
        ],
        "tips": [
            {"title": "推荐书用 You'd love it if you're into...", "description": "推荐时先定位对方兴趣再推荐，比直接说 You should read 更自然", "example": "You'd love it if you're into psychological thrillers. The ending blew my mind.", "note": "blew my mind = 震惊了我；口语表达惊喜"},
            {"title": "表达阅读感受用情感词而非 good/bad", "description": "gripping(抓人的) / heartbreaking(心碎的) / hilarious(搞笑的) / unsettling(不安的) 比 good 生动 10 倍", "example": "The first half is slow, but it gets absolutely gripping after chapter 10.", "note": "先给小缺点再给大优点——更可信的推荐方式"},
        ],
        "dialogue": [
            {"speaker": "A", "text": "Oh, I see you're reading that one! I finished it last month. What do you think so far?", "translation": "噢，你在看那本啊！我上个月看完了。目前觉得怎么样？", "notes": [{"term": "What do you think so far?", "explanation": "到目前为止觉得怎样？so far = 到现在为止；避免剧透的贴心问法"}]},
            {"speaker": "B", "text": "I'm only halfway through, but I couldn't put it down last night. The plot twist in chapter 8 totally caught me off guard.", "translation": "我才看了一半，但昨晚完全放不下。第八章的反转完全出乎我意料。", "notes": [{"term": "caught me off guard", "explanation": "让我措手不及/出乎意料；off guard = 没有防备"}, {"term": "halfway through", "explanation": "看了一半；through 表示进度"}]},
        ],
    },
    "music": {
        "title": "Music & Creation",
        "vocabulary": [
            {"word": "chord", "phonetic": "/kɔːrd/", "meaning": "和弦", "example": "I'm learning my first four chords on guitar."},
            {"word": "melody", "phonetic": "/ˈmelədi/", "meaning": "旋律", "example": "That melody has been stuck in my head all day."},
            {"word": "vibe", "phonetic": "/vaɪb/", "meaning": "氛围/感觉", "example": "This song has such a chill vibe."},
            {"word": "gig", "phonetic": "/ɡɪɡ/", "meaning": "演出/现场表演", "example": "They're playing a gig downtown this Friday."},
            {"word": "lyrics", "phonetic": "/ˈlɪrɪks/", "meaning": "歌词", "example": "The lyrics really resonate with me."},
        ],
        "expressions": [
            {"phrase": "stuck in my head", "phonetic": "/stʌk ɪn maɪ hed/", "meaning": "脑海里循环播放", "example": "That chorus has been stuck in my head for days."},
            {"phrase": "grow on you", "phonetic": "/ɡrəʊ ɒn juː/", "meaning": "越听越喜欢", "example": "The album grows on you after a few listens."},
            {"phrase": "I'm into...", "phonetic": "/aɪm ˈɪntə/", "meaning": "我在听/我喜欢...", "example": "I'm really into lo-fi beats when I study."},
        ],
        "tips": [
            {"title": "描述音乐用 vibe/feel 而非 good/nice", "description": "说音乐 good 太笼统。用 vibe 或 feel 加形容词更地道：chill vibe, dreamy feel, raw energy", "example": "This track has such a dreamy, nostalgic vibe — perfect for late nights.", "note": "nostalgic = 怀旧的；late nights = 深夜（氛围用语）"},
            {"title": "说不擅长用 I'm still working on...", "description": "比 I'm bad at 更积极——暗示你在进步中", "example": "I'm still working on barre chords — my fingers just won't cooperate!", "note": "won't cooperate = 不配合（幽默拟人化表达）"},
        ],
        "dialogue": [
            {"speaker": "A", "text": "Is that a guitar case? Do you play?", "translation": "那是吉他包吗？你会弹吗？", "notes": [{"term": "Do you play?", "explanation": "你会弹/演奏吗？play 后省略乐器名——对方看得到"}]},
            {"speaker": "B", "text": "Yeah! I've been playing for about two years, mostly acoustic stuff. I'm still working on barre chords though. What about you?", "translation": "对！我弹了大概两年了，主要是木吉他。不过横按和弦还在练。你呢？", "notes": [{"term": "acoustic stuff", "explanation": "木吉他/原声类的东西；stuff 口语万能词"}, {"term": "What about you?", "explanation": "你呢？自然地把话题抛回对方"}]},
        ],
    },
    "lost_item": {
        "title": "Lost & Found",
        "vocabulary": [
            {"word": "misplace", "phonetic": "/ˌmɪsˈpleɪs/", "meaning": "放错地方/遗失", "example": "I think I misplaced my wallet on the train."},
            {"word": "belongings", "phonetic": "/bɪˈlɒŋɪŋz/", "meaning": "随身物品", "example": "Please check you have all your belongings."},
            {"word": "retrieve", "phonetic": "/rɪˈtriːv/", "meaning": "取回/找回", "example": "How do I retrieve my lost bag?"},
            {"word": "distinctive", "phonetic": "/dɪˈstɪŋktɪv/", "meaning": "有辨识度的", "example": "It has a distinctive red tag on the handle."},
            {"word": "file a report", "phonetic": "/faɪl ə rɪˈpɔːrt/", "meaning": "报案/填写报告", "example": "You'll need to file a lost item report."},
        ],
        "expressions": [
            {"phrase": "I seem to have lost...", "phonetic": "/aɪ siːm tə hæv lɒst/", "meaning": "我好像丢了...（委婉表达）", "example": "I seem to have lost my phone on the subway."},
            {"phrase": "The last time I had it was...", "phonetic": "/ðə lɑːst taɪm aɪ hæd ɪt wɒz/", "meaning": "我最后一次看到它是在...", "example": "The last time I had it was at the security checkpoint."},
            {"phrase": "Is there any chance...?", "phonetic": "/ɪz ðeər ˈeni tʃæns/", "meaning": "有没有可能...？", "example": "Is there any chance someone handed it in?"},
        ],
        "tips": [
            {"title": "描述物品用 It's a + 颜色 + 材质 + 类型", "description": "越具体越容易找回。按 颜色→材质→大小→品牌 顺序描述", "example": "It's a black leather backpack, medium-sized, with a North Face logo.", "note": "形容词顺序：观点→尺寸→颜色→材质→品牌（英语固定搭配）"},
            {"title": "用 I seem to have + 过去分词 表达尴尬情况", "description": "比 I lost 更委婉——暗示你不确定是丢了还是放错了地方", "example": "I seem to have left my passport at the check-in counter.", "note": "seem to 降低语气强度，适合尴尬/麻烦场景"},
        ],
        "dialogue": [
            {"speaker": "A", "text": "Hi, I seem to have lost my backpack. I think I left it on the subway about an hour ago.", "translation": "你好，我好像丢了书包。我觉得大概一小时前落在地铁上了。", "notes": [{"term": "seem to have lost", "explanation": "好像丢了；seem to + 完成时，委婉不确定的表达"}, {"term": "left it on", "explanation": "落在...上面；leave 做\"遗忘/落下\"讲"}]},
            {"speaker": "B", "text": "I'm sorry to hear that. Can you describe it for me? Any distinctive features?", "translation": "很遗憾听到这个。能描述一下吗？有什么明显特征吗？", "notes": [{"term": "distinctive features", "explanation": "明显特征/辨识度；帮助工作人员快速识别"}]},
        ],
    },
    "nutrition": {
        "title": "Diet & Health",
        "vocabulary": [
            {"word": "meal prep", "phonetic": "/miːl prep/", "meaning": "备餐（提前做好几天的饭）", "example": "I've started meal prepping on Sundays."},
            {"word": "macros", "phonetic": "/ˈmækrəʊz/", "meaning": "宏量营养素（蛋白质/碳水/脂肪）", "example": "I'm trying to hit my macros every day."},
            {"word": "portion", "phonetic": "/ˈpɔːrʃən/", "meaning": "食物份量", "example": "Portion control is key to weight management."},
            {"word": "cravings", "phonetic": "/ˈkreɪvɪŋz/", "meaning": "嘴馋/对食物的渴望", "example": "I get sugar cravings in the afternoon."},
            {"word": "sustainable", "phonetic": "/səˈsteɪnəbl/", "meaning": "可持续的（长期坚持的）", "example": "The key is finding a diet that's sustainable."},
        ],
        "expressions": [
            {"phrase": "cut back on", "phonetic": "/kʌt bæk ɒn/", "meaning": "减少...的摄入", "example": "I'm trying to cut back on sugar and processed food."},
            {"phrase": "What works for me is...", "phonetic": "/wɒt wɜːrks fɔːr miː ɪz/", "meaning": "对我有效的是...", "example": "What works for me is eating smaller meals more frequently."},
            {"phrase": "everything in moderation", "phonetic": "/ˈevrɪθɪŋ ɪn ˌmɒdəˈreɪʃən/", "meaning": "什么都适量", "example": "I believe in everything in moderation — no need to cut anything completely."},
        ],
        "tips": [
            {"title": "分享经验用 What works for me is... 而非 You should...", "description": "讨论饮食时避免给建议语气（显得说教），用个人经验句式更友好", "example": "What works for me is keeping healthy snacks around so I don't reach for junk food.", "note": "reach for = 去拿/伸手拿；junk food = 垃圾食品"},
            {"title": "用 I'm trying to... 表达正在努力的目标", "description": "比 I want to 更真实——暗示你在行动中而非空想", "example": "I'm trying to cut back on takeout and cook more at home.", "note": "cut back on = 减少；比 reduce 更口语化"},
        ],
        "dialogue": [
            {"speaker": "A", "text": "I've been trying to eat healthier lately. I just started meal prepping on Sundays. Do you pay attention to your diet?", "translation": "我最近在尝试吃得更健康。刚开始周日备餐。你注意饮食吗？", "notes": [{"term": "pay attention to", "explanation": "注意/关注；比 care about 更具体"}, {"term": "meal prepping", "explanation": "提前批量做饭；现在分词做动名词"}]},
            {"speaker": "B", "text": "Honestly, I'm terrible at cooking! But I've been cutting back on sugar and trying to hit my protein goals. What do you usually prep?", "translation": "说实话我做饭超烂！但我一直在减少糖摄入，努力达到蛋白质目标。你一般都做什么？", "notes": [{"term": "terrible at", "explanation": "在...方面很差；自嘲的常用结构"}, {"term": "hit my goals", "explanation": "达到目标；hit = 达到（口语）"}]},
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
