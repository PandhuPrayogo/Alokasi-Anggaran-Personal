# main.py
"""
File utama untuk aplikasi analisis Knapsack 'expert-level' berbasis CLI.

Aplikasi ini menerapkan model Multi-Criteria Decision Analysis (MCDA) untuk
memberikan rekomendasi budgeting yang lebih personal dan komprehensif bagi mahasiswa.
"""
import time
import matplotlib.pyplot as plt
import seaborn as sns
from knapsack.models import Barang, PreferensiPengguna, SolusiKnapsack
from knapsack.strategies import StrategiGreedy, StrategiDynamicProgramming
from knapsack.analyzer import AnalisKnapsack

# --- Fungsi-fungsi untuk Interaksi dan Visualisasi ---

def get_preferensi_pengguna() -> PreferensiPengguna:
    """Meminta dan memvalidasi input preferensi dari pengguna."""
    print("="*60)
    print("TAHAP 1: TENTUKAN PROFIL PRIORITAS ANDA")
    print("="*60)
    print("Alokasikan total 100 poin untuk 3 dimensi berikut:")
    
    while True:
        try:
            p_urgensi = int(input("  - Poin untuk Urgensi (seberapa mendesak): "))
            p_edukasi = int(input("  - Poin untuk Nilai Edukasi/Karir: "))
            p_kepuasan = int(input("  - Poin untuk Kepuasan Jangka Pendek: "))

            if p_urgensi < 0 or p_edukasi < 0 or p_kepuasan < 0:
                print("Poin tidak boleh negatif. Coba lagi.")
                continue

            total_poin = p_urgensi + p_edukasi + p_kepuasan
            if total_poin != 100:
                print(f"Total poin Anda adalah {total_poin}, harus tepat 100. Silakan ulangi.")
                continue
            
            return PreferensiPengguna(
                bobot_urgensi=p_urgensi / 100.0,
                bobot_edukasi=p_edukasi / 100.0,
                bobot_kepuasan=p_kepuasan / 100.0
            )
        except ValueError:
            print("Input tidak valid. Masukkan hanya angka.")

def get_user_input_barang() -> tuple[int, list[Barang]]:
    """Meminta dan memvalidasi input data barang dari pengguna."""
    print("\n" + "="*60)
    print("TAHAP 2: MASUKKAN DATA KEBUTUHAN & KEINGINAN")
    print("="*60)
    
    budget = _get_int_input("Masukkan total anggaran (budget): ", min_val=1)
    jumlah_barang = _get_int_input("Berapa banyak barang yang ingin Anda analisis? ", min_val=1)
    
    items = []
    for i in range(1, jumlah_barang + 1):
        print(f"\n--- Barang #{i}/{jumlah_barang} ---")
        nama = input("Nama barang: ")
        harga = _get_int_input(f"Harga '{nama}': ", min_val=1)
        
        print("Pilih Kategori:")
        for idx, kat in enumerate(Barang.KATEGORI_LIST, 1):
            print(f"  {idx}. {kat}")
        kat_idx = _get_int_input("Pilihan Kategori (angka): ", 1, len(Barang.KATEGORI_LIST))
        kategori = Barang.KATEGORI_LIST[kat_idx - 1]

        print("\nBeri nilai dari 1 (sangat rendah) hingga 10 (sangat tinggi):")
        urgensi = _get_int_input("  - Seberapa URGENT barang ini? (1-10): ", 1, 10)
        edukasi = _get_int_input("  - Apa NILAI EDUKASI/KARIR-nya? (1-10): ", 1, 10)
        kepuasan = _get_int_input("  - Apa tingkat KEPUASAN JANGKA PENDEK-nya? (1-10): ", 1, 10)
        
        items.append(Barang(nama, harga, kategori, urgensi, edukasi, kepuasan))
    
    return budget, items

