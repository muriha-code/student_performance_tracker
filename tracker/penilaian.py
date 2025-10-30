class Penilaian:
    """Simpan quiz, tugas, uts, uas dan hitung nilai akhir."""
    def __init__(self, quiz=0, tugas=0, uts=0, uas=0):
        # inisialisasi private attribute
        self._quiz = 0.0
        self._tugas = 0.0
        self._uts = 0.0
        self._uas = 0.0

        # set melalui property agar tervalidasi
        self.quiz = quiz
        self.tugas = tugas
        self.uts = uts
        self.uas = uas

    def _validate(self, v):
        """Validasi nilai: harus angka dan 0..100."""
        if v is None:
            raise ValueError("nilai tidak boleh None")
        try:
            x = float(v)
        except Exception:
            raise ValueError("nilai harus angka")
        if x < 0 or x > 100:
            raise ValueError("nilai harus antara 0 dan 100")
        return round(x, 2)

    @property
    def quiz(self):
        return self._quiz

    @quiz.setter
    def quiz(self, v):
        self._quiz = self._validate(v)

    @property
    def tugas(self):
        return self._tugas

    @tugas.setter
    def tugas(self, v):
        self._tugas = self._validate(v)

    @property
    def uts(self):
        return self._uts

    @uts.setter
    def uts(self, v):
        self._uts = self._validate(v)

    @property
    def uas(self):
        return self._uas

    @uas.setter
    def uas(self, v):
        self._uas = self._validate(v)

    def nilai_akhir(self, w_quiz=0.15, w_tugas=0.25, w_uts=0.25, w_uas=0.35):
        """
        Hitung nilai akhir dengan bobot default:
        quiz 15%, tugas 25%, uts 25%, uas 35%.
        """
        total = (self.quiz * w_quiz) + (self.tugas * w_tugas) + (self.uts * w_uts) + (self.uas * w_uas)
        return round(total, 2)

    def __repr__(self):
        return f"<Penilaian quiz={self.quiz} tugas={self.tugas} uts={self.uts} uas={self.uas}>"
