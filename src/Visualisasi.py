import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

class VisualisasiHillClimbing:
    
    def plot_progress(self, hist_iter, hist_skor, stats):
        # bikin grafik progress
        plt.figure(figsize=(10, 6))
        plt.plot(hist_iter, hist_skor, marker='o', linestyle='-', linewidth=2)
        plt.xlabel('Iteration')
        plt.ylabel('Penalty Value')
        plt.title('Progress')
        plt.grid(True, alpha=0.3)
        
        # info box
        info = f"Iterasi: {stats['total_iterasi']}\n"
        info += f"Awal: {stats['skor_awal']}\n"
        info += f"Akhir: {stats['skor_akhir']}\n"
        info += f"Waktu: {stats['durasi']:.2f}s"
        
        plt.text(0.02, 0.98, info, transform=plt.gca().transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # atur batas y supaya grafik tidak terlihat 'mendekati 0' palsu
        # set default agar nanti annotate tidak error
        y_min, y_max = 0, 1
        try:
            y_min = min(hist_skor)
            y_max = max(hist_skor)
            yrange = y_max - y_min
            if yrange <= 0:
                # kalo semua skor sama, beri range kecil
                y_min = y_min - 1
                y_max = y_max + 1
            else:
                # tambahkan margin: atas 10%, bawah 5%
                y_min = max(0, y_min - 0.05 * yrange)
                y_max = y_max + 0.10 * yrange
            plt.ylim(y_min, y_max)
        except Exception:
            pass

        # tandai skor akhir supaya jelas berapa nilainya
        if hist_iter and hist_skor:
            akhir_iter = hist_iter[-1]
            akhir_skor = hist_skor[-1]
            plt.axhline(y=akhir_skor, color='orange', linestyle='--', linewidth=1)
            plt.scatter([akhir_iter], [akhir_skor], color='red', zorder=5)
            plt.annotate(f'Akhir: {akhir_skor}', xy=(akhir_iter, akhir_skor),
                         xytext=(akhir_iter, akhir_skor + 0.03 * (y_max - y_min)),
                         arrowprops=dict(arrowstyle='->', color='gray'),
                         fontsize=9, bbox=dict(boxstyle='round', fc='wheat', alpha=0.6))

        plt.tight_layout()
        plt.show()
    
    def plot_containers(self, sol_awal, sol_akhir, kapasitas):
        # bikin perbandingan before after
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
        
        self._plot_one_solution(ax1, sol_awal.state, kapasitas, "Before", sol_awal)
        self._plot_one_solution(ax2, sol_akhir.state, kapasitas, "After", sol_akhir)
        
        fig.suptitle('Container: Before vs After', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def _plot_one_solution(self, ax, containers, kapasitas, title, solusi):
        n_containers = len(containers)
        width = 0.5
        space = 0.7
        
        colors = plt.cm.Set3(np.linspace(0, 1, 15))
        
        # cari max height buat overload
        max_h = kapasitas
        for c in containers:
            total = solusi.hitung_total_ukuran(c)
            if total > max_h:
                max_h = total
        max_h = max_h * 1.1
        
        for idx, container in enumerate(containers):
            x = idx * space
            y = 0
            total_size = solusi.hitung_total_ukuran(container)
            overload = total_size > kapasitas
            
            # border kontainer
            border = 'red' if overload else 'black'
            lw = 2.5 if overload else 1.5
            
            # kotak kontainer utama
            ax.add_patch(patches.Rectangle(
                (x, 0), width, kapasitas,
                linewidth=lw, edgecolor=border, facecolor='white', alpha=0.2
            ))
            
            # kalo overload, tampilin area merah
            if overload:
                ax.add_patch(patches.Rectangle(
                    (x, kapasitas), width, total_size - kapasitas,
                    linewidth=lw, edgecolor='red', 
                    facecolor='pink', alpha=0.3, linestyle='--'
                ))
            
            # tampilin barang
            for item_id in container:
                size = solusi.ukuran_barang[item_id]
                color = colors[hash(item_id) % len(colors)]
                
                ax.add_patch(patches.Rectangle(
                    (x, y), width, size,
                    linewidth=0.8, edgecolor='black', facecolor=color, alpha=0.7
                ))
                
                # text barang (kalo cukup besar)
                if size > 12:
                    ax.text(x + width/2, y + size/2, 
                           f'{item_id}\n({size})',
                           ha='center', va='center', fontsize=5)
                
                y += size
            
            # ruang kosong
            if not overload and total_size < kapasitas:
                sisa = kapasitas - total_size
                ax.add_patch(patches.Rectangle(
                    (x, y), width, sisa,
                    linewidth=0.5, edgecolor='gray', facecolor='lightgray', 
                    alpha=0.15, linestyle=':'
                ))
        
        # garis kapasitas
        ax.axhline(y=kapasitas, color='green', linestyle='-', linewidth=1.5, 
                  alpha=0.6, label=f'Kapasitas: {kapasitas}')
        
        # set xlim yang bener: posisi terakhir + width + margin
        ax.set_xlim(-0.3, (n_containers - 1) * space + width + 0.3)
        ax.set_ylim(0, max_h)
        ax.set_xlabel('Containers')
        ax.set_ylabel('Capacity')
        ax.set_title(f'{title}\nTotal: {n_containers} containers', fontweight='bold')
        ax.grid(True, alpha=0.2, axis='y')
        
        # set x-ticks di tengah setiap kontainer
        tick_positions = [i * space + width/2 for i in range(n_containers)]
        tick_labels = [str(i+1) for i in range(n_containers)]
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, fontsize=7)
        
        ax.legend(loc='upper right', fontsize=8)
        
        # info overload
        n_overload = sum(1 for c in containers if solusi.hitung_total_ukuran(c) > kapasitas)
        info = f"Score: {solusi.objective_function():.1f}"
        if n_overload > 0:
            info += f"\nOverload: {n_overload}"
        
        ax.text(0.02, 0.98, info, transform=ax.transAxes,
               fontsize=9, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    
    def visualisasi_lengkap(self, stats):
        sol_awal = stats['solusi_awal']
        sol_akhir = stats['solusi_akhir']
        hist_iter = stats['history_iterasi']
        hist_skor = stats['history_skor']
        
        kapasitas = stats['kapasitas_kontainer']
        
        print("\n" + "="*70)
        print("VISUALISASI")
        print("="*70)
        
        self.plot_progress(hist_iter, hist_skor, stats)
        self.plot_containers(sol_awal, sol_akhir, kapasitas)
        
        print("\n" + "="*70)
        print("SELESAI")
        print("="*70)

class VisualisasiGenetic(VisualisasiHillClimbing):
    
    def plot_progress_ga(self, hist_generasi, hist_skor_terbaik, hist_skor_rata2, stats):
        #Membuat plot progres: Skor Terbaik (min) vs Skor Rata-rata
        plt.figure(figsize=(10, 6))
        
        plt.plot(hist_generasi, hist_skor_terbaik, 
                 label='Skor Terbaik (Min)', color='blue', linewidth=2)
        plt.plot(hist_generasi, hist_skor_rata2, 
                 label='Skor Rata-rata', color='orange', linestyle='--', linewidth=2)
        
        plt.xlabel('Generasi')
        plt.ylabel('Objective Function (Skor)')
        plt.title(f'Evolusi Genetic Algorithm (Pop: {stats["pop_size"]}, Mut: {stats["mutation_rate"]})')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # info box
        info = f"Generasi: {stats['total_generasi']}\n"
        info += f"Populasi: {stats['pop_size']}\n"
        info += f"Skor Awal: {stats['skor_awal']:.2f}\n"
        info += f"Skor Akhir: {stats['skor_akhir']:.2f}\n"
        info += f"Waktu: {stats['durasi']:.2f}s"
        
        plt.text(0.98, 0.98, info, transform=plt.gca().transAxes,
                fontsize=10, verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.show()

    def visualisasi_lengkap_ga(self, stats):
        """
        Menjalankan semua visualisasi untuk GA.
        """
        sol_awal = stats['solusi_awal']
        sol_akhir = stats['solusi_akhir']
        hist_generasi = stats['history_generasi']
        hist_skor_terbaik = stats['history_skor_terbaik']
        hist_skor_rata2 = stats['history_skor_rata2']
        
        kapasitas = stats['kapasitas_kontainer']
        
        print("\n" + "="*70)
        print("VISUALISASI GENETIC ALGORITHM")
        print("="*70)
        
        # Plot 1: Grafik Progres (Max dan Rata-rata)
        self.plot_progress_ga(hist_generasi, hist_skor_terbaik, hist_skor_rata2, stats)
        
        # Plot 2: Perbandingan Kontainer (Awal vs Akhir)
        self.plot_containers(sol_awal, sol_akhir, kapasitas)
        
        print("\n" + "="*70)
        print("SELESAI")
        print("="*70)