"""Write 404.html, offline.html and errors/*.html from one template."""
import html, sys
OUT = sys.argv[1]

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title} · dunne.systems</title>
<meta name="robots" content="noindex">
<meta name="theme-color" content="#008080">
<link rel="icon" href="/assets/images/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/images/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/images/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/css/error-screen.css">
</head>
<body data-loop="/assets/images/dialing-{name}-loop.gif" data-once="{once}">
<main class="desk">
  <h1 class="sr">{h1}</h1>
  <picture>
    <source media="(prefers-reduced-motion: reduce)" srcset="/assets/images/dialing-{name}-end.png">
    <img id="dialog" src="/assets/images/dialing-{name}.gif" width="640" height="460"
      alt="{alt}">
  </picture>
</main>

<nav class="taskbar" aria-label="Taskbar">
  <a class="btn home" href="/"><img src="/assets/images/favicon.svg" alt="">Home</a>
  <span class="btn task down" title="{tip}"><img src="/assets/images/favicon-32.png" alt=""><span id="task">{task}</span></span>
{extra}  <span class="tray" aria-hidden="true" id="clock"></span>
</nav>

<script src="/assets/js/error-screen.js"></script>
{script}</body>
</html>
"""

# name, file, title, h1, task, once-ms, alt
JOKES = [
    ("403", "403 Forbidden", "403: you don't have access to rack A01",
     "A Dialing Progress window. The PC reaches for the server rack, but a padlocked cage drops around it and the orange cat paws at the bars. The PC screen says 403 ACCESS DENIED and the status reads 'Error 403: you don't have access to rack A01.'", 3000),
    ("500", "500 Internal Server Error", "500: Dunne.systems is on fire",
     "A Dialing Progress window. The server rack overheats and catches fire, smoke rolls out, the fiber burns through and the PC screen reads 500 NO CARRIER while the cat chases the mouse across the floor. The status reads 'Error 500: Dunne.systems is on fire.'", 2880),
    ("503", "503 Service Unavailable", "503: rack A01 is down for maintenance",
     "A Dialing Progress window. The rack's lights go dark, a yellow MAINTENANCE sign is hung across it, and the orange cat naps on top of the monitor, whose screen says BRB, BACK SOON. The status reads 'Error 503: rack A01 is down for maintenance.'", 2800),
    ("418", "418 I'm a teapot", "418: I'm a teapot",
     "A Dialing Progress window. The server rack has been replaced by a big steaming teapot, the PC tries to BREW COFFEE and gives up with 418 I'M A TEAPOT, and the orange cat sits by the pot. The status reads 'Error 418: I'm a teapot. I can't brew coffee.'", 2600),
]

def page(path, **kw):
    kw = {k: (html.escape(v, quote=False).replace('"', "&quot;") if k in ("title", "h1", "alt", "task", "tip") else v) for k, v in kw.items()}
    kw.setdefault("tip", kw["task"]); kw.setdefault("extra", ""); kw.setdefault("script", "")
    open(f"{OUT}/{path}", "w").write(PAGE.format(**kw))

page("404.html", name="404", once=3600, title="404 Not Found", h1="404: that page doesn't exist", task="Not found",
     alt="A Dialing Progress window. The PC searches the server rack unit by unit for the page, panics with a question mark, and gives up: the screen says 404 Not Found and the status reads 'Error 404: that page doesn't exist.'",
     script="""<script>
// Name the missing page in the task button (as text, never as HTML)
(function(){var p=location.pathname;if(p&&p!=="/404.html"){var t=document.getElementById("task");t.textContent="Not found: "+p;t.parentNode.title="Not found: "+p}})();
</script>
""")

# The service worker serves this one in place of any page that can't load
page("offline.html", name="offline", once=3200, title="Offline", h1="You're offline", task="No dial tone",
     alt="A Dialing Progress window. The PC dials three times with no answer, then gives up: the fiber has been chewed in half, and the orange cat sits next to the gap looking innocent. The screen says NO DIALTONE and the status reads 'Error: no dial tone. Check your connection.'",
     extra='  <button class="btn next" id="retry" type="button">Redial</button>\n',
     script="""<script>
// Redial by hand, or on its own once the connection comes back
document.getElementById("retry").onclick=function(){location.reload()};
addEventListener("online",function(){location.reload()});
</script>
""")

for i, (name, title, h1, alt, once) in enumerate(JOKES):
    nxt = JOKES[(i + 1) % len(JOKES)][0]
    page(f"errors/{name}.html", name=name, once=once, title=title, h1=h1, alt=alt,
         task=f"{title} (demo)", tip="Just a demo. The real site is fine.",
         extra=f'  <a class="btn next" href="/errors/{nxt}.html" title="Next error screen">Next ›</a>\n')
