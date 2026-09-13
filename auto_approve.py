#!/usr/bin/env python3
"""
=============================================================================
FASIH-SM AUTOMATION — APPROVE BY ADMIN KABUPATEN (SENSUS EKONOMI 2026)
=============================================================================
Script otomasi untuk melakukan persetujuan (approval) assignment dokumen 
Sensus Ekonomi 2026 yang berstatus 'EDITED BY ADMIN KABUPATEN' pada FASIH-SM.

Alur:
1. Menjalankan Google Chrome asli dengan remote debugging (CDP port 9222) &
   profil persisten (./chrome_debug_profile) agar sesi & cookies tersimpan
   dan terhindar dari deteksi bot BPS.
2. Pengguna login manual & navigasi ke halaman Data, pasang filter status
   'EDITED BY ADMIN KABUPATEN', serta mengatur jumlah data per halaman (100).
3. Setelah siap, pengguna menekan tombol ENTER di terminal.
4. Jendela Google Chrome dipindahkan ke posisi off-screen (luar layar)
   sehingga saat tab baru dibuka, pengguna TIDAK TERGANGGU dan bebas
   mengerjakan aktivitas lain di Mac.
5. Script beriterasi pada setiap assignment:
   - Klik kode assignment (membuka modal review).
   - Klik tombol 'Review' (membuka tab baru assignment di background off-screen).
   - Di tab baru, klik tombol approve (checklist hijau).
   - Pada modal konfirmasi approve, klik 'Konfirmasi'.
   - Tunggu 2 detik, lalu tutup tab assignment.
   - Kembali ke tab utama, tutup modal review.
6. Otomatis klik 'Next Page' jika semua data pada halaman aktif telah selesai,
   dan mengulangi proses hingga halaman terakhir.
7. Saat selesai atau dihentikan (Ctrl+C), jendela Chrome otomatis dikembalikan
   ke posisi semula di layar.
=============================================================================
"""

import asyncio
import os
import random
import re
import subprocess
import sys
import time
from pathlib import Path
from playwright.async_api import async_playwright

CDP_PORT = 9222
CHROME_PROFILE_DIR = os.path.abspath("./chrome_debug_profile")
BOT_CODE_PATTERN = re.compile(r"BOT-\d{10,}", re.IGNORECASE)


