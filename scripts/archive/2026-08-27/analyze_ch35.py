import json

ch35_analysis = [
  {
    "id": "s-0",
    "elem_idx": 0,
    "tag": "h1",
    "text": "THIRTY-FIVE",
    "is_heading": True,
    "trans": "第三十五章",
    "vocab": []
  },
  {
    "id": "s-1",
    "elem_idx": 1,
    "tag": "p",
    "text": "Andrew told me that I shouldn’t be doing any work for the house, but Monday I usually go grocery shopping, and we’re low on a lot of supplies.",
    "is_heading": False,
    "trans": "安德鲁跟我说过不用再做家里的任何活儿了，但周一我通常都要去买菜采买，而且家里的很多日用品也快见底了。",
    "vocab": [
      {
        "word": "low on",
        "pos": "adj",
        "def": "（某物）短缺，存量不足，快用完了"
      },
      {
        "word": "supplies",
        "pos": "n",
        "def": "生活用品，日常物资"
      }
    ]
  },
  {
    "id": "s-2",
    "elem_idx": 1,
    "tag": "p",
    "text": "And after I flip through a few books I pulled out of the bookcase and watch a little TV, I’m itching for something else to do with myself.",
    "is_heading": False,
    "trans": "在随手翻了翻从书架上抽出来的几本书、又看了会儿电视之后，我心里直犯痒，总想找点别的事情来打发时间。",
    "vocab": [
      {
        "word": "flip through",
        "pos": "phr v",
        "def": "快速翻阅，随手翻看"
      },
      {
        "word": "itching for",
        "pos": "phrase",
        "def": "渴望做……，心里按捺不住想做……"
      },
      {
        "word": "do with oneself",
        "pos": "phrase",
        "def": "打发时间，安置自己"
      }
    ]
  },
  {
    "id": "s-3",
    "elem_idx": 1,
    "tag": "p",
    "text": "Unlike Nina, I like keeping busy.",
    "is_heading": False,
    "trans": "不像妮娜那样，我喜欢让自己忙碌充实起来。",
    "vocab": [
      {
        "word": "keep busy",
        "pos": "phrase",
        "def": "让自己保持忙碌/充实"
      }
    ]
  },
  {
    "id": "s-4",
    "elem_idx": 1,
    "tag": "p",
    "text": "I have been meticulously avoiding the grocery store where that security guard tried to apprehend me.",
    "is_heading": False,
    "trans": "我一直谨小慎微地避开那个曾有保安试图扣押我的杂货超市。",
    "vocab": [
      {
        "word": "meticulously",
        "pos": "adv",
        "def": "一丝不苟地，谨小慎微地"
      },
      {
        "word": "apprehend",
        "pos": "v",
        "def": "拘捕，扣押，逮捕"
      }
    ]
  },
  {
    "id": "s-5",
    "elem_idx": 1,
    "tag": "p",
    "text": "Instead, I go to a different grocery store in another part of town.",
    "is_heading": False,
    "trans": "相反，我去了城镇另一头的另一家杂货店。",
    "vocab": []
  },
  {
    "id": "s-6",
    "elem_idx": 1,
    "tag": "p",
    "text": "They’re all the same anyway.",
    "is_heading": False,
    "trans": "反正这些超市都大同小异。",
    "vocab": [
      {
        "word": "all the same",
        "pos": "phrase",
        "def": "大同小异，都一样"
      }
    ]
  },
  {
    "id": "s-7",
    "elem_idx": 2,
    "tag": "p",
    "text": "The best part is pushing my cart around the store and not having to follow Nina’s stupid pretentious grocery list.",
    "is_heading": False,
    "trans": "最爽的莫过于推着购物车在店里闲逛，再也不用照着妮娜那张愚蠢又做作的采购清单买了。",
    "vocab": [
      {
        "word": "the best part",
        "pos": "phrase",
        "def": "最棒的部分，最惬意的事"
      },
      {
        "word": "pretentious",
        "pos": "adj",
        "def": "自命不凡的，做作矫情的"
      }
    ]
  },
  {
    "id": "s-8",
    "elem_idx": 2,
    "tag": "p",
    "text": "I can buy whatever I want.",
    "is_heading": False,
    "trans": "我想买什么就可以买什么。",
    "vocab": []
  },
  {
    "id": "s-9",
    "elem_idx": 2,
    "tag": "p",
    "text": "If I want to get brioche bread, I’ll get brioche.",
    "is_heading": False,
    "trans": "如果我想买布里欧修面包，我就买布里欧修。",
    "vocab": [
      {
        "word": "brioche",
        "pos": "n",
        "def": "法式布里欧修奶油面包"
      }
    ]
  },
  {
    "id": "s-10",
    "elem_idx": 2,
    "tag": "p",
    "text": "And if I want to get sourdough, I’ll get that.",
    "is_heading": False,
    "trans": "如果我想买酸种面包，我就买酸种面包。",
    "vocab": [
      {
        "word": "sourdough",
        "pos": "n",
        "def": "天然酵母酸面包，酸种面包"
      }
    ]
  },
  {
    "id": "s-11",
    "elem_idx": 2,
    "tag": "p",
    "text": "I don’t have to send her a hundred pictures of every kind of bread.",
    "is_heading": False,
    "trans": "我再也不用把每种面包拍上一百张照片发给她过目了。",
    "vocab": []
  },
  {
    "id": "s-12",
    "elem_idx": 2,
    "tag": "p",
    "text": "It’s so liberating.",
    "is_heading": False,
    "trans": "这种感觉真是太解脱、太自由了。",
    "vocab": [
      {
        "word": "liberating",
        "pos": "adj",
        "def": "令人倍感自由的，解脱束缚的"
      }
    ]
  },
  {
    "id": "s-13",
    "elem_idx": 3,
    "tag": "p",
    "text": "While I am looking through the dairy aisle, my phone rings inside my purse.",
    "is_heading": False,
    "trans": "当我正在乳制品通道挑选时，手提包里的手机响了起来。",
    "vocab": [
      {
        "word": "dairy aisle",
        "pos": "n",
        "def": "超市乳品专区通道"
      }
    ]
  },
  {
    "id": "s-14",
    "elem_idx": 3,
    "tag": "p",
    "text": "Again, I get that unsettled feeling.",
    "is_heading": False,
    "trans": "那种惴惴不安的感觉再次涌上心头。",
    "vocab": [
      {
        "word": "unsettled",
        "pos": "adj",
        "def": "忐忑不安的，心神不宁的"
      }
    ]
  },
  {
    "id": "s-15",
    "elem_idx": 3,
    "tag": "p",
    "text": "Who could be calling me?",
    "is_heading": False,
    "trans": "会是谁打给我的呢？",
    "vocab": []
  },
  {
    "id": "s-16",
    "elem_idx": 3,
    "tag": "p",
    "text": "Maybe it’s Andrew.",
    "is_heading": False,
    "trans": "也许是安德鲁。",
    "vocab": []
  },
  {
    "id": "s-17",
    "elem_idx": 3,
    "tag": "p",
    "text": "I reach into my purse and pull out the phone.",
    "is_heading": False,
    "trans": "我把手伸进包里，掏出了手机。",
    "vocab": [
      {
        "word": "reach into",
        "pos": "phrase",
        "def": "伸手伸入……中"
      }
    ]
  },
  {
    "id": "s-18",
    "elem_idx": 3,
    "tag": "p",
    "text": "Again, there’s that blocked number.",
    "is_heading": False,
    "trans": "屏幕上显示的又是那个被屏蔽的隐藏号码。",
    "vocab": [
      {
        "word": "blocked number",
        "pos": "n",
        "def": "隐藏号码，未显示来电号码"
      }
    ]
  },
  {
    "id": "s-19",
    "elem_idx": 3,
    "tag": "p",
    "text": "Whoever called me this morning is trying to call me again.",
    "is_heading": False,
    "trans": "今天早上给我打电话的那个人又试着打进来了。",
    "vocab": []
  },
  {
    "id": "s-20",
    "elem_idx": 4,
    "tag": "p",
    "text": "“Millie, is it?”",
    "is_heading": False,
    "trans": "“你是米莉，对吧？”",
    "vocab": []
  },
  {
    "id": "s-21",
    "elem_idx": 5,
    "tag": "p",
    "text": "I nearly jump out of my skin.",
    "is_heading": False,
    "trans": "我吓得差点魂飞魄散。",
    "vocab": [
      {
        "word": "jump out of one's skin",
        "pos": "idiom",
        "def": "大吃一惊，吓得魂飞魄散"
      }
    ]
  },
  {
    "id": "s-22",
    "elem_idx": 5,
    "tag": "p",
    "text": "I look up and it’s one of those women Nina had over for her PTA meeting—I can’t remember her name.",
    "is_heading": False,
    "trans": "我抬起头，认出她是妮娜之前请来家里开家长教师联谊会（PTA）的那些女人之一——我记不清她的名字了。",
    "vocab": [
      {
        "word": "PTA",
        "pos": "n",
        "def": "家长教师协会（Parent-Teacher Association）"
      },
      {
        "word": "have sb over",
        "pos": "phr v",
        "def": "请某人到家里来"
      }
    ]
  },
  {
    "id": "s-23",
    "elem_idx": 5,
    "tag": "p",
    "text": "She’s pushing her own shopping cart, and she’s got a phony smile on her plump, painted lips.",
    "is_heading": False,
    "trans": "她推着自己的购物车，丰满且涂抹得精致的嘴唇上挂着一抹虚情假意的假笑。",
    "vocab": [
      {
        "word": "phony",
        "pos": "adj",
        "def": "虚假的，虚情假意的"
      },
      {
        "word": "plump",
        "pos": "adj",
        "def": "丰满的，圆润的"
      },
      {
        "word": "painted lips",
        "pos": "phrase",
        "def": "涂抹口红的嘴唇"
      }
    ]
  },
  {
    "id": "s-24",
    "elem_idx": 6,
    "tag": "p",
    "text": "“Yes?”",
    "is_heading": False,
    "trans": "“找我有事吗？”",
    "vocab": []
  },
  {
    "id": "s-25",
    "elem_idx": 6,
    "tag": "p",
    "text": "I say.",
    "is_heading": False,
    "trans": "我说道。",
    "vocab": []
  },
  {
    "id": "s-26",
    "elem_idx": 7,
    "tag": "p",
    "text": "“I’m Patrice,” she says.",
    "is_heading": False,
    "trans": "“我是帕特里斯，”她说。",
    "vocab": []
  },
  {
    "id": "s-27",
    "elem_idx": 7,
    "tag": "p",
    "text": "“You’re Nina’s girl, right?”",
    "is_heading": False,
    "trans": "“你是妮娜家的小女佣，对吧？”",
    "vocab": [
      {
        "word": "girl",
        "pos": "n",
        "def": "（轻蔑/居高临下的称呼）女佣，丫鬟"
      }
    ]
  },
  {
    "id": "s-28",
    "elem_idx": 8,
    "tag": "p",
    "text": "I bristle at the label she gave me.",
    "is_heading": False,
    "trans": "她给我扣上的这个称呼让我瞬间恼火刺痛。",
    "vocab": [
      {
        "word": "bristle at",
        "pos": "phr v",
        "def": "对……感到恼怒/炸毛，反感"
      },
      {
        "word": "label",
        "pos": "n",
        "def": "标签，贬称"
      }
    ]
  },
  {
    "id": "s-29",
    "elem_idx": 8,
    "tag": "p",
    "text": "Nina’s girl.",
    "is_heading": False,
    "trans": "妮娜的小女佣。",
    "vocab": []
  },
  {
    "id": "s-30",
    "elem_idx": 8,
    "tag": "p",
    "text": "Wow.",
    "is_heading": False,
    "trans": "呵，可真有意思。",
    "vocab": []
  },
  {
    "id": "s-31",
    "elem_idx": 8,
    "tag": "p",
    "text": "Wait till she finds out that Andrew dumped Nina and she’s going to be screwed over in the divorce thanks to the prenup.",
    "is_heading": False,
    "trans": "等她发现安德鲁把妮娜给甩了、而且多亏婚前协议妮娜在离婚时落得净身出户血本无归，看她怎么说。",
    "vocab": [
      {
        "word": "dump",
        "pos": "v",
        "def": "甩掉（伴侣），抛弃"
      },
      {
        "word": "screwed over",
        "pos": "phrase",
        "def": "被坑惨，落入惨境"
      },
      {
        "word": "prenup",
        "pos": "n",
        "def": "婚前协议（prenuptial agreement口语缩写）"
      }
    ]
  },
  {
    "id": "s-32",
    "elem_idx": 8,
    "tag": "p",
    "text": "Wait till she finds out that I am Andrew Winchester’s new girlfriend.",
    "is_heading": False,
    "trans": "等她知道我才是安德鲁·温彻斯特的新女友时，瞧瞧她会是什么嘴脸。",
    "vocab": []
  },
  {
    "id": "s-33",
    "elem_idx": 8,
    "tag": "p",
    "text": "Soon maybe I’ll be the one she has to suck up to.",
    "is_heading": False,
    "trans": "说不定很快，我就会变成那个她不得不低头巴结讨好的人了。",
    "vocab": [
      {
        "word": "suck up to",
        "pos": "phr v",
        "def": "巴结，奉承，讨好"
      }
    ]
  },
  {
    "id": "s-34",
    "elem_idx": 9,
    "tag": "p",
    "text": "“I work for the Winchesters,” I say stiffly.",
    "is_heading": False,
    "trans": "“我受雇于温彻斯特一家，”我语气生硬地纠正道。",
    "vocab": [
      {
        "word": "stiffly",
        "pos": "adv",
        "def": "生硬地，冷淡地"
      }
    ]
  },
  {
    "id": "s-35",
    "elem_idx": 10,
    "tag": "p",
    "text": "But not for long.",
    "is_heading": False,
    "trans": "不过很快就不是雇佣关系了。",
    "vocab": [
      {
        "word": "not for long",
        "pos": "phrase",
        "def": "不会太久了，马上就变了"
      }
    ]
  },
  {
    "id": "s-36",
    "elem_idx": 11,
    "tag": "p",
    "text": "“Oh, good.”",
    "is_heading": False,
    "trans": "“噢，太好了。”",
    "vocab": []
  },
  {
    "id": "s-37",
    "elem_idx": 11,
    "tag": "p",
    "text": "Her smile broadens.",
    "is_heading": False,
    "trans": "她的笑容更深了。",
    "vocab": [
      {
        "word": "broaden",
        "pos": "v",
        "def": "（笑容）放大，笑得更开"
      }
    ]
  },
  {
    "id": "s-38",
    "elem_idx": 11,
    "tag": "p",
    "text": "“I’ve been trying to get in touch with Nina all morning.",
    "is_heading": False,
    "trans": "“我一整个早上都在设法联系妮娜。",
    "vocab": [
      {
        "word": "get in touch with",
        "pos": "phrase",
        "def": "与……取得联系"
      }
    ]
  },
  {
    "id": "s-39",
    "elem_idx": 11,
    "tag": "p",
    "text": "She and I were supposed to get together for brunch—we always have brunch Monday and Thursday at Kristen’s Diner—but she never showed up.",
    "is_heading": False,
    "trans": "我和她原本约好一起吃早午餐——我们每周一和周四总会在克里斯汀餐厅吃早午餐——但她根本没露面。",
    "vocab": [
      {
        "word": "supposed to",
        "pos": "phrase",
        "def": "原本应该，按约定"
      },
      {
        "word": "get together",
        "pos": "phr v",
        "def": "聚会，碰头"
      },
      {
        "word": "show up",
        "pos": "phr v",
        "def": "露面，现身，出席"
      }
    ]
  },
  {
    "id": "s-40",
    "elem_idx": 11,
    "tag": "p",
    "text": "Is everything okay?”",
    "is_heading": False,
    "trans": "一切都还好吗？”",
    "vocab": []
  },
  {
    "id": "s-41",
    "elem_idx": 12,
    "tag": "p",
    "text": "“Yes,” I lie.",
    "is_heading": False,
    "trans": "“挺好的，”我撒谎道。",
    "vocab": []
  },
  {
    "id": "s-42",
    "elem_idx": 12,
    "tag": "p",
    "text": "“Everything is fine.”",
    "is_heading": False,
    "trans": "“一切都很正常。”",
    "vocab": []
  },
  {
    "id": "s-43",
    "elem_idx": 13,
    "tag": "p",
    "text": "Patrice purses her lips.",
    "is_heading": False,
    "trans": "帕特里斯撇了撇嘴。",
    "vocab": [
      {
        "word": "purse one's lips",
        "pos": "phrase",
        "def": "噘嘴，抿嘴（表示怀疑或不满）"
      }
    ]
  },
  {
    "id": "s-44",
    "elem_idx": 13,
    "tag": "p",
    "text": "“I guess she must’ve just forgotten then.",
    "is_heading": False,
    "trans": "“那我猜她肯定只是忘了吧。",
    "vocab": []
  },
  {
    "id": "s-45",
    "elem_idx": 13,
    "tag": "p",
    "text": "You know Nina can be a bit flaky, I’m sure.”",
    "is_heading": False,
    "trans": "我相信你也知道，妮娜这个人有时候是有点靠不住、丢三落四的。”",
    "vocab": [
      {
        "word": "flaky",
        "pos": "adj",
        "def": "不可靠的，健忘不靠谱的，神经兮兮的"
      }
    ]
  },
  {
    "id": "s-46",
    "elem_idx": 14,
    "tag": "p",
    "text": "Oh, she’s a lot more than that.",
    "is_heading": False,
    "trans": "呵，她何止只是有点不靠谱。",
    "vocab": [
      {
        "word": "a lot more than that",
        "pos": "phrase",
        "def": "远不止于此，何止是那样"
      }
    ]
  },
  {
    "id": "s-47",
    "elem_idx": 14,
    "tag": "p",
    "text": "But I keep my mouth shut.",
    "is_heading": False,
    "trans": "但我紧紧闭上了嘴巴，什么也没说。",
    "vocab": [
      {
        "word": "keep one's mouth shut",
        "pos": "phrase",
        "def": "守口如瓶，闭嘴不言"
      }
    ]
  },
  {
    "id": "s-48",
    "elem_idx": 14,
    "tag": "p",
    "text": "Her eyes fall on the phone in my hand.",
    "is_heading": False,
    "trans": "她的视线落在了我手中的手机上。",
    "vocab": [
      {
        "word": "eyes fall on",
        "pos": "phrase",
        "def": "目光落在……上"
      }
    ]
  },
  {
    "id": "s-49",
    "elem_idx": 15,
    "tag": "p",
    "text": "“Is that the phone Nina gave you to use?”",
    "is_heading": False,
    "trans": "“那是妮娜给你配的手机吗？”",
    "vocab": []
  },
  {
    "id": "s-50",
    "elem_idx": 16,
    "tag": "p",
    "text": "“Uh, yeah.",
    "is_heading": False,
    "trans": "“呃，是的。",
    "vocab": []
  },
  {
    "id": "s-51",
    "elem_idx": 16,
    "tag": "p",
    "text": "It is.”",
    "is_heading": False,
    "trans": "是的。”",
    "vocab": []
  },
  {
    "id": "s-52",
    "elem_idx": 17,
    "tag": "p",
    "text": "She throws her head back and laughs.",
    "is_heading": False,
    "trans": "她仰起头笑了起来。",
    "vocab": [
      {
        "word": "throw one's head back",
        "pos": "phrase",
        "def": "仰头，仰面"
      }
    ]
  },
  {
    "id": "s-53",
    "elem_idx": 17,
    "tag": "p",
    "text": "“I have to say, it’s nice of you to let her keep track of where you are at all times.",
    "is_heading": False,
    "trans": "“我不得不说，你脾气可真好，居然愿意让她时时刻刻追踪你的行踪。",
    "vocab": [
      {
        "word": "keep track of",
        "pos": "phrase",
        "def": "追踪，随时掌握……的动向"
      },
      {
        "word": "at all times",
        "pos": "phrase",
        "def": "随时，无时无刻"
      }
    ]
  },
  {
    "id": "s-54",
    "elem_idx": 17,
    "tag": "p",
    "text": "I don’t know if I would be okay with that if I were you.”",
    "is_heading": False,
    "trans": "要是换做我，我可受不了这种事。”",
    "vocab": [
      {
        "word": "okay with",
        "pos": "phrase",
        "def": "接受，认可"
      }
    ]
  },
  {
    "id": "s-55",
    "elem_idx": 18,
    "tag": "p",
    "text": "I shrug.",
    "is_heading": False,
    "trans": "我耸了耸肩。",
    "vocab": [
      {
        "word": "shrug",
        "pos": "v",
        "def": "耸肩"
      }
    ]
  },
  {
    "id": "s-56",
    "elem_idx": 18,
    "tag": "p",
    "text": "“She mostly just texts me.",
    "is_heading": False,
    "trans": "“她平时主要就是发发短信找我。",
    "vocab": []
  },
  {
    "id": "s-57",
    "elem_idx": 18,
    "tag": "p",
    "text": "It’s not that bad.”",
    "is_heading": False,
    "trans": "没那么夸张。”",
    "vocab": [
      {
        "word": "not that bad",
        "pos": "phrase",
        "def": "没那么严重/糟糕"
      }
    ]
  },
  {
    "id": "s-58",
    "elem_idx": 19,
    "tag": "p",
    "text": "“That’s not what I mean.”",
    "is_heading": False,
    "trans": "“我说的不是这个意思。”",
    "vocab": []
  },
  {
    "id": "s-59",
    "elem_idx": 19,
    "tag": "p",
    "text": "She nods at the phone.",
    "is_heading": False,
    "trans": "她朝我手里的手机点了点下巴。",
    "vocab": [
      {
        "word": "nod at",
        "pos": "phrase",
        "def": "朝……点头示意/使眼色"
      }
    ]
  },
  {
    "id": "s-60",
    "elem_idx": 19,
    "tag": "p",
    "text": "“I’m talking about the tracking app she installed.",
    "is_heading": False,
    "trans": "“我说的是她在手机里装的定位追踪应用。",
    "vocab": [
      {
        "word": "tracking app",
        "pos": "n",
        "def": "定位追踪软件"
      },
      {
        "word": "install",
        "pos": "v",
        "def": "安装（软件/设备）"
      }
    ]
  },
  {
    "id": "s-61",
    "elem_idx": 19,
    "tag": "p",
    "text": "Doesn’t it drive you crazy that she wants to know where you are all the time?”",
    "is_heading": False,
    "trans": "她无时无刻都想监控你在哪儿，这难道不把你逼疯吗？”",
    "vocab": [
      {
        "word": "drive sb crazy",
        "pos": "phrase",
        "def": "把某人逼疯，使极度抓狂"
      }
    ]
  },
  {
    "id": "s-62",
    "elem_idx": 20,
    "tag": "p",
    "text": "I feel like I got sucker-punched in the stomach.",
    "is_heading": False,
    "trans": "我顿觉胃部像是挨了一记猝不及防的闷拳，整个人僵住了。",
    "vocab": [
      {
        "word": "sucker-punch",
        "pos": "v",
        "def": "冷不防给……一记重拳，暗中突袭"
      }
    ]
  },
  {
    "id": "s-63",
    "elem_idx": 21,
    "tag": "p",
    "text": "Nina tracks me on my phone?",
    "is_heading": False,
    "trans": "妮娜用手机定位追踪我？",
    "vocab": [
      {
        "word": "track",
        "pos": "v",
        "def": "追踪，定位监控"
      }
    ]
  },
  {
    "id": "s-64",
    "elem_idx": 22,
    "tag": "p",
    "text": "What the hell?",
    "is_heading": False,
    "trans": "这他妈算怎么回事？",
    "vocab": [
      {
        "word": "what the hell",
        "pos": "phrase",
        "def": "到底怎么回事，搞什么鬼"
      }
    ]
  },
  {
    "id": "s-65",
    "elem_idx": 23,
    "tag": "p",
    "text": "I’m so stupid.",
    "is_heading": False,
    "trans": "我真是太蠢了。",
    "vocab": []
  },
  {
    "id": "s-66",
    "elem_idx": 23,
    "tag": "p",
    "text": "Of course she would do something like that.",
    "is_heading": False,
    "trans": "她当然能做出这种事来。",
    "vocab": []
  },
  {
    "id": "s-67",
    "elem_idx": 23,
    "tag": "p",
    "text": "It makes perfect sense.",
    "is_heading": False,
    "trans": "这下一切都完全说得通了。",
    "vocab": [
      {
        "word": "make perfect sense",
        "pos": "phrase",
        "def": "完全合情合理，完全说得通"
      }
    ]
  },
  {
    "id": "s-68",
    "elem_idx": 23,
    "tag": "p",
    "text": "And now I realize that she didn’t have to go through my purse to find that playbill or call the house the night of the show.",
    "is_heading": False,
    "trans": "现在我才想明白，那天晚上她根本不需要翻我的包找演出节目单，也不用往家里打电话查岗。",
    "vocab": [
      {
        "word": "go through",
        "pos": "phr v",
        "def": "翻找，搜查"
      },
      {
        "word": "playbill",
        "pos": "n",
        "def": "戏单，演出节目单"
      }
    ]
  },
  {
    "id": "s-69",
    "elem_idx": 23,
    "tag": "p",
    "text": "She knew exactly where I was.",
    "is_heading": False,
    "trans": "她清清楚楚地掌握着我所在的每一个位置。",
    "vocab": [
      {
        "word": "exactly where",
        "pos": "phrase",
        "def": "确切知道……在哪里"
      }
    ]
  },
  {
    "id": "s-70",
    "elem_idx": 24,
    "tag": "p",
    "text": "“Oh!”",
    "is_heading": False,
    "trans": "“哎呀！”",
    "vocab": []
  },
  {
    "id": "s-71",
    "elem_idx": 24,
    "tag": "p",
    "text": "Patrice clasps a hand over her mouth.",
    "is_heading": False,
    "trans": "帕特里斯一把捂住嘴巴。",
    "vocab": [
      {
        "word": "clasp a hand over",
        "pos": "phrase",
        "def": "用手捂住（嘴巴等）"
      }
    ]
  },
  {
    "id": "s-72",
    "elem_idx": 24,
    "tag": "p",
    "text": "“I’m so sorry.",
    "is_heading": False,
    "trans": "“真对不起。",
    "vocab": []
  },
  {
    "id": "s-73",
    "elem_idx": 24,
    "tag": "p",
    "text": "Did you not realize…?”",
    "is_heading": False,
    "trans": "你难道一直都不知道……？”",
    "vocab": []
  },
  {
    "id": "s-74",
    "elem_idx": 25,
    "tag": "p",
    "text": "I want to slap her across her Botoxed face.",
    "is_heading": False,
    "trans": "我真想狠狠扇她那张打了肉毒杆菌的僵硬脸蛋一记耳光。",
    "vocab": [
      {
        "word": "slap sb across the face",
        "pos": "phrase",
        "def": "扇某人耳光"
      },
      {
        "word": "Botoxed",
        "pos": "adj",
        "def": "注射了肉毒素的，除皱僵硬的"
      }
    ]
  },
  {
    "id": "s-75",
    "elem_idx": 25,
    "tag": "p",
    "text": "I’m not sure whether she knew that I knew about it or not, but she looks like she’s taking great pleasure in being the one to tell me.",
    "is_heading": False,
    "trans": "我拿不准她到底是不是知晓我被蒙在鼓里，但她此刻的神情分明写满了充当爆料者的幸灾乐祸与快感。",
    "vocab": [
      {
        "word": "take great pleasure in",
        "pos": "phrase",
        "def": "在……中获得极大乐趣/快感，幸灾乐祸"
      }
    ]
  },
  {
    "id": "s-76",
    "elem_idx": 26,
    "tag": "p",
    "text": "A cold sweat breaks out in the back of my neck.",
    "is_heading": False,
    "trans": "一层冷汗瞬间从我的后颈渗了出来。",
    "vocab": [
      {
        "word": "cold sweat breaks out",
        "pos": "phrase",
        "def": "冒出一身冷汗"
      }
    ]
  },
  {
    "id": "s-77",
    "elem_idx": 27,
    "tag": "p",
    "text": "“Excuse me,” I say to Patrice.",
    "is_heading": False,
    "trans": "“失陪了，”我冷冷地对帕特里斯说。",
    "vocab": [
      {
        "word": "excuse me",
        "pos": "phrase",
        "def": "失陪，借过"
      }
    ]
  },
  {
    "id": "s-78",
    "elem_idx": 27,
    "tag": "p",
    "text": "I push past her, leaving my grocery cart behind.",
    "is_heading": False,
    "trans": "我径直从她身旁挤了过去，把装满东西的购物车直接扔在原地。",
    "vocab": [
      {
        "word": "push past",
        "pos": "phr v",
        "def": "挤过，硬推开……走过去"
      },
      {
        "word": "leave behind",
        "pos": "phr v",
        "def": "把……抛在脑后/扔在原地"
      }
    ]
  },
  {
    "id": "s-79",
    "elem_idx": 28,
    "tag": "p",
    "text": "I race out into the parking lot and I can only breathe again when I’m out of the store.",
    "is_heading": False,
    "trans": "我一路冲出超市跑进停车场，直到离开那家店，我才觉得自己能够重新呼吸。",
    "vocab": [
      {
        "word": "race out",
        "pos": "phr v",
        "def": "飞奔而出，疾速冲出"
      }
    ]
  },
  {
    "id": "s-80",
    "elem_idx": 28,
    "tag": "p",
    "text": "I put my hands on my knees and lean forward until my breathing returns to normal.",
    "is_heading": False,
    "trans": "我双手撑在膝盖上，身子前倾大口喘息，直到呼吸逐渐平复下来。",
    "vocab": [
      {
        "word": "hands on knees",
        "pos": "phrase",
        "def": "双手按在膝盖上（弯腰喘息姿态）"
      },
      {
        "word": "return to normal",
        "pos": "phrase",
        "def": "恢复正常"
      }
    ]
  },
  {
    "id": "s-81",
    "elem_idx": 29,
    "tag": "p",
    "text": "When I straighten up again, a car is making a quick exit from the parking lot.",
    "is_heading": False,
    "trans": "当我重新直起身子时，一辆车正飞快地驶离停车场。",
    "vocab": [
      {
        "word": "straighten up",
        "pos": "phr v",
        "def": "直起身子，挺直身体"
      },
      {
        "word": "make a quick exit",
        "pos": "phrase",
        "def": "迅速离开，仓促离去"
      }
    ]
  },
  {
    "id": "s-82",
    "elem_idx": 29,
    "tag": "p",
    "text": "I recognize the white Lexus.",
    "is_heading": False,
    "trans": "我认出了那辆白色雷克萨斯。",
    "vocab": [
      {
        "word": "recognize",
        "pos": "v",
        "def": "认出，识别出"
      }
    ]
  },
  {
    "id": "s-83",
    "elem_idx": 29,
    "tag": "p",
    "text": "It looks like Nina’s car.",
    "is_heading": False,
    "trans": "看着极像妮娜的车。",
    "vocab": []
  },
  {
    "id": "s-84",
    "elem_idx": 30,
    "tag": "p",
    "text": "And then my phone starts to ring again.",
    "is_heading": False,
    "trans": "紧接着，我的手机又开始疯狂响铃了。",
    "vocab": []
  },
  {
    "id": "s-85",
    "elem_idx": 30,
    "tag": "p",
    "text": "I rip it out of my purse.",
    "is_heading": False,
    "trans": "我一把将手机从包里扯了出来。",
    "vocab": [
      {
        "word": "rip out",
        "pos": "phr v",
        "def": "一把拽出，猛力扯出"
      }
    ]
  },
  {
    "id": "s-86",
    "elem_idx": 30,
    "tag": "p",
    "text": "Again, it says blocked number.",
    "is_heading": False,
    "trans": "屏幕上依然显示着隐藏号码。",
    "vocab": []
  },
  {
    "id": "s-87",
    "elem_idx": 31,
    "tag": "p",
    "text": "Fine, if she wants to talk to me, she can go ahead and say what she wants to say.",
    "is_heading": False,
    "trans": "行啊，既然她想找我谈，那就让她尽管说个痛快好了。",
    "vocab": [
      {
        "word": "go ahead and",
        "pos": "phrase",
        "def": "尽管……，放手去做"
      }
    ]
  },
  {
    "id": "s-88",
    "elem_idx": 31,
    "tag": "p",
    "text": "If she wants to threaten me and call me a homewrecker, let her do it.",
    "is_heading": False,
    "trans": "要是她想威胁我、骂我是破坏别人家庭的小三，那就随她骂去吧。",
    "vocab": [
      {
        "word": "homewrecker",
        "pos": "n",
        "def": "第三者，破坏他人家庭者"
      },
      {
        "word": "threaten",
        "pos": "v",
        "def": "威胁，恐吓"
      }
    ]
  },
  {
    "id": "s-89",
    "elem_idx": 31,
    "tag": "p",
    "text": "I jab at the green button.",
    "is_heading": False,
    "trans": "我狠狠戳向绿色的接听键。",
    "vocab": [
      {
        "word": "jab at",
        "pos": "phr v",
        "def": "用力戳，猛按"
      }
    ]
  },
  {
    "id": "s-90",
    "elem_idx": 32,
    "tag": "p",
    "text": "“Hello?",
    "is_heading": False,
    "trans": "“喂？",
    "vocab": []
  },
  {
    "id": "s-91",
    "elem_idx": 32,
    "tag": "p",
    "text": "Nina?”",
    "is_heading": False,
    "trans": "妮娜吗？”",
    "vocab": []
  },
  {
    "id": "s-92",
    "elem_idx": 33,
    "tag": "p",
    "text": "“Hello!” a cheerful voice says.",
    "is_heading": False,
    "trans": "“您好！”一个欢快热情的声音传来。",
    "vocab": [
      {
        "word": "cheerful",
        "pos": "adj",
        "def": "欢快的，兴高采烈的"
      }
    ]
  },
  {
    "id": "s-93",
    "elem_idx": 33,
    "tag": "p",
    "text": "“It’s come to our attention that your vehicle warranty may have recently expired!”",
    "is_heading": False,
    "trans": "“我们注意到您的车辆保修期可能最近已经过期了！”",
    "vocab": [
      {
        "word": "come to one's attention",
        "pos": "phrase",
        "def": "获悉，注意到（官方/客服常见套话）"
      },
      {
        "word": "vehicle warranty",
        "pos": "n",
        "def": "车辆保修，车险延保"
      },
      {
        "word": "expire",
        "pos": "v",
        "def": "到期，失效"
      }
    ]
  },
  {
    "id": "s-94",
    "elem_idx": 34,
    "tag": "p",
    "text": "I pull the phone away from my ear and stare at it in disbelief.",
    "is_heading": False,
    "trans": "我把手机从耳边拿开，难以置信地瞪着屏幕。",
    "vocab": [
      {
        "word": "in disbelief",
        "pos": "phrase",
        "def": "难以置信地，怀疑地"
      }
    ]
  },
  {
    "id": "s-95",
    "elem_idx": 34,
    "tag": "p",
    "text": "It wasn’t Nina after all.",
    "is_heading": False,
    "trans": "原来根本就不是妮娜。",
    "vocab": [
      {
        "word": "after all",
        "pos": "phrase",
        "def": "终究，原来（与预期相反）"
      }
    ]
  },
  {
    "id": "s-96",
    "elem_idx": 34,
    "tag": "p",
    "text": "It was a stupid spam caller.",
    "is_heading": False,
    "trans": "就是个该死的垃圾推销电话。",
    "vocab": [
      {
        "word": "spam caller",
        "pos": "n",
        "def": "骚扰电话，垃圾推销来电"
      }
    ]
  },
  {
    "id": "s-97",
    "elem_idx": 34,
    "tag": "p",
    "text": "I just completely overreacted to the entire thing.",
    "is_heading": False,
    "trans": "我刚才完全是对整件事草木皆兵、反应过度了。",
    "vocab": [
      {
        "word": "overreact to",
        "pos": "phr v",
        "def": "对……反应过度，大惊小怪"
      }
    ]
  },
  {
    "id": "s-98",
    "elem_idx": 34,
    "tag": "p",
    "text": "But I still can’t push away the feeling that I’m in danger.",
    "is_heading": False,
    "trans": "然而，那种深陷险境的危机感依然盘踞在心头，挥之不去。",
    "vocab": [
      {
        "word": "push away",
        "pos": "phr v",
        "def": "驱散，摒弃，排遣（情绪）"
      },
      {
        "word": "in danger",
        "pos": "phrase",
        "def": "处于危险之中，身陷险境"
      }
    ]
  }
]

out_path = "/Users/lindy/Vault/audiobook/The Housemaid/the_housemaid_ch35_full_analysis.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(ch35_analysis, f, indent=2, ensure_ascii=False)

print(f"Successfully generated {out_path} with {len(ch35_analysis)} sentences.")
