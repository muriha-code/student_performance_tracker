class Mahasiswa:
    """Kelas sederhana untuk menyimpan NIM, nama, dan persen hadir."""
    def __init__(self, nim, nama):
        # simpan langsung NIM dan nama
        self.nim = nim
        self.nama = nama
        # internal: simpan persen hadir di attribute private
        # default 0.0 (belum hadir sama sekali)
        self._persen_hadir = 0.0

    @property
    def hadir_persen(self):
        """Ambil nilai persen hadir (angka antara 0 sampai 100)."""
        return self._persen_hadir

    @hadir_persen.setter
    def hadir_persen(self, nilai):
        """Set persen hadir dengan validasi sederhana."""
        if nilai is None:
            raise ValueError("hadir_persen tidak boleh None")
        # pastikan bisa dikonversi ke float
        try:
            n = float(nilai)
        except Exception:
            raise ValueError("hadir_persen harus angka")
        if n < 0 or n > 100:
            raise ValueError("hadir_persen harus antara 0 dan 100")
        # simpan 2 desimal agar rapi
        self._persen_hadir = round(n, 2)

    def info(self):
        """Kembalikan string informasi singkat tentang mahasiswa."""
        return f"{self.nim} - {self.nama} (Hadir: {self._persen_hadir:.2f}%)"

    def __repr__(self):
        return f"<Mahasiswa {self.nim} {self.nama} hadir={self._persen_hadir:.2f}%>"
