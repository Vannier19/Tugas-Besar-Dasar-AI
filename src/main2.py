import json
import os
from Container import SolusiPacking
from HillClimb import HillClimbAlgoritma
from Visualisasi import VisualisasiHillClimbing
from Genetic import GeneticAlgoritma
from Visualisasi import VisualisasiGenetic

def load_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def tampilkan_menu_algoritma():
    print("\n" + "="*70)
    print(" "*22 + "BIN PACKING PROBLEM SOLVER")
    print("="*70)
    print("Data sudah dimuat. Pilih Algoritma:")
    print("1. Hill Climbing (Steepest Ascent w/ Sideways)")
    print("2. Simulated Annealing")
    print("3. Genetic Algorithm")
    print("0. Kembali (Pilih Ulang Data)")
    print("-"*70)

def tampilkan_menu_input():
    print("\n" + "="*70)
    print(" "*20 + " - MODE INPUT")
    print("="*70)
    print("\nPilih mode input:")
    print("1. Gunakan Test Case yang sudah ada")
    print("2. Input data manual")
    print("0. Keluar Program")
    print("-"*70)

def tampilkan_test_cases():
    print("\n" + "="*70)
    print(" "*25 + "DAFTAR TEST CASE")
    print("="*70)
    
    test_cases = []
    data_dir = "../data"
    
    for i in range(1, 10):
        file_path = os.path.join(data_dir, f"test_case_{i}.json")
        if os.path.exists(file_path):
            try:
                data = load_data(file_path)
                test_cases.append({
                    'nomor': i,
                    'file': file_path,
                    'nama': data.get('nama', f'Test Case {i}'),
                    'deskripsi': data.get('deskripsi', ''),
                    'kapasitas': data['kapasitas_kontainer'],
                    'jumlah_barang': len(data['barang'])
                })
            except:
                pass
    
    if not test_cases:
        print("Tidak ada test case yang tersedia!")
        return None
    
    for tc in test_cases:
        print(f"\n{tc['nomor']}. {tc['nama']}")
        print(f"   {tc['deskripsi']}")
        print(f"   Kapasitas: {tc['kapasitas']} | Jumlah Barang: {tc['jumlah_barang']}")
    
    print("\n0. Kembali ke menu utama")
    print("-"*70)
    
    return test_cases

def input_data_manual():
    print("\n" + "="*70)
    print(" "*25 + "INPUT DATA MANUAL")
    print("="*70)
    
    while True:
        try:
            kapasitas = int(input("\nMasukkan kapasitas kontainer: "))
            if kapasitas <= 0:
                print(" Kapasitas harus lebih dari 0!")
                continue
            break
        except ValueError:
            print(" Input tidak valid! Masukkan angka.")
    
    while True:
        try:
            jumlah_barang = int(input("Masukkan jumlah barang: "))
            if jumlah_barang <= 0:
                print(" Jumlah barang harus lebih dari 0!")
                continue
            break
        except ValueError:
            print(" Input tidak valid! Masukkan angka.")
    
    daftar_barang = []
    print(f"\n{'-'*70}\nMasukkan detail barang:\n{'-'*70}")
    
    for i in range(jumlah_barang):
        print(f"\nBarang ke-{i+1}:")
        while True:
            id_barang = input(f"  ID Barang: ").strip()
            if not id_barang:
                print("   ID tidak boleh kosong!")
                continue
            if any(b['id'] == id_barang for b in daftar_barang):
                print("   ID sudah digunakan! Gunakan ID lain.")
                continue
            break
        
        while True:
            try:
                ukuran = int(input(f"  Ukuran: "))
                if ukuran <= 0:
                    print("   Ukuran harus lebih dari 0!")
                    continue
                break
            except ValueError:
                print("   Input tidak valid! Masukkan angka.")
        
        daftar_barang.append({'id': id_barang, 'ukuran': ukuran})
    
    print(f"\n{'-'*70}\n Berhasil menginput {jumlah_barang} barang!\n{'-'*70}")
    return kapasitas, daftar_barang

