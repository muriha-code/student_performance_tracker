import csv
from pathlib import Path

# =========================================================
# Import modul dari package tracker
# =========================================================
try:
    from tracker import RekapKelas, Mahasiswa
    from tracker import build_markdown_report, save_text, build_html_report
except Exception:
    from tracker.rekap_kelas import RekapKelas
    from tracker.mahasiswa import Mahasiswa
    from tracker.report import build_markdown_report, save_text, build_html_report

# =========================================================
# Konstanta dasar
# =========================================================
DATA_DIR = Path("data")
OUT_DIR = Path("out")

if not OUT_DIR.exists():
    OUT_DIR.mkdir(parents=True)

ATT_HEADERS = ["student_id", "name", "week1", "week2", "week3", "week4", "week5"]
GRD_HEADERS = ["student_id", "name", "quiz", "assignment", "mid", "final"]

# =========================================================
# Fungsi bantu untuk CSV
# =========================================================
def read_csv(path):
    """Membaca file CSV dan mengembalikan list of dict."""
    rows = []
    p = Path(path)
    if not p.exists():
        return rows
    with p.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(dict(r))
    return rows


def write_csv(path, fieldnames, rows):
    """Menulis list of dict ke file CSV (header manual + isi)."""
    p = Path(path)
    if not p.parent.exists():
        p.parent.mkdir(parents=True)
    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            clean = {k: r.get(k, "") for k in fieldnames}
            writer.writerow(clean)


# =========================================================
# Fungsi bantu kehadiran & nilai
# =========================================================
def calculate_attendance_percent_from_row(row):
    """Hitung persentase kehadiran dari kolom week1..week5."""
    total = 0
    hadir = 0
    for i in range(1, 6):
        val = row.get(f"week{i}", "0")
        try:
            if int(float(val)) != 0:
                hadir += 1
        except Exception:
            pass
        total += 1
    return round(hadir / total * 100, 2) if total > 0 else 0.0


# =========================================================
# Update data ke file CSV
# =========================================================
def update_attendance_csv(nim, weeks_update):
    """Memperbarui presensi mahasiswa tertentu berdasarkan dictionary week."""
    att_path = DATA_DIR / "attendance.csv"
    rows = read_csv(att_path)
    updated = False
    for r in rows:
        if r.get("student_id") == nim:
            for i in range(1, 6):
                key = f"week{i}"
                val = weeks_update.get(key)
                if val in ("0", "1"):
                    r[key] = val
            updated = True
            break
    if not updated:
        raise KeyError("NIM tidak ditemukan di attendance.csv")
    write_csv(att_path, ATT_HEADERS, rows)
    return rows


def update_grades_csv(nim, quiz=None, assignment=None, mid=None, final=None, fallback_name=""):
    """Memperbarui atau menambah data nilai ke grades.csv."""
    grd_path = DATA_DIR / "grades.csv"
    rows = read_csv(grd_path)
    found = False
    for r in rows:
        if r.get("student_id") == nim:
            if quiz is not None: r["quiz"] = str(float(quiz))
            if assignment is not None: r["assignment"] = str(float(assignment))
            if mid is not None: r["mid"] = str(float(mid))
            if final is not None: r["final"] = str(float(final))
            if not r.get("name"):
                r["name"] = fallback_name
            found = True
            break
    if not found:
        new_row = {
            "student_id": nim,
            "name": fallback_name,
            "quiz": str(float(quiz or 0)),
            "assignment": str(float(assignment or 0)),
            "mid": str(float(mid or 0)),
            "final": str(float(final or 0)),
        }
        rows.append(new_row)
    write_csv(grd_path, GRD_HEADERS, rows)
    return rows


# =========================================================
# Memuat data dari CSV ke dalam objek OOP
# =========================================================
def load_attendance_into_rekap(rekap, att_path):
    """Membaca attendance.csv dan mengisi ke objek RekapKelas."""
    rows = read_csv(att_path)
    for r in rows:
        nim = r.get("student_id")
        nama = r.get("name")
        if not nim or not nama:
            continue
        if nim not in rekap._data_by_nim:
            rekap.tambah_mahasiswa(Mahasiswa(nim, nama))
        persen = calculate_attendance_percent_from_row(r)
        rekap.ubah_hadir(nim, persen)


def load_grades_into_rekap(rekap, grd_path):
    """Membaca grades.csv dan mengisi nilai ke objek RekapKelas."""
    rows = read_csv(grd_path)
    for r in rows:
        nim = r.get("student_id")
        nama = r.get("name")
        if not nim:
            continue
        if nim not in rekap._data_by_nim:
            rekap.tambah_mahasiswa(Mahasiswa(nim, nama or nim))
        try:
            q = float(r.get("quiz", 0))
            a = float(r.get("assignment", 0))
            m = float(r.get("mid", 0))
            f = float(r.get("final", 0))
        except Exception:
            q = a = m = f = 0
        rekap.ubah_penilaian(nim, quiz=q, tugas=a, uts=m, uas=f)


# =========================================================
# Laporan dan tampilan tabel CLI
# =========================================================
def show_summary_rows(rows):
    """Menampilkan tabel rekap sederhana (rata kanan & sejajar)."""
    if not rows:
        print("\n(tidak ada data untuk ditampilkan)\n")
        return

    # Tentukan lebar kolom dinamis
    max_nama = max(len(str(r["nama"])) for r in rows)
    if max_nama < 10:
        max_nama = 10

    print(f"\n{'NIM':<10} | {'Nama':<{max_nama}} | Hadir% | Nilai | Pred")
    print("-" * (max_nama + 36))

    for r in rows:
        print(f"{r['nim']:<10} | {r['nama']:<{max_nama}} | {r['hadir']:>6.2f} | {r['akhir']:>6.2f} | {r['predikat']}")
    print()


def generate_and_save_report(rekap):
    """Membuat file report.md dan report.html di folder out/."""
    data = rekap.export_for_report()
    md = build_markdown_report(data)
    save_text(OUT_DIR / "report.md", md)
    html = build_html_report(data)
    save_text(OUT_DIR / "report.html", html)
    print("✅ Laporan berhasil dibuat di folder 'out'.")


# =========================================================
# Program utama CLI
# =========================================================
def main():
    """Fungsi utama CLI untuk menjalankan program Student Performance Tracker."""
    rekap = RekapKelas()

    att_path = DATA_DIR / "attendance.csv"
    grd_path = DATA_DIR / "grades.csv"

    if att_path.exists():
        load_attendance_into_rekap(rekap, att_path)
    if grd_path.exists():
        load_grades_into_rekap(rekap, grd_path)

    while True:
        print("\n=== Student Performance Tracker (versi PEMULA) ===")
        print("1) Muat ulang data CSV")
        print("2) Tambah mahasiswa")
        print("3) Ubah presensi")
        print("4) Ubah nilai")
        print("5) Lihat rekap")
        print("6) Simpan laporan (MD & HTML)")
        print("7) Keluar")
        pilihan = input("Pilih (1–7): ").strip()

        if pilihan == "1":
            if att_path.exists():
                load_attendance_into_rekap(rekap, att_path)
            if grd_path.exists():
                load_grades_into_rekap(rekap, grd_path)
            print("✅ Data CSV berhasil dimuat ulang.")

        elif pilihan == "2":
            nim = input("Masukkan NIM: ").strip()
            nama = input("Masukkan Nama: ").strip()
            if nim and nama:
                rekap.tambah_mahasiswa(Mahasiswa(nim, nama))
                print(f"✅ Mahasiswa {nama} berhasil ditambahkan.")
            else:
                print("❌ NIM dan Nama tidak boleh kosong.")

        elif pilihan == "3":
            nim = input("Masukkan NIM mahasiswa: ").strip()
            w = {}
            for i in range(1, 6):
                val = input(f"Week {i} (1 hadir, 0 tidak, kosong=skip): ").strip()
                w[f"week{i}"] = val if val in ("0", "1") else None
            try:
                rows = update_attendance_csv(nim, w)
                for r in rows:
                    if r["student_id"] == nim:
                        p = calculate_attendance_percent_from_row(r)
                        rekap.ubah_hadir(nim, p)
                        break
                print("✅ Presensi berhasil diperbarui.")
            except Exception as e:
                print("❌ Gagal:", e)

        elif pilihan == "4":
            nim = input("Masukkan NIM: ").strip()
            def ask(prompt):
                s = input(prompt).strip()
                return float(s) if s else None
            q = ask("Nilai Quiz: ")
            a = ask("Nilai Tugas: ")
            m = ask("Nilai UTS: ")
            f = ask("Nilai UAS: ")
            try:
                rekap.ubah_penilaian(nim, quiz=q, tugas=a, uts=m, uas=f)
                nm = rekap._data_by_nim[nim]["mhs"].nama if nim in rekap._data_by_nim else ""
                update_grades_csv(nim, q, a, m, f, nm)
                print("✅ Nilai berhasil diperbarui.")
            except Exception as e:
                print("❌ Gagal:", e)

        elif pilihan == "5":
            rows = rekap.rekap()
            print("1) Semua mahasiswa\n2) Hanya nilai akhir < 70")
            sub = input("Pilih (1/2): ").strip()
            if sub == "2":
                rows = [r for r in rows if r["akhir"] < 70]
            show_summary_rows(rows)

        elif pilihan == "6":
            generate_and_save_report(rekap)

        elif pilihan == "7":
            print("👋 Terima kasih sudah menggunakan aplikasi ini!")
            break

        else:
            print("❌ Pilihan tidak valid. Coba lagi.")


if __name__ == "__main__":
    main()
