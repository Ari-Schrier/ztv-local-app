def emoji(name):
    return {
        "calendar": "\U0001F4C5",       # 📅
        "brain": "\U0001F9E0",          # 🧠
        "cross_mark": "\u274C",         # ❌
        "check": "\u2705",              # ✅
        "inbox": "\U0001F4E5",          # 📥
        "frame": "\U0001F5BC",          # 🖼️
        "rocket": "\U0001F680",         # 🚀
        "tada": "\U0001F389",           # 🎉
        "broom": "\U0001F9F9",          # 🧹
        "hammer": "\U0001F528",           # 🔨
    }.get(name, "")