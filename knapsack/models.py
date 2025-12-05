# knapsack/models.py
"""
Mendefinisikan model data inti untuk aplikasi analisis knapsack yang lebih canggih.
Model ini mencakup beberapa kriteria untuk penilaian barang dan preferensi pengguna.
"""
from dataclasses import dataclass

@dataclass
class PreferensiPengguna:
    """Menyimpan bobot preferensi yang ditentukan oleh pengguna."""
    bobot_urgensi: float = 0.5  # Contoh bobot default
    bobot_edukasi: float = 0.3
    bobot_kepuasan: float = 0.2

    def __post_init__(self):
        # Memastikan total bobot adalah 1.0 (100%)
        total = self.bobot_urgensi + self.bobot_edukasi + self.bobot_kepuasan
        if not (0.999 < total < 1.001):
            raise ValueError("Total bobot dari semua preferensi harus tepat 1.0 (atau 100%).")

class Barang:
    """
    Mewakili satu item dengan atribut multi-kriteria untuk analisis yang lebih mendalam.
    """
    KATEGORI_LIST = ['Kebutuhan', 'Investasi', 'Keinginan']

    def __init__(self, nama: str, harga: int, kategori: str, 
                 urgensi: int, nilai_edukasi: int, kepuasan_hedonis: int):
        
        if kategori not in self.KATEGORI_LIST:
            raise ValueError(f"Kategori tidak valid. Pilih dari: {self.KATEGORI_LIST}")

        self.nama = nama
        self.harga = harga
        self.kategori = kategori
        self.urgensi = urgensi                 # Skala 1-10
        self.nilai_edukasi = nilai_edukasi         # Skala 1-10
        self.kepuasan_hedonis = kepuasan_hedonis # Skala 1-10
        
        # Skor nilai akan dihitung nanti setelah preferensi pengguna diketahui
        self.skor_nilai_total = 0.0

    def hitung_skor_nilai(self, preferensi: PreferensiPengguna):
        """Menghitung skor nilai total berdasarkan preferensi pengguna."""
        self.skor_nilai_total = (
            (self.urgensi * preferensi.bobot_urgensi) +
            (self.nilai_edukasi * preferensi.bobot_edukasi) +
            (self.kepuasan_hedonis * preferensi.bobot_kepuasan)
        )

    def __repr__(self) -> str:
        return (f"Barang(nama='{self.nama}', harga={self.harga}, kategori='{self.kategori}', "
                f"skor_nilai={self.skor_nilai_total:.2f})")

@dataclass
class SolusiKnapsack:
    """Mewakili hasil dari sebuah strategi penyelesaian knapsack."""
    nama_strategi: str
    barang_terpilih: list[Barang]
    total_skor_nilai: float
    total_harga: int
    waktu_eksekusi: float