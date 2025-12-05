# knapsack/analyzer.py
import time
from .models import Barang, SolusiKnapsack, PreferensiPengguna
from .strategies import StrategiPenyelesaian

class AnalisKnapsack:
    """
    Kelas utama yang mengorkestrasi proses analisis perbandingan.
    Versi ini terintegrasi penuh dengan model MCDA (Multi-Criteria Decision Analysis)
    dan menangani preferensi pengguna secara langsung.
    """
    def __init__(self, daftar_barang: list[Barang], budget: int, preferensi: PreferensiPengguna):
        """
        Inisialisasi analis dengan data, budget, dan preferensi pengguna.
        """
        self.daftar_barang = daftar_barang
        self.budget = budget
        self.preferensi = preferensi
        self._strategi_list: list[StrategiPenyelesaian] = []

    def tambah_strategi(self, strategi_class):
        """
        Mendaftarkan sebuah kelas strategi. Kelas akan diinisialisasi
        secara internal dengan preferensi pengguna yang ada.
        """
        # Inisialisasi kelas strategi dengan preferensi saat ditambahkan
        strategi_instance = strategi_class(self.preferensi)
        self._strategi_list.append(strategi_instance)

    def jalankan_analisis(self) -> list[SolusiKnapsack]:
        """
        Menjalankan semua strategi pada data.
        Langkah 1: Hitung skor untuk semua barang berdasarkan preferensi.
        Langkah 2: Saring barang yang tidak memenuhi skor minimal (>= 5).
        Langkah 3: Jalankan strategi pada barang yang layak.
        """
        # Langkah 1: Hitung skor untuk semua barang
        for item in self.daftar_barang:
            item.hitung_skor_nilai(self.preferensi)

        # Langkah 2: Saring barang dengan skor di bawah 5
        eligible_items = [item for item in self.daftar_barang if item.skor_nilai_total >= 5]
        
        # Langkah 3: Jalankan analisis pada barang yang layak
        daftar_solusi = []
        for strategi in self._strategi_list:
            start_time = time.perf_counter()
            
            # Panggil metode solve dari instance strategi dengan daftar barang yang sudah difilter
            barang_terpilih, total_skor_nilai, total_harga = strategi.solve(eligible_items, self.budget)
            
            end_time = time.perf_counter()
            waktu_eksekusi = end_time - start_time
            
            solusi = SolusiKnapsack(
                nama_strategi=strategi.get_nama(),
                barang_terpilih=barang_terpilih,
                total_skor_nilai=total_skor_nilai,
                total_harga=total_harga,
                waktu_eksekusi=waktu_eksekusi
            )
            daftar_solusi.append(solusi)
        return daftar_solusi
