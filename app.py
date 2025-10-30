import csv
from pathlib import Path

# Mengimpor kelas/fungsi dari paket tracker.
# Gunakan try/except supaya fleksibel jika dijalankan sebagai paket atau file tunggal.
try:
    from tracker import RekapKelas, Mahasiswa, Penilaian
    from tracker import build_markdown_report, save_text, letter_grade, build_html_report
except Exception:
    # fallback: impor langsung dari submodule (jika modul belum diinstall sebagai package)
    from tracker.rekap_kelas import RekapKelas
    from tracker.mahasiswa import Mahasiswa
    from tracker.penilaian import Penilaian
    from tracker.report import build_markdown_report, save_text, letter_grade, build_html_report

# Direktori data dan output
DATA_DIR = Path("data")
OUT_DIR = Path("out")
# Pastikan folder out ada supaya bisa menyimpan report
if not OUT_DIR.exists():
    OUT_DIR.mkdir(parents=True)

# header yang akan dipakai untuk CSV attendance dan grades
ATT_HEADERS = ["student_id", "name", "week1", "week2", "week3", "week4", "week5"]
GRD_HEADERS = ["student_id", "name", "quiz", "assignment", "mid", "final"]

# ---------- Helper CSV sederhana (manual style) -----------
def read_csv(path):
    """Baca CSV ke list of dict. Jika file tidak ada, kembalikan list kosong."""
    p = Path(path)
    rows = []
    if not p.exists():
        return rows
    # baca menggunakan csv.DictReader supaya kolom menjadi key
    with p.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(dict(r))
    return rows

def write_csv(path, fieldnames, rows):
    """Tulis list of dict ke CSV, tulis header manual lalu baris per baris."""
    p = Path(path)
    if not p.parent.exists():
        p.parent.mkdir(parents=True)
    # tulis file, jangan gunakan newline aneh
    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        # tulis satu per satu, pastikan hanya kolom yang ada di fieldnames ditulis
        for r in rows:
            out = {}
            for key in fieldnames:
                # pakai get agar tidak error kalau kunci tidak ada
                out[key] = r.get(key, "")
            writer.writerow(out)

# ---------- Kalkulasi attendance (manual) -------------
def calculate_attendance_percent_from_row(row):
    """Hitung persen hadir dari kolom week1..week5 secara manual."""
    # kumpulkan key week yang ditemukan (urut dari 1..5)
    weeks = []
    for i in range(1, 6):
        k = f"week{i}"
        if k in row:
            weeks.append(k)
    if len(weeks) == 0:
        return 0.0
    total = 0
    present = 0
    for w in weeks:
        total += 1
        raw = row.get(w, "")
        raw = (raw or "").strip()
        # terima "1", "0", atau angka lain -> coba konversi ke int
        if raw == "":
            # kosong dianggap tidak hadir (0)
            val = 0
        else:
            try:
                # beberapa orang menulis '1.0' atau '1', kita gunakan int(float())
                val = int(float(raw))
            except Exception:
                # kalau gagal konversi, anggap 0 dan lanjut
                val = 0
        if val != 0:
            present += 1
    try:
        percent = round(present / total * 100.0, 2)
    except Exception:
        percent = 0.0
    return percent

# ---------- Tambah mahasiswa ke CSV (manual) ----------
def add_student_to_csvs(nim, nama):
    """Tambahkan mahasiswa ke kedua CSV (attendance + grades) jika belum ada."""
    att_path = DATA_DIR / "attendance.csv"
    grd_path = DATA_DIR / "grades.csv"

    # attendance
    att_rows = read_csv(att_path)
    exists = False
    for r in att_rows:
        if r.get("student_id") == nim:
            exists = True
            break
    if not exists:
        # buat baris attendance default manual
        new = {"student_id": nim, "name": nama, "week1": "0", "week2": "0", "week3": "0", "week4": "0", "week5": "0"}
        att_rows.append(new)
        write_csv(att_path, ATT_HEADERS, att_rows)

    # grades
    grd_rows = read_csv(grd_path)
    exists = False
    for r in grd_rows:
        if r.get("student_id") == nim:
            exists = True
            break
    if not exists:
        new = {"student_id": nim, "name": nama, "quiz": "0", "assignment": "0", "mid": "0", "final": "0"}
        grd_rows.append(new)
        write_csv(grd_path, GRD_HEADERS, grd_rows)

