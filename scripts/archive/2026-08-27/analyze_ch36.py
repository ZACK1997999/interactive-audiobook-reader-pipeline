import json

ch36_analysis = [
  {
    "id": "s-0",
    "elem_idx": 0,
    "tag": "h1",
    "text": "THIRTY-SIX",
    "is_heading": True,
    "trans": "第三十六章",
    "vocab": []
  },
  {
    "id": "s-1",
    "elem_idx": 1,
    "tag": "p",
    "text": "Andrew is stuck at work tonight.",
    "is_heading": False,
    "trans": "今晚安德鲁被工作脱不开身，困在了公司。",
    "vocab": [
      {
        "word": "stuck at work",
        "pos": "phrase",
        "def": "被工作缠身，困在公司脱不开身"
      }
    ]
  },
  {
    "id": "s-2",
    "elem_idx": 1,
    "tag": "p",
    "text": "He sent me a regretful text at a quarter to seven:",
    "is_heading": False,
    "trans": "六点四十五分的时候，他带着歉意给我发了一条短信：",
    "vocab": [
      {
        "word": "regretful",
        "pos": "adj",
        "def": "充满歉意的，遗憾的"
      },
      {
        "word": "a quarter to",
        "pos": "phrase",
        "def": "差一刻钟到（几点）"
      }
    ]
  },
  {
    "id": "s-3",
    "elem_idx": 2,
    "tag": "p",
    "text": "Problem at work.",
    "is_heading": False,
    "trans": "工作上出了点状况。",
    "vocab": []
  },
  {
    "id": "s-4",
    "elem_idx": 3,
    "tag": "p",
    "text": "I’m stuck here at least another hour.",
    "is_heading": False,
    "trans": "我至少还得在这儿被绊住一个小时。",
    "vocab": []
  },
  {
    "id": "s-5",
    "elem_idx": 4,
    "tag": "p",
    "text": "Eat without me.",
    "is_heading": False,
    "trans": "你不用等我，先吃吧。",
    "vocab": [
      {
        "word": "eat without sb",
        "pos": "phrase",
        "def": "不用等某人自己先吃"
      }
    ]
  },
  {
    "id": "s-6",
    "elem_idx": 5,
    "tag": "p",
    "text": "I texted back:",
    "is_heading": False,
    "trans": "我回复道：",
    "vocab": [
      {
        "word": "text back",
        "pos": "phr v",
        "def": "回短信"
      }
    ]
  },
  {
    "id": "s-7",
    "elem_idx": 6,
    "tag": "p",
    "text": "No problem.",
    "is_heading": False,
    "trans": "没问题。",
    "vocab": []
  },
  {
    "id": "s-8",
    "elem_idx": 7,
    "tag": "p",
    "text": "Drive safely.",
    "is_heading": False,
    "trans": "开车注意安全。",
    "vocab": []
  },
  {
    "id": "s-9",
    "elem_idx": 8,
    "tag": "p",
    "text": "But inside, I was reeling with disappointment.",
    "is_heading": False,
    "trans": "但我的内心却被强烈的失落感冲击得一阵眩晕。",
    "vocab": [
      {
        "word": "reel with",
        "pos": "phr v",
        "def": "因（强烈情绪/打击）感到眩晕、难以承受"
      },
      {
        "word": "disappointment",
        "pos": "n",
        "def": "失望，失落"
      }
    ]
  },
  {
    "id": "s-10",
    "elem_idx": 8,
    "tag": "p",
    "text": "I had so much fun having dinner in Manhattan with Andrew, and I had been attempting to re-create one of the meals we had at that French restaurant.",
    "is_heading": False,
    "trans": "之前和安德鲁在曼哈顿共进晚餐让我感到无比快乐，我今晚一直在尝试复刻我们当时在那家法餐厅品尝过的一道菜品。",
    "vocab": [
      {
        "word": "re-create",
        "pos": "v",
        "def": "再现，复刻（美食/场景）"
      }
    ]
  },
  {
    "id": "s-11",
    "elem_idx": 8,
    "tag": "p",
    "text": "Steak au poivre.",
    "is_heading": False,
    "trans": "法式黑椒牛排（Steak au poivre）。",
    "vocab": [
      {
        "word": "steak au poivre",
        "pos": "n",
        "def": "法式黑椒牛排"
      }
    ]
  },
  {
    "id": "s-12",
    "elem_idx": 8,
    "tag": "p",
    "text": "I used black peppercorns that I picked up at the supermarket (after I worked up the nerve to go back in), minced shallot, cognac, red wine, beef broth, and heavy whipping cream.",
    "is_heading": False,
    "trans": "我用了在超市买的黑胡椒粒（那是在我鼓足勇气重新走回超市之后买的）、切碎的红葱头、干邑白兰地、红酒、牛肉高汤以及浓奶油。",
    "vocab": [
      {
        "word": "work up the nerve",
        "pos": "phrase",
        "def": "鼓起勇气，壮起胆子"
      },
      {
        "word": "minced shallot",
        "pos": "n",
        "def": "切碎的红葱头/分葱"
      },
      {
        "word": "cognac",
        "pos": "n",
        "def": "干邑白兰地"
      }
    ]
  },
  {
    "id": "s-13",
    "elem_idx": 8,
    "tag": "p",
    "text": "The smell was incredible, but it wasn’t going to keep for another hour or two—steak just isn’t the same reheated.",
    "is_heading": False,
    "trans": "香气扑鼻诱人，但这菜可经不起再放上一两个小时——牛排一旦二次加热就全变味了。",
    "vocab": [
      {
        "word": "keep",
        "pos": "v",
        "def": "（食物）保鲜，存放而不变质"
      },
      {
        "word": "reheated",
        "pos": "adj",
        "def": "重新加热的，热过剩菜的"
      }
    ]
  },
  {
    "id": "s-14",
    "elem_idx": 8,
    "tag": "p",
    "text": "I had no choice but to eat my magnificent dinner all alone.",
    "is_heading": False,
    "trans": "我别无选择，只能孤零零地独自享用这顿丰盛的大餐。",
    "vocab": [
      {
        "word": "have no choice but to",
        "pos": "phrase",
        "def": "别无选择只能……"
      },
      {
        "word": "magnificent",
        "pos": "adj",
        "def": "华丽丰盛的，宏伟的"
      }
    ]
  },
  {
    "id": "s-15",
    "elem_idx": 9,
    "tag": "p",
    "text": "And now it’s sitting in my stomach like a rock while I flick through stations of the television.",
    "is_heading": False,
    "trans": "而现在，当我漫无目的地切换着电视节目频道时，那顿饭就像沉重的石头一样堵在我的胃里。",
    "vocab": [
      {
        "word": "sit like a rock",
        "pos": "phrase",
        "def": "沉甸甸地堵在胃里（难以消化）"
      },
      {
        "word": "flick through",
        "pos": "phr v",
        "def": "频繁切换，快速浏览（频道、书页）"
      }
    ]
  },
  {
    "id": "s-16",
    "elem_idx": 9,
    "tag": "p",
    "text": "I don’t like being in this house alone.",
    "is_heading": False,
    "trans": "我讨厌一个人呆在这栋大宅子里。",
    "vocab": []
  },
  {
    "id": "s-17",
    "elem_idx": 9,
    "tag": "p",
    "text": "When Andrew is here, it feels like his house, which it is.",
    "is_heading": False,
    "trans": "当安德鲁在这里时，这里感觉就像是他真正的家——事实也本该如此。",
    "vocab": []
  },
  {
    "id": "s-18",
    "elem_idx": 9,
    "tag": "p",
    "text": "But when he’s not here, the whole place reeks of Nina.",
    "is_heading": False,
    "trans": "可一旦他不在，整座宅子就充斥着妮娜那股令人作呕的浓烈气息。",
    "vocab": [
      {
        "word": "reek of",
        "pos": "phr v",
        "def": "散发着浓烈/令人不快的恶臭或气息，充斥着"
      }
    ]
  },
  {
    "id": "s-19",
    "elem_idx": 9,
    "tag": "p",
    "text": "Her perfume emanates from every crack and crevice—she’s marked her territory with her scent, like an animal.",
    "is_heading": False,
    "trans": "她的香水味从每一个缝隙角落里弥漫出来——她就像一只野兽，用自己的气味标记了整片领地。",
    "vocab": [
      {
        "word": "emanate from",
        "pos": "phr v",
        "def": "从……散发出来，弥漫"
      },
      {
        "word": "crack and crevice",
        "pos": "phrase",
        "def": "每一个缝隙与角落，角角落落"
      },
      {
        "word": "mark one's territory",
        "pos": "phrase",
        "def": "标记领地，圈地盘"
      }
    ]
  },
  {
    "id": "s-20",
    "elem_idx": 10,
    "tag": "p",
    "text": "Even though Andrew told me not to, I did a deep clean of the house after my shopping trip, trying to get rid of her perfume.",
    "is_heading": False,
    "trans": "尽管安德鲁嘱咐过我别干活，但我采买回来后还是把房子彻底深度打扫了一遍，试图驱散她的香水味。",
    "vocab": [
      {
        "word": "deep clean",
        "pos": "n",
        "def": "深度彻底清洁"
      },
      {
        "word": "get rid of",
        "pos": "phrase",
        "def": "摆脱，去除，消除"
      }
    ]
  },
  {
    "id": "s-21",
    "elem_idx": 10,
    "tag": "p",
    "text": "But I can still smell it.",
    "is_heading": False,
    "trans": "但我依然能闻到那股味道。",
    "vocab": []
  },
  {
    "id": "s-22",
    "elem_idx": 11,
    "tag": "p",
    "text": "As obnoxious as Patrice was in the supermarket, she did me one big favor.",
    "is_heading": False,
    "trans": "虽然帕特里斯在超市里的那副嘴脸令人作呕，但她确实帮了我一个大忙。",
    "vocab": [
      {
        "word": "obnoxious",
        "pos": "adj",
        "def": "令人极度讨厌的，可憎的"
      },
      {
        "word": "do sb a favor",
        "pos": "phrase",
        "def": "帮某人一个忙"
      }
    ]
  },
  {
    "id": "s-23",
    "elem_idx": 11,
    "tag": "p",
    "text": "Nina was tracking me.",
    "is_heading": False,
    "trans": "妮娜一直在暗中定位监控我。",
    "vocab": []
  },
  {
    "id": "s-24",
    "elem_idx": 11,
    "tag": "p",
    "text": "I found the tracking app hidden in a random folder, somewhere I never would’ve seen it.",
    "is_heading": False,
    "trans": "我在一个随意建立的文件夹深处找到了那个追踪软件，藏在我平时绝不会注意到的角落。",
    "vocab": [
      {
        "word": "random folder",
        "pos": "phrase",
        "def": "不起眼的杂项文件夹"
      }
    ]
  },
  {
    "id": "s-25",
    "elem_idx": 11,
    "tag": "p",
    "text": "I deleted it immediately.",
    "is_heading": False,
    "trans": "我毫不犹豫地立刻把它给删了。",
    "vocab": []
  },
  {
    "id": "s-26",
    "elem_idx": 12,
    "tag": "p",
    "text": "But I still can’t shake the feeling that she’s watching me.",
    "is_heading": False,
    "trans": "可我依然无法摆脱那种她正死死盯着我的毛骨悚然感。",
    "vocab": [
      {
        "word": "shake the feeling",
        "pos": "phrase",
        "def": "摆脱/消除某种感觉"
      }
    ]
  },
  {
    "id": "s-27",
    "elem_idx": 13,
    "tag": "p",
    "text": "I close my eyes and I think of the warning Enzo gave me this morning.",
    "is_heading": False,
    "trans": "我闭上双眼，脑海中浮现出恩佐今早给我的警告。",
    "vocab": [
      {
        "word": "warning",
        "pos": "n",
        "def": "警告，告诫"
      }
    ]
  },
  {
    "id": "s-28",
    "elem_idx": 14,
    "tag": "p",
    "text": "You must get out of here.",
    "is_heading": False,
    "trans": "你必须离开这里。",
    "vocab": []
  },
  {
    "id": "s-29",
    "elem_idx": 15,
    "tag": "p",
    "text": "You are in terrible danger.",
    "is_heading": False,
    "trans": "你正处于极度危险之中。",
    "vocab": [
      {
        "word": "in terrible danger",
        "pos": "phrase",
        "def": "身处极度危险中"
      }
    ]
  },
  {
    "id": "s-30",
    "elem_idx": 16,
    "tag": "p",
    "text": "He was afraid of Nina.",
    "is_heading": False,
    "trans": "他当时是在害怕妮娜。",
    "vocab": []
  },
  {
    "id": "s-31",
    "elem_idx": 16,
    "tag": "p",
    "text": "I could see it in his eyes when he and I were talking and she passed within earshot.",
    "is_heading": False,
    "trans": "之前我和他说话时妮娜从能听见声音的近处走过，我能从他的眼神里看出来那种恐惧。",
    "vocab": [
      {
        "word": "within earshot",
        "pos": "phrase",
        "def": "在听力所及的范围内，在听得见声音的距离"
      }
    ]
  },
  {
    "id": "s-32",
    "elem_idx": 17,
    "tag": "p",
    "text": "You are in terrible danger.",
    "is_heading": False,
    "trans": "你正处于极度危险之中。",
    "vocab": []
  },
  {
    "id": "s-33",
    "elem_idx": 18,
    "tag": "p",
    "text": "I push away a wave of nausea.",
    "is_heading": False,
    "trans": "我强行压下一阵阵翻涌上来的恶心感。",
    "vocab": [
      {
        "word": "push away",
        "pos": "phr v",
        "def": "压制，驱散（不适感受）"
      },
      {
        "word": "wave of nausea",
        "pos": "phrase",
        "def": "一阵阵翻涌的恶心感"
      }
    ]
  },
  {
    "id": "s-34",
    "elem_idx": 18,
    "tag": "p",
    "text": "She’s gone now.",
    "is_heading": False,
    "trans": "她现在已经滚蛋了。",
    "vocab": []
  },
  {
    "id": "s-35",
    "elem_idx": 18,
    "tag": "p",
    "text": "But maybe she could still hurt me.",
    "is_heading": False,
    "trans": "但也许她依然有办法伤害我。",
    "vocab": []
  },
  {
    "id": "s-36",
    "elem_idx": 19,
    "tag": "p",
    "text": "The sun has gone down and when I look out the window, all I can see is my reflection.",
    "is_heading": False,
    "trans": "太阳已经落山，当我望向窗外时，入目的只有玻璃上自己的倒影。",
    "vocab": [
      {
        "word": "go down",
        "pos": "phr v",
        "def": "（太阳）落山，下沉"
      },
      {
        "word": "reflection",
        "pos": "n",
        "def": "倒影，反光镜像"
      }
    ]
  },
  {
    "id": "s-37",
    "elem_idx": 20,
    "tag": "p",
    "text": "I stand up from the sofa and walk over to the window, my heart pounding.",
    "is_heading": False,
    "trans": "我从沙发上站起身走向窗边，心脏剧烈地跳动着。",
    "vocab": [
      {
        "word": "heart pounding",
        "pos": "phrase",
        "def": "心怦怦直跳，心跳加速"
      }
    ]
  },
  {
    "id": "s-38",
    "elem_idx": 20,
    "tag": "p",
    "text": "I press my forehead against the cool glass, peering into the dark outside.",
    "is_heading": False,
    "trans": "我把额头贴在冰凉的玻璃上，凝神窥探着外面的漆黑夜色。",
    "vocab": [
      {
        "word": "peer into",
        "pos": "phr v",
        "def": "凝视，眯着眼睛费力端详/窥视"
      }
    ]
  },
  {
    "id": "s-39",
    "elem_idx": 21,
    "tag": "p",
    "text": "Is that a car parked outside the gates?",
    "is_heading": False,
    "trans": "大门外停着的是一辆车吗？",
    "vocab": []
  },
  {
    "id": "s-40",
    "elem_idx": 22,
    "tag": "p",
    "text": "I squint into the darkness, trying to figure out if I’m just imagining things.",
    "is_heading": False,
    "trans": "我眯起眼睛望向黑暗，试图辨清自己是不是在疑神疑鬼、凭空臆想。",
    "vocab": [
      {
        "word": "squint into",
        "pos": "phr v",
        "def": "眯起眼睛打量……"
      },
      {
        "word": "imagine things",
        "pos": "phrase",
        "def": "胡思乱想，疑神疑鬼，产生幻觉"
      }
    ]
  },
  {
    "id": "s-41",
    "elem_idx": 23,
    "tag": "p",
    "text": "I suppose I could go outside and get a closer look.",
    "is_heading": False,
    "trans": "我想我可以出去走近点看个究竟。",
    "vocab": [
      {
        "word": "get a closer look",
        "pos": "phrase",
        "def": "走近仔细看，近距离观察"
      }
    ]
  },
  {
    "id": "s-42",
    "elem_idx": 23,
    "tag": "p",
    "text": "But that would involve unlocking the doors to the house.",
    "is_heading": False,
    "trans": "但那就必须得打开房门的反锁。",
    "vocab": [
      {
        "word": "involve",
        "pos": "v",
        "def": "需要，涉及"
      }
    ]
  },
  {
    "id": "s-43",
    "elem_idx": 24,
    "tag": "p",
    "text": "Of course, what’s the difference if the door is unlocked when Nina has a key?",
    "is_heading": False,
    "trans": "当然，既然妮娜手里握着钥匙，门锁不锁又有什么区别呢？",
    "vocab": [
      {
        "word": "what's the difference",
        "pos": "phrase",
        "def": "有什么区别呢"
      }
    ]
  },
  {
    "id": "s-44",
    "elem_idx": 25,
    "tag": "p",
    "text": "My thoughts are interrupted by the sound of my phone ringing on the coffee table.",
    "is_heading": False,
    "trans": "茶几上响起的手机铃声打断了我的思绪。",
    "vocab": [
      {
        "word": "interrupted by",
        "pos": "phrase",
        "def": "被……打断"
      },
      {
        "word": "coffee table",
        "pos": "n",
        "def": "茶几，咖啡桌"
      }
    ]
  },
  {
    "id": "s-45",
    "elem_idx": 25,
    "tag": "p",
    "text": "I hurry over to grab it before I miss the call and frown when I find another blocked number on the screen.",
    "is_heading": False,
    "trans": "我赶在漏接前匆忙跑过去抓起手机，当看到屏幕上又是一个隐藏号码时，不由得皱紧了眉头。",
    "vocab": [
      {
        "word": "hurry over",
        "pos": "phr v",
        "def": "匆忙赶过去"
      },
      {
        "word": "frown",
        "pos": "v",
        "def": "皱眉"
      }
    ]
  },
  {
    "id": "s-46",
    "elem_idx": 25,
    "tag": "p",
    "text": "I shake my head.",
    "is_heading": False,
    "trans": "我摇了摇头。",
    "vocab": []
  },
  {
    "id": "s-47",
    "elem_idx": 25,
    "tag": "p",
    "text": "Another spam call.",
    "is_heading": False,
    "trans": "又是一个垃圾骚扰电话。",
    "vocab": []
  },
  {
    "id": "s-48",
    "elem_idx": 25,
    "tag": "p",
    "text": "Just what I need.",
    "is_heading": False,
    "trans": "可真是嫌我事不够多（反语）。",
    "vocab": [
      {
        "word": "just what I need",
        "pos": "phrase",
        "def": "（反讽）真来得不是时候，真是雪上加霜"
      }
    ]
  },
  {
    "id": "s-49",
    "elem_idx": 26,
    "tag": "p",
    "text": "I press the green button to accept the call, expecting to hear that obnoxious recorded voice.",
    "is_heading": False,
    "trans": "我按下绿色按键接通电话，做好了听到那讨厌的自动录音语音的心理准备。",
    "vocab": [
      {
        "word": "obnoxious recorded voice",
        "pos": "phrase",
        "def": "令人讨厌的机器录音声音"
      }
    ]
  },
  {
    "id": "s-50",
    "elem_idx": 26,
    "tag": "p",
    "text": "But instead, I hear a distorted, mechanical voice:",
    "is_heading": False,
    "trans": "然而听筒里传来的，却是一个经过变调处理的、冰冷的机械声音：",
    "vocab": [
      {
        "word": "distorted",
        "pos": "adj",
        "def": "变声的，失真的，扭曲的"
      },
      {
        "word": "mechanical",
        "pos": "adj",
        "def": "机械般的，生硬冰冷的"
      }
    ]
  },
  {
    "id": "s-51",
    "elem_idx": 27,
    "tag": "p",
    "text": "“Stay away from Andrew Winchester!”",
    "is_heading": False,
    "trans": "“离安德鲁·温彻斯特远一点！”",
    "vocab": [
      {
        "word": "stay away from",
        "pos": "phrase",
        "def": "远离，离……远点"
      }
    ]
  },
  {
    "id": "s-52",
    "elem_idx": 28,
    "tag": "p",
    "text": "I suck in a breath.",
    "is_heading": False,
    "trans": "我猛地倒吸了一口凉气。",
    "vocab": [
      {
        "word": "suck in a breath",
        "pos": "phrase",
        "def": "倒吸一口凉气"
      }
    ]
  },
  {
    "id": "s-53",
    "elem_idx": 29,
    "tag": "p",
    "text": "“Nina?”",
    "is_heading": False,
    "trans": "“妮娜？”",
    "vocab": []
  },
  {
    "id": "s-54",
    "elem_idx": 30,
    "tag": "p",
    "text": "I couldn’t tell if it was a man or a woman, much less whether it was Nina.",
    "is_heading": False,
    "trans": "我根本分辨不出对方是男是女，更别说判断是不是妮娜了。",
    "vocab": [
      {
        "word": "tell",
        "pos": "v",
        "def": "分辨，辨别出"
      },
      {
        "word": "much less",
        "pos": "phrase",
        "def": "更不用说"
      }
    ]
  },
  {
    "id": "s-55",
    "elem_idx": 30,
    "tag": "p",
    "text": "Then there’s a click on the other line.",
    "is_heading": False,
    "trans": "紧接着电话那头传来咔哒一声。",
    "vocab": [
      {
        "word": "click",
        "pos": "n",
        "def": "咔哒声（挂断电话的声音）"
      },
      {
        "word": "other line",
        "pos": "phrase",
        "def": "电话那一端"
      }
    ]
  },
  {
    "id": "s-56",
    "elem_idx": 30,
    "tag": "p",
    "text": "It’s gone dead.",
    "is_heading": False,
    "trans": "对方挂断了，只剩下一片忙音盲音。",
    "vocab": [
      {
        "word": "go dead",
        "pos": "phrase",
        "def": "（电话）断线，变盲音"
      }
    ]
  },
  {
    "id": "s-57",
    "elem_idx": 31,
    "tag": "p",
    "text": "I swallow.",
    "is_heading": False,
    "trans": "我咽了口唾沫。",
    "vocab": [
      {
        "word": "swallow",
        "pos": "v",
        "def": "咽口水（表现紧张害怕）"
      }
    ]
  },
  {
    "id": "s-58",
    "elem_idx": 31,
    "tag": "p",
    "text": "I’ve had enough of Nina’s games.",
    "is_heading": False,
    "trans": "我已经受够了妮娜玩的这套把戏。",
    "vocab": [
      {
        "word": "have enough of",
        "pos": "phrase",
        "def": "受够了……，对……忍无可忍"
      },
      {
        "word": "games",
        "pos": "n",
        "def": "把戏，花招，心机手段"
      }
    ]
  },
  {
    "id": "s-59",
    "elem_idx": 31,
    "tag": "p",
    "text": "Starting tomorrow, I’m taking back this house.",
    "is_heading": False,
    "trans": "从明天开始，我要彻底夺回这栋房子。",
    "vocab": [
      {
        "word": "take back",
        "pos": "phr v",
        "def": "收回，夺回（主权/空间）"
      }
    ]
  },
  {
    "id": "s-60",
    "elem_idx": 31,
    "tag": "p",
    "text": "I’m calling a locksmith to change the locks on the doors.",
    "is_heading": False,
    "trans": "我要找锁匠把所有门上的锁全给换了。",
    "vocab": [
      {
        "word": "locksmith",
        "pos": "n",
        "def": "锁匠"
      },
      {
        "word": "change the locks",
        "pos": "phrase",
        "def": "更换门锁"
      }
    ]
  },
  {
    "id": "s-61",
    "elem_idx": 32,
    "tag": "p",
    "text": "And tonight, I’m spending the night in the master bedroom.",
    "is_heading": False,
    "trans": "而且今晚，我就要搬到主卧去睡。",
    "vocab": [
      {
        "word": "master bedroom",
        "pos": "n",
        "def": "主卧，主人房"
      }
    ]
  },
  {
    "id": "s-62",
    "elem_idx": 32,
    "tag": "p",
    "text": "Enough of this guest bedroom bullshit.",
    "is_heading": False,
    "trans": "我受够了客房那些缩手缩脚的烂事。",
    "vocab": [
      {
        "word": "enough of",
        "pos": "phrase",
        "def": "……到此为止，受够了……"
      },
      {
        "word": "bullshit",
        "pos": "n",
        "def": "烂事，狗屁规矩"
      }
    ]
  },
  {
    "id": "s-63",
    "elem_idx": 32,
    "tag": "p",
    "text": "I’m not a guest here anymore.",
    "is_heading": False,
    "trans": "我在这里不再是什么借宿的客人了。",
    "vocab": []
  },
  {
    "id": "s-64",
    "elem_idx": 32,
    "tag": "p",
    "text": "Andrew said he wanted this to become permanent.",
    "is_heading": False,
    "trans": "安德鲁说过他希望我们之间成为长久固定的关系。",
    "vocab": [
      {
        "word": "permanent",
        "pos": "adj",
        "def": "长期的，永久的，固定长久的"
      }
    ]
  },
  {
    "id": "s-65",
    "elem_idx": 32,
    "tag": "p",
    "text": "So now, this is my home too.",
    "is_heading": False,
    "trans": "所以从现在起，这也是我的家了。",
    "vocab": []
  },
  {
    "id": "s-66",
    "elem_idx": 33,
    "tag": "p",
    "text": "I head for the stairs, taking them two at a time.",
    "is_heading": False,
    "trans": "我朝楼梯走去，一步两级台阶快步往上爬。",
    "vocab": [
      {
        "word": "head for",
        "pos": "phr v",
        "def": "走向，前往"
      },
      {
        "word": "take sth two at a time",
        "pos": "phrase",
        "def": "一次跨两级（台阶）"
      }
    ]
  },
  {
    "id": "s-67",
    "elem_idx": 33,
    "tag": "p",
    "text": "I keep going until I get up to the stuffy room in the attic—my bedroom.",
    "is_heading": False,
    "trans": "我一路向上，直到来到阁楼上那间闷热逼仄的房间——也就是我原来的卧室。",
    "vocab": [
      {
        "word": "stuffy",
        "pos": "adj",
        "def": "闷热憋闷的，不透气的"
      },
      {
        "word": "attic",
        "pos": "n",
        "def": "阁楼，顶楼房间"
      }
    ]
  },
  {
    "id": "s-68",
    "elem_idx": 33,
    "tag": "p",
    "text": "Except it won’t be my bedroom after tonight.",
    "is_heading": False,
    "trans": "只不过过了今晚，这里就不再是我的卧室了。",
    "vocab": []
  },
  {
    "id": "s-69",
    "elem_idx": 34,
    "tag": "p",
    "text": "I’m packing everything up and moving downstairs.",
    "is_heading": False,
    "trans": "我要把所有行李统统打包，搬到楼下去住。",
    "vocab": [
      {
        "word": "pack up",
        "pos": "phr v",
        "def": "收拾行李，打包整理"
      }
    ]
  },
  {
    "id": "s-70",
    "elem_idx": 34,
    "tag": "p",
    "text": "This will be my last time in this claustrophobic little room with the weird lock on the outside of the door.",
    "is_heading": False,
    "trans": "这将是我最后一次呆在这间狭窄压抑、门外还装着奇怪门锁的小破屋里。",
    "vocab": [
      {
        "word": "claustrophobic",
        "pos": "adj",
        "def": "狭窄压抑的，让人窒息幽闭的"
      },
      {
        "word": "on the outside of",
        "pos": "phrase",
        "def": "在……外面"
      }
    ]
  },
  {
    "id": "s-71",
    "elem_idx": 35,
    "tag": "p",
    "text": "I grab one of my pieces of luggage out of the closet.",
    "is_heading": False,
    "trans": "我从壁橱里拉出我的一个行李箱。",
    "vocab": [
      {
        "word": "piece of luggage",
        "pos": "n",
        "def": "一件行李箱/包"
      }
    ]
  },
  {
    "id": "s-72",
    "elem_idx": 35,
    "tag": "p",
    "text": "I start throwing clothing inside, not bothering to be too careful, given that I’m just carrying it down one flight of stairs.",
    "is_heading": False,
    "trans": "我开始把衣服往里扔，也没费心思仔细叠好，反正也就是搬下一层楼而已。",
    "vocab": [
      {
        "word": "not bother to",
        "pos": "phrase",
        "def": "懒得……，不费心思去……"
      },
      {
        "word": "given that",
        "pos": "conjunction",
        "def": "考虑到，鉴于"
      },
      {
        "word": "flight of stairs",
        "pos": "n",
        "def": "一段楼梯"
      }
    ]
  },
  {
    "id": "s-73",
    "elem_idx": 35,
    "tag": "p",
    "text": "Of course, I’ll have to ask Andrew’s permission before I clean out a drawer downstairs.",
    "is_heading": False,
    "trans": "当然，在清理楼下的抽屉腾地方之前，我肯定得先征求安德鲁的同意。",
    "vocab": [
      {
        "word": "ask sb's permission",
        "pos": "phrase",
        "def": "征求某人的许可/同意"
      },
      {
        "word": "clean out",
        "pos": "phr v",
        "def": "清空，腾空（抽屉/柜子）"
      }
    ]
  },
  {
    "id": "s-74",
    "elem_idx": 35,
    "tag": "p",
    "text": "But he can’t expect me to live up here anymore.",
    "is_heading": False,
    "trans": "但他绝不可能指望我还继续住在上面这里。",
    "vocab": []
  },
  {
    "id": "s-75",
    "elem_idx": 35,
    "tag": "p",
    "text": "It’s inhuman.",
    "is_heading": False,
    "trans": "这根本不是人住的地方。",
    "vocab": [
      {
        "word": "inhuman",
        "pos": "adj",
        "def": "不人道的，惨无人道的，非人的"
      }
    ]
  },
  {
    "id": "s-76",
    "elem_idx": 35,
    "tag": "p",
    "text": "This room is like some sort of torture chamber.",
    "is_heading": False,
    "trans": "这间屋子简直就像某种刑讯折磨室一样。",
    "vocab": [
      {
        "word": "torture chamber",
        "pos": "n",
        "def": "刑讯室，酷刑折磨密室"
      }
    ]
  },
  {
    "id": "s-77",
    "elem_idx": 36,
    "tag": "p",
    "text": "“Millie?",
    "is_heading": False,
    "trans": "“米莉？",
    "vocab": []
  },
  {
    "id": "s-78",
    "elem_idx": 36,
    "tag": "p",
    "text": "What are you doing?”",
    "is_heading": False,
    "trans": "你在干什么呢？”",
    "vocab": []
  },
  {
    "id": "s-79",
    "elem_idx": 37,
    "tag": "p",
    "text": "The voice from behind me nearly gives me a heart attack.",
    "is_heading": False,
    "trans": "身后冷不丁传来的声音差点把我吓出心脏病。",
    "vocab": [
      {
        "word": "give sb a heart attack",
        "pos": "idiom",
        "def": "把某人吓一大跳/吓得半死"
      }
    ]
  },
  {
    "id": "s-80",
    "elem_idx": 37,
    "tag": "p",
    "text": "I clutch my chest and turn around.",
    "is_heading": False,
    "trans": "我捂着胸口转过身来。",
    "vocab": [
      {
        "word": "clutch one's chest",
        "pos": "phrase",
        "def": "捂住胸口"
      }
    ]
  },
  {
    "id": "s-81",
    "elem_idx": 38,
    "tag": "p",
    "text": "“Andrew.",
    "is_heading": False,
    "trans": "“安德鲁。",
    "vocab": []
  },
  {
    "id": "s-82",
    "elem_idx": 38,
    "tag": "p",
    "text": "I didn’t hear you come in.”",
    "is_heading": False,
    "trans": "我都没听到你进屋的声音。”",
    "vocab": []
  },
  {
    "id": "s-83",
    "elem_idx": 39,
    "tag": "p",
    "text": "His gaze darts over my luggage.",
    "is_heading": False,
    "trans": "他的目光扫向了我的行李箱。",
    "vocab": [
      {
        "word": "gaze darts over",
        "pos": "phrase",
        "def": "目光敏锐迅速地扫过"
      }
    ]
  },
  {
    "id": "s-84",
    "elem_idx": 39,
    "tag": "p",
    "text": "“What are you doing?”",
    "is_heading": False,
    "trans": "“你这是在做什么？”",
    "vocab": []
  },
  {
    "id": "s-85",
    "elem_idx": 40,
    "tag": "p",
    "text": "I shove the handful of bras I was holding into the luggage.",
    "is_heading": False,
    "trans": "我把手里攥着的一把文胸塞进了箱子里。",
    "vocab": [
      {
        "word": "shove",
        "pos": "v",
        "def": "猛推，硬塞"
      },
      {
        "word": "handful of",
        "pos": "n",
        "def": "一把，少量"
      }
    ]
  },
  {
    "id": "s-86",
    "elem_idx": 40,
    "tag": "p",
    "text": "“Well, I thought I might move downstairs.”",
    "is_heading": False,
    "trans": "“嗯……我想着或许我可以搬到楼下去。”",
    "vocab": []
  },
  {
    "id": "s-87",
    "elem_idx": 41,
    "tag": "p",
    "text": "“Oh.”",
    "is_heading": False,
    "trans": "“噢。”",
    "vocab": []
  },
  {
    "id": "s-88",
    "elem_idx": 42,
    "tag": "p",
    "text": "“Is… is that okay?”",
    "is_heading": False,
    "trans": "“这……可以吗？”",
    "vocab": []
  },
  {
    "id": "s-89",
    "elem_idx": 43,
    "tag": "p",
    "text": "I feel suddenly awkward.",
    "is_heading": False,
    "trans": "我突然感到一阵局促尴尬。",
    "vocab": [
      {
        "word": "awkward",
        "pos": "adj",
        "def": "尴尬局促的，不自然的"
      }
    ]
  },
  {
    "id": "s-90",
    "elem_idx": 43,
    "tag": "p",
    "text": "I had assumed Andrew would be fine with it, but maybe I shouldn’t have made that assumption.",
    "is_heading": False,
    "trans": "我本以为安德鲁肯定不会介意，但也许我不该擅自做这种预设。",
    "vocab": [
      {
        "word": "fine with it",
        "pos": "phrase",
        "def": "不介意，乐意接受"
      },
      {
        "word": "make that assumption",
        "pos": "phrase",
        "def": "做出那种臆断/假定"
      }
    ]
  },
  {
    "id": "s-91",
    "elem_idx": 44,
    "tag": "p",
    "text": "He takes a step toward me.",
    "is_heading": False,
    "trans": "他朝我迈近了一步。",
    "vocab": []
  },
  {
    "id": "s-92",
    "elem_idx": 44,
    "tag": "p",
    "text": "I bite down on my lip until it hurts.",
    "is_heading": False,
    "trans": "我紧咬着嘴唇，直到感到隐隐生疼。",
    "vocab": [
      {
        "word": "bite down on",
        "pos": "phrase",
        "def": "紧咬住（嘴唇等）"
      }
    ]
  },
  {
    "id": "s-93",
    "elem_idx": 45,
    "tag": "p",
    "text": "“Of course it’s okay.",
    "is_heading": False,
    "trans": "“当然可以了。",
    "vocab": []
  },
  {
    "id": "s-94",
    "elem_idx": 45,
    "tag": "p",
    "text": "I was going to suggest it myself.",
    "is_heading": False,
    "trans": "我本来也打算主动向你提议的。",
    "vocab": [
      {
        "word": "suggest",
        "pos": "v",
        "def": "建议，提议"
      }
    ]
  },
  {
    "id": "s-95",
    "elem_idx": 45,
    "tag": "p",
    "text": "But I wasn’t sure if you would want to.”",
    "is_heading": False,
    "trans": "只是我不确定你是否愿意。”",
    "vocab": []
  },
  {
    "id": "s-96",
    "elem_idx": 46,
    "tag": "p",
    "text": "My shoulders sag.",
    "is_heading": False,
    "trans": "我紧绷的双肩终于松弛了下来。",
    "vocab": [
      {
        "word": "shoulders sag",
        "pos": "phrase",
        "def": "双肩下沉，如释重负地放松下来"
      }
    ]
  },
  {
    "id": "s-97",
    "elem_idx": 47,
    "tag": "p",
    "text": "“I definitely want to.",
    "is_heading": False,
    "trans": "“我当然非常愿意。",
    "vocab": []
  },
  {
    "id": "s-98",
    "elem_idx": 47,
    "tag": "p",
    "text": "I… I had kind of a rough day.”",
    "is_heading": False,
    "trans": "我……我今天过得挺糟糕折腾的。”",
    "vocab": [
      {
        "word": "rough day",
        "pos": "phrase",
        "def": "艰难/心力交瘁的一天"
      }
    ]
  },
  {
    "id": "s-99",
    "elem_idx": 48,
    "tag": "p",
    "text": "“What have you been up to?",
    "is_heading": False,
    "trans": "“你今天都忙什么了？",
    "vocab": [
      {
        "word": "up to",
        "pos": "phrase",
        "def": "忙于做……，从事……"
      }
    ]
  },
  {
    "id": "s-100",
    "elem_idx": 48,
    "tag": "p",
    "text": "I saw some of my books on the coffee table.",
    "is_heading": False,
    "trans": "我看到茶几上放着我的几本书。",
    "vocab": []
  },
  {
    "id": "s-101",
    "elem_idx": 48,
    "tag": "p",
    "text": "Have you been reading?”",
    "is_heading": False,
    "trans": "你在看书吗？”",
    "vocab": []
  },
  {
    "id": "s-102",
    "elem_idx": 49,
    "tag": "p",
    "text": "I wish that’s all I had been doing today.",
    "is_heading": False,
    "trans": "我真希望我今天就只是看了书而已。",
    "vocab": []
  },
  {
    "id": "s-103",
    "elem_idx": 49,
    "tag": "p",
    "text": "“Honestly, I don’t want to talk about it.”",
    "is_heading": False,
    "trans": "“说实话，我不太想谈今天的事。”",
    "vocab": []
  },
  {
    "id": "s-104",
    "elem_idx": 50,
    "tag": "p",
    "text": "He takes another step closer and reaches out to trace my jaw with the tip of his finger.",
    "is_heading": False,
    "trans": "他又走近了一步，伸出指尖轻柔地抚摹着我的下颌线。",
    "vocab": [
      {
        "word": "trace",
        "pos": "v",
        "def": "勾勒，用指尖抚摸"
      },
      {
        "word": "jaw",
        "pos": "n",
        "def": "下巴，下颌"
      }
    ]
  },
  {
    "id": "s-105",
    "elem_idx": 51,
    "tag": "p",
    "text": "“Maybe I could make you forget about it…”",
    "is_heading": False,
    "trans": "“也许我能让你把那些烦心事全忘掉……”",
    "vocab": [
      {
        "word": "forget about",
        "pos": "phr v",
        "def": "忘掉，抛之脑后"
      }
    ]
  },
  {
    "id": "s-106",
    "elem_idx": 52,
    "tag": "p",
    "text": "I shiver at his touch.",
    "is_heading": False,
    "trans": "在他的触碰下，我浑身泛起一阵战栗。",
    "vocab": [
      {
        "word": "shiver at",
        "pos": "phrase",
        "def": "在……下战栗/微颤"
      }
    ]
  },
  {
    "id": "s-107",
    "elem_idx": 53,
    "tag": "p",
    "text": "“I bet you could…”",
    "is_heading": False,
    "trans": "“我敢打赌你肯定行……”",
    "vocab": [
      {
        "word": "I bet",
        "pos": "phrase",
        "def": "我敢肯定，我敢打赌"
      }
    ]
  },
  {
    "id": "s-108",
    "elem_idx": 54,
    "tag": "p",
    "text": "And he does.",
    "is_heading": False,
    "trans": "而他也确实做到了。",
    "vocab": []
  }
]

out_path = "/Users/lindy/Vault/audiobook/The Housemaid/the_housemaid_ch36_full_analysis.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(ch36_analysis, f, indent=2, ensure_ascii=False)

print(f"Successfully generated {out_path} with {len(ch36_analysis)} sentences.")
