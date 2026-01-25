# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
EXPORTER 3D MAP - Generazione mappa 3D interattiva con traccia e terrain
Vista 3D della traccia con altimetria in stile "drone view"
"""

import json
import logging
import numpy as np
import pandas as pd
import bisect
from typing import List, Tuple, Dict, Any

logger = logging.getLogger(__name__)

# Mapbox token pubblico per tile e terrain
MAPBOX_TOKEN = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"
# MapTiler API key (provided by user)
MAPTILER_KEY = "Q8Zxgdc7Nfnb2aiu8p72"


def export_traccia_geojson(df: pd.DataFrame) -> Tuple[dict, List[int]]:
    """
    Esporta la traccia in formato GeoJSON LineString con altitudine.
    
    Args:
        df: DataFrame con colonne position_lat, position_long, altitude
        
    Returns:
        Dict GeoJSON FeatureCollection con traccia LineString
    """
    if 'position_lat' not in df.columns or 'position_long' not in df.columns:
        raise ValueError("DataFrame deve contenere position_lat e position_long")
    
    lat = df['position_lat'].values
    lon = df['position_long'].values
    alt = df['altitude'].values if 'altitude' in df.columns else [0] * len(lat)
    
    # Crea coordinate [lon, lat, alt] (GeoJSON format)
    coordinates = [[float(lon[i]), float(lat[i]), float(alt[i])] for i in range(len(lat))]
    # Mantieni mappatura verso indici originali del DataFrame filtrato
    orig_indices = df.index.to_list()
    
    feature = {
        "type": "Feature",
        "properties": {
            "name": "Traccia ciclo",
            "description": f"Traccia con {len(coordinates)} punti"
        },
        "geometry": {
            "type": "LineString",
            "coordinates": coordinates
        }
    }
    
    return {
        "type": "FeatureCollection",
        "features": [feature]
    }, orig_indices


def generate_3d_map_html(df: pd.DataFrame, efforts: List[Tuple[int, int, float]], 
                         ftp: float, weight: float) -> str:
    """
    Genera HTML interattivo per visualizzare traccia 3D con Mapbox GL JS.
    
    Args:
        df: DataFrame con dati attività (lat, lon, alt, power, etc)
        efforts: Lista efforts (start, end, avg_power)
        ftp: Functional Threshold Power
        weight: Peso atleta
        
    Returns:
        String HTML completo per visualizzazione 3D
    """
    try:
        logger.info("Generazione mappa 3D...")
        
        # Filtra coordinate non valide (NaN, fuori range, 0,0)
        lat_all = df['position_lat'].values
        lon_all = df['position_long'].values
        nan_mask = (~np.isnan(lat_all)) & (~np.isnan(lon_all))
        range_mask = (np.abs(lat_all) <= 90) & (np.abs(lon_all) <= 180)
        zero_mask = ~((np.abs(lat_all) < 1e-9) & (np.abs(lon_all) < 1e-9))
        valid_mask = nan_mask & range_mask & zero_mask

        df_valid = df.loc[valid_mask].copy()
        logger.info(f"Dati geografici: {len(df_valid)} punti validi su {len(df)} totali")

        # Estrai traccia GeoJSON dal DF filtrato e mappatura indici originali
        geojson_data, orig_indices = export_traccia_geojson(df_valid)
        geojson_str = json.dumps(geojson_data)

        # Calcola bounds per centramento mappa
        lat = df_valid['position_lat'].values
        lon = df_valid['position_long'].values
        
        # Valida dati geografici
        if len(lat) == 0 or len(lon) == 0:
            raise ValueError("Nessun dato geografico valido disponibile")
        
        center_lat = float(np.nanmean([lat.min(), lat.max()]))
        center_lon = float(np.nanmean([lon.min(), lon.max()]))
        
        # Valida NaN
        if np.isnan(center_lat) or np.isnan(center_lon):
            raise ValueError(f"Coordinate non valide: lat={center_lat}, lon={center_lon}")
        
        # Calcola zoom basato sull'extent
        lat_range = float(lat.max() - lat.min())
        lon_range = float(lon.max() - lon.min())
        max_range = float(max(lat_range, lon_range))
        
        if max_range < 0.01:
            zoom = 15
        elif max_range < 0.05:
            zoom = 14
        elif max_range < 0.1:
            zoom = 13
        elif max_range < 0.5:
            zoom = 12
        else:
            zoom = 11
        
        # Info stats
        if 'altitude' in df.columns:
            alt_min = df['altitude'].min()
            alt_max = df['altitude'].max()
            elevation_gain = alt_max - alt_min
        else:
            elevation_gain = 0
            alt_min = 0
            alt_max = 0
        
        power = df['power'].values
        max_power = power.max() if len(power) > 0 else 0
        avg_power = power.mean() if len(power) > 0 else 0
        distance_km = (df['distance'].values[-1] - df['distance'].values[0]) / 1000 if 'distance' in df.columns else 0
        
        # Prepara dati efforts per JavaScript (adatta indice in base ai punti validi)
        efforts_list: List[Dict[str, Any]] = []
        for s, e, avg in efforts[:10]:
            # trova primo indice valido >= s
            pos = bisect.bisect_left(orig_indices, s)
            if pos >= len(orig_indices):
                pos = len(orig_indices) - 1
            if pos < 0:
                pos = 0
            efforts_list.append({'pos': int(pos), 'avg': float(avg)})
        efforts_data = json.dumps(efforts_list)
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8' />
    <title>3D Map View - {distance_km:.1f} km</title>
    <meta name='viewport' content='initial-scale=1,maximum-scale=1,user-scalable=no' />
    <script src='https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js'></script>
    <link href='https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css' rel='stylesheet' />
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #fff; }}
        #map {{ position: absolute; top: 0; bottom: 0; width: 100%; height: 100%; }}
        .info-panel {{ position: absolute; top: 20px; left: 20px; background: rgba(15,23,42,.95); padding: 20px; border-radius: 10px; border: 1px solid rgba(255,255,255,.2); font-size: 14px; max-width: 280px; z-index: 10; box-shadow: 0 4px 20px rgba(0,0,0,.4); }}
        .info-panel h3 {{ color: #60a5fa; margin-bottom: 12px; font-size: 16px; }}
        .info-row {{ display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,.1); }}
        .info-row:last-child {{ border-bottom: none; }}
        .info-label {{ color: #9ca3af; font-weight: 500; }}
        .info-value {{ color: #fbbf24; font-weight: 600; }}
        .controls {{ position: absolute; bottom: 20px; right: 20px; display: flex; flex-direction: column; gap: 10px; z-index: 10; }}
        .control-btn {{ background: #1e40af; color: white; border: none; padding: 10px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; transition: all .3s ease; box-shadow: 0 2px 8px rgba(0,0,0,.3); }}
        .control-btn:hover {{ background: #1e3a8a; box-shadow: 0 4px 12px rgba(0,0,0,.4); }}
        #styleSelect {{ background: #1e40af; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 13px; box-shadow: 0 2px 8px rgba(0,0,0,.3); }}
        .legend {{ position: absolute; bottom: 20px; right: 20px; background: rgba(15,23,42,.95); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,.2); font-size: 12px; z-index: 10; }}
        .legend-item {{ display: flex; align-items: center; margin: 6px 0; }}
        .legend-color {{ width: 20px; height: 3px; margin-right: 8px; border-radius: 2px; }}
    </style>
</head>
<body>
    <div id='map'></div>

    <div class='info-panel'>
        <h3>📊 Traccia 3D</h3>
        <div class='info-row'><span class='info-label'>Distanza:</span><span class='info-value'>{distance_km:.2f} km</span></div>
        <div class='info-row'><span class='info-label'>Altitudine:</span><span class='info-value'>{elevation_gain:.0f} m</span></div>
        <div class='info-row'><span class='info-label'>Power max:</span><span class='info-value'>{max_power:.0f} W</span></div>
        <div class='info-row'><span class='info-label'>Power med:</span><span class='info-value'>{avg_power:.0f} W</span></div>
        <div class='info-row'><span class='info-label'>Efforts:</span><span class='info-value'>{len(efforts)}</span></div>
    </div>

    <div class='controls'>
        <select id='styleSelect'>
            <option value='0'>Outdoor</option>
            <option value='1'>Streets</option>
            <option value='2'>Topo</option>
            <option value='3'>Bright</option>
            <option value='4'>Dark</option>
            <option value='5'>Winter</option>
            <option value='6'>Satellite</option>
            <option value='7'>Hybrid</option>
        </select>
        <button class='control-btn' onclick='resetView()'>🎯 Reset View</button>
    </div>

    <script>
        const styles = [
            {{ key: 'outdoor', name: 'Outdoor', url: `https://api.maptiler.com/maps/outdoor-v2/style.json?key={MAPTILER_KEY}` }},
            {{ key: 'streets', name: 'Streets', url: `https://api.maptiler.com/maps/streets-v2/style.json?key={MAPTILER_KEY}` }},
            {{ key: 'topo', name: 'Topo', url: `https://api.maptiler.com/maps/topo-v2/style.json?key={MAPTILER_KEY}` }},
            {{ key: 'bright', name: 'Bright', url: `https://api.maptiler.com/maps/bright-v2/style.json?key={MAPTILER_KEY}` }},
            {{ key: 'dark', name: 'Dark', url: `https://api.maptiler.com/maps/darkmatter/style.json?key={MAPTILER_KEY}` }},
            {{ key: 'winter', name: 'Winter', url: `https://api.maptiler.com/maps/winter/style.json?key={MAPTILER_KEY}` }},
            {{ key: 'satellite', name: 'Satellite', url: `https://api.maptiler.com/maps/satellite/style.json?key={MAPTILER_KEY}` }},
            {{ key: 'hybrid', name: 'Hybrid', url: `https://api.maptiler.com/maps/hybrid/style.json?key={MAPTILER_KEY}` }}
        ];
        let currentStyleIndex = 0;

        const map = new maplibregl.Map({{
            container: 'map',
            style: styles[currentStyleIndex].url,
            center: [{center_lon}, {center_lat}],
            zoom: {zoom},
            pitch: 45,
            bearing: 0
        }});
        try {{ map.setProjection({{ name: 'globe' }}); }} catch(e) {{ console.warn('Projection set failed:', e); }}
        map.addControl(new maplibregl.NavigationControl());

        const tracceGeoJSON = {geojson_str};
        console.log('Traccia GeoJSON caricata:', tracceGeoJSON);

        function addTerrain() {{
            try {{
                if (!map.getSource('terrain-dem')) {{
                    map.addSource('terrain-dem', {{
                        'type': 'raster-dem',
                        'url': `https://api.maptiler.com/tiles/terrain-rgb/tiles.json?key={MAPTILER_KEY}`,
                        'tileSize': 256
                    }});
                }}
                map.setTerrain({{ 'source': 'terrain-dem', 'exaggeration': 1.5 }});
                console.log('Terrain enabled');
            }} catch(e) {{ console.warn('Terrain not available:', e); }}
        }}

        function addOverlays() {{
            if (!map.getSource('traccia')) {{
                map.addSource('traccia', {{ 'type': 'geojson', 'data': tracceGeoJSON }});
            }} else {{
                map.getSource('traccia').setData(tracceGeoJSON);
            }}
            if (!map.getLayer('traccia-line')) {{
                map.addLayer({{
                    'id': 'traccia-line',
                    'type': 'line',
                    'source': 'traccia',
                    'paint': {{ 'line-color': '#FFB500', 'line-width': 4, 'line-opacity': 0.9 }}
                }});
            }}
            console.log('Overlays added');
        }}

        map.on('load', () => {{
            console.log('MAP LOAD EVENT FIRED');
            addTerrain();
            addOverlays();

            // Aggiungi marcatori per gli efforts (pos indicizza coordinates filtrate)
            const efforts = JSON.parse('{efforts_data}');
            console.log('Efforts loaded:', efforts);

            efforts.forEach(function(effort, idx) {{
                const feature = tracceGeoJSON.features[0];
                if (!feature || !feature.geometry || !feature.geometry.coordinates) {{
                    console.error('Invalid feature or coordinates');
                    return;
                }}
                const coordStart = feature.geometry.coordinates[effort.pos];
                if (!coordStart) {{
                    console.warn(`No coordinate at pos index ${{effort.pos}}`);
                    return;
                }}
                const marker = new maplibregl.Marker({{ color: '#60a5fa' }})
                    .setLngLat([coordStart[0], coordStart[1]])
                    .setPopup(new maplibregl.Popup().setHTML(`<b>Effort #${{idx + 1}}</b><br>${{effort.avg.toFixed(0)}} W`))
                    .addTo(map);
            }});
            console.log('Markers added');
        }});

        map.on('error', (e) => {{ console.error('Map error:', e); }})

        function updateStyleName() {{
            document.getElementById('styleSelect').value = currentStyleIndex;
        }}

        function applyStyle(newIndex) {{
            currentStyleIndex = (newIndex + styles.length) % styles.length;
            const url = styles[currentStyleIndex].url;
            map.setStyle(url);
            const onStyle = () => {{
                addTerrain();
                addOverlays();
                updateStyleName();
                map.off('styledata', onStyle);
            }};
            map.on('styledata', onStyle);
        }}

        function nextStyle() {{ applyStyle(currentStyleIndex + 1); }}
        function prevStyle() {{ applyStyle(currentStyleIndex - 1); }}
        
        // Event listener per il dropdown
        document.getElementById('styleSelect').addEventListener('change', (e) => {{
            applyStyle(parseInt(e.target.value));
        }});

        function resetView() {{
            map.flyTo({{ center: [{center_lon}, {center_lat}], zoom: {zoom}, pitch: 45, bearing: 0, duration: 1500 }});
        }}

        // Initialize style name on first load
        map.on('load', () => {{ updateStyleName(); }});
    </script>
</body>
</html>"""
        
        logger.info("Mappa 3D generata")
        return html
        
    except Exception as e:
        logger.error(f"Errore generazione mappa 3D: {e}", exc_info=True)
        raise