# ---------- Update attendance CSV (manual) ----------
def update_attendance_csv(nim, weeks_update):
    """
    weeks_update adalah dict sederhana, misal {'week1': '1', 'week2': '0', ...}
    Jika nilai None artinya tidak diubah.
    """
    att_path = DATA_DIR / "attendance.csv"
    if not att_path.exists():
        raise FileNotFoundError("attendance.csv tidak ditemukan.")
    rows = read_csv(att_path)
    found = False
    for r in rows:
        if r.get("student_id") == nim:
            found = True
            # per week, lakukan update manual
            for i in range(1, 6):
                k = f"week{i}"
                if k in weeks_update:
                    v = weeks_update[k]
                    # hanya terima '1' atau '0' (string)
                    if v is None:
                        # berarti tidak diubah
                        continue
                    val = str(v).strip()
                    if val == "1":
                        r[k] = "1"
                    elif val == "0":
                        r[k] = "0"
                    else:
                        # jika bukan 1/0, kita abaikan dan tidak ubah
                        pass
            break
    if not found:
        raise KeyError("NIM tidak ditemukan di attendance.csv.")
    write_csv(att_path, ATT_HEADERS, rows)
    return rows

# ---------- Update grades CSV (manual) ----------
def update_grades_csv(nim, quiz=None, assignment=None, mid=None, final=None, fallback_name=""):
    """
    Update atau tambahkan baris di grades.csv.
    Jika argument None maka tidak diubah (kecuali jika baris baru dibuat -> default 0).
    """
    grd_path = DATA_DIR / "grades.csv"
    rows = read_csv(grd_path)
    found = False
    for r in rows:
        if r.get("student_id") == nim:
            found = True
            if quiz is not None:
                try:
                    r["quiz"] = str(float(quiz))
                except Exception:
                    r["quiz"] = "0"
            if assignment is not None:
                try:
                    r["assignment"] = str(float(assignment))
                except Exception:
                    r["assignment"] = "0"
            if mid is not None:
                try:
                    r["mid"] = str(float(mid))
                except Exception:
                    r["mid"] = "0"
            if final is not None:
                try:
                    r["final"] = str(float(final))
                except Exception:
                    r["final"] = "0"
            if not r.get("name"):
                r["name"] = fallback_name
            break
    if not found:
        # buat baris baru, nilai None -> 0
        new = {
            "student_id": nim,
            "name": fallback_name,
            "quiz": str(float(quiz or 0)),
            "assignment": str(float(assignment or 0)),
            "mid": str(float(mid or 0)),
            "final": str(float(final or 0))
        }
        rows.append(new)
    write_csv(grd_path, GRD_HEADERS, rows)
    return rows

# ---------- Muat data CSV ke object RekapKelas (manual) ----------
def load_attendance_into_rekap(rekap, att_path):
    """Muat attendance.csv ke objek RekapKelas satu per satu (manual loop)."""
    rows = read_csv(att_path)
    for row in rows:
        nim = row.get("student_id")
        nama = row.get("name")
        if not nim or not nama:
            continue
        # jika belum ada di rekap, tambahkan Mahasiswa
        if nim not in rekap._data_by_nim:
            # pakai Mahasiswa class
            m = Mahasiswa(nim, nama)
            rekap.tambah_mahasiswa(m)
        # hitung persen hadir dan set
        persen = calculate_attendance_percent_from_row(row)
        rekap.ubah_hadir(nim, persen)

def load_grades_into_rekap(rekap, grd_path):
    """Muat grades.csv ke RekapKelas (manual)."""
    rows = read_csv(grd_path)
    for r in rows:
        nim = r.get("student_id")
        nama = r.get("name")
        if not nim:
            continue
        if nim not in rekap._data_by_nim:
            rekap.tambah_mahasiswa(Mahasiswa(nim, nama or nim))
        # ambil nilai, coba konversi manual
        try:
            q = float(r.get("quiz", 0) or 0)
        except Exception:
            q = 0.0
        try:
            a = float(r.get("assignment", 0) or 0)
        except Exception:
            a = 0.0
        try:
            m = float(r.get("mid", 0) or 0)
        except Exception:
            m = 0.0
        try:
            f = float(r.get("final", 0) or 0)
        except Exception:
            f = 0.0
        # gunakan method ubah_penilaian pada rekap
        rekap.ubah_penilaian(nim, quiz=q, tugas=a, uts=m, uas=f)

# ---------- Generate report helper ----------
def generate_and_save_report(rekap):
    """Ambil data dari rekap dan buat file report.md di folder out."""
    records = rekap.export_for_report()
    md = build_markdown_report(records)
    out_path = OUT_DIR / "report.md"
    save_text(out_path, md)
    return out_path

