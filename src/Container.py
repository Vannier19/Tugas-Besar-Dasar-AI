import random

class SolusiPacking:
    # weight buat objective function
    W_JUMLAH_KONTAINER = 2
    W_PENALTI_OVERLOAD = 10
    W_KEPADATAN = 1

    def __init__(self, kapasitas_kontainer, daftar_barang):
        self.kapasitas = kapasitas_kontainer
        self.barang = daftar_barang
        self.ukuran_barang = {}
        for item in self.barang:
            self.ukuran_barang[item['id']] = item['ukuran']
        self.state = []

    def hitung_total_ukuran(self, kontainer):
        total = 0
        for item_id in kontainer:
            total += self.ukuran_barang[item_id]
        return total

    def objective_function(self):
        # hitung skor total
        skor = 0
        ruang_kosong_total = 0
        
        # jumlah kontainer
        skor = len(self.state) * self.W_JUMLAH_KONTAINER

        # cek setiap kontainer
        for kontainer in self.state:
            ukuran = self.hitung_total_ukuran(kontainer)
            
            if ukuran > self.kapasitas:
                # kena penalty kalo overload
                overload = ukuran - self.kapasitas
                skor += overload * self.W_PENALTI_OVERLOAD
            else:
                # hitung ruang kosong
                ruang_kosong = self.kapasitas - ukuran
                ruang_kosong_total += ruang_kosong
        
        skor += ruang_kosong_total * self.W_KEPADATAN
        return skor

    def inisialisasi_random(self):
        # bikin state awal random (agak jelek biar bisa di-improve)
        self.state = []
        barang_list = self.barang.copy()
        random.shuffle(barang_list)
        
        for brg in barang_list:
            item_id = brg['id']
            ukuran = brg['ukuran']
            
            if not self.state:
                # kontainer pertama
                self.state.append([item_id])
            else:
                # random placement - sengaja ga optimal
                if random.random() < 0.5:
                    # masukin ke kontainer random (bisa overload)
                    idx = random.randint(0, len(self.state) - 1)
                    self.state[idx].append(item_id)
                elif random.random() < 0.4:
                    # bikin kontainer baru (boros)
                    self.state.append([item_id])
                else:
                    # coba cari yang muat
                    cek_muat = []
                    for i in range(len(self.state)):
                        if self.hitung_total_ukuran(self.state[i]) + ukuran <= self.kapasitas:
                            cek_muat.append(i)
                    
                    if len(cek_muat) > 0:
                        idx = random.choice(cek_muat)
                        self.state[idx].append(item_id)
                    else:
                        # ga ada yang muat, paksa aja
                        idx = random.randint(0, len(self.state) - 1)
                        self.state[idx].append(item_id)
        
        # bikin beberapa kontainer overload buat state awal jelek
        jumlah_overload = max(1, int(len(self.state) * 0.3))
        for i in range(jumlah_overload):
            if len(self.state) >= 2:
                idx1 = random.randint(0, len(self.state) - 1)
                idx2 = random.randint(0, len(self.state) - 1)
                if idx1 != idx2 and len(self.state[idx2]) > 0:
                    # pindahin barang biar overload
                    item = self.state[idx2].pop(0)
                    self.state[idx1].append(item)
        
        # hapus kontainer kosong
        self.state = [k for k in self.state if len(k) > 0]

    def pindah_barang(self, id_barang, idx_tujuan):
        # cari barang di kontainer mana
        idx_asal = -1
        for i in range(len(self.state)):
            if id_barang in self.state[i]:
                idx_asal = i
                break

        if idx_asal == -1:
            return
        
        # pindahin barangnya
        self.state[idx_asal].remove(id_barang)

        if idx_tujuan >= len(self.state):
            # bikin kontainer baru
            self.state.append([id_barang])
        else:
            self.state[idx_tujuan].append(id_barang)

        # hapus kontainer kosong
        if len(self.state[idx_asal]) == 0:
            del self.state[idx_asal]

    def tukar_barang(self, id1, id2):
        # cari posisi dua barang
        pos1 = None
        pos2 = None
        
        for i in range(len(self.state)):
            if id1 in self.state[i]:
                pos1 = (i, self.state[i].index(id1))
            if id2 in self.state[i]:
                pos2 = (i, self.state[i].index(id2))

        if pos1 is None or pos2 is None:
            return

        # kalo di kontainer yang sama, ga usah tuker
        if pos1[0] == pos2[0]:
            return

        # tuker posisi barang
        idx_k1, idx_i1 = pos1
        idx_k2, idx_i2 = pos2
        
        self.state[idx_k1][idx_i1] = id2
        self.state[idx_k2][idx_i2] = id1

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