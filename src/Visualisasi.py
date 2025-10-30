import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

class VisualisasiHillClimbing:
    
    def plot_progress(self, hist_iter, hist_score, stats):
        plt.figure(figsize=(10, 6))
        plt.plot(hist_iter, hist_score, marker='o', linestyle='-', linewidth=2)
        plt.xlabel('Iteration')
        plt.ylabel('Objective Function Value')
        plt.title('Hill Climbing Progress')
        plt.grid(True, alpha=0.3)
        
        info = f"Iterasi: {stats['total_iterasi']}\n"
        info += f"Awal: {stats['skor_awal']}\n"
        info += f"Akhir: {stats['skor_akhir']}\n"
        info += f"Waktu: {stats['durasi']:.2f}s"
        
        plt.text(0.02, 0.98, info, transform=plt.gca().transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        y_min, y_max = 0, 1
        try:
            y_min = min(hist_score)
            y_max = max(hist_score)
            yrange = y_max - y_min
            if yrange <= 0:
                y_min = y_min - 1
                y_max = y_max + 1
            else:
                y_min = max(0, y_min - 0.05 * yrange)
                y_max = y_max + 0.10 * yrange
            plt.ylim(y_min, y_max)
        except Exception:
            pass

        if hist_iter and hist_score:
            final_iter = hist_iter[-1]
            final_score = hist_score[-1]
            plt.axhline(y=final_score, color='orange', linestyle='--', linewidth=1)
            plt.scatter([final_iter], [final_score], color='red', zorder=5)
            plt.annotate(f'Final: {final_score}', xy=(final_iter, final_score),
                         xytext=(final_iter, final_score + 0.03 * (y_max - y_min)),
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
        info = f"Value: {solusi.objective_function():.1f}"
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
    
    def plot_progress_ga(self, hist_gen, hist_best, hist_avg, stats):
        plt.figure(figsize=(10, 6))
        
        plt.plot(hist_gen, hist_best, 
                 label='Best', color='blue', linewidth=2)
        plt.plot(hist_gen, hist_avg, 
                 label='Average', color='orange', linestyle='--', linewidth=2)
        
        plt.xlabel('Generation')
        plt.ylabel('Objective Function Value')
        plt.title(f'Genetic Algorithm Evolution (Pop: {stats["pop_size"]}, Mut: {stats["mutation_rate"]})')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        info = f"Generation: {stats['total_generasi']}\n"
        info += f"Population: {stats['pop_size']}\n"
        info += f"Initial: {stats['skor_awal']:.2f}\n"
        info += f"Final: {stats['skor_akhir']:.2f}\n"
        info += f"Time: {stats['durasi']:.2f}s"
        
        plt.text(0.98, 0.98, info, transform=plt.gca().transAxes,
                fontsize=10, verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Add final marker on best score line
        if hist_gen and hist_best:
            final_gen = hist_gen[-1]
            final_best = hist_best[-1]
            plt.axhline(y=final_best, color='lightblue', linestyle='--', linewidth=1)
            plt.scatter([final_gen], [final_best], color='red', zorder=5, s=50)
            
            # Calculate y-range for annotation placement
            y_min = min(min(hist_best), min(hist_avg))
            y_max = max(max(hist_best), max(hist_avg))
            yrange = y_max - y_min if y_max != y_min else 1
            
            plt.annotate(f'Final: {final_best:.2f}', xy=(final_gen, final_best),
                        xytext=(final_gen, final_best + 0.03 * yrange),
                        arrowprops=dict(arrowstyle='->', color='gray'),
                        fontsize=9, bbox=dict(boxstyle='round', fc='wheat', alpha=0.6))
        
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


class VisualisasiSimulatedAnnealing(VisualisasiHillClimbing):
    
    def plot_progress_sa(self, hist_iter, hist_score, stats):
        plt.figure(figsize=(10, 6))
        plt.plot(hist_iter, hist_score, linestyle='-', linewidth=1.5, alpha=0.8)
        plt.xlabel('Iteration')
        plt.ylabel('Objective Function Value')
        plt.title(f'Simulated Annealing Progress (T_init: {stats["temp_awal"]}, Rate: {stats["cooling_rate"]})')
        plt.grid(True, alpha=0.3)
        
        info = f"Iteration: {stats['total_iterasi']}\n"
        info += f"Initial: {stats['skor_awal']:.2f}\n"
        info += f"Final: {stats['skor_akhir']:.2f}\n"
        info += f"Time: {stats['durasi']:.2f}s"
        
        plt.text(0.02, 0.98, info, transform=plt.gca().transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Add final marker
        if hist_iter and hist_score:
            final_iter = hist_iter[-1]
            final_score = hist_score[-1]
            plt.axhline(y=final_score, color='orange', linestyle='--', linewidth=1)
            plt.scatter([final_iter], [final_score], color='red', zorder=5, s=50)
            
            # Calculate y-range for annotation placement
            y_min = min(hist_score)
            y_max = max(hist_score)
            yrange = y_max - y_min if y_max != y_min else 1
            
            plt.annotate(f'Final: {final_score:.2f}', xy=(final_iter, final_score),
                        xytext=(final_iter, final_score + 0.03 * yrange),
                        arrowprops=dict(arrowstyle='->', color='gray'),
                        fontsize=9, bbox=dict(boxstyle='round', fc='wheat', alpha=0.6))
        
        plt.tight_layout()
        plt.show()

    def plot_exp_delta_e(self, hist_iter, hist_exp_delta, stats):
        plt.figure(figsize=(12, 6))
        
        filtered_exp = []
        filtered_iter = []
        max_val = 100
        
        for i, val in enumerate(hist_exp_delta):
            if val != float('inf') and val <= max_val:
                filtered_exp.append(val)
                filtered_iter.append(hist_iter[i])
        
        if filtered_exp:
            plt.plot(filtered_iter, filtered_exp, 
                    color='darkgreen', linewidth=0.8, alpha=0.3, 
                    zorder=1)
            
            step = 1
            if len(filtered_iter) > 5000:
                step = len(filtered_iter) // 5000
            
            plt.scatter(filtered_iter[::step], filtered_exp[::step], 
                       marker='o', alpha=0.6, s=15, 
                       color='darkgreen', edgecolors='none',
                       label='$e^{\\Delta E/T}$', zorder=2)
        
        plt.xlabel('Iteration', fontsize=11)
        plt.ylabel('$e^{\\Delta E/T}$', fontsize=12)
        plt.title('Value of $e^{\\Delta E/T}$ vs Iteration (Simulated Annealing)', 
                 fontsize=12, fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        info = f"Total Iteration: {stats['total_iterasi']}\n"
        info += f"T Initial: {stats['temp_awal']}\n"
        info += f"T Final: {stats['temp_akhir']}\n"
        info += f"Cooling Rate: {stats['cooling_rate']}"
        
        plt.text(0.98, 0.98, info, transform=plt.gca().transAxes,
                fontsize=9, verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='lightyellow', 
                         edgecolor='darkorange', alpha=0.85))
        
        plt.legend(loc='upper left', fontsize=10)
        plt.tight_layout()
        plt.show()

    def plot_stuck_frequency(self, stats):
        plt.figure(figsize=(10, 5))
        
        stuck_cnt = stats.get('stuck_count', 0)
        total_iter = stats['total_iterasi']
        
        categories = ['Total Iteration', 'Stuck', 'Productive']
        values = [total_iter, stuck_cnt * 50, total_iter - (stuck_cnt * 50)]
        colors = ['skyblue', 'salmon', 'lightgreen']
        
        bars = plt.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
        
        for bar, val in zip(bars, values):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(val)}',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        plt.ylabel('Number of Iterations', fontsize=11)
        plt.title(f'Stuck Frequency in Local Optima (Total: {stuck_cnt} times)', 
                 fontsize=12, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='y')
        
        info = f"Stuck Frequency: {stuck_cnt} times\n"
        info += f"Total Iteration: {total_iter}\n"
        if total_iter > 0:
            stuck_rate = (stuck_cnt * 50 / total_iter) * 100
            info += f"Stuck Rate: {stuck_rate:.2f}%"
        
        plt.text(0.98, 0.98, info, transform=plt.gca().transAxes,
                fontsize=10, verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        plt.show()

    def visualisasi_lengkap_sa(self, stats):
        sol_awal = stats['solusi_awal']
        sol_akhir = stats['solusi_akhir']
        hist_iter = stats['history_iterasi']
        hist_skor = stats['history_skor']
        hist_exp_delta = stats['history_exp_delta']  # e^(ΔE/T)
        
        kapasitas = stats['kapasitas_kontainer']
        
        print("\n" + "="*70)
        print("VISUALISASI SIMULATED ANNEALING")
        print("="*70)
        
        # Plot 1: Grafik Progres Skor
        self.plot_progress_sa(hist_iter, hist_skor, stats)
        
        # Plot 2: Perbandingan Kontainer (Awal vs Akhir)
        self.plot_containers(sol_awal, sol_akhir, kapasitas)
        
        # Plot 3: e^(ΔE/T) vs Iterasi (SESUAI SPESIFIKASI!)
        self.plot_exp_delta_e(hist_iter, hist_exp_delta, stats)
        
        # Plot 4: Frekuensi Stuck di Local Optima (SESUAI SPESIFIKASI!)
        self.plot_stuck_frequency(stats)
        
        print("\n" + "="*70)
        print("SELESAI")
        print("="*70)