# ---------- Bootstrap helper (gunakan CSV jika ada) ----------
def bootstrap_from_csv(rekap, att_path, grd_path):
    """Isi rekap dari CSV (dipanggil saat program mulai jika file ada)."""
    # load attendance dulu kalau ada
    if att_path.exists():
        rows = read_csv(att_path)
        for r in rows:
            nim = r.get("student_id"); nama = r.get("name")
            if not nim or not nama:
                continue
            m = Mahasiswa(nim, nama)
            rekap.tambah_mahasiswa(m)
            persen = calculate_attendance_percent_from_row(r)
            rekap.ubah_hadir(nim, persen)
    # load grades lalu match ke nim yang sudah ada
    if grd_path.exists():
        grd = read_csv(grd_path)
        # buat dict by nim manual
        by_nim = {}
        for g in grd:
            sid = g.get("student_id")
            if sid:
                by_nim[sid] = g
        # update nilai mahasiswa yang sudah ada
        for nim in list(rekap._data_by_nim.keys()):
            g = by_nim.get(nim)
            if not g:
                continue
            try:
                q = float(g.get("quiz", 0) or 0)
            except Exception:
                q = 0.0
            try:
                a = float(g.get("assignment", 0) or 0)
            except Exception:
                a = 0.0
            try:
                m = float(g.get("mid", 0) or 0)
            except Exception:
                m = 0.0
            try:
                f = float(g.get("final", 0) or 0)
            except Exception:
                f = 0.0
            rekap.ubah_penilaian(nim, quiz=q, tugas=a, uts=m, uas=f)

# ---------- Tampilan tabel sederhana (manual formatting) ----------
def print_table(headers, rows):
    """Cetak tabel sederhana, manual hitung lebar kolom."""
    # filter kosong
    filtered = []
    for r in rows:
        values = [str(r.get(h, "") or "").strip() for h in headers]
        ok = False
        for v in values:
            if v != "":
                ok = True
                break
        if ok:
            # zip headers->values manual
            mapped = {}
            for i, h in enumerate(headers):
                mapped[h] = values[i]
            filtered.append(mapped)
    if not filtered:
        print("(tidak ada data untuk ditampilkan)")
        return
    widths = []
    for h in headers:
        widths.append(len(h))
    for r in filtered:
        for i, h in enumerate(headers):
            if len(str(r.get(h, ""))) > widths[i]:
                widths[i] = len(str(r.get(h, "")))
    # buat fungsi format baris manual
    def fmt_row(values):
        parts = []
        for i, v in enumerate(values):
            parts.append(str(v).ljust(widths[i]))
        return " | ".join(parts)
    # print header
    print()
    print(fmt_row(headers))
    # print separator
    sep_parts = []
    for w in widths:
        sep_parts.append("-" * w)
    print("-+-".join(sep_parts))
    # print rows
    for r in filtered:
        vals = [r.get(h, "") for h in headers]
        print(fmt_row(vals))
    print()

def show_summary_rows(rows):
    """Tampilkan rekap singkat (fixed format) seperti contoh di tugas."""
    if not rows:
        print("\n(tidak ada data untuk ditampilkan)\n")
        return

    # hitung lebar kolom nama paling panjang
    lebar_nama = max(len(str(r["nama"])) for r in rows)
    if lebar_nama < 10:
        lebar_nama = 10  # jaga minimal

    print("\nNIM        | {:<{w}} | Hadir% | Akhir | Pred".format("Nama", w=lebar_nama))
    print("-" * (12 + lebar_nama + 24))  # garis pemisah proporsional

    for r in rows:
        print("{:<10} | {:<{w}} | {:>6.2f} | {:>6.2f} | {:<3}".format(
            r["nim"], r["nama"], float(r["hadir"]), float(r["akhir"]), r["predikat"], w=lebar_nama
        ))

    print()

