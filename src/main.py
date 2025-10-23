import json
import os
from Container import SolusiPacking
from HillClimb import HillClimbAlgoritma
from Visualisasi import VisualisasiHillClimbing

def load_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def tampilkan_menu_algoritma():
    print("\n" + "="*70)
    print(" "*22 + "BIN PACKING PROBLEM SOLVER")
    print("="*70)
    print("\nPilih Algoritma:")
    print("1. Steepest Ascent ")
    print("2. Simulated Annealing")
    print("3. Genetic Algorithm")
    print("0. Keluar")
    print("-"*70)

def tampilkan_menu_input():
    print("\n" + "="*70)
    print(" "*20 + " - MODE INPUT")
    print("="*70)
    print("\nPilih mode input:")
    print("1. Gunakan Test Case yang sudah ada")
    print("2. Input data manual")
    print("0. Kembali ke menu algoritma")
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
    """Input data secara manual dari user."""
    print("\n" + "="*70)
    print(" "*25 + "INPUT DATA MANUAL")
    print("="*70)
    
    # Input kapasitas kontainer
    while True:
        try:
            kapasitas = int(input("\nMasukkan kapasitas kontainer: "))
            if kapasitas <= 0:
                print(" Kapasitas harus lebih dari 0!")
                continue
            break
        except ValueError:
            print(" Input tidak valid! Masukkan angka.")
    
    # Input jumlah barang
    while True:
        try:
            jumlah_barang = int(input("Masukkan jumlah barang: "))
            if jumlah_barang <= 0:
                print(" Jumlah barang harus lebih dari 0!")
                continue
            break
        except ValueError:
            print(" Input tidak valid! Masukkan angka.")
    
    # Input detail setiap barang
    daftar_barang = []
    print(f"\n{'-'*70}")
    print("Masukkan detail barang:")
    print("-"*70)
    
    for i in range(jumlah_barang):
        print(f"\nBarang ke-{i+1}:")
        
        # Input ID barang
        while True:
            id_barang = input(f"  ID Barang: ").strip()
            if not id_barang:
                print("   ID tidak boleh kosong!")
                continue
            # Cek apakah ID sudah ada
            if any(b['id'] == id_barang for b in daftar_barang):
                print("   ID sudah digunakan! Gunakan ID lain.")
                continue
            break
        
        # Input ukuran barang
        while True:
            try:
                ukuran = int(input(f"  Ukuran: "))
                if ukuran <= 0:
                    print("   Ukuran harus lebih dari 0!")
                    continue
                break
            except ValueError:
                print("   Input tidak valid! Masukkan angka.")
        
        daftar_barang.append({
            'id': id_barang,
            'ukuran': ukuran
        })
    
    print(f"\n{'-'*70}")
    print(f" Berhasil menginput {jumlah_barang} barang!")
    print("-"*70)
    
    return kapasitas, daftar_barang

def jalankan_hill_climbing(kapasitas_kontainer, daftar_barang, max_sideways=100):
    print("\n" + "="*70)
    print("Membuat solusi awal (Random)...")
    
    solusi_awal = SolusiPacking(kapasitas_kontainer, daftar_barang)
    solusi_awal.inisialisasi_random()
    
    print(f"Solusi awal: {len(solusi_awal.state)} kontainer")
    print(f"Objective function: {solusi_awal.objective_function()}")
    
    print("\nMenjalankan ...")
    algoritma = HillClimbAlgoritma(
        solusi_awal=solusi_awal,
        max_sideways_moves=max_sideways
    )
    
    solusi_akhir, statistik = algoritma.run()
    
    print("\n" + "="*70)
    print("DETAIL SOLUSI AKHIR")
    print("="*70)
    for idx, kontainer in enumerate(solusi_akhir.state):
        total_ukuran = solusi_akhir.hitung_total_ukuran(kontainer)
        ruang_kosong = kapasitas_kontainer - total_ukuran
        persentase = (total_ukuran / kapasitas_kontainer) * 100
        
        print(f"\nKontainer {idx + 1}:")
        print(f"  Items: {len(kontainer)}")
        print(f"  Ukuran: {total_ukuran}/{kapasitas_kontainer} ({persentase:.1f}%)")
        print(f"  Sisa: {ruang_kosong}")
        print(f"  IDs: {kontainer}")
    
    while True:
        print("\n" + "="*70)
        print("Apakah Anda ingin membuat visualisasi grafik?")
        print("1. Ya")
        print("2. Tidak")
        print("-"*70)
        pilih = input("Pilih (1/2): ").strip()
        
        if pilih == "1":
            try:
                viz = VisualisasiHillClimbing()
                viz.visualisasi_lengkap(statistik)
            except Exception as e:
                print(f"\nError saat membuat visualisasi: {e}")
                print("Pastikan matplotlib dan numpy sudah terinstall.")
                print("Install dengan: pip install matplotlib numpy")
            break
        elif pilih == "2":
            break
        else:
            print("\nPilihan tidak valid!")
    
    return solusi_akhir, statistik