def print_banner():
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║               FASIH-SM AUTOMATION — SE2026                             ║
║             Approve by Admin Kabupaten Otomatis                        ║
║                                                                        ║
║   Mode: Connect ke Chrome via CDP (Anti-Bot & Persistent Session)      ║
╚════════════════════════════════════════════════════════════════════════╝
""")


# ─────────────────────────────────────────────────────────────
# 1. HELPER: WINDOW MANAGEMENT (CROSS-PLATFORM: MAC, WIN, LINUX)
# ─────────────────────────────────────────────────────────────
def get_chrome_bounds() -> str:
    """Mengambil koordinat dan ukuran jendela Chrome saat ini."""
    if sys.platform == "darwin":
        try:
            res = subprocess.run(
                ["osascript", "-e", 'tell application "Google Chrome" to get bounds of window 1'],
                capture_output=True, text=True, timeout=2
            )
            return res.stdout.strip()
        except Exception:
            return ""
    elif sys.platform == "win32":
        return "win32"
    return ""


def maximize_chrome():
    """Membuat jendela Google Chrome tampil penuh (full screen / maximized)."""
    if sys.platform == "darwin":
        try:
            script = '''
            tell application "Google Chrome"
                activate
                if (count of windows) > 0 then
                    tell application "Finder"
                        set b to bounds of window of desktop
                    end tell
                    set bounds of window 1 to b
                end if
            end tell
            '''
            subprocess.run(["osascript", "-e", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
        except Exception:
            pass
    elif sys.platform == "win32":
        try:
            import ctypes
            user32 = ctypes.windll.user32
            def enum_handler(hwnd, extra):
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value
                    if "Chrome" in title or "FASIH" in title:
                        user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE
                return True
            EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
            user32.EnumWindows(EnumWindowsProc(enum_handler), 0)
        except Exception:
            pass
    elif sys.platform.startswith("linux"):
        try:
            subprocess.run(["wmctrl", "-r", "Chrome", "-b", "add,maximized_vert,maximized_horz"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass


def move_chrome_offscreen():
    """Memindahkan jendela Chrome ke luar layar agar tidak menutupi kerjaan user."""
    if sys.platform == "darwin":
        try:
            # Menggunakan resolusi Full HD (1920x1080) saat off-screen agar layout tetap penuh
            subprocess.run(
                ["osascript", "-e", 'tell application "Google Chrome" to set bounds of window 1 to {-3000, -3000, -1080, -1920}'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2
            )
        except Exception:
            pass
    elif sys.platform == "win32":
        try:
            import ctypes
            user32 = ctypes.windll.user32
            def enum_handler(hwnd, extra):
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value
                    if "Chrome" in title or "FASIH" in title:
                        # Pindahkan ke (-3000, -3000) dengan ukuran 1920x1080
                        user32.SetWindowPos(hwnd, 0, -3000, -3000, 1920, 1080, 0x0010 | 0x0004)  # SWP_NOACTIVATE | SWP_NOZORDER
                return True
            EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
            user32.EnumWindows(EnumWindowsProc(enum_handler), 0)
        except Exception:
            pass


def restore_chrome_bounds(bounds: str = ""):
    """Mengembalikan jendela Chrome ke layar normal / maximized penuh."""
    if sys.platform == "darwin":
        if bounds and bounds != "win32":
            try:
                subprocess.run(
                    ["osascript", "-e", f'tell application "Google Chrome" to set bounds of window 1 to {{{bounds}}}'],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2
                )
                return
            except Exception:
                pass
        maximize_chrome()
    elif sys.platform == "win32":
        maximize_chrome()
    elif sys.platform.startswith("linux"):
        maximize_chrome()


def get_frontmost_app() -> str:
    """Mendapatkan nama/ID aplikasi yang sedang aktif digunakan pengguna."""
    if sys.platform == "darwin":
        try:
            res = subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to get name of first application process whose frontmost is true'],
                capture_output=True, text=True, timeout=1
            )
            name = res.stdout.strip()
            if name and name != "Google Chrome":
                return name
        except Exception:
            pass
    elif sys.platform == "win32":
        try:
            import ctypes
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            return str(hwnd)
        except Exception:
            pass
    return ""


def restore_user_app(app_name: str):
    """Menjaga agar aplikasi kerja pengguna tetap aktif di layar."""
    if sys.platform == "darwin":
        front = get_frontmost_app()
        target = front if (front and front != "Google Chrome") else app_name
        if target and target != "Google Chrome":
            try:
                subprocess.run(
                    ["osascript", "-e", f'tell application "{target}" to activate'],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1
                )
            except Exception:
                pass
    elif sys.platform == "win32":
        if app_name and app_name.isdigit():
            try:
                import ctypes
                user32 = ctypes.windll.user32
                user32.SetForegroundWindow(int(app_name))
            except Exception:
                pass


# ─────────────────────────────────────────────────────────────
# 2. HELPER: CHROME CDP LAUNCHER & DETECTION
# ─────────────────────────────────────────────────────────────
def find_chrome_path() -> str:
    """Mencari path binary Google Chrome di macOS, Windows, atau Linux."""
    import shutil

    # 1. macOS paths
    if sys.platform == "darwin":
        mac_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        ]
        for p in mac_paths:
            if os.path.isfile(p):
                return p

    # 2. Windows paths
    elif sys.platform == "win32":
        win_paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        for p in win_paths:
            if os.path.isfile(p):
                return p

    # 3. Linux paths
    elif sys.platform.startswith("linux"):
        linux_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/snap/bin/chromium",
        ]
        for p in linux_paths:
            if os.path.isfile(p):
                return p

    # 4. Fallback jika ada di PATH sistem
    for name in ["google-chrome", "google-chrome-stable", "chrome", "chromium", "chromium-browser"]:
        found = shutil.which(name)
        if found:
            return found

    return ""


def is_chrome_cdp_ready() -> bool:
    """Memeriksa apakah remote debugging port Chrome sudah aktif."""
    import urllib.request
    try:
        req = urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/version", timeout=2)
        req.read()
        return True
    except Exception:
        return False


def launch_chrome_with_cdp():
    """Membuka Google Chrome dengan remote debugging port jika belum berjalan."""
    if is_chrome_cdp_ready():
        print(f"[INFO] Chrome sudah berjalan di port {CDP_PORT}, langsung menghubungkan...")
        return None

    chrome_path = find_chrome_path()
    if not chrome_path:
        print("[ERROR] Google Chrome tidak ditemukan di sistem!")
        print("  Silakan install Google Chrome atau buka Chrome secara manual dengan perintah:")
        print(f'  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port={CDP_PORT} --user-data-dir="{CHROME_PROFILE_DIR}"')
        sys.exit(1)

    os.makedirs(CHROME_PROFILE_DIR, exist_ok=True)
    print(f"[INFO] Membuka Google Chrome dengan profil persisten: {CHROME_PROFILE_DIR}")
    print(f"[INFO] Remote debugging port: {CDP_PORT}")

    proc = subprocess.Popen(
        [
            chrome_path,
            f"--remote-debugging-port={CDP_PORT}",
            f"--user-data-dir={CHROME_PROFILE_DIR}",
            "--start-maximized",
            "--no-first-run",
            "--no-default-browser-check",
            "https://fasih-sm.bps.go.id/",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Tunggu hingga CDP siap
    for _ in range(30):
        time.sleep(1)
        if is_chrome_cdp_ready():
            print("[INFO] Google Chrome CDP siap terhubung!")
            maximize_chrome()
            return proc

    print("[ERROR] Batas waktu habis menunggu Chrome CDP aktif.")
    proc.terminate()
    sys.exit(1)


# ─────────────────────────────────────────────────────────────
# 3. ANTI-BOT BLOCK DETECTION
# ─────────────────────────────────────────────────────────────
async def check_and_handle_bot_block(page, orig_bounds: str = "") -> bool:
    """Memeriksa apakah ada pesan pencegahan bot dari FASIH BPS."""
    try:
        content = await page.content()
        is_blocked = (
            "mendeteksi koneksi anda sebagai bot" in content.lower()
            or "perilaku yang tidak wajar" in content.lower()
            or BOT_CODE_PATTERN.search(content)
        )
        if is_blocked:
            # Kembalikan jendela Chrome ke layar agar user bisa melihat dan menyelesaikan
            if orig_bounds:
                restore_chrome_bounds(orig_bounds)

            print("\a\n" + "!" * 65)
            print("  ⚠️ TERDETEKSI SISTEM PENGAMAN BPS (BOT BLOCK)!")
            print("  Jendela Chrome telah dikembalikan ke layar:")
            print("  1. Klik tombol '[Kembali]' atau refresh halaman di Chrome.")
            print("  2. Pastikan halaman normal kembali.")
            print("!" * 65)
            input("\nSetelah halaman kembali normal, tekan ENTER di sini untuk lanjut...")
            
            # Pindahkan kembali ke luar layar
            if orig_bounds:
                move_chrome_offscreen()
            await asyncio.sleep(2)
            return True
    except Exception:
        pass
    return False


# ─────────────────────────────────────────────────────────────
# 4. TAB DAN ELEMENT HELPERS
# ─────────────────────────────────────────────────────────────
async def find_data_page(context):
    """Mencari tab browser yang sedang membuka halaman Data FASIH."""
    for pg in context.pages:
        try:
            url = pg.url
            if "/data" in url or "/surveys/" in url:
                return pg
        except Exception:
            continue
    return context.pages[0] if context.pages else await context.new_page()


async def close_review_modal_if_open(page):
    """Menutup modal review 'Assignment Detail' jika masih terbuka di tab utama."""
    try:
        dialog = page.locator('div[role="dialog"]:has-text("Assignment Detail")')
        if await dialog.count() > 0 and await dialog.first.is_visible():
            close_btn = dialog.locator('button:has(svg.tabler-icon-x), button:has-text("Close")')
            if await close_btn.count() > 0 and await close_btn.first.is_visible():
                await close_btn.first.click()
            else:
                await page.keyboard.press("Escape")
            await dialog.first.wait_for(state="hidden", timeout=2500)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────
# 5. INTI PROSES: APPROVE PER TAB ASSIGNMENT
# ─────────────────────────────────────────────────────────────
async def process_single_assignment(page, context, btn, assignment_id: str, user_app: str = "") -> bool:
    """
    Menjalankan alur approve untuk satu dokumen assignment:
    1. Klik kode assignment di halaman data.
    2. Tunggu modal Assignment Detail muncul.
    3. Klik tombol Review (membuka tab baru).
    4. Di tab baru, cari & klik tombol checklist hijau (approve).
    5. Klik tombol Konfirmasi pada modal konfirmasi approve.
    6. Tunggu 2 detik.
    7. Tutup tab assignment.
    8. Tutup modal review di tab utama jika masih ada.
    """
    print(f"\n[PROSES] Menangani: {assignment_id}")

    # 1. Klik tombol assignment di tabel
    try:
        await btn.scroll_into_view_if_needed()
        await btn.click()
    except Exception as e:
        print(f"  ❌ Gagal mengklik tombol assignment di tabel: {e}")
        return False

    # 2. Tunggu modal Assignment Detail muncul
    dialog = page.locator('div[role="dialog"]:has-text("Assignment Detail")')
    try:
        await dialog.first.wait_for(state="visible", timeout=8000)
    except Exception:
        print("  ⚠️ Modal 'Assignment Detail' tidak muncul dalam 8 detik. Mencoba ulang klik...")
        try:
            await btn.click()
            await dialog.first.wait_for(state="visible", timeout=5000)
        except Exception as e:
            print(f"  ❌ Modal tetap tidak terbuka: {e}")
            return False

    # 3. Cari tombol Review (a[target="_blank"] dengan tombol Review)
    review_btn = dialog.locator('a[target="_blank"]:has-text("Review"), button:has-text("Review")')
    try:
        await review_btn.first.wait_for(state="visible", timeout=6000)
    except Exception as e:
        print(f"  ❌ Tombol 'Review' tidak ditemukan pada modal: {e}")
        await close_review_modal_if_open(page)
        return False

    # 4. Buka tab baru assignment
    assignment_tab = None
    try:
        async with context.expect_page(timeout=15000) as new_page_info:
            await review_btn.first.click()
        assignment_tab = await new_page_info.value
        # Pastikan fokus tetap di aplikasi yang sedang digunakan pengguna
        restore_user_app(user_app)
        await assignment_tab.wait_for_load_state("domcontentloaded")
    except Exception as e:
        print(f"  ❌ Gagal membuka tab baru assignment: {e}")
        await close_review_modal_if_open(page)
        return False

    # 5. Bekerja di dalam assignment_tab
    try:
        await check_and_handle_bot_block(assignment_tab)

        # Cari tombol approve checklist hijau
        approve_selectors = [
            'button.f\\:bg-success:has(svg.tabler-icon-check)',
            'button:has(svg.tabler-icon-check)',
            'button.f\\:bg-success',
        ]

        approve_btn = None
        for sel in approve_selectors:
            loc = assignment_tab.locator(sel)
            if await loc.count() > 0 and await loc.first.is_visible():
                approve_btn = loc.first
                break

        if not approve_btn:
            # Tunggu jika toolbar masih merender
            try:
                await assignment_tab.wait_for_selector(
                    'button.f\\:bg-success:has(svg.tabler-icon-check), button:has(svg.tabler-icon-check)',
                    timeout=10000
                )
                approve_btn = assignment_tab.locator('button.f\\:bg-success:has(svg.tabler-icon-check), button:has(svg.tabler-icon-check)').first
            except Exception:
                pass

        if not approve_btn:
            print("  ⚠️ Tombol Approve (checklist hijau) tidak ditemukan pada tab ini.")
            print("     Kemungkinan dokumen ini sudah pernah di-approve atau statusnya berbeda.")
            await assignment_tab.close()
            restore_user_app(user_app)
            await close_review_modal_if_open(page)
            return False

        # Klik tombol Approve
        await approve_btn.click()
        print("  -> Tombol Approve diklik, menunggu modal konfirmasi...")

        # 6. Tunggu modal konfirmasi approve (modal_approve.html)
        confirm_btn = assignment_tab.locator('button:has-text("Konfirmasi"), div[role="alertdialog"] button:has-text("Konfirmasi")')
        await confirm_btn.first.wait_for(state="visible", timeout=7000)
        await confirm_btn.first.click()
        print(f"  ✅ Tombol Konfirmasi diklik!")

        # 7. Tunggu 2 detik sesuai instruksi
        print("  ⏳ Menunggu 2 detik agar status tersimpan di server...")
        await asyncio.sleep(2)

    except Exception as e:
        print(f"  ❌ Terjadi kendala di tab assignment: {e}")
        try:
            if assignment_tab and not assignment_tab.is_closed():
                await assignment_tab.close()
        except Exception:
            pass
        restore_user_app(user_app)
        await close_review_modal_if_open(page)
        return False

    # 8. Tutup tab assignment & kembali ke halaman utama
    try:
        if assignment_tab and not assignment_tab.is_closed():
            await assignment_tab.close()
    except Exception:
        pass

    restore_user_app(user_app)
    await close_review_modal_if_open(page)

    print(f"  🎉 Sukses approve: {assignment_id}")

    # Delay natural singkat antar dokumen
    await asyncio.sleep(random.uniform(0.8, 1.4))
    return True


# ─────────────────────────────────────────────────────────────
# 6. LOOP UTAMA: ITERASI TABEL & PAGINATION
# ─────────────────────────────────────────────────────────────
async def run_automation(page, context, user_app: str = "", orig_bounds: str = ""):
    """Menjalankan otomasi seluruh halaman secara berulang."""
    current_page_number = 1
    total_approved_session = 0

    while True:
        print(f"\n{'='*65}")
        print(f"📄 MEMPROSES HALAMAN: {current_page_number}")
        print(f"{'='*65}")

        await check_and_handle_bot_block(page, orig_bounds)

        # Tunggu tabel termuat di halaman
        try:
            await page.wait_for_selector("table tbody tr", timeout=12000)
        except Exception:
            print("  ❌ Tabel data belum terlihat atau memuat terlalu lama.")
            input("  Silakan pastikan tabel data tampil di browser, lalu tekan ENTER di terminal...")

        # Pastikan tidak ada modal yang menghalangi
        await close_review_modal_if_open(page)

        # Ambil semua baris di tbody
        rows = page.locator("table tbody tr")
        total_rows = await rows.count()
        print(f"[INFO] Ditemukan {total_rows} baris pada halaman saat ini.")

        if total_rows == 0:
            print("  ⚠️ Tidak ada baris data pada tabel.")
            break

        processed_this_page = set()

        for i in range(total_rows):
            # Ambil baris ke-i
            row = page.locator("table tbody tr").nth(i)
            btn = row.locator('td:nth-child(2) button, button.f\\:underline, button:has(span[class*="truncate"])').first
            if await btn.count() == 0:
                continue

            try:
                text_id = (await btn.inner_text()).strip()
            except Exception:
                continue

            if not text_id or text_id in processed_this_page:
                continue

            processed_this_page.add(text_id)
            success = await process_single_assignment(page, context, btn, text_id, user_app)
            if success:
                total_approved_session += 1

            print(f"[PROGRESS] Total approve sesi ini: {total_approved_session} dokumen")

        # ─────────────────────────────────────────────────────────────
        # PAGINATION: Cek apakah ada halaman berikutnya (Next Page)
        # ─────────────────────────────────────────────────────────────
        next_btn = page.locator('button[aria-label="Go to next page"]')
        has_next = False

        if await next_btn.count() > 0:
            is_disabled = await next_btn.first.is_disabled()
            is_visible = await next_btn.first.is_visible()
            if is_visible and not is_disabled:
                has_next = True

        if has_next:
            print(f"\n[NAVIGASI] Semua data di halaman {current_page_number} selesai diproses.")
            print("           Mengeklik tombol 'Next Page' (halaman berikutnya)...")

            try:
                first_row_btn = page.locator("table tbody tr td:nth-child(2) button").first
                old_id = (await first_row_btn.inner_text()).strip() if await first_row_btn.count() > 0 else ""

                await next_btn.first.click()

                # Tunggu pergantian data halaman
                await asyncio.sleep(2)
                for _ in range(15):
                    new_btn = page.locator("table tbody tr td:nth-child(2) button").first
                    new_id = (await new_btn.inner_text()).strip() if await new_btn.count() > 0 else ""
                    if new_id and new_id != old_id:
                        break
                    await asyncio.sleep(0.5)

                current_page_number += 1
                await asyncio.sleep(1)
            except Exception as e:
                print(f"  ❌ Gagal berpindah ke halaman berikutnya: {e}")
                break
        else:
            print(f"\n[SELESAI] Tombol 'Next Page' tidak aktif / sudah mencapai halaman terakhir.")
            break

    print(f"\n{'='*65}")
    print(f"🏆 OTOMASI SELESAI!")
    print(f"   Total dokumen berhasil di-approve pada sesi ini: {total_approved_session}")
    print(f"{'='*65}\n")


# ─────────────────────────────────────────────────────────────
# 7. MAIN RUNNER
# ─────────────────────────────────────────────────────────────
async def main():
    print_banner()

    # 1. Jalankan atau sambungkan ke Google Chrome asli
    chrome_proc = launch_chrome_with_cdp()

    async with async_playwright() as p:
        print("[INFO] Menghubungkan Playwright ke Google Chrome via CDP...")
        try:
            browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
        except Exception as e:
            print(f"[ERROR] Gagal connect ke Chrome di port {CDP_PORT}: {e}")
            sys.exit(1)

        ctx = browser.contexts[0]
        page = await find_data_page(ctx)
        maximize_chrome()

        print("\n" + "=" * 65)
        print("📌 INSTRUKSI PERSIAPAN MANUAL DI CHROME:")
        print("   1. Pastikan Anda sudah LOGIN ke akun FASIH-SM.")
        print("   2. Masuk ke halaman DATA survei SE2026.")
        print("   3. Pasang filter status: 'EDITED BY ADMIN KABUPATEN'.")
        print("   4. Atur jumlah data per halaman menjadi 100 data.")
        print("   5. Pastikan tabel data sudah muncul di layar Chrome.")
        print("=" * 65)
        input("\n👉 Jika halaman Data sudah siap & difilter, tekan ENTER di sini untuk mulai...")

        # Ambil posisi jendela Chrome saat ini agar bisa dikembalikan nanti
        orig_bounds = get_chrome_bounds()
        user_app = get_frontmost_app()

        print("\n[INFO] Memindahkan jendela Chrome ke background luar layar agar Anda bebas beraktivitas...")
        move_chrome_offscreen()
        restore_user_app(user_app)

        # Pastikan kita memakai tab data yang aktif
        page = await find_data_page(ctx)

        try:
            await run_automation(page, ctx, user_app, orig_bounds)
        except (KeyboardInterrupt, asyncio.CancelledError):
            print("\n\n[INFO] Otomasi dihentikan secara manual oleh pengguna (Ctrl+C).")
        except Exception as e:
            print(f"\n[ERROR] Terjadi kendala saat otomasi: {e}")
            import traceback
            traceback.print_exc()
        finally:
            restore_chrome_bounds(orig_bounds)
            print("[INFO] Jendela Google Chrome telah dikembalikan ke layar.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\n[INFO] Program selesai dihentikan.")