def input_int(prompt, default, min_val=0):
    while True:
        try:
            val_str = input(prompt).strip()
            if val_str == "":
                return default
            val_int = int(val_str)
            if val_int < min_val:
                print(f" Nilai harus >= {min_val}!")
                continue
            return val_int
        except ValueError:
            print(" Input tidak valid! Masukkan angka.")

def input_float(prompt, default, min_val=0.0, max_val=1.0):
    while True:
        try:
            val_str = input(prompt).strip()
            if val_str == "":
                return default
            val_float = float(val_str)
            if not (min_val <= val_float <= max_val):
                print(f" Nilai harus di antara {min_val} dan {max_val}!")
                continue
            return val_float
        except ValueError:
            print(" Input tidak valid! Masukkan angka.")

def jalankan_hill_climbing(kapasitas_kontainer, daftar_barang, max_sideways=100):
    print("\n" + "="*70)
    print("Membuat solusi awal (Random)...")
    solusi_awal = SolusiPacking(kapasitas_kontainer, daftar_barang)
    solusi_awal.inisialisasi_random()
    print(f"Solusi awal: {len(solusi_awal.state)} kontainer, Skor: {solusi_awal.objective_function()}")
    
    print("\nMenjalankan Hill Climbing...")
    algoritma = HillClimbAlgoritma(solusi_awal=solusi_awal, max_sideways_moves=max_sideways)
    solusi_akhir, statistik = algoritma.run()
    
    print("\n" + "="*70)
    print("DETAIL SOLUSI AKHIR (HILL CLIMBING)")
    print("="*70)
    for idx, kontainer in enumerate(solusi_akhir.state):
        total_ukuran = solusi_akhir.hitung_total_ukuran(kontainer)
        persentase = (total_ukuran / kapasitas_kontainer) * 100
        print(f"\nKontainer {idx + 1} (Items: {len(kontainer)}):")
        print(f"  Ukuran: {total_ukuran}/{kapasitas_kontainer} ({persentase:.1f}%) | Sisa: {kapasitas_kontainer - total_ukuran}")
        print(f"  IDs: {kontainer}")
    
    while True:
        pilih = input("\nBuat visualisasi grafik? (1. Ya / 2. Tidak): ").strip()
        if pilih == "1":
            try:
                viz = VisualisasiHillClimbing()
                viz.visualisasi_lengkap(statistik)
            except Exception as e:
                print(f"\nError visualisasi: {e} (Pastikan matplotlib/numpy terinstall)")
            break
        elif pilih == "2":
            break
        else:
            print("Pilihan tidak valid!")

def jalankan_genetic_algorithm(kapasitas_kontainer, daftar_barang, pop_size, mutation_rate, max_generasi):
    print("\nMenjalankan Genetic Algorithm...")
    
    algoritma = GeneticAlgoritma(
        kapasitas_kontainer=kapasitas_kontainer,
        daftar_barang=daftar_barang,
        pop_size=pop_size,
        mutation_rate=mutation_rate,
        max_generasi=max_generasi
    )
    solusi_akhir, statistik = algoritma.run()
    
    print("\n" + "="*70)
    print("DETAIL SOLUSI AKHIR (GENETIC ALGORITHM)")
    print("="*70)
    for idx, kontainer in enumerate(solusi_akhir.state):
        total_ukuran = solusi_akhir.hitung_total_ukuran(kontainer)
        persentase = (total_ukuran / kapasitas_kontainer) * 100
        print(f"\nKontainer {idx + 1} (Items: {len(kontainer)}):")
        print(f"  Ukuran: {total_ukuran}/{kapasitas_kontainer} ({persentase:.1f}%) | Sisa: {kapasitas_kontainer - total_ukuran}")
        print(f"  IDs: {kontainer}")
    
    while True:
        pilih = input("\nBuat visualisasi grafik? (1. Ya / 2. Tidak): ").strip()
        if pilih == "1":
            try:
                viz = VisualisasiGenetic() 
                viz.visualisasi_lengkap_ga(statistik)
            except Exception as e:
                print(f"\nError visualisasi: {e} (Pastikan matplotlib/numpy terinstall)")
            break
        elif pilih == "2":
            break
        else:
            print("Pilihan tidak valid!")