def algoritma_simulated_annealing():
    print("\n" + "="*70)
    print(" "*20 + "SIMULATED ANNEALING")
    print("="*70)
    print("\nAlgoritma belum diimplementasi.")
    print("="*70)
    input("\nTekan Enter...")

def algoritma_genetic():
    print("\n" + "="*70)
    print(" "*22 + "GENETIC ALGORITHM")
    print("="*70)
    print("\nAlgoritma belum diimplementasi.")
    print("="*70)
    input("\nTekan Enter...")

def algoritma_hill_climbing():
    while True:
        tampilkan_menu_input()
        
        try:
            pilihan = input("\nPilih menu (0-2): ").strip()
            
            if pilihan == "0":
                # Kembali ke menu algoritma
                break
            
            elif pilihan == "1":
                # Mode Test Case
                test_cases = tampilkan_test_cases()
                
                if test_cases is None:
                    continue
                
                try:
                    pilih_tc = input("\nPilih test case (0 untuk kembali): ").strip()
                    
                    if pilih_tc == "0":
                        continue
                    
                    pilih_tc = int(pilih_tc)
                    
                    # Cari test case yang dipilih
                    selected_tc = None
                    for tc in test_cases:
                        if tc['nomor'] == pilih_tc:
                            selected_tc = tc
                            break
                    
                    if selected_tc is None:
                        print("\n Test case tidak ditemukan!")
                        input("Tekan Enter untuk melanjutkan...")
                        continue
                    
                    # Load data dari test case
                    print(f"\n{'='*70}")
                    print(f"Memuat: {selected_tc['nama']}")
                    print(f"{'='*70}")
                    
                    data = load_data(selected_tc['file'])
                    kapasitas_kontainer = data['kapasitas_kontainer']
                    daftar_barang = data['barang']
                    
                    # Tanya max sideways moves
                    while True:
                        try:
                            max_sw = input("\nMasukkan max sideways moves (default 100): ").strip()
                            if max_sw == "":
                                max_sw = 100
                            else:
                                max_sw = int(max_sw)
                            if max_sw < 0:
                                print(" Nilai harus >= 0!")
                                continue
                            break
                        except ValueError:
                            print(" Input tidak valid!")
                    
                    # Jalankan 
                    jalankan_hill_climbing(kapasitas_kontainer, daftar_barang, max_sw)
                    
                    input("\n Tekan Enter untuk kembali ke menu...")
                    
                except ValueError:
                    print("\n Input tidak valid!")
                    input("Tekan Enter untuk melanjutkan...")
            
            elif pilihan == "2":
                # Mode Input Manual
                try:
                    kapasitas_kontainer, daftar_barang = input_data_manual()
                    
                    # Tanya max sideways moves
                    while True:
                        try:
                            max_sw = input("\nMasukkan max sideways moves (default 100): ").strip()
                            if max_sw == "":
                                max_sw = 100
                            else:
                                max_sw = int(max_sw)
                            if max_sw < 0:
                                print(" Nilai harus >= 0!")
                                continue
                            break
                        except ValueError:
                            print(" Input tidak valid!")
                    
                    # Jalankan 
                    jalankan_hill_climbing(kapasitas_kontainer, daftar_barang, max_sw)
                    
                    input("\n Tekan Enter untuk kembali ke menu...")
                    
                except KeyboardInterrupt:
                    print("\n\n Input dibatalkan.")
                    input("Tekan Enter untuk melanjutkan...")
            
            else:
                print("\n Pilihan tidak valid! Pilih 0, 1, atau 2.")
                input("Tekan Enter untuk melanjutkan...")
        
        except KeyboardInterrupt:
            print("\n\n Input dibatalkan.")
            input("Tekan Enter untuk melanjutkan...")
            break
        except Exception as e:
            print(f"\n Terjadi error: {e}")
            input("Tekan Enter untuk melanjutkan...")

def main():
    """Fungsi main program."""
    while True:
        tampilkan_menu_algoritma()
        
        try:
            pilihan = input("\nPilih algoritma (0-3): ").strip()
            
            if pilihan == "0":
                print("\n" + "="*70)
                print("Terima kasih! Program selesai.")
                print("="*70 + "\n")
                break
            
            elif pilihan == "1":
                # 
                algoritma_hill_climbing()
            
            elif pilihan == "2":
                # Simulated Annealing (belum diimplementasi)
                algoritma_simulated_annealing()
            
            elif pilihan == "3":
                # Genetic Algorithm (belum diimplementasi)
                algoritma_genetic()
            
            else:
                print("\n Pilihan tidak valid! Pilih 0, 1, 2, atau 3.")
                input("Tekan Enter untuk melanjutkan...")
        
        except KeyboardInterrupt:
            print("\n\n" + "="*70)
            print("Program dihentikan oleh user.")
            print("="*70 + "\n")
            break
        except Exception as e:
            print(f"\n Terjadi error: {e}")
            input("Tekan Enter untuk melanjutkan...")

if __name__ == "__main__":
    main()