import copy
import time

class HillClimbAlgoritma:
    def __init__(self, solusi_awal, max_sideways_moves=100):
        self.solusi_awal = solusi_awal
        self.max_sideways = max_sideways_moves

    def cari_tetangga_terbaik(self, solusi_skrg):
        # coba semua kemungkinan neighbor
        best_neighbor = None
        best_score = solusi_skrg.objective_function()
        
        # dapetin semua barang
        all_items = []
        for container in solusi_skrg.state:
            for item in container:
                all_items.append(item)

        # coba pindahin barang ke kontainer lain
        for item in all_items:
            for idx in range(len(solusi_skrg.state) + 1):
                neighbor = copy.deepcopy(solusi_skrg)
                neighbor.pindah_barang(item, idx)
                
                score = neighbor.objective_function()
                if score <= best_score:
                    best_score = score
                    best_neighbor = neighbor
        
        # coba tuker dua barang
        for i in range(len(all_items)):
            for j in range(i + 1, len(all_items)):
                neighbor = copy.deepcopy(solusi_skrg)
                neighbor.tukar_barang(all_items[i], all_items[j])
                
                score = neighbor.objective_function()
                if score <= best_score:
                    best_score = score
                    best_neighbor = neighbor
        
        return best_neighbor, best_score

    def run(self):
        start_time = time.time()
        sol_awal = copy.deepcopy(self.solusi_awal)
        score_awal = sol_awal.objective_function()
        
        current_sol = copy.deepcopy(self.solusi_awal)
        current_score = score_awal
        
        hist_score = [score_awal]
        hist_iter = [0]
        sideways_cnt = 0
        iteration = 0
        
        sideways_log = []
        better_moves = 0

        print("\n" + "="*70)
        print("HILL CLIMBING")
        print("="*70)
        print(f"\nState Awal:")
        print(f"  Objective Function: {score_awal}")
        print(f"  Jumlah Kontainer: {len(sol_awal.state)}")
        print(f"  Max Sideways: {self.max_sideways}")
        print("\nSedang mencari solusi...\n")

        while True:
            iteration += 1
            best_neighbor, best_score = self.cari_tetangga_terbaik(current_sol)

            if best_neighbor is None:
                break

            if best_score < current_score:
                # dapet yang lebih baik
                current_sol = best_neighbor
                current_score = best_score
                sideways_cnt = 0
                better_moves += 1
                hist_score.append(current_score)
                hist_iter.append(iteration)
                
            elif best_score == current_score and sideways_cnt < self.max_sideways:
                # sideways move
                current_sol = best_neighbor
                sideways_cnt += 1
                hist_score.append(current_score)
                hist_iter.append(iteration)
                sideways_log.append((iteration, current_score, sideways_cnt))
                
            else:
                break
        
        end_time = time.time()
        durasi = end_time - start_time
        score_akhir = current_sol.objective_function()
        
        # print sideways moves
        if len(sideways_log) > 0:
            print("\n" + "="*70)
            print("SIDEWAYS MOVES")
            print("="*70)
            print(f"{'SIDEWAYS KE':<15} {'ITERASI':<15} {'SKOR':<20}")
            print("-"*70)
            for iter_num, scr, sw_num in sideways_log:
                print(f"{sw_num:<15} {iter_num:<15} {scr:<20}")
            print("="*70)
        
        # print hasil akhir
        print("\n" + "="*70)
        print("HASIL AKHIR")
        print("="*70)
        print(f"\nState Akhir:")
        print(f"  Objective Function: {score_akhir}")
        print(f"  Jumlah Kontainer: {len(current_sol.state)}")
        print(f"\nStatistik:")
        print(f"  Skor Awal: {score_awal}")
        print(f"  Skor Akhir: {score_akhir}")
        improvement = score_awal - score_akhir
        pct = (improvement / score_awal * 100) if score_awal != 0 else 0
        print(f"  Peningkatan: {improvement} ({pct:.2f}%)")
        print(f"  Total Iterasi: {iteration}")
        print(f"  Better Moves: {better_moves}")
        print(f"  Sideways Moves: {len(sideways_log)}")
        print(f"  Durasi: {durasi:.4f} detik")
        print(f"  Sideways Terakhir: {sideways_cnt}/{self.max_sideways}")
        print("="*70 + "\n")
        
        # return hasil
        stats = {
            'solusi_awal': sol_awal,
            'solusi_akhir': current_sol,
            'skor_awal': score_awal,
            'skor_akhir': score_akhir,
            'peningkatan': improvement,
            'persentase_peningkatan': pct,
            'total_iterasi': iteration,
            'total_better_moves': better_moves,
            'total_sideways': len(sideways_log),
            'sideways_terakhir': sideways_cnt,
            'durasi': durasi,
            'max_sideways_moves': self.max_sideways,
            'history_skor': hist_score,
            'history_iterasi': hist_iter,
            'sideways_log': sideways_log,
            'kapasitas_kontainer': sol_awal.kapasitas
        }
        
        return current_sol, stats

     