# ---------- MAIN CLI ---------
def main(auto_bootstrap=True):
    # buat objek rekap
    rekap = RekapKelas()
    # jika ada CSV, isi data awal
    if auto_bootstrap:
        att_path = DATA_DIR / "attendance.csv"
        grd_path = DATA_DIR / "grades.csv"
        if att_path.exists() and grd_path.exists():
            bootstrap_from_csv(rekap, att_path, grd_path)

    # loop menu sederhana
    while True:
        print("=== Student Performance Tracker (versi PEMULA) ===")
        print("1) Muat data dari CSV")
        print("2) Tambah mahasiswa")
        print("3) Ubah presensi")
        print("4) Ubah nilai")
        print("5) Lihat rekap")
        print("6) Simpan laporan (MD + HTML)")
        print("7) Keluar")
        pilihan = input("Pilih (1-7): ").strip()

        if pilihan == "1":
            print("Muat data: 1) attendance.csv  2) grades.csv")
            sub = input("Pilih (1/2): ").strip()
            if sub == "1":
                p = DATA_DIR / "attendance.csv"
                if not p.exists():
                    print("! File attendance.csv tidak ditemukan.")
                else:
                    load_attendance_into_rekap(rekap, p)
                    print("Attendance berhasil dimuat ke memori.")
                    rows = read_csv(p)
                    print_table(ATT_HEADERS, rows)
            elif sub == "2":
                p = DATA_DIR / "grades.csv"
                if not p.exists():
                    print("! File grades.csv tidak ditemukan.")
                else:
                    load_grades_into_rekap(rekap, p)
                    print("Grades berhasil dimuat ke memori.")
                    rows = read_csv(p)
                    print_table(GRD_HEADERS, rows)
            else:
                print("Pilihan tidak valid.")

        elif pilihan == "2":
            nim = input("Masukkan NIM: ").strip()
            nama = input("Masukkan Nama: ").strip()
            if not nim or not nama:
                print("NIM dan Nama wajib diisi.")
            else:
                try:
                    # tambahkan ke rekap dan CSV
                    rekap.tambah_mahasiswa(Mahasiswa(nim, nama))
                    add_student_to_csvs(nim, nama)
                    outp = generate_and_save_report(rekap)
                    print(f"Mahasiswa ditambahkan. Laporan dibuat: {outp}")
                except Exception as e:
                    print("!Gagal menambah mahasiswa:", e)

        elif pilihan == "3":
            nim = input("Masukkan NIM mahasiswa yang akan diubah presensinya: ").strip()
            # untuk pemula: input tiap week satu per satu, kosong = biarkan
            w_updates = {}
            for i in range(1, 6):
                val = input(f"week {i} (masukkan 1 untuk hadir, 0 untuk tidak hadir, kosong = tidak ubah): ").strip()
                if val == "":
                    w_updates[f"week{i}"] = None
                elif val == "1":
                    w_updates[f"week{i}"] = "1"
                elif val == "0":
                    w_updates[f"week{i}"] = "0"
                else:
                    # input lain kita anggap tidak ubah
                    w_updates[f"week{i}"] = None
            try:
                rows = update_attendance_csv(nim, w_updates)
                # cari baris terbaru dan update memori rekap
                found_row = None
                for r in rows:
                    if r.get("student_id") == nim:
                        found_row = r
                        break
                if found_row:
                    perc = calculate_attendance_percent_from_row(found_row)
                    rekap.ubah_hadir(nim, perc)
                outp = generate_and_save_report(rekap)
                print(f"Presensi berhasil diperbarui. Laporan: {outp}")
            except Exception as e:
                print("!Gagal ubah presensi:", e)

        elif pilihan == "4":
            nim = input("Masukkan NIM: ").strip()
            # pemula: masukkan nilai satu per satu (boleh kosong)
            def ask_number(prompt):
                s = input(prompt).strip()
                if s == "":
                    return None
                try:
                    return float(s)
                except Exception:
                    print("Input tidak valid, dianggap kosong.")
                    return None
            q = ask_number("Nilai Quiz (kosong = tidak ubah): ")
            a = ask_number("Nilai Tugas (kosong = tidak ubah): ")
            m = ask_number("Nilai UTS (kosong = tidak ubah): ")
            f = ask_number("Nilai UAS (kosong = tidak ubah): ")
            try:
                rekap.ubah_penilaian(nim, quiz=q, tugas=a, uts=m, uas=f)
                # simpan juga ke CSV
                fallback_name = ""
                if nim in rekap._data_by_nim:
                    fallback_name = rekap._data_by_nim[nim]['mhs'].nama
                update_grades_csv(nim, q, a, m, f, fallback_name)
                outp = generate_and_save_report(rekap)
                print(f"Nilai diperbarui. Laporan: {outp}")
            except Exception as e:
                print("!Gagal ubah nilai:", e)

        elif pilihan == "5":
            print("1) Semua mahasiswa  2) Hanya nilai akhir < 70")
            sub = input("Pilih (1/2): ").strip()
            rows = rekap.rekap()
            if sub == "2":
                # filter manual
                low = []
                for rr in rows:
                    try:
                        val = float(rr.get('akhir', 0))
                    except Exception:
                        val = 0.0
                    if val < 70.0:
                        low.append(rr)
                rows = low
            show_summary_rows(rows)

        elif pilihan == "6":
            try:
                records = rekap.export_for_report()
                md = build_markdown_report(records)
                out_md = OUT_DIR / "report.md"
                save_text(out_md, md)
                html = build_html_report(records)
                out_html = OUT_DIR / "report.html"
                save_text(out_html, html)
                print(f"Laporan disimpan ke {out_md} dan {out_html}")
            except Exception as e:
                print("!Gagal menyimpan laporan:", e)

        elif pilihan == "7":
            print("Keluar. Terimakasih dan Sampai Jumpa!")
            break

        else:
            print("Pilihan tidak dikenali. Silakan coba lagi.")

# jalankan jika dipanggil langsung
if __name__ == "__main__":
    main()
