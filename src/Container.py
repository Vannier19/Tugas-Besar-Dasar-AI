import random

class SolusiPacking:
    W_JUMLAH_KONTAINER = 1000
    W_PENALTI_OVERLOAD = 1000000
    W_KEPADATAN = 1

    def __init__(self, kapasitas_kontainer, daftar_barang):
        self.kapasitas = kapasitas_kontainer
        self.barang = daftar_barang
        self.ukuran_barang = {item['id']: item['ukuran'] for item in self.barang}
        self.state = []

    def hitung_total_ukuran(self, kontainer):
        return sum(self.ukuran_barang[item_id] for item_id in kontainer)

    def objective_function(self):
        total_skor = 0
        total_ruang_kosong = 0
        
        total_skor += len(self.state) * self.W_JUMLAH_KONTAINER

        for kontainer in self.state:
            total_ukuran = self.hitung_total_ukuran(kontainer)
            
            if total_ukuran > self.kapasitas:
                overload = total_ukuran - self.kapasitas
                total_skor += overload * self.W_PENALTI_OVERLOAD
            else:
                ruang_kosong = self.kapasitas - total_ukuran
                total_ruang_kosong += ruang_kosong
        
        total_skor += total_ruang_kosong * self.W_KEPADATAN
        return total_skor

    def inisialisasi_first_fit_decreasing(self):
        self.state = []
        barang_terurut = sorted(self.barang, key=lambda x: x['ukuran'], reverse=True)

        for barang in barang_terurut:
            item_id = barang['id']
            item_ukuran = barang['ukuran']
            
            ditempatkan = False
            for kontainer in self.state:
                if self.hitung_total_ukuran(kontainer) + item_ukuran <= self.kapasitas:
                    kontainer.append(item_id)
                    ditempatkan = True
                    break
            
            if not ditempatkan:
                self.state.append([item_id])

    def inisialisasi_random(self):
        self.state = []
        barang_acak = self.barang.copy()
        random.shuffle(barang_acak)
        
        for barang in barang_acak:
            item_id = barang['id']
            item_ukuran = barang['ukuran']
            
            if not self.state or (random.random() < 0.3 and len(self.state) < len(barang_acak)):
                self.state.append([item_id])
            else:
                kontainer_tersedia = [
                    i for i, k in enumerate(self.state) 
                    if self.hitung_total_ukuran(k) + item_ukuran <= self.kapasitas
                ]
                
                if kontainer_tersedia:
                    idx_kontainer = random.choice(kontainer_tersedia)
                    self.state[idx_kontainer].append(item_id)
                else:
                    self.state.append([item_id])

    def pindah_barang(self, id_barang, idx_kontainer_tujuan):
        idx_kontainer_asal = -1
        for i, kontainer in enumerate(self.state):
            if id_barang in kontainer:
                idx_kontainer_asal = i
                break

        if idx_kontainer_asal == -1:
            return

        self.state[idx_kontainer_asal].remove(id_barang)

        if idx_kontainer_tujuan >= len(self.state):
            self.state.append([id_barang])
        else:
            self.state[idx_kontainer_tujuan].append(id_barang)

        if not self.state[idx_kontainer_asal]:
            del self.state[idx_kontainer_asal]

    def tukar_barang(self, id_barang_1, id_barang_2):
        posisi_1, posisi_2 = None, None
        for i, kontainer in enumerate(self.state):
            if id_barang_1 in kontainer:
                posisi_1 = (i, kontainer.index(id_barang_1))
            if id_barang_2 in kontainer:
                posisi_2 = (i, kontainer.index(id_barang_2))

        if not posisi_1 or not posisi_2:
            return

        if posisi_1[0] == posisi_2[0]:
            return

        idx_kontainer_1, idx_item_1 = posisi_1
        idx_kontainer_2, idx_item_2 = posisi_2
        
        self.state[idx_kontainer_1][idx_item_1] = id_barang_2
        self.state[idx_kontainer_2][idx_item_2] = id_barang_1

    def tampilkan_solusi(self, judul="Solusi Pengepakan"):
        print("\n" + "="*40)
        print(f"{judul}")
        print("="*40)
        print(f"Total Kontainer: {len(self.state)}")
        for i, kontainer in enumerate(self.state):
            total_ukuran = self.hitung_total_ukuran(kontainer)
            print(f"\nKontainer {i+1} (Total: {total_ukuran}/{self.kapasitas}):")
            for item_id in kontainer:
                print(f"   - {item_id} ({self.ukuran_barang[item_id]})")
        
        skor = self.objective_function()
        print("-" * 40)
        print(f"Skor: {skor}")
        print("="*40)