import random
import copy
import time
from Container import SolusiPacking

class GeneticAlgoritma:
    def __init__(self, kapasitas_kontainer, daftar_barang, 
                 pop_size=100, mutation_rate=0.1,
                 max_generasi=500, elitism_count=2):
        
        self.kapasitas_kontainer = kapasitas_kontainer
        self.daftar_barang = daftar_barang
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.max_generasi = max_generasi
        self.elitism_count = elitism_count  # Jumlah individu terbaik yang dipertahankan
        
        self.populasi = []
        self.hist_skor_terbaik = []
        self.hist_skor_rata2 = []
        self.hist_generasi = []
        
        # Simpan ID barang untuk validasi
        self.semua_barang_id = set(b['id'] for b in self.daftar_barang)
        self.ukuran_barang = {b['id']: b['ukuran'] for b in self.daftar_barang}



    def _inisialisasi_populasi(self):
        self.populasi = []
        
        print(f"  Membuat {self.pop_size} individu dengan inisialisasi random...")
        
        for _ in range(self.pop_size):
            individu = SolusiPacking(self.kapasitas_kontainer, self.daftar_barang)
            individu.inisialisasi_random()
            self.populasi.append(individu)

    def _hitung_fitness(self, individu):
        skor = individu.objective_function()
        if skor == 0:
            return float('inf')
        return 1 / skor

    def _seleksi_roulette(self):
        fitness_list = [self._hitung_fitness(ind) for ind in self.populasi]
        total_fitness = sum(fitness_list)
        
        if total_fitness == 0 or total_fitness == float('inf'):
            return random.choice(self.populasi)
        
        prob_kumulatif = []
        kumulatif = 0
        for fitness in fitness_list:
            kumulatif += fitness / total_fitness
            prob_kumulatif.append(kumulatif)
        
        r = random.random()
        
        for i, prob in enumerate(prob_kumulatif):
            if r <= prob:
                return self.populasi[i]
        
        return self.populasi[-1]

    def _crossover(self, parent1, parent2):
        child = SolusiPacking(self.kapasitas_kontainer, self.daftar_barang)
        
        state1 = parent1.state
        start, end = sorted(random.sample(range(len(state1)), 2))
        
        child_partial = [copy.deepcopy(k) for k in state1[start:end]]
        items_exist = set(item for k in child_partial for item in k)
        
        items_missing = []
        for kontainer in parent2.state:
            for item_id in kontainer:
                if item_id not in items_exist:
                    items_missing.append(item_id)
        
        state_final = child_partial
        
        for item_id in items_missing:
            item_size = self.ukuran_barang[item_id]
            placed = False
            
            for kontainer in state_final:
                total = child.hitung_total_ukuran(kontainer)
                if total + item_size <= self.kapasitas_kontainer:
                    kontainer.append(item_id)
                    placed = True
                    break
            
            if not placed:
                state_final.append([item_id])
                
        child.state = [k for k in state_final if k]
        
        items_in_child = set(item for k in child.state for item in k)
        if items_in_child != self.semua_barang_id:
             return copy.deepcopy(parent1)

        return child


    def _mutasi(self, individu, num_mutations=1):
        for _ in range(num_mutations):
            if random.random() > self.mutation_rate:
                continue
            
            move_type = random.choice(['pindah', 'tukar'])
            
            if move_type == 'pindah' and len(individu.state) > 0:
                try:
                    idx_asal = random.randint(0, len(individu.state) - 1)
                    if not individu.state[idx_asal]:
                        continue
                    
                    item = random.choice(individu.state[idx_asal])
                    idx_tujuan = random.randint(0, len(individu.state))
                    
                    individu.pindah_barang(item, idx_tujuan)
                except:
                    continue
                
            elif move_type == 'tukar' and len(individu.state) >= 2:
                try:
                    idx1 = random.randint(0, len(individu.state) - 1)
                    idx2 = random.randint(0, len(individu.state) - 1)
                    
                    if idx1 == idx2 or not individu.state[idx1] or not individu.state[idx2]:
                        continue
                    
                    item1 = random.choice(individu.state[idx1])
                    item2 = random.choice(individu.state[idx2])
                    
                    individu.tukar_barang(item1, item2)
                except:
                    continue


    def run(self):
        start_time = time.time()
        
        print("\n" + "="*70)
        print("GENETIC ALGORITHM")
        print("="*70)
        print(f"\nParameter:")
        print(f"  Jumlah Populasi: {self.pop_size}")
        print(f"  Max Generasi: {self.max_generasi}")
        print(f"  Mutation Rate: {self.mutation_rate}")
        print(f"  Elitism: {self.elitism_count} individu" if self.elitism_count > 0 else "  Elitism: Tidak aktif")
        print(f"  Seleksi: Roulette Wheel")
        print("\nMembuat populasi awal...")
        
        self._inisialisasi_populasi()
        
        best_init = min(self.populasi, key=lambda x: x.objective_function())
        score_init = best_init.objective_function()
        
        scores = [ind.objective_function() for ind in self.populasi]
        best_gen = min(scores)
        avg_gen = sum(scores) / len(scores)
        worst_gen = max(scores)
        
        self.hist_skor_terbaik.append(best_gen)
        self.hist_skor_rata2.append(avg_gen)
        self.hist_generasi.append(0)

        print(f"\nStatistik Populasi Awal:")
        print(f"  Nilai Objective Function Terbaik: {best_gen:.2f}")
        print(f"  Nilai Objective Function Rata-rata: {avg_gen:.2f}")
        print(f"  Nilai Objective Function Terburuk: {worst_gen:.2f}")
        print(f"  Range: {worst_gen - best_gen:.2f}")
        print("\nMemulai evolusi...\n")
        
        for gen in range(1, self.max_generasi + 1):
            new_pop = []
            
            if self.elitism_count > 0:
                sorted_pop = sorted(self.populasi, key=lambda x: x.objective_function())
                elite = [copy.deepcopy(ind) for ind in sorted_pop[:self.elitism_count]]
                new_pop.extend(elite)
            
            while len(new_pop) < self.pop_size:
                p1 = self._seleksi_roulette()
                p2 = self._seleksi_roulette()
                
                child = self._crossover(p1, p2)
                self._mutasi(child)
                
                new_pop.append(child)
            
            self.populasi = new_pop
            
            scores = [ind.objective_function() for ind in self.populasi]
            best_gen = min(scores)
            avg_gen = sum(scores) / len(scores)
            
            self.hist_skor_terbaik.append(best_gen)
            self.hist_skor_rata2.append(avg_gen)
            self.hist_generasi.append(gen)
            
            if gen % 100 == 0 or gen == self.max_generasi:
                print(f"Generasi {gen}/{self.max_generasi} | Nilai Objective Function: {best_gen:.2f} | Rata-rata: {avg_gen:.2f}")

        end_time = time.time()
        durasi = end_time - start_time
        
        best_final = min(self.populasi, key=lambda x: x.objective_function())
        score_final = best_final.objective_function()
        
        improvement = score_init - score_final
        pct = (improvement / score_init * 100) if score_init != 0 else 0

        print("\n" + "="*70)
        print("HASIL AKHIR")
        print("="*70)
        print(f"\nState Akhir (Terbaik):")
        print(f"  Nilai Objective Function: {score_final}")
        print(f"  Jumlah Kontainer: {len(best_final.state)}")
        print(f"\nStatistik:")
        print(f"  Nilai Objective Function Awal: {score_init}")
        print(f"  Nilai Objective Function Akhir: {score_final}")
        print(f"  Peningkatan: {improvement} ({pct:.2f}%)")
        print(f"  Total Generasi: {self.max_generasi}")
        print(f"  Durasi: {durasi:.4f} detik")
        print("="*70 + "\n")
        
        stats = {
            'solusi_awal': best_init,
            'solusi_akhir': best_final,
            'skor_awal': score_init,
            'skor_akhir': score_final,
            'peningkatan': improvement,
            'persentase_peningkatan': pct,
            'total_generasi': self.max_generasi,
            'durasi': durasi,
            'pop_size': self.pop_size,
            'mutation_rate': self.mutation_rate,
            'elitism_count': self.elitism_count,
            'history_skor_terbaik': self.hist_skor_terbaik,
            'history_skor_rata2': self.hist_skor_rata2,
            'history_generasi': self.hist_generasi,
            'kapasitas_kontainer': self.kapasitas_kontainer
        }
        
        return best_final, stats