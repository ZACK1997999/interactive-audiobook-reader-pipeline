import json

ch37_analysis = [
  {
    "id": "s-0",
    "elem_idx": 0,
    "tag": "h1",
    "text": "THIRTY-SEVEN",
    "is_heading": True,
    "trans": "第三十七章",
    "vocab": []
  },
  {
    "id": "s-1",
    "elem_idx": 1,
    "tag": "p",
    "text": "Despite how incredibly uncomfortable my cot is compared with the incredible mattress in the guestroom, I pass out soon after Andrew and I make love up there, wrapped tightly in his arms.",
    "is_heading": False,
    "trans": "尽管与客房那张棒极了的床垫相比，我这间小折叠床难受得要命，但和安德鲁在上头温存之后，我很快就在他紧紧的臂弯中昏睡了过去。",
    "vocab": [
      {
        "word": "pass out",
        "pos": "phr v",
        "def": "昏睡过去，失去意识"
      },
      {
        "word": "make love",
        "pos": "phrase",
        "def": "做爱，温存亲热"
      },
      {
        "word": "cot",
        "pos": "n",
        "def": "简易小床，折叠床"
      }
    ]
  },
  {
    "id": "s-2",
    "elem_idx": 1,
    "tag": "p",
    "text": "I never thought I would be having sex in this room.",
    "is_heading": False,
    "trans": "我从没想过自己会在这间屋子里做爱。",
    "vocab": []
  },
  {
    "id": "s-3",
    "elem_idx": 1,
    "tag": "p",
    "text": "Especially since Nina was so strict about letting me have any guests over.",
    "is_heading": False,
    "trans": "尤其是妮娜曾经对我带任何客人来过夜都有着极其严苛的限制。",
    "vocab": [
      {
        "word": "have sb over",
        "pos": "phr v",
        "def": "邀请某人来家里（做客或过夜）"
      },
      {
        "word": "strict about",
        "pos": "adj",
        "def": "对……要求严厉/严苛"
      }
    ]
  },
  {
    "id": "s-4",
    "elem_idx": 2,
    "tag": "p",
    "text": "That rule certainly didn’t work out too well for her.",
    "is_heading": False,
    "trans": "不过那条规矩显然没给她带来什么好结果。",
    "vocab": [
      {
        "word": "work out",
        "pos": "phr v",
        "def": "产生结果，起作用，有好的结局"
      }
    ]
  },
  {
    "id": "s-5",
    "elem_idx": 3,
    "tag": "p",
    "text": "I wake up again at around three in the morning.",
    "is_heading": False,
    "trans": "凌晨三点左右，我再次醒了过来。",
    "vocab": []
  },
  {
    "id": "s-6",
    "elem_idx": 3,
    "tag": "p",
    "text": "The first sensation I become aware of is my bladder—full and slightly uncomfortable.",
    "is_heading": False,
    "trans": "我最先察觉到的感觉是我的膀胱——胀得满满的，隐隐有些不适。",
    "vocab": [
      {
        "word": "sensation",
        "pos": "n",
        "def": "身体知觉，感官感受"
      },
      {
        "word": "bladder",
        "pos": "n",
        "def": "膀胱"
      }
    ]
  },
  {
    "id": "s-7",
    "elem_idx": 3,
    "tag": "p",
    "text": "I’ve got to hit the bathroom.",
    "is_heading": False,
    "trans": "我得去一趟洗手间了。",
    "vocab": [
      {
        "word": "hit the bathroom",
        "pos": "phrase",
        "def": "去洗手间/上厕所"
      }
    ]
  },
  {
    "id": "s-8",
    "elem_idx": 3,
    "tag": "p",
    "text": "Usually, I go right before bed, but Andrew wore me out and I fell asleep before I could muster up the energy.",
    "is_heading": False,
    "trans": "平时我总会在睡前去一趟，但安德鲁把我折腾得筋疲力尽，我还没来得及提上劲就睡过去了。",
    "vocab": [
      {
        "word": "wear sb out",
        "pos": "phr v",
        "def": "使某人筋疲力尽/精疲力竭"
      },
      {
        "word": "muster up",
        "pos": "phr v",
        "def": "鼓起，攒出（力气、勇气等）"
      }
    ]
  },
  {
    "id": "s-9",
    "elem_idx": 4,
    "tag": "p",
    "text": "And that’s the other sensation I become aware of.",
    "is_heading": False,
    "trans": "紧接着，我察觉到了另一种异样的感觉。",
    "vocab": []
  },
  {
    "id": "s-10",
    "elem_idx": 4,
    "tag": "p",
    "text": "A sense of emptiness.",
    "is_heading": False,
    "trans": "一种空落落的感觉。",
    "vocab": [
      {
        "word": "sense of emptiness",
        "pos": "phrase",
        "def": "空虚感，空荡荡的感觉"
      }
    ]
  },
  {
    "id": "s-11",
    "elem_idx": 4,
    "tag": "p",
    "text": "Andrew isn’t in the cot anymore.",
    "is_heading": False,
    "trans": "安德鲁已经不在小床上了。",
    "vocab": []
  },
  {
    "id": "s-12",
    "elem_idx": 5,
    "tag": "p",
    "text": "I suspect after I fell asleep, he decided to relocate to his own bed.",
    "is_heading": False,
    "trans": "我猜是我睡着之后，他决定移步回他自己的床上去睡了。",
    "vocab": [
      {
        "word": "relocate",
        "pos": "v",
        "def": "转移，换地方，搬迁"
      }
    ]
  },
  {
    "id": "s-13",
    "elem_idx": 5,
    "tag": "p",
    "text": "I can’t blame him.",
    "is_heading": False,
    "trans": "这也怪不得他。",
    "vocab": [
      {
        "word": "can't blame sb",
        "pos": "phrase",
        "def": "不能怪某人，完全情有可原"
      }
    ]
  },
  {
    "id": "s-14",
    "elem_idx": 5,
    "tag": "p",
    "text": "This cot is hardly comfortable for one person, much less two, and the room is so claustrophobic.",
    "is_heading": False,
    "trans": "这张简易床一个人睡都谈不上舒服，更别提两个人了，而且这屋子还狭小得令人窒息。",
    "vocab": [
      {
        "word": "much less",
        "pos": "phrase",
        "def": "更不用说，何况"
      },
      {
        "word": "claustrophobic",
        "pos": "adj",
        "def": "引起幽闭恐惧的，狭窄压抑的"
      }
    ]
  },
  {
    "id": "s-15",
    "elem_idx": 5,
    "tag": "p",
    "text": "Maybe he tried to tough it out, but after tossing and turning, he migrated downstairs.",
    "is_heading": False,
    "trans": "也许他曾试着硬撑，但翻来覆去实在难受，便转移到了楼下。",
    "vocab": [
      {
        "word": "tough it out",
        "pos": "phrase",
        "def": "硬撑过去，咬牙熬过去"
      },
      {
        "word": "toss and turn",
        "pos": "phrase",
        "def": "辗转反侧，翻来覆去睡不着"
      },
      {
        "word": "migrate",
        "pos": "v",
        "def": "迁移，移步（生动/拟人用法）"
      }
    ]
  },
  {
    "id": "s-16",
    "elem_idx": 5,
    "tag": "p",
    "text": "Andrew is more than ten years older than me, and my back can barely make it through the night with this mattress, so I can hardly blame him.",
    "is_heading": False,
    "trans": "安德鲁比我大了十多岁，连我的腰睡在这张床垫上都很难熬过一整夜，所以我真的丝毫不怪他。",
    "vocab": [
      {
        "word": "make it through",
        "pos": "phr v",
        "def": "顺利熬过，度过（困难境况）"
      }
    ]
  },
  {
    "id": "s-17",
    "elem_idx": 6,
    "tag": "p",
    "text": "I’m so glad this is the last night I’ll be sleeping here.",
    "is_heading": False,
    "trans": "我真庆幸这是我在这里睡的最后一晚了。",
    "vocab": []
  },
  {
    "id": "s-18",
    "elem_idx": 6,
    "tag": "p",
    "text": "Maybe after I use the bathroom, I’ll go join Andrew downstairs.",
    "is_heading": False,
    "trans": "也许等我去完洗手间，就可以下楼去陪安德鲁了。",
    "vocab": []
  },
  {
    "id": "s-19",
    "elem_idx": 7,
    "tag": "p",
    "text": "I rise to my feet, the floorboards groaning under my weight.",
    "is_heading": False,
    "trans": "我站起身来，地板在我的体重下发出吱嘎的呻吟声。",
    "vocab": [
      {
        "word": "rise to one's feet",
        "pos": "phrase",
        "def": "站起身来"
      },
      {
        "word": "floorboard",
        "pos": "n",
        "def": "地板，木地板条"
      },
      {
        "word": "groan",
        "pos": "v",
        "def": "（木板等受重压）发出吱嘎呻吟声"
      }
    ]
  },
  {
    "id": "s-20",
    "elem_idx": 7,
    "tag": "p",
    "text": "I make my way to the door and turn the doorknob.",
    "is_heading": False,
    "trans": "我走向房门，转动门把手。",
    "vocab": [
      {
        "word": "make one's way to",
        "pos": "phrase",
        "def": "前往，走向"
      },
      {
        "word": "doorknob",
        "pos": "n",
        "def": "球形门把手"
      }
    ]
  },
  {
    "id": "s-21",
    "elem_idx": 7,
    "tag": "p",
    "text": "As usual, it sticks.",
    "is_heading": False,
    "trans": "和平常一样，把手卡住了。",
    "vocab": [
      {
        "word": "stick",
        "pos": "v",
        "def": "卡住，卡滞，转不动"
      }
    ]
  },
  {
    "id": "s-22",
    "elem_idx": 7,
    "tag": "p",
    "text": "So I turn it more firmly.",
    "is_heading": False,
    "trans": "于是我加大力道又拧了一下。",
    "vocab": [
      {
        "word": "firmly",
        "pos": "adv",
        "def": "用力地，坚决地"
      }
    ]
  },
  {
    "id": "s-23",
    "elem_idx": 8,
    "tag": "p",
    "text": "It still doesn’t turn.",
    "is_heading": False,
    "trans": "它还是转不动。",
    "vocab": []
  },
  {
    "id": "s-24",
    "elem_idx": 9,
    "tag": "p",
    "text": "Panic mounts in my chest.",
    "is_heading": False,
    "trans": "一股恐慌在我胸口不断升腾蔓延。",
    "vocab": [
      {
        "word": "mount",
        "pos": "v",
        "def": "（情绪、压力等）逐渐加剧，升腾"
      }
    ]
  },
  {
    "id": "s-25",
    "elem_idx": 9,
    "tag": "p",
    "text": "I press myself against the door, the scratch marks in the wood splintering into my shoulder, and place my right hand squarely on the knob.",
    "is_heading": False,
    "trans": "我整个人紧贴在门上，木板上残留的抓痕木刺扎入我的肩膀，我将右手结结实实地扣在门把手上。",
    "vocab": [
      {
        "word": "splinter into",
        "pos": "v",
        "def": "刺入，扎进（如碎木刺等）"
      },
      {
        "word": "squarely",
        "pos": "adv",
        "def": "端正地，结结实实地"
      }
    ]
  },
  {
    "id": "s-26",
    "elem_idx": 9,
    "tag": "p",
    "text": "I try once again to turn it clockwise.",
    "is_heading": False,
    "trans": "我再次试着顺时针去拧它。",
    "vocab": [
      {
        "word": "clockwise",
        "pos": "adv",
        "def": "按顺时针方向"
      }
    ]
  },
  {
    "id": "s-27",
    "elem_idx": 9,
    "tag": "p",
    "text": "But it doesn’t budge.",
    "is_heading": False,
    "trans": "但它纹丝未动。",
    "vocab": [
      {
        "word": "budge",
        "pos": "v",
        "def": "微微移动，产生丝毫松动"
      }
    ]
  },
  {
    "id": "s-28",
    "elem_idx": 9,
    "tag": "p",
    "text": "Not even a millimeter.",
    "is_heading": False,
    "trans": "甚至连一毫米都没动弹。",
    "vocab": []
  },
  {
    "id": "s-29",
    "elem_idx": 9,
    "tag": "p",
    "text": "And that’s when I realize what’s going on.",
    "is_heading": False,
    "trans": "就在那一瞬间，我猛然意识到了到底是怎么回事。",
    "vocab": [
      {
        "word": "what's going on",
        "pos": "phrase",
        "def": "正在发生什么，背后的真相"
      }
    ]
  },
  {
    "id": "s-30",
    "elem_idx": 10,
    "tag": "p",
    "text": "The door isn’t stuck.",
    "is_heading": False,
    "trans": "门并不是卡住了。",
    "vocab": [
      {
        "word": "stuck",
        "pos": "adj",
        "def": "卡住的，动不了的"
      }
    ]
  },
  {
    "id": "s-31",
    "elem_idx": 11,
    "tag": "p",
    "text": "It’s locked.",
    "is_heading": False,
    "trans": "它被反锁了。",
    "vocab": [
      {
        "word": "locked",
        "pos": "adj",
        "def": "上锁的，被反锁的"
      }
    ]
  }
]

out_path = "/Users/lindy/Vault/audiobook/The Housemaid/the_housemaid_ch37_full_analysis.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(ch37_analysis, f, indent=2, ensure_ascii=False)

print(f"Successfully generated {out_path} with {len(ch37_analysis)} sentences.")
