import subprocess

ENABLE = 0
DISABLE = 1
DISABLE_TIME_SECONDS = 600

def is_installed():
    try:
        return __call_command('pihole') is 0
    except:
        return False

def enable():
    try:
        __call_command('pihole enable')
    except: pass

def disable(time):
    try:
        __call_command('pihole disable ' + time)
    except: pass

def status():
    try:
        res = __call_command('pihole status | grep Enabled')
        return ENABLE if res is 0 else DISABLE
    except:
        return DISABLE

def dns_queries_today():
    return "Queries: " + __request_section("dns_queries_today")

def ads_blocked_today():
    return "Blocked: " + __request_section("ads_blocked_today")

def ads_percentage_today():
	percentage = float(__request_section("ads_percentage_today") or 0.0)
	return "Percent: " + '%.2f' % percentage + "%"

def clients_ever_seen():
    return "Clients: " + __request_section("clients_ever_seen")

def unique_clients():
    return "Clients: " + __request_section("unique_clients")

# Private functions
def __request_section(section):
    cmd = "curl -f -s http://127.0.0.1/admin/api.php | jq ." + section
    return subprocess.check_output(cmd, shell = True).strip()

def __call_command(cmd):
    return subprocess.call(cmd, shell = True, stdout=subprocess.PIPE)
