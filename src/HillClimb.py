import copy
import time

class HillClimbAlgoritma:
    def __init__(self, solusi_awal, max_sideways_moves=100):
        self.solusi_awal = solusi_awal
        self.max_sideways_moves = max_sideways_moves

    def _cari_tetangga_terbaik(self, solusi_sekarang):
        tetangga_terbaik = None
        skor_terbaik = solusi_sekarang.objective_function()
        semua_barang = [item_id for kontainer in solusi_sekarang.state for item_id in kontainer]

        for id_barang in semua_barang:
            for idx_tujuan in range(len(solusi_sekarang.state) + 1):
                tetangga_baru = copy.deepcopy(solusi_sekarang)
                tetangga_baru.pindah_barang(id_barang, idx_tujuan)
                
                skor_baru = tetangga_baru.objective_function()
                if skor_baru <= skor_terbaik:
                    skor_terbaik = skor_baru
                    tetangga_terbaik = tetangga_baru
        
        for i in range(len(semua_barang)):
            for j in range(i + 1, len(semua_barang)):
                id_barang_1 = semua_barang[i]
                id_barang_2 = semua_barang[j]

                tetangga_baru = copy.deepcopy(solusi_sekarang)
                tetangga_baru.tukar_barang(id_barang_1, id_barang_2)

                skor_baru = tetangga_baru.objective_function()
                if skor_baru <= skor_terbaik:
                    skor_terbaik = skor_baru
                    tetangga_terbaik = tetangga_baru
        
        return tetangga_terbaik, skor_terbaik

    def run(self):
        waktu_mulai = time.time()
        solusi_awal_copy = copy.deepcopy(self.solusi_awal)
        skor_awal = solusi_awal_copy.objective_function()
        
        solusi_sekarang = copy.deepcopy(self.solusi_awal)
        skor_sekarang = skor_awal
        
        history_skor = [skor_awal]
        history_iterasi = [0]
        sideways_count = 0
        langkah = 0

        print("="*70)
        print("HILL CLIMBING ALGORITHM")
        print("="*70)
        print(f"\nState Awal:")
        print(f"  Objective Function: {skor_awal}")
        print(f"  Jumlah Kontainer: {len(solusi_awal_copy.state)}")
        print(f"  Max Sideways Moves: {self.max_sideways_moves}")
        print("\n" + "-"*70)
        print(f"{'ITERASI':<10} {'AKSI':<30} {'SKOR':<15} {'SIDEWAYS':<15}")
        print("-"*70)

        while True:
            langkah += 1
            tetangga_terbaik, skor_terbaik = self._cari_tetangga_terbaik(solusi_sekarang)

            if tetangga_terbaik is None:
                print(f"{langkah:<10} {'Tidak ada tetangga':<30} {skor_sekarang:<15} {sideways_count}/{self.max_sideways_moves}")
                print("\nTidak ada tetangga lebih baik. Berhenti.")
                break

            if skor_terbaik < skor_sekarang:
                solusi_sekarang = tetangga_terbaik
                skor_sekarang = skor_terbaik
                sideways_count = 0
                history_skor.append(skor_sekarang)
                history_iterasi.append(langkah)
                print(f"{langkah:<10} {'Pindah (better)':<30} {skor_sekarang:<15} {sideways_count}/{self.max_sideways_moves}")
                
            elif skor_terbaik == skor_sekarang and sideways_count < self.max_sideways_moves:
                solusi_sekarang = tetangga_terbaik
                sideways_count += 1
                history_skor.append(skor_sekarang)
                history_iterasi.append(langkah)
                print(f"{langkah:<10} {'Sideways move':<30} {skor_sekarang:<15} {sideways_count}/{self.max_sideways_moves}")
                
            else:
                print(f"{langkah:<10} {'Batas tercapai':<30} {skor_sekarang:<15} {sideways_count}/{self.max_sideways_moves}")
                print("\nBatas sideways tercapai. Berhenti.")
                break
        
        waktu_selesai = time.time()
        durasi = waktu_selesai - waktu_mulai
        skor_akhir = solusi_sekarang.objective_function()
        
        print("\n" + "="*70)
        print("HASIL AKHIR")
        print("="*70)
        print(f"\nState Akhir:")
        print(f"  Objective Function: {skor_akhir}")
        print(f"  Jumlah Kontainer: {len(solusi_sekarang.state)}")
        print(f"\nStatistik:")
        print(f"  Skor Awal: {skor_awal}")
        print(f"  Skor Akhir: {skor_akhir}")
        print(f"  Peningkatan: {skor_awal - skor_akhir} ({((skor_awal - skor_akhir) / skor_awal * 100):.2f}%)")
        print(f"  Total Iterasi: {langkah}")
        print(f"  Durasi: {durasi:.4f} detik")
        print(f"  Sideways Moves: {sideways_count}/{self.max_sideways_moves}")
        print("="*70 + "\n")
        
        hasil_statistik = {
            'solusi_awal': solusi_awal_copy,
            'solusi_akhir': solusi_sekarang,
            'skor_awal': skor_awal,
            'skor_akhir': skor_akhir,
            'peningkatan': skor_awal - skor_akhir,
            'persentase_peningkatan': ((skor_awal - skor_akhir) / skor_awal * 100) if skor_awal != 0 else 0,
            'total_iterasi': langkah,
            'durasi': durasi,
            'sideways_count': sideways_count,
            'max_sideways_moves': self.max_sideways_moves,
            'history_skor': history_skor,
            'history_iterasi': history_iterasi
        }
        
        return solusi_sekarang, hasil_statistik