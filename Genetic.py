import random
import copy
import time
from Container import SolusiPacking

class GeneticAlgoritma:
    def __init__(self, kapasitas_kontainer, daftar_barang, 
                 pop_size=100, mutation_rate=0.1, tournament_size=5,
                 max_generasi=500, elitism_count=1):
        
        self.kapasitas_kontainer = kapasitas_kontainer
        self.daftar_barang = daftar_barang
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        self.max_generasi = max_generasi
        self.elitism_count = elitism_count # Jumlah individu terbaik yg langsung lolos
        
        self.populasi = []
        self.hist_skor_terbaik = []
        self.hist_skor_rata2 = []
        self.hist_generasi = []
        
        # Simpan ID barang untuk validasi
        self.semua_barang_id = set(b['id'] for b in self.daftar_barang)
        self.ukuran_barang = {b['id']: b['ukuran'] for b in self.daftar_barang}

    def _inisialisasi_first_fit_decreasing(self):
        """
        Inisialisasi individu menggunakan heuristik First Fit Decreasing (FFD).
        Ini adalah inisialisasi yang 'lebih baik' seperti permintaan Anda.
        """
        individu = SolusiPacking(self.kapasitas_kontainer, self.daftar_barang)
        
        # Urutkan barang berdasarkan ukuran, dari besar ke kecil
        barang_terurut = sorted(self.daftar_barang, key=lambda x: x['ukuran'], reverse=True)
        
        state = []
        
        for item in barang_terurut:
            item_id = item['id']
            item_ukuran = item['ukuran']
            
            ditempatkan = False
            
            # 1. Coba masukkan ke kontainer yang ada
            for kontainer in state:
                total_kontainer = individu.hitung_total_ukuran(kontainer)
                if total_kontainer + item_ukuran <= self.kapasitas:
                    kontainer.append(item_id)
                    ditempatkan = True
                    break
            
            # 2. Jika tidak muat, buat kontainer baru
            if not ditempatkan:
                state.append([item_id])
                
        individu.state = state
        return individu

    def _inisialisasi_populasi(self):
        """Membuat populasi awal menggunakan FFD."""
        self.populasi = []
        for _ in range(self.pop_size):
            # Gunakan FFD untuk membuat individu awal yang bagus
            # Kita bisa tambahkan sedikit 'noise' jika ingin variasi
            individu = self._inisialisasi_first_fit_decreasing()
            
            # Opsional: Tambah sedikit mutasi awal agar populasi bervariasi
            if random.random() < 0.5: # 50% kemungkinan mutasi awal
                 self._mutasi(individu, num_mutations=max(1, int(len(self.daftar_barang) * 0.05)))
            
            self.populasi.append(individu)

    def _hitung_fitness(self, individu):
        """
        Menghitung fitness. Skor lebih rendah = fitness lebih tinggi.
        """
        skor = individu.objective_function()
        
        # Balikkan skor jadi fitness (karena kita minimasi)
        if skor == 0:
            return float('inf') # Solusi sempurna
        return 1 / skor

    def _seleksi(self):
        """
        Seleksi menggunakan Tournament Selection.
        """
        # Pilih k individu secara acak
        turnamen = random.sample(self.populasi, self.tournament_size)
        
        # Pilih yang terbaik (fitness tertinggi / skor terendah)
        pemenang = min(turnamen, key=lambda x: x.objective_function())
        
        return pemenang

    def _crossover(self, parent1, parent2):
        """
        Crossover khusus untuk Bin Packing (Order-based Crossover).
        Ini adalah implementasi yang lebih baik daripada yang saya tunjukkan sebelumnya.
        """
        child = SolusiPacking(self.kapasitas_kontainer, self.daftar_barang)
        
        # 1. Ambil subset kontainer dari parent 1
        state1 = parent1.state
        start, end = sorted(random.sample(range(len(state1)), 2))
        
        child_state_partial = [copy.deepcopy(kont) for kont in state1[start:end]]
        barang_sudah_ada = set(item for kont in child_state_partial for item in kont)
        
        # 2. Ambil barang yang BELUM ADA dari parent 2, sesuai urutan
        barang_hilang = []
        for kontainer in parent2.state:
            for item_id in kontainer:
                if item_id not in barang_sudah_ada:
                    barang_hilang.append(item_id)
        
        # 3. Masukkan barang hilang ke child menggunakan FFD
        #    Kita masukkan ke kontainer parsial dari Parent 1 terlebih dahulu
        
        state_final = child_state_partial
        
        for item_id in barang_hilang:
            item_ukuran = self.ukuran_barang[item_id]
            ditempatkan = False
            
            # Coba masukkan ke kontainer yang ada
            for kontainer in state_final:
                total_kontainer = child.hitung_total_ukuran(kontainer)
                if total_kontainer + item_ukuran <= self.kapasitas:
                    kontainer.append(item_id)
                    ditempatkan = True
                    break
            
            # Jika tidak muat, buat kontainer baru
            if not ditempatkan:
                state_final.append([item_id])
                
        child.state = [k for k in state_final if k] # Hapus kontainer kosong
        
        # Cek validasi (darurat jika ada bug crossover)
        barang_di_child = set(item for kont in child.state for item in kont)
        if barang_di_child != self.semua_barang_id:
             # Jika gagal, kembalikan saja parent1 (lebih aman)
             return copy.deepcopy(parent1)

        return child


    def _mutasi(self, individu, num_mutations=1):
        """
        Mutasi menggunakan 'move' yang didefinisikan di spesifikasi.
        """
        for _ in range(num_mutations):
            if random.random() > self.mutation_rate:
                continue # Tidak jadi mutasi
            
            # Pilih salah satu move (sesuai spesifikasi)
            move_type = random.choice(['pindah', 'tukar'])
            
            if move_type == 'pindah' and len(individu.state) > 0:
                # 1. Pindah barang
                try:
                    idx_kont_asal = random.randint(0, len(individu.state) - 1)
                    if not individu.state[idx_kont_asal]:
                        continue
                    
                    item_pindah = random.choice(individu.state[idx_kont_asal])
                    
                    # Pindah ke kontainer baru (idx = len) atau kontainer lama
                    idx_kont_tujuan = random.randint(0, len(individu.state))
                    
                    individu.pindah_barang(item_pindah, idx_kont_tujuan)
                except:
                    continue # Error acak (misal: list kosong)
                
            elif move_type == 'tukar' and len(individu.state) >= 2:
                # 2. Tukar barang
                try:
                    idx1 = random.randint(0, len(individu.state) - 1)
                    idx2 = random.randint(0, len(individu.state) - 1)
                    
                    if idx1 == idx2 or not individu.state[idx1] or not individu.state[idx2]:
                        continue # kontainer sama atau kosong
                    
                    item1 = random.choice(individu.state[idx1])
                    item2 = random.choice(individu.state[idx2])
                    
                    individu.tukar_barang(item1, item2)
                except:
                    continue # Error acak


    def run(self):
        start_time = time.time()
        
        print("\n" + "="*70)
        print("GENETIC ALGORITHM")
        print("="*70)
        print(f"\nParameter:")
        print(f"  Jumlah Populasi: {self.pop_size}")
        print(f"  Max Generasi: {self.max_generasi}")
        print(f"  Mutation Rate: {self.mutation_rate}")
        print(f"  Elitism: {self.elitism_count}")
        print("\nMembuat populasi awal (FFD)...")
        
        self._inisialisasi_populasi()
        
        solusi_awal = min(self.populasi, key=lambda x: x.objective_function())
        skor_awal = solusi_awal.objective_function()
        
        # Simpan statistik awal
        skor_saat_ini = [ind.objective_function() for ind in self.populasi]
        skor_terbaik_gen = min(skor_saat_ini)
        skor_rata2_gen = sum(skor_saat_ini) / len(skor_saat_ini)
        self.hist_skor_terbaik.append(skor_terbaik_gen)
        self.hist_skor_rata2.append(skor_rata2_gen)
        self.hist_generasi.append(0)

        print(f"Skor terbaik awal: {skor_awal:.2f} | Rata-rata awal: {skor_rata2_gen:.2f}")
        print("\nMemulai evolusi...\n")
        
        for gen in range(1, self.max_generasi + 1):
            populasi_baru = []
            
            # Elitisme: pertahankan individu terbaik
            sorted_pop = sorted(self.populasi, key=lambda x: x.objective_function())
            populasi_baru.extend(copy.deepcopy(sorted_pop[:self.elitism_count]))
            
            # Loop untuk buat sisa populasi
            while len(populasi_baru) < self.pop_size:
                # 1. Seleksi
                parent1 = self._seleksi()
                parent2 = self._seleksi()
                
                # 2. Crossover
                child = self._crossover(parent1, parent2)
                
                # 3. Mutasi
                self._mutasi(child)
                
                populasi_baru.append(child)
            
            self.populasi = populasi_baru
            
            # Catat statistik
            skor_saat_ini = [ind.objective_function() for ind in self.populasi]
            skor_terbaik_gen = min(skor_saat_ini)
            skor_rata2_gen = sum(skor_saat_ini) / len(skor_saat_ini)
            
            self.hist_skor_terbaik.append(skor_terbaik_gen)
            self.hist_skor_rata2.append(skor_rata2_gen)
            self.hist_generasi.append(gen)
            
            if gen % 100 == 0 or gen == self.max_generasi:
                print(f"Generasi {gen}/{self.max_generasi} | Terbaik: {skor_terbaik_gen:.2f} | Rata-rata: {skor_rata2_gen:.2f}")

        end_time = time.time()
        durasi = end_time - start_time
        
        solusi_akhir = min(self.populasi, key=lambda x: x.objective_function())
        skor_akhir = solusi_akhir.objective_function()
        
        improvement = skor_awal - skor_akhir
        pct = (improvement / skor_awal * 100) if skor_awal != 0 else 0

        print("\n" + "="*70)
        print("HASIL AKHIR GENETIC ALGORITHM")
        print("="*70)
        print(f"\nState Akhir (Terbaik):")
        print(f"  Objective Function: {skor_akhir}")
        print(f"  Jumlah Kontainer: {len(solusi_akhir.state)}")
        print(f"\nStatistik:")
        print(f"  Skor Awal (Terbaik): {skor_awal}")
        print(f"  Skor Akhir (Terbaik): {skor_akhir}")
        print(f"  Peningkatan: {improvement} ({pct:.2f}%)")
        print(f"  Total Generasi: {self.max_generasi}")
        print(f"  Durasi: {durasi:.4f} detik")
        print("="*70 + "\n")
        
        stats = {
            'solusi_awal': solusi_awal,
            'solusi_akhir': solusi_akhir,
            'skor_awal': skor_awal,
            'skor_akhir': skor_akhir,
            'peningkatan': improvement,
            'persentase_peningkatan': pct,
            'total_generasi': self.max_generasi,
            'durasi': durasi,
            'pop_size': self.pop_size,
            'mutation_rate': self.mutation_rate,
            'history_skor_terbaik': self.hist_skor_terbaik,
            'history_skor_rata2': self.hist_skor_rata2,
            'history_generasi': self.hist_generasi,
            'kapasitas_kontainer': self.kapasitas_kontainer
        }
        
        return solusi_akhir, stats