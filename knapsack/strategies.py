# knapsack/strategies.py
"""
Mengimplementasikan berbagai strategi algoritma untuk menyelesaikan 0/1 Knapsack Problem.
Versi ini disesuaikan untuk bekerja dengan model 'skor nilai' yang dihitung,
bukan nilai kepuasan sederhana.
"""
from abc import ABC, abstractmethod
from .models import Barang, PreferensiPengguna

class StrategiPenyelesaian(ABC):
    """Kelas abstrak (interface) untuk semua strategi penyelesaian Knapsack."""
    
    def __init__(self, preferensi: PreferensiPengguna):
        self.preferensi = preferensi

    def _hitung_semua_skor(self, daftar_barang: list[Barang]):
        """Helper untuk menghitung skor untuk semua barang sebelum analisis."""
        for item in daftar_barang:
            item.hitung_skor_nilai(self.preferensi)

    @abstractmethod
    def solve(self, daftar_barang: list[Barang], budget: int) -> tuple[list[Barang], float, int]:
        """
        Metode utama untuk menjalankan algoritma.
        Harus mengembalikan: (barang_terpilih, total_skor_nilai, total_harga)
        """
        pass

    def get_nama(self) -> str:
        """Mengembalikan nama strategi dari nama kelasnya."""
        return self.__class__.__name__.replace("Strategi", "")


class StrategiGreedy(StrategiPenyelesaian):
    """
    Implementasi Knapsack menggunakan pendekatan Greedy.
    Kriteria 'greedy' sekarang adalah rasio skor_nilai / harga.
    """
    def solve(self, daftar_barang: list[Barang], budget: int) -> tuple[list[Barang], float, int]:
        # Hitung rasio (nilai/harga) untuk setiap barang tanpa mengubah objek aslinya.
        # Buat daftar sementara berisi (rasio, barang) untuk diurutkan.
        barang_dengan_rasio = []
        for item in daftar_barang:
            rasio = item.skor_nilai_total / item.harga if item.harga > 0 else float('inf')
            barang_dengan_rasio.append((rasio, item))

        # Urutkan daftar berdasarkan rasio (elemen pertama dari tuple) secara menurun.
        barang_urut = sorted(barang_dengan_rasio, key=lambda x: x[0], reverse=True)
        
        total_skor_nilai = 0.0
        total_harga = 0
        keranjang = []

        # Iterasi melalui daftar yang sudah diurutkan (isinya tuple)
        for rasio, item in barang_urut:
            if total_harga + item.harga <= budget:
                keranjang.append(item)
                total_skor_nilai += item.skor_nilai_total
                total_harga += item.harga
                
        return keranjang, total_skor_nilai, total_harga


class StrategiDynamicProgramming(StrategiPenyelesaian):
    """
    Implementasi Knapsack menggunakan Dynamic Programming untuk solusi optimal.
    Menggunakan 'skor_nilai_total' sebagai 'value' dalam tabel DP.
    """
    def solve(self, daftar_barang: list[Barang], budget: int) -> tuple[list[Barang], float, int]:
        n = len(daftar_barang)
        # Tabel DP sekarang menyimpan float (skor nilai), bukan integer
        dp = [[0.0 for _ in range(budget + 1)] for _ in range(n + 1)]

        for i in range(1, n + 1):
            item = daftar_barang[i-1]
            for w in range(budget + 1):
                if item.harga <= w:
                    # Pilih antara memasukkan item atau tidak
                    dp[i][w] = max(item.skor_nilai_total + dp[i-1][w-item.harga], dp[i-1][w])
                else:
                    dp[i][w] = dp[i-1][w]
        
        max_skor_nilai = dp[n][budget]
        keranjang = []
        w = budget
        for i in range(n, 0, -1):
            # Gunakan toleransi float untuk perbandingan
            if not (abs(dp[i][w] - dp[i-1][w]) < 1e-9):
                item = daftar_barang[i-1]
                keranjang.append(item)
                w -= item.harga
                
        total_harga = sum(item.harga for item in keranjang)
        return keranjang, max_skor_nilai, total_harga