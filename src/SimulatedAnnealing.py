import copy
import time
import math
import random
from Container import SolusiPacking

class SimulatedAnnealingAlgoritma:
    
    def __init__(self, solusi_awal, temperatur_awal, temperatur_akhir, cooling_rate):
        self.solusi_awal = solusi_awal
        self.temp_awal = temperatur_awal
        self.temp_akhir = temperatur_akhir
        self.cooling_rate = cooling_rate

    def _dapatkan_tetangga_acak(self, solusi_sekarang):
        tetangga = copy.deepcopy(solusi_sekarang)
        
        all_items = []
        for container in tetangga.state:
            for item in container:
                all_items.append(item)

        if not all_items:
            return tetangga

        if random.random() < 0.5:
            try:
                item_to_move = random.choice(all_items)
                idx_tujuan = random.randint(0, len(tetangga.state)) 
                tetangga.pindah_barang(item_to_move, idx_tujuan)
            except:
                pass
            
        else:
            if len(all_items) >= 2:
                try:
                    item1, item2 = random.sample(all_items, 2)
                    tetangga.tukar_barang(item1, item2)
                except:
                    pass
                
        return tetangga

    def run(self):
        start_time = time.time()
        
        current = copy.deepcopy(self.solusi_awal)
        current_score = current.objective_function()
        
        best = copy.deepcopy(current)
        best_score = current_score
        
        T = self.temp_awal
        iteration = 0
        
        hist_score = [current_score]
        hist_iter = [0]
        hist_exp_delta = [0.0]
        hist_temp = [T]
        
        stuck_count = 0
        threshold = 50
        last_best = best_score
        no_improve_cnt = 0

        print("\n" + "="*70)
        print(" "*24 + "SIMULATED ANNEALING")
        print("="*70)
        print(f"\nState Awal: Nilai Objective Function = {current_score:.2f}, T = {T:.2f}")
        print("\nSedang mencari solusi...\n")

        while T > self.temp_akhir:
            iteration += 1
            
            neighbor = self._dapatkan_tetangga_acak(current)
            neighbor_score = neighbor.objective_function()
            
            delta = neighbor_score - current_score
            
            exp_val = 0.0
            
            if delta < 0:
                current = neighbor
                current_score = neighbor_score
                
                if current_score < best_score:
                    best = copy.deepcopy(current)
                    best_score = current_score
                    no_improve_cnt = 0
                else:
                    no_improve_cnt += 1
                
                try:
                    exp_val = math.exp(delta / T)
                except (OverflowError, ZeroDivisionError):
                    exp_val = 0.0
                
            else:
                try:
                    exp_val = math.exp(delta / T)
                except (OverflowError, ZeroDivisionError):
                    exp_val = float('inf') if delta > 0 else 0.0
                
                try:
                    prob = math.exp(-delta / T)
                except (OverflowError, ZeroDivisionError):
                    prob = 0.0
                
                if random.random() < prob:
                    current = neighbor
                    current_score = neighbor_score
                else:
                    pass
                
                no_improve_cnt += 1
            
            if no_improve_cnt >= threshold:
                stuck_count += 1
                no_improve_cnt = 0

            hist_score.append(current_score)
            hist_iter.append(iteration)
            hist_exp_delta.append(exp_val)
            hist_temp.append(T)

            T *= self.cooling_rate
            
            if iteration % 1000 == 0:
                print(f"Iter: {iteration}, T: {T:.2f}, Nilai Objective Function: {current_score:.2f}, Best: {best_score:.2f}")

        end_time = time.time()
        durasi = end_time - start_time

        print("\n" + "="*70)
        print("HASIL AKHIR")
        print("="*70)
        print(f"\nState Akhir (Terbaik):")
        print(f"  Nilai Objective Function: {best_score}")
        print(f"  Jumlah Kontainer: {len(best.state)}")
        print(f"\nStatistik:")
        print(f"  Nilai Objective Function Awal: {self.solusi_awal.objective_function()}")
        print(f"  Nilai Objective Function Akhir: {best_score}")
        print(f"  Total Iterasi: {iteration}")
        print(f"  Frekuensi Stuck di Local Optima: {stuck_count} kali")
        print(f"  Durasi: {durasi:.4f} detik")
        print("="*70 + "\n")
        
        stats = {
            'solusi_awal': self.solusi_awal,
            'solusi_akhir': best,
            'skor_awal': self.solusi_awal.objective_function(),
            'skor_akhir': best_score,
            'total_iterasi': iteration,
            'durasi': durasi,
            'history_skor': hist_score,
            'history_iterasi': hist_iter,
            'history_exp_delta': hist_exp_delta,
            'history_temperature': hist_temp,
            'stuck_count': stuck_count,
            'kapasitas_kontainer': self.solusi_awal.kapasitas,
            'temp_awal': self.temp_awal,
            'temp_akhir': self.temp_akhir,
            'cooling_rate': self.cooling_rate
        }
        
        return best, stats