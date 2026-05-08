import py5
import pandas as pd
import hashlib
import json
from pathlib import Path
import numpy as np

# Load Data and Manifest
DATA_PATH = Path("sphy_data/sphy_simulation.parquet")
MANIFEST_PATH = Path("sphy_data/sphy_manifest.json")

# SPHY Constants para o mapeamento de cor (Deywe Spectrum)
LAMBDA, G, GAMMA_S = 0.8, 1.5, 0.5
S_MIN = (LAMBDA * G) / (1 + GAMMA_S * 0.25)
S_MAX = LAMBDA * G

df = None
manifest = None
current_frame = 0
total_frames = 0
integrity_status = "WAITING"

def setup():
    global df, manifest, total_frames
    py5.size(1920, 1080, py5.P3D)
    py5.background(0)
    py5.color_mode(py5.HSB, 360, 100, 100)
    py5.window_title("Harpia Engine - SPHY Parquet Auditor & Visualizer")
    
    if DATA_PATH.exists() and MANIFEST_PATH.exists():
        df = pd.read_parquet(DATA_PATH)
        with open(MANIFEST_PATH, 'r') as f:
            manifest = json.load(f)
        total_frames = int(df['frame_idx'].max() + 1)
    else:
        print("ERROR: Dataset files not found. Run generator first.")
        py5.exit_sketch()

def draw():
    global current_frame, integrity_status
    
    # Rastro cinético (Efeito Ghosting SPHY)
    py5.fill(0, 0, 0, 15)
    py5.rect(0, 0, py5.width, py5.height)
    
    # Extrai exatamente os dados do frame atual
    frame_data = df[df['frame_idx'] == current_frame]
    
    # --- AUDITORIA DETERMINÍSTICA (A Chave da Soberania) ---
    # Convertemos para dicionário e forçamos ordenação para bater o SHA-256
    frame_dict = frame_data.to_dict(orient='records')
    frame_json = json.dumps(frame_dict, sort_keys=True).encode()
    calculated_hash = hashlib.sha256(frame_json).hexdigest()
    
    expected_hash = manifest["frames"][current_frame]["hash"]
    
    # Validação Rigorosa de Integridade
    if calculated_hash == expected_hash:
        integrity_status = "VERIFIED (SHA-256 MATCH)"
        status_color = (120, 80, 100) # Verde Soberano
    else:
        integrity_status = "CRITICAL: HASH MISMATCH"
        status_color = (0, 100, 100) # Vermelho (Corrupção detectada)

    # Renderização das Partículas (Recuperando o Lilás/Ciano)
    x_coords = frame_data['x'].values * py5.width
    y_coords = frame_data['y'].values * py5.height
    s_phi_values = frame_data['s_phi'].values
    
    for i in range(len(x_coords)):
        hue = py5.remap(s_phi_values[i], S_MIN, S_MAX, 300, 190)
        py5.stroke(hue, 90, 100, 180)
        py5.stroke_weight(1.5)
        py5.point(x_coords[i], y_coords[i])
    
    # HUD Interface com Estabilidade e Auditoria
    avg_stability = np.mean(s_phi_values)
    render_hud(calculated_hash, status_color, avg_stability)
    
    # Ciclo de Frames
    current_frame = (current_frame + 1) % total_frames

def render_hud(h, col, stability):
    py5.no_stroke()
    py5.fill(0, 0, 0, 200)
    py5.rect(10, 10, 850, 130) # Ajustado para caber o hash longo
    
    py5.fill(0, 0, 100)
    py5.text_size(20)
    py5.text("SPHY CORE: GRAVITATIONAL STABILIZER (PARQUET)", 25, 40)
    
    # Estabilidade S(Φ)
    py5.fill(180, 80, 100) # Ciano
    py5.text(f"STABILITY S(Φ): {stability:.6f}", 25, 65)
    
    # Status de Integridade SHA-256
    py5.fill(col[0], col[1], col[2])
    py5.text(f"INTEGRITY: {integrity_status}", 25, 95)
    
    # Hash SHA-256 (O carimbo de verdade)
    py5.fill(45, 90, 100) # Amarelo de Paridade
    py5.text_size(13)
    py5.text(f"FRAME SHA-256: {h}", 25, 120)

if __name__ == "__main__":
    py5.run_sketch()
