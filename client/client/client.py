"""Frutiger Aero + glass chat client.  Setup:  pip install pywebview
Works with the existing server.py unchanged."""
import socket, threading, json
import webview

DEFAULT_HOST = "sxfjnapzke.localto.net"   # change to your tunnel host for remote use
DEFAULT_PORT = "2119"        # change to your tunnel port for remote use

HTML = r"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box;margin:0}
html,body{height:100%;font-family:"Segoe UI","Trebuchet MS",sans-serif;color:#0b3550;overflow:hidden}
body{background:
 radial-gradient(circle at 15% 20%,rgba(255,255,255,.8) 0,rgba(255,255,255,0) 18%),
 radial-gradient(circle at 85% 30%,rgba(255,255,255,.55) 0,rgba(255,255,255,0) 14%),
 radial-gradient(ellipse 120% 40% at 50% 108%,#5fd35f 0,#8fe07a 45%,rgba(143,224,122,0) 70%),
 linear-gradient(180deg,#2aa7ee 0%,#7fd6ff 50%,#d6f5ff 82%)}
.bubble{position:fixed;border-radius:50%;background:radial-gradient(circle at 30% 28%,#fff 0,rgba(255,255,255,.35) 22%,rgba(160,230,255,.18) 60%,rgba(255,255,255,.45) 100%);border:1px solid rgba(255,255,255,.7);pointer-events:none;animation:f 9s ease-in-out infinite}
@keyframes f{50%{transform:translateY(-18px)}}
.screen{position:absolute;inset:0;display:none;padding:22px;flex-direction:column}
.screen.on{display:flex}
.glass{background:linear-gradient(160deg,rgba(255,255,255,.5),rgba(255,255,255,.18));backdrop-filter:blur(18px) saturate(170%);-webkit-backdrop-filter:blur(18px) saturate(170%);border:1px solid rgba(255,255,255,.75);border-radius:24px;box-shadow:0 10px 34px rgba(0,90,150,.28),inset 0 1px 0 #fff,inset 0 -1px 0 rgba(255,255,255,.35)}
#login{justify-content:center}
.card{padding:30px 28px}
h1{font-size:28px;font-weight:600;text-shadow:0 1px 0 #fff,0 2px 8px rgba(255,255,255,.7)}
.sub{font-size:13px;opacity:.7;margin:2px 0 18px}
label{font-size:11px;font-weight:600;opacity:.75;margin-left:6px}
input{width:100%;padding:11px 16px;margin:3px 0 12px;border-radius:999px;border:1px solid rgba(255,255,255,.9);background:rgba(255,255,255,.6);font:inherit;color:#0b3550;outline:0;box-shadow:inset 0 2px 5px rgba(0,80,130,.18)}
input:focus{background:rgba(255,255,255,.85);box-shadow:inset 0 2px 5px rgba(0,80,130,.18),0 0 0 3px rgba(60,180,255,.5)}
.row{display:flex;gap:10px}.row>*:first-child{flex:1}.row>*:last-child{width:90px}
.btn{position:relative;overflow:hidden;border:1px solid rgba(0,90,150,.55);border-radius:999px;padding:11px 20px;font:600 14px inherit;font-family:inherit;color:#fff;cursor:pointer;text-shadow:0 1px 2px rgba(0,60,110,.6);background:linear-gradient(180deg,#5fd0ff,#1a8fe0 55%,#35b2f5);box-shadow:0 4px 10px rgba(0,110,190,.4),inset 0 -3px 6px rgba(255,255,255,.35)}
.btn:before{content:"";position:absolute;left:6%;right:6%;top:2px;height:48%;border-radius:999px;background:linear-gradient(180deg,rgba(255,255,255,.85),rgba(255,255,255,.15))}
.btn:hover{filter:brightness(1.08)}.btn:active{transform:translateY(1px)}
.btn.green{border-color:rgba(20,110,30,.55);background:linear-gradient(180deg,#9df07a,#3fb93f 55%,#66d654);box-shadow:0 4px 10px rgba(30,140,40,.4),inset 0 -3px 6px rgba(255,255,255,.35);text-shadow:0 1px 2px rgba(0,80,20,.6)}
.btn.sm{padding:7px 16px;font-size:12px}
.btns{display:flex;gap:10px}.btns .btn{flex:1}
#err{min-height:18px;font-size:12px;color:#c0182b;margin:0 6px 8px;font-weight:600}
.chk{font-size:12px;margin:-4px 0 8px 6px;opacity:.8}.chk input{width:auto;margin:0 6px 0 0;box-shadow:none}
#chat{gap:12px}
.head{display:flex;align-items:center;gap:10px;padding:12px 16px}
.head b{font-size:16px;flex:1}.dot{width:10px;height:10px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#eaffd8,#3fd13f);box-shadow:0 0 8px #5f5}
#log{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px}
#log::-webkit-scrollbar{width:8px}#log::-webkit-scrollbar-thumb{background:rgba(255,255,255,.7);border-radius:8px}
.msg{max-width:78%;padding:9px 14px;border-radius:18px;font-size:14px;line-height:1.35;word-wrap:break-word;box-shadow:0 3px 8px rgba(0,90,150,.18)}
.msg small{display:block;font-size:10px;font-weight:700;opacity:.65;margin-bottom:2px}
.msg.them{align-self:flex-start;background:linear-gradient(180deg,rgba(255,255,255,.95),rgba(225,247,255,.8));border:1px solid #fff;border-bottom-left-radius:6px}
.msg.me{align-self:flex-end;color:#fff;text-shadow:0 1px 2px rgba(0,60,110,.5);background:linear-gradient(180deg,#5fd0ff,#1a8fe0);border:1px solid rgba(0,90,150,.4);border-bottom-right-radius:6px}
.sys{align-self:center;font-size:11px;font-weight:600;padding:4px 14px;border-radius:999px;background:rgba(255,255,255,.55);border:1px solid #fff}
.sys.bad{color:#c0182b;background:rgba(255,230,230,.8)}
.bar{display:flex;gap:10px;padding:10px 12px;align-items:center}.bar input{margin:0}
</style></head><body>
<div class="bubble" style="width:90px;height:90px;left:8%;top:62%"></div>
<div class="bubble" style="width:46px;height:46px;right:10%;top:14%;animation-delay:2s"></div>
<div class="bubble" style="width:120px;height:120px;right:-30px;top:66%;animation-delay:4s"></div>

<div id="login" class="screen on"><div class="glass card">
 <h1>Secure Chat</h1><div class="sub">Sign in or create an account to join the room</div>
 <div class="row"><div><label>Server</label><input id="host"></div><div><label>Port</label><input id="port"></div></div>
 <label>Username</label><input id="user" autocomplete="off">
 <label>Password</label><input id="pass" type="password">
 <div class="chk"><label><input type="checkbox" id="show">Show password</label></div>
 <div id="err"></div>
 <div class="btns"><button class="btn" id="bl">Log in</button><button class="btn green" id="br">Register</button></div>
</div></div>

<div id="chat" class="screen">
 <div class="glass head"><span class="dot"></span><b># general</b><span id="who" style="font-size:12px;opacity:.7"></span><button class="btn sm" id="leave">Leave</button></div>
 <div class="glass" id="log"></div>
 <div class="glass bar"><input id="msg" placeholder="Type a message…" autocomplete="off"><button class="btn" id="send">Send</button></div>
</div>

<script>
const $=id=>document.getElementById(id);let me="";
$("host").value=%HOST%;$("port").value=%PORT%;
$("show").onchange=e=>$("pass").type=e.target.checked?"text":"password";
function scr(n){document.querySelectorAll(".screen").forEach(s=>s.classList.remove("on"));$(n).classList.add("on")}
function add(cls,text,name){const d=document.createElement("div");d.className=cls;
 if(name){const s=document.createElement("small");s.textContent=name;d.appendChild(s)}
 d.appendChild(document.createTextNode(text));$("log").appendChild(d);$("log").scrollTop=1e9}
async function auth(action){
 const u=$("user").value.trim(),p=$("pass").value,h=$("host").value.trim(),pt=$("port").value.trim();
 if(!u||!p){$("err").textContent="Username and password are required.";return}
 if(!h||!/^\d+$/.test(pt)){$("err").textContent="Enter a valid server and port.";return}
 $("err").textContent="Connecting…";
 const r=await pywebview.api.login(h,parseInt(pt),action,u,p);
 if(!r.ok){$("err").textContent=r.msg;return}
 me=u;$("err").textContent="";$("pass").value="";$("who").textContent="signed in as "+u;
 $("log").innerHTML="";scr("chat");add("sys","You joined the chat. Say hi!");$("msg").focus()}
$("bl").onclick=()=>auth("LOGIN");$("br").onclick=()=>auth("REGISTER");
$("pass").onkeydown=e=>{if(e.key==="Enter")auth("LOGIN")};
function send(){const m=$("msg").value.trim();if(!m)return;pywebview.api.send(m);add("msg me",m,me);$("msg").value=""}
$("send").onclick=send;$("msg").onkeydown=e=>{if(e.key==="Enter")send()};
$("leave").onclick=async()=>{await pywebview.api.leave();scr("login")};
function onLine(l){if(!l.trim())return;
 if(l.startsWith("***"))add("sys",l.replace(/\*/g,"").trim());
 else if(l.startsWith("Inappropriate word"))add("sys bad",l);
 else if(l.startsWith("Disconnecting"))add("sys",l);
 else{const i=l.indexOf(": ");if(i>0&&!l.slice(0,i).includes(" "))add("msg them",l.slice(i+2),l.slice(0,i));else add("sys",l)}}
function onClosed(){alert("You have been disconnected from the server.");scr("login")}
</script></body></html>"""


class Api:
    def __init__(self):
        self.sock = None
        self.session = 0

    def login(self, host, port, action, user, pw):
        try:
            sock = socket.create_connection((host, port), timeout=8)
            sock.settimeout(10)
            f = sock.makefile("r", encoding="utf-8")
            if f.readline().strip() != "AUTH_REQUIRED":
                raise ConnectionError("Unexpected reply from server")
            sock.sendall(f"{action}|{user}|{pw}\n".encode("utf-8"))
            resp = f.readline().strip()
            if not resp:
                raise ConnectionError("Server closed the connection")
            if not resp.startswith("OK"):
                sock.close()
                return {"ok": False, "msg": resp.replace("ERR ", "", 1)}
        except (OSError, ConnectionError) as e:
            return {"ok": False, "msg": f"Could not connect: {e}"}
        sock.settimeout(None)
        self.sock = sock
        self.session += 1
        threading.Thread(target=self._reader, args=(f, self.session), daemon=True).start()
        return {"ok": True, "msg": resp}

    def _reader(self, f, sid):
        try:
            for line in f:
                if sid != self.session:
                    return
                window.evaluate_js(f"onLine({json.dumps(line.rstrip(chr(10)))})")
        except (OSError, ValueError):
            pass
        if sid == self.session:
            self.sock = None
            window.evaluate_js("onClosed()")

    def send(self, msg):
        try:
            self.sock.sendall((msg + "\n").encode("utf-8"))
        except (OSError, AttributeError):
            pass

    def leave(self):
        self.session += 1
        try:
            self.sock.sendall(b"disconnect1122\n")
            self.sock.close()
        except (OSError, AttributeError):
            pass
        self.sock = None


if __name__ == "__main__":
    html = HTML.replace("%HOST%", json.dumps(DEFAULT_HOST)).replace("%PORT%", json.dumps(DEFAULT_PORT))
    window = webview.create_window("Secure Chat", html=html, js_api=Api(),
                                   width=460, height=720, min_size=(380, 560))
    webview.start()