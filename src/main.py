# src/main.py
import json
from Container import SolusiPacking 

def muat_data(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

# Main program
if __name__ == "__main__":
    # Muat data dari file JSON
    path_data = '../data/input_data.json' 
    input_data = muat_data(path_data)

    # Inisialisasi solusi
    solusi = SolusiPacking(input_data["kapasitas_kontainer"], input_data["barang"])
    
    # Buat state awal dan tampilkan hasilnya
    solusi.inisialisasi_first_fit_decreasing()
    solusi.tampilkan_solusi("State Awal (Hasil First Fit Decreasing)")

    #----- CONTOH PENGGUNAAN FUNGSI DAN SKORNYA -----
    
    # Contoh 1: Pindah Barang
    print("\n--- Contoh Move 1: Pindah Barang ---")
    solusi.pindah_barang("BRG007", 0) # Pindah BRG007 ke kontainer index 0
    solusi.tampilkan_solusi("State Setelah BRG007 Dipindah")
    # Perhatikan: Skor akan sangat tinggi karena ada penalti overload!

    # Contoh 2: Tukar Barang
    print("\n--- Contoh Move 2: Tukar Barang ---")
    solusi.tukar_barang("BRG004", "BRG003")
    solusi.tampilkan_solusi("State Setelah BRG004 dan BRG003 Ditukar")