def algoritma_simulated_annealing():
    print("\n" + "="*70)
    print(" "*20 + "SIMULATED ANNEALING")
    print("="*70)
    print("\nAlgoritma belum diimplementasi.")
    print("="*70)
    input("\nTekan Enter...")

def main():
    """
    Fungsi main program dengan alur "Input Data Dulu".
    """
    while True:
        # --- LANGKAH 1: PILIH INPUT ---
        tampilkan_menu_input()
        
        kapasitas_kontainer = None
        daftar_barang = None
        
        try:
            pilihan_input = input("\nPilih menu (0-2): ").strip()
            
            if pilihan_input == "0":
                print("\n" + "="*70 + "\nTerima kasih! Program selesai.\n" + "="*70 + "\n")
                break # Keluar program
            
            elif pilihan_input == "1":
                # Mode Test Case
                test_cases = tampilkan_test_cases()
                if test_cases is None:
                    continue
                
                try:
                    pilih_tc = input("\nPilih test case (0 untuk kembali): ").strip()
                    if pilih_tc == "0":
                        continue # Kembali ke menu input
                    pilih_tc = int(pilih_tc)
                    
                    selected_tc = next((tc for tc in test_cases if tc['nomor'] == pilih_tc), None)
                    
                    if selected_tc is None:
                        print("\n Test case tidak ditemukan!")
                        input("Tekan Enter...")
                        continue
                    
                    print(f"\n{'='*70}\nMemuat: {selected_tc['nama']}\n{'='*70}")
                    data = load_data(selected_tc['file'])
                    kapasitas_kontainer = data['kapasitas_kontainer']
                    daftar_barang = data['barang']
                    
                except ValueError:
                    print("\n Input tidak valid!")
                    input("Tekan Enter...")
                    continue
            
            elif pilihan_input == "2":
                # Mode Input Manual
                try:
                    kapasitas_kontainer, daftar_barang = input_data_manual()
                except KeyboardInterrupt:
                    print("\n\n Input dibatalkan.")
                    input("Tekan Enter...")
                    continue
            
            else:
                print("\n Pilihan tidak valid! Pilih 0, 1, atau 2.")
                input("Tekan Enter...")
                continue
            
            # --- LANGKAH 2: JIKA DATA SIAP, PILIH ALGORITMA ---
            if kapasitas_kontainer is not None and daftar_barang is not None:
                while True:
                    tampilkan_menu_algoritma()
                    pilihan_algo = input("\nPilih algoritma (0-3): ").strip()
                    
                    if pilihan_algo == "0":
                        break # Kembali ke menu input
                    
                    elif pilihan_algo == "1":
                        # Hill Climbing
                        max_sw = input_int("\nMasukkan max sideways moves (default 100): ", 100, min_val=0)
                        jalankan_hill_climbing(kapasitas_kontainer, daftar_barang, max_sw)
                        input("\n Tekan Enter untuk kembali ke menu algoritma...")
                    
                    elif pilihan_algo == "2":
                        # Simulated Annealing
                        algoritma_simulated_annealing()
                    
                    elif pilihan_algo == "3":
                        # Genetic Algorithm
                        print("\nMasukkan Parameter Genetic Algorithm:")
                        pop_size = input_int("  Jumlah Populasi (default 100): ", 100, min_val=10)
                        max_gen = input_int("  Max Generasi (default 500): ", 500, min_val=10)
                        mut_rate = input_float("  Mutation Rate (0.0 - 1.0, default 0.1): ", 0.1)
                        
                        jalankan_genetic_algorithm(kapasitas_kontainer, daftar_barang, pop_size, mut_rate, max_gen)
                        input("\n Tekan Enter untuk kembali ke menu algoritma...")
                    
                    else:
                        print("\n Pilihan tidak valid! Pilih 0, 1, 2, atau 3.")
                        input("Tekan Enter...")
        
        except KeyboardInterrupt:
            print("\n\n" + "="*70 + "\nProgram dihentikan oleh user.\n" + "="*70 + "\n")
            break
        except Exception as e:
            print(f"\n Terjadi error global: {e}")
            input("Tekan Enter untuk melanjutkan...")

if __name__ == "__main__":
    main()