def _get_int_input(prompt: str, min_val: int = None, max_val: int = None) -> int:
    """Helper untuk mengambil input integer yang tervalidasi."""
    while True:
        try:
            val = int(input(prompt))
            if min_val is not None and val < min_val:
                print(f"Input harus lebih besar atau sama dengan {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"Input harus lebih kecil atau sama dengan {max_val}.")
                continue
            return val
        except ValueError:
            print("Input tidak valid. Masukkan hanya angka.")

def print_results_table(solutions: list[SolusiKnapsack]):
    """Mencetak tabel ringkasan hasil percobaan dari semua strategi."""
    print("\n" + "="*80)
    print("HASIL PERCOBAAN (EXPERIMENTAL RESULTS)".center(80))
    print("="*80)
    
    header = (f"{'Metode Penyelesaian':<25} | {'Total Skor Nilai':>18} | {'Total Harga':>12} | {'Waktu (ms)':>12}")
    print(header)
    print("-" * len(header))

    for s in solutions:
        print(f"{s.nama_strategi:<25} | {s.total_skor_nilai:>18.2f} | {s.total_harga:>12} | {s.waktu_eksekusi * 1000:>12.4f}")
    print("="*80)


def print_shopping_priority_list(all_items: list[Barang], solution: SolusiKnapsack, title: str):
    """Mencetak daftar rekomendasi belanja berdasarkan solusi yang diberikan."""
    print("\n" + "="*80)
    print(title.upper())
    print("="*80)

    bought_item_names = {item.nama for item in solution.barang_terpilih}
    recommendations = []
    for item in all_items:
        # Tentukan status berdasarkan skor dan apakah barang dipilih
        if item.skor_nilai_total < 5:
            status = "❌ DITOLAK"
        elif item.nama in bought_item_names:
            status = "✅ DIBELI"
        else:
            status = "❌ DILEWATI"
            
        recommendations.append({
            "item": item,
            "status": status
        })

    # Urutkan berdasarkan status (dibeli dulu) lalu skor nilai tertinggi
    recommendations.sort(key=lambda x: (x['status'], -x['item'].skor_nilai_total), reverse=True)
    
    print(f"{'Status':<15} | {'Nama Barang':<25} | {'Kategori':<12} | {'Skor Nilai':>12}")
    print("-" * 80)

    for rec in recommendations:
        item = rec['item']
        print(f"{rec['status']:<15} | {item.nama:<25} | {item.kategori:<12} | {item.skor_nilai_total:>12.2f}")

def visualize_results(solutions: list[SolusiKnapsack]):
    """Membuat dan menampilkan visualisasi perbandingan hasil dari berbagai strategi."""
    sns.set_theme(style="whitegrid")
    labels = [s.nama_strategi for s in solutions]
    score_values = [s.total_skor_nilai for s in solutions]
    
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    fig.suptitle('Visualisasi Perbandingan Algoritma', fontsize=16)

    colors = ['#ffc107', '#198754']  # Kuning untuk Greedy, Hijau untuk DP (Optimal)
    bars = ax.bar(labels, score_values, color=colors)
    ax.set_title('Perbandingan Total Skor Nilai', fontsize=12)
    ax.set_ylabel('Total Skor Nilai (berdasarkan preferensi Anda)')
    ax.bar_label(bars, fmt='%.2f')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    print("\nMenampilkan jendela visualisasi...")
    plt.show()

def print_analysis_report():
    """Mencetak laporan analisis teknis algoritma dan proposal."""
    print("\n" + "="*80)
    print("ANALISIS ALGORITMA & PROPOSAL".center(80))
    print("="*80)
    
    # --- Analisis Greedy ---
    print("\n1. Metode Penyelesaian: Greedy")
    print("   - Deskripsi: Algoritma ini bekerja dengan cara yang 'rakus', yaitu selalu memilih")
    print("     barang dengan rasio 'skor nilai / harga' tertinggi terlebih dahulu, hingga")
    print("     budget tidak lagi mencukupi.")
    print("   - Analisis Kompleksitas: O(N log N), di mana N adalah jumlah barang.")
    print("     Kompleksitas ini didominasi oleh proses pengurutan (sorting) barang")
    print("     berdasarkan rasio nilai/harganya.")
    print("   - Kelebihan: Sangat cepat dan memberikan solusi yang 'cukup baik' dan intuitif.")
    
    # --- Analisis Dynamic Programming ---
    print("\n2. Metode Penyelesaian: Dynamic Programming (DP)")
    print("   - Deskripsi: Algoritma ini membangun sebuah tabel untuk mengevaluasi semua")
    print("     kemungkinan kombinasi barang yang muat dalam budget, dan memilih kombinasi")
    print("     yang memberikan total skor nilai paling maksimal.")
    print("   - Analisis Kompleksitas: O(N * W), di mana N adalah jumlah barang dan W")
    print("     adalah kapasitas budget.")
    print("   - Kelebihan: Dijamin menemukan solusi paling optimal secara absolut.")
    print("   - Kelemahan: Bisa menjadi sangat lambat jika budget (W) sangat besar.")

    # --- Proposal ---
    print("\n" + "-"*80)
    print("PROPOSAL ALGORITMA".center(80))
    print("-" * 80)
    print("-> Gunakan 'Dynamic Programming' untuk mendapatkan 'Kombinasi Optimal' barang")
    print("   jika tujuan Anda adalah memaksimalkan total nilai dari keseluruhan pembelian.")
    print("   Ini adalah proposal utama untuk hasil akhir terbaik.")
    print("\n-> Gunakan 'Greedy' jika Anda membutuhkan keputusan yang cepat atau jika Anda")
    print("   membeli barang secara bertahap. Daftar 'Value for Money'-nya adalah panduan")
    print("   prioritas yang sangat baik untuk setiap pembelian individu.")
    print("="*80)


def main():
    """Fungsi utama untuk menjalankan keseluruhan aplikasi CLI."""
    # Pastikan library yang dibutuhkan terinstal: pip install matplotlib seaborn
    
    preferensi = get_preferensi_pengguna()
    budget, items = get_user_input_barang()

    if not items:
        print("Tidak ada barang untuk dianalisis. Program berhenti.")
        return

    # Gunakan AnalisKnapsack yang sudah bersih dan terpusat
    analis = AnalisKnapsack(items, budget, preferensi)
    analis.tambah_strategi(StrategiGreedy)
    analis.tambah_strategi(StrategiDynamicProgramming)
    
    hasil_semua_strategi = analis.jalankan_analisis()
    
    greedy_solution = next((s for s in hasil_semua_strategi if s.nama_strategi == 'Greedy'), None)
    dp_solution = next((s for s in hasil_semua_strategi if s.nama_strategi == 'DynamicProgramming'), None)

    if greedy_solution:
        title = "Rekomendasi Berdasarkan 'Value for Money' (Strategi Greedy)"
        print_shopping_priority_list(items, greedy_solution, title)

    if dp_solution:
        title = "Kombinasi Optimal untuk Skor Nilai Maksimal (Strategi Dynamic Programming)"
        print_shopping_priority_list(items, dp_solution, title)

    if hasil_semua_strategi:
        print("\n\n" + "#"*80)
        print(" LAPORAN AKHIR ANALISIS ".center(80, '#'))
        print("#"*80)

        # 1. Tampilkan tabel hasil percobaan kuantitatif
        print_results_table(hasil_semua_strategi)

        # 2. Tampilkan analisis teknis algoritma dan proposal
        print_analysis_report()

        # 3. Tampilkan visualisasi sebagai ringkasan grafis
        visualize_results(hasil_semua_strategi)
    
    print("\nAnalisis selesai. Program ditutup.")

if __name__ == '__main__':
    main()