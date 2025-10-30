import copy
import time

class HillClimbAlgoritma:
    def __init__(self, solusi_awal, max_sideways_moves=100):
        self.solusi_awal = solusi_awal
        self.max_sideways = max_sideways_moves
    # cari tetangga terbaik (move + swap)
    def cari_tetangga(self, solusi_skrg):
        best_tetangga = None
        best_skor = solusi_skrg.objective_function()

        # kumpulin semua barang dulu biar gampang
        semua_barang = []
        for kont in solusi_skrg.state:
            for brg in kont:
                semua_barang.append(brg)

        # Operator: pindah barang ke semua posisi (termasuk bikin kontainer baru)
        for brg in semua_barang:
            for pos in range(len(solusi_skrg.state) + 1):
                tetangga = copy.deepcopy(solusi_skrg)
                tetangga.pindah_barang(brg, pos)

                skor = tetangga.objective_function()
                if skor <= best_skor:
                    best_skor = skor
                    best_tetangga = tetangga

        # Operator: tukar setiap pasangan barang
        for a in range(len(semua_barang)):
            for b in range(a + 1, len(semua_barang)):
                tet = copy.deepcopy(solusi_skrg)
                tet.tukar_barang(semua_barang[a], semua_barang[b])

                skor = tet.objective_function()
                if skor <= best_skor:
                    best_skor = skor
                    best_tetangga = tet

        return best_tetangga, best_skor

    def run(self):
        start_time = time.time()
        sol_awal = copy.deepcopy(self.solusi_awal)
        score_awal = sol_awal.objective_function()
        # sekarang adalah solusi yang sedang diproses
        current = copy.deepcopy(self.solusi_awal)
        now_skor = score_awal

        hist_score = [score_awal]
        hist_iter = [0]
        sideways = 0
        iteration = 0

        sideways_log = []
        baik_moves = 0

        print("\n" + "="*70)
        print("HILL CLIMBING")
        print("="*70)
        print("\nState Awal:")
        print("  Nilai Objective Function:", score_awal)
        print("  Jumlah Kontainer:", len(sol_awal.state))
        print("  Max Sideways:", self.max_sideways)
        print("\nSedang mencari solusi...\n")

        while True:
            iteration += 1
            # cari tetangga terbaik sekarang
            best_neighbor, best_score = self.cari_tetangga(current)

            if best_neighbor is None:
                break

            if best_score < now_skor:
                # move lebih baik
                current = best_neighbor
                now_skor = best_score
                sideways = 0
                baik_moves += 1
                hist_score.append(now_skor)
                hist_iter.append(iteration)

            elif best_score == now_skor and sideways < self.max_sideways:
                # sideways, masih boleh
                current = best_neighbor
                sideways += 1
                hist_score.append(now_skor)
                hist_iter.append(iteration)
                sideways_log.append((iteration, now_skor, sideways))

            else:
                # nggak ada yang bisa dilakukan lagi
                break
        
        end_time = time.time()
        durasi = end_time - start_time
        score_akhir = current.objective_function()

        if len(sideways_log) > 0:
            print("\n" + "="*70)
            print("SIDEWAYS MOVES")
            print("="*70)
            print(f"{'SIDEWAYS KE':<15} {'ITERASI':<15} {'NILAI OBJECTIVE FUNCTION':<20}")
            print("-"*70)
            for iter_num, scr, sw_num in sideways_log:
                print(f"{sw_num:<15} {iter_num:<15} {scr:<20}")
            print("="*70)
        
        print("\n" + "="*70)
        print("HASIL AKHIR")
        print("="*70)
        print("\nState Akhir:")
        print("  Nilai Objective Function:", score_akhir)
        print("  Jumlah Kontainer:", len(current.state))
        print("\nStatistik:")
        print("  Nilai Objective Function Awal:", score_awal)
        print("  Nilai Objective Function Akhir:", score_akhir)
        improvement = score_awal - score_akhir
        pct = (improvement / score_awal * 100) if score_awal != 0 else 0
        print("  Peningkatan:", improvement, f"({pct:.2f}% )")
        print("  Total Iterasi:", iteration)
        print("  Better Moves:", baik_moves)
        print("  Sideways Moves:", len(sideways_log))
        print("  Durasi:", f"{durasi:.4f} detik")
        print("  Sideways Terakhir:", f"{sideways}/{self.max_sideways}")
        print("="*70 + "\n")

        stats = {
            'solusi_awal': sol_awal,
            'solusi_akhir': current,
            'skor_awal': score_awal,
            'skor_akhir': score_akhir,
            'peningkatan': improvement,
            'persentase_peningkatan': pct,
            'total_iterasi': iteration,
            'total_better_moves': baik_moves,
            'total_sideways': len(sideways_log),
            'sideways_terakhir': sideways,
            'durasi': durasi,
            'max_sideways_moves': self.max_sideways,
            'history_skor': hist_score,
            'history_iterasi': hist_iter,
            'sideways_log': sideways_log,
            'kapasitas_kontainer': sol_awal.kapasitas
        }

        return current, stats