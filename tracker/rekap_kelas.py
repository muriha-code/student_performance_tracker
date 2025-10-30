# Pengelola daftar mahasiswa dan nilai

from .mahasiswa import Mahasiswa
from .penilaian import Penilaian

class RekapKelas:
    """Kelas untuk menyimpan banyak mahasiswa beserta nilai mereka."""
    def __init__(self):
        # struktur internal sederhana: nim -> {'mhs': Mahasiswa, 'nilai': Penilaian}
        self._data_by_nim = {}

    def tambah_mahasiswa(self, mhs):
        """Tambah objek Mahasiswa baru. Validasi tipe sederhana."""
        if not isinstance(mhs, Mahasiswa):
            raise TypeError("tambah_mahasiswa membutuhkan objek Mahasiswa")
        if mhs.nim in self._data_by_nim:
            raise KeyError("NIM sudah terdaftar: " + str(mhs.nim))
        # buat entry baru dengan objek Penilaian kosong
        self._data_by_nim[mhs.nim] = {'mhs': mhs, 'nilai': Penilaian()}

    def ubah_hadir(self, nim, persen):
        """Ubah persen hadir mahasiswa berdasarkan NIM."""
        if nim not in self._data_by_nim:
            raise KeyError("NIM tidak ditemukan")
        # pakai property pada objek mahasiswa
        self._data_by_nim[nim]['mhs'].hadir_persen = persen

    def ubah_penilaian(self, nim, quiz=None, tugas=None, uts=None, uas=None):
        """Ubah komponen nilai (jika parameter None maka tidak diubah)."""
        if nim not in self._data_by_nim:
            raise KeyError("NIM tidak ditemukan")
        p = self._data_by_nim[nim]['nilai']
        if quiz is not None:
            p.quiz = quiz
        if tugas is not None:
            p.tugas = tugas
        if uts is not None:
            p.uts = uts
        if uas is not None:
            p.uas = uas

    def predikat(self, skor):
        """Konversi skor jadi huruf A..E (aturan tugas)."""
        if skor >= 85:
            return "A"
        if skor >= 75:
            return "B"
        if skor >= 65:
            return "C"
        if skor >= 50:
            return "D"
        return "E"

    def rekap(self):
        """Kembalikan list of dict yang mudah dipakai untuk tampilkan di CLI."""
        out = []
        # loop manual di semua mahasiswa
        for nim in self._data_by_nim:
            d = self._data_by_nim[nim]
            m = d['mhs']
            p = d['nilai']
            akhir = p.nilai_akhir()
            row = {
                'nim': nim,
                'nama': m.nama,
                'hadir': m.hadir_persen,
                'akhir': akhir,
                'predikat': self.predikat(akhir)
            }
            out.append(row)
        return out

    def export_for_report(self):
        """Bentuk data yang cocok untuk report builder (markdown/html)."""
        rows = []
        for nim in self._data_by_nim:
            d = self._data_by_nim[nim]
            m = d['mhs']
            p = d['nilai']
            rows.append({
                'student_id': nim,
                'name': m.nama,
                'attendance_rate': m.hadir_persen,
                'final_score': p.nilai_akhir()
            })
        return rows
