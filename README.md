# wifi-Tools
# WiFi Scanner v6.0

![Banner](https://via.placeholder.com/800x200?text=WiFi+Scanner+v6.0)

WiFi Scanner v6.0 adalah alat canggih untuk analisis jaringan WiFi yang dikembangkan khusus untuk perangkat Android melalui Termux. Alat ini menyediakan berbagai fitur untuk memindai, menganalisis, dan melakukan uji keamanan pada jaringan WiFi di sekitar Anda.

## Fitur Utama

- ✅ **Pemindaian Jaringan WiFi**:
  - Deteksi semua jaringan WiFi di sekitar
  - Tampilkan detail lengkap (SSID, BSSID, kekuatan sinyal, dll)
  - Analisis keamanan jaringan (WEP, WPA, WPA2, WPA3)

- ⚡ **Fitur Serangan Jaringan**:
  - Deauthentication Attack
  - WPS PIN Attack
  - Brute Force Password
  - Rogue AP (Evil Twin)

- 🔐 **Manajemen Keamanan**:
  - Menampilkan password WiFi tersimpan (perangkat root)
  - Analisis kerentanan jaringan
  - Deteksi jaringan terbuka dan rentan

- 📶 **Manajemen Hotspot**:
  - Aktifkan/nonaktifkan hotspot
  - Ubah SSID dan password hotspot
  - Manajemen jaringan seluler

- 🌐 **Informasi Jaringan**:
  - Detail jaringan WAN
  - Informasi IP publik dan ISP
  - Analisis lokasi jaringan

## Instalasi

1. Instal Termux dari [F-Droid](https://f-droid.org/en/packages/com.termux/)
2. Buka Termux dan jalankan perintah berikut:

```bash
pkg update && pkg upgrade
pkg install git python
git clone https://github.com/kitoxl/wifi-Tools.git
cd wifi-scanner
pip install rich
python wifi_scanner.py
```

## Penggunaan

Setelah menjalankan aplikasi, Anda akan disajikan dengan menu interaktif:

```
╔═╗╔═╗╔═╗╦═╗╔═╗╔╦╗  
╚═╗║╣ ║  ╠╦╝║╣  ║    
╚═╝╚═╝╚═╝╩╚═╚═╝ ╩   

::=========[ ☠ WIFI SCANNER v6.0 ☠ ]=========::

```

### Menu Utama

```
📋 Menu Utama:
[1] Link Users                [5] Scripts Setup_Jarangan
[2] Scripts Detail_Jarangan   [6] Target Serangan
[3] Scripts Setup_Jarangan    [7] Info Sistem
[4] Scripts Setup_Jarangan    [8] Kelola Hotspot
[0] Keluar
```

1. **Memindai jaringan WiFi**:
   - Pilih opsi 6 untuk memulai pemindaian
   - Sistem akan menampilkan semua jaringan terdeteksi

2. **Analisis jaringan**:
   - Setelah pemindaian, pilih nomor jaringan untuk melihat detail
   - Dapatkan informasi keamanan, kekuatan sinyal, dan estimasi jarak

3. **Serangan jaringan**:
   - Pilih "Target Serangan" (menu 6)
   - Pilih jaringan target
   - Pilih jenis serangan (Deauth, WPS, Brute Force, atau Rogue AP)

4. **Manajemen Hotspot**:
   - Pilih "Kelola Hotspot" (menu 8)
   - Pilih aksi yang diinginkan (aktifkan, nonaktifkan, ubah SSID/password)

## Persyaratan Sistem

- Perangkat Android dengan versi 7.0 atau lebih baru
- Termux versi terbaru
- Akses root diperlukan untuk beberapa fitur (menampilkan password WiFi)
- Koneksi internet untuk instalasi dependensi

## Kontribusi

Kontribusi dipersilakan! Silakan fork repositori dan ajukan pull request dengan perubahan Anda.

## Penafian

Alat ini ditujukan hanya untuk tujuan edukasi dan pengujian keamanan jaringan Anda sendiri. Pengguna bertanggung jawab penuh atas penggunaan alat ini. Pengembang tidak bertanggung jawab atas penyalahgunaan alat ini.

---

**© 2023 WiFi Scanner v6.0** - Alat Analisis Jaringan WiFi untuk Termux
