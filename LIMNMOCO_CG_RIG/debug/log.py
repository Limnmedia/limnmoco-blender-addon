DEBUG_ENABLED = True
DEBUG_SOLVER = True
DEBUG_SCENE = True
DEBUG_UI = True
DEBUG_VERSION = "v02a-debug-pass"

def log(*args):
    if DEBUG_ENABLED:
        print("[LIMNMOCO]", *args)

def section(title):
    if DEBUG_ENABLED:
        print("")
        print("[LIMNMOCO] ==================================================")
        print(f"[LIMNMOCO] {title}")
        print("[LIMNMOCO] ==================================================")

def solver(*args):
    if DEBUG_ENABLED and DEBUG_SOLVER:
        print("[LIMNMOCO][SOLVER]", *args)

def scene(*args):
    if DEBUG_ENABLED and DEBUG_SCENE:
        print("[LIMNMOCO][SCENE]", *args)

def warning(*args):
    if DEBUG_ENABLED:
        print("[LIMNMOCO][WARNING]", *args)
