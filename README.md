# Student Performance Tracker

Proyek ini adalah tugas kuliah untuk mata kuliah **Pemrograman Python**  
dengan materi **Integrasi OOP dan Modularisasi** menggunakan bahasa **Python**.  

Program ini dibuat untuk membantu dosen atau asisten dalam mencatat, menghitung, dan menampilkan **rekap nilai mahasiswa** secara sederhana melalui **CLI (Command Line Interface)**.

---

## 🎯 Tujuan
Menerapkan konsep:
- **Kelas dan Objek (OOP)**  
  Setiap mahasiswa direpresentasikan sebagai objek dengan atribut dan perilaku sendiri.
- **Modularisasi Program**  
  Setiap bagian program dipisah ke modul terpisah (`mahasiswa.py`, `penilaian.py`, dll) agar mudah dirawat.
- **Integrasi antar modul**  
  File `app.py` menghubungkan semua kelas dan modul untuk membentuk satu sistem lengkap.

---

## 🗂️ Struktur Folder

```
student_performance_tracker/
│
├── __pycache__/          
│
├── data/                 
│   ├── attendance.csv    
│   └── grades.csv        
│
├── out/                  
│   ├── report.md         
│   └── report.html
│
├── tracker/              
│   ├── __init__.py       
│   ├── __main__.py       
│   ├── mahasiswa.py      
│   ├── penilaian.py      
│   ├── rekap_kelas.py    
│   └── report.py         
│
├── app.py               
├── README.md             
└── requereiments.txt     

```

---


## 📘 Penjelasan Singkat Modul

**mahasiswa.py**	= Menyimpan data dasar mahasiswa (NIM, Nama, dan persentase kehadiran).

**penilaian.py**    = Mengatur nilai-nilai komponen (Quiz, Tugas, UTS, UAS) serta menghitung nilai akhir.

**rekap_kelas.py**	= Menggabungkan data mahasiswa dan penilaian ke dalam satu rekap kelas.

**report.py**	    =    Membuat laporan dalam format Markdown (.md) dan HTML berwarna.

**app.py**	= Program utama berbasis CLI yang menghubungkan semua modul.


---

## ⚙️ Cara Menjalankan Program

1. Buat Virtual Environtment 
   ```bash
   python -m venv .venv
   ```

2. Aktifkan Virtual Environtment
   ```bash
   .venv\Scripts\activate        # windows
   source .venv/bin/activate     # Linux / macOS
   ```

2. Jalankan program melalui terminal atau CMD:
   ```bash
   python app.py
   ```
   atau bisa juga lewat modul 
   ```bash
   python -m tracker
   ```
