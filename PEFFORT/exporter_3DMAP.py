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
from .engine_PEFFORT import get_zone_color

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
        
        # Prepara dati per il grafico altimetrico totale
        alt_values = df_valid['altitude'].values if 'altitude' in df_valid.columns else np.zeros(len(df_valid))
        dist_km_values = df_valid['distance_km'].values if 'distance_km' in df_valid.columns else np.zeros(len(df_valid))
        alt_total = alt_values.tolist()
        dist_total = dist_km_values.tolist()
        
        # Prepara dati efforts per JavaScript (adatta indice in base ai punti validi)
        efforts_list: List[Dict[str, Any]] = []
        coords = geojson_data['features'][0]['geometry']['coordinates']
        
        for s, e, avg in efforts:  # Prendi TUTTI gli effort, non solo i primi 10
            # Trovi il primo indice filtrato che è >= s
            pos_start = 0
            for idx_f, idx_orig in enumerate(orig_indices):
                if idx_orig >= s:
                    pos_start = idx_f
                    break
            
            # Trovi il primo indice filtrato che è >= e
            pos_end = len(orig_indices) - 1
            for idx_f, idx_orig in enumerate(orig_indices):
                if idx_orig >= e:
                    pos_end = idx_f
                    break
            
            # Sicurezza: assicurati che start < end
            if pos_end < pos_start:
                pos_end = pos_start + 1
            
            # Assicurati di non andare oltre i bounds
            if pos_end >= len(coords):
                pos_end = len(coords) - 1
            
            zone_color = get_zone_color(avg, ftp)
            # Estrai segmento di coordinate per questo effort
            segment_coords = coords[pos_start:pos_end+1]
            segment_alt = alt_values[pos_start:pos_end+1].tolist() if pos_end < len(alt_values) else []
            segment_dist = dist_km_values[pos_start:pos_end+1].tolist() if pos_end < len(dist_km_values) else []
            
            if len(segment_coords) > 0:  # Solo se il segmento ha dati
                efforts_list.append({
                    'pos': int(pos_start), 
                    'start': int(pos_start),
                    'end': int(pos_end),
                    'avg': float(avg),
                    'color': zone_color,
                    'segment': segment_coords,
                    'altitude': segment_alt,
                    'distance': segment_dist
                })
        efforts_data = json.dumps(efforts_list)
        elevation_graph_data = json.dumps({'distance': dist_total, 'altitude': alt_total, 'efforts': efforts_list})
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8' />
    <title>3D Map View - {distance_km:.1f} km</title>
    <meta name='viewport' content='initial-scale=1,maximum-scale=1,user-scalable=no' />
    <script src='https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js'></script>
    <link href='https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css' rel='stylesheet' />
    <script src='https://cdn.plot.ly/plotly-latest.min.js'></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #fff; }}
        #map {{ position: absolute; top: 0; bottom: 320px; width: 100%; height: calc(100% - 320px); }}
        #elevation-chart {{ position: absolute; bottom: 0; width: 100%; height: 300px; background: rgba(15,23,42,.95); border-top: 1px solid rgba(255,255,255,.2); }}
        .info-panel {{ position: absolute; top: 20px; left: 20px; background: rgba(15,23,42,.95); padding: 20px; border-radius: 10px; border: 1px solid rgba(255,255,255,.2); font-size: 14px; max-width: 280px; z-index: 10; box-shadow: 0 4px 20px rgba(0,0,0,.4); }}
        .info-panel h3 {{ color: #60a5fa; margin-bottom: 12px; font-size: 16px; }}
        .info-row {{ display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,.1); }}
        .info-row:last-child {{ border-bottom: none; }}
        .info-label {{ color: #9ca3af; font-weight: 500; }}
        .info-value {{ color: #fbbf24; font-weight: 600; }}
        .controls {{ position: absolute; bottom: 320px; right: 20px; display: flex; flex-direction: column; gap: 10px; z-index: 10; }}
        .control-btn {{ background: #1e40af; color: white; border: none; padding: 10px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; transition: all .3s ease; box-shadow: 0 2px 8px rgba(0,0,0,.3); }}
        .control-btn:hover {{ background: #1e3a8a; box-shadow: 0 4px 12px rgba(0,0,0,.4); }}
        #styleSelect {{ background: #1e40af; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 13px; box-shadow: 0 2px 8px rgba(0,0,0,.3); }}
    </style>
</head>
<body>
    <div id='map'></div>
    <div id='elevation-chart'></div>

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
        const elevationData = JSON.parse('{elevation_graph_data}');
        console.log('Elevation data:', elevationData);
        
        let activeEffortLayer = null;
        let activeEffortIdx = null;

        function removeActiveEffortLayer() {{
            if (activeEffortLayer && map.getLayer(activeEffortLayer)) {{
                map.removeLayer(activeEffortLayer);
            }}
            if (activeEffortLayer && map.getSource(activeEffortLayer)) {{
                map.removeSource(activeEffortLayer);
            }}
            activeEffortLayer = null;
        }}

        function drawElevationChart(effort, idx) {{
            const distance = effort.distance;
            const altitude = effort.altitude;
            
            const trace = {{
                x: distance,
                y: altitude,
                fill: 'tozeroy',
                type: 'scatter',
                name: `Effort #${{idx + 1}}`,
                line: {{ color: effort.color, width: 2 }},
                fillcolor: effort.color.replace('#', 'rgba(') + ', 0.3)'
            }};
            
            const layout = {{
                title: {{
                    text: `Profilo Altimetrico - Effort #${{idx + 1}} | Potenza: ${{effort.avg.toFixed(0)}}W`,
                    font: {{ color: '#fff', size: 14 }}
                }},
                xaxis: {{
                    title: 'Distanza (km)',
                    color: '#9ca3af',
                    gridcolor: 'rgba(255,255,255,0.1)'
                }},
                yaxis: {{
                    title: 'Altitudine (m)',
                    color: '#9ca3af',
                    gridcolor: 'rgba(255,255,255,0.1)'
                }},
                plot_bgcolor: 'rgba(15,23,42,0)',
                paper_bgcolor: 'rgba(15,23,42,.95)',
                font: {{ family: 'Segoe UI', color: '#9ca3af' }},
                margin: {{ l: 50, r: 20, t: 50, b: 40 }},
                hovermode: false
            }};
            
            const config = {{ responsive: true, displayModeBar: false }};
            Plotly.newPlot('elevation-chart', [trace], layout, config);
        }}

        function drawFullElevationChart() {{
            // Traccia base altimetria con fill
            const baseTrace = {{
                x: elevationData.distance,
                y: elevationData.altitude,
                fill: 'tozeroy',
                type: 'scatter',
                name: 'Altitudine',
                line: {{ color: '#9ca3af', width: 1 }},
                fillcolor: 'rgba(156,163,175,0.3)',
                hoverinfo: 'skip'
            }};
            
            // Tracce effort sovrapposte
            const traces = [baseTrace];
            elevationData.efforts.forEach((effort, idx) => {{
                const effortTrace = {{
                    x: effort.distance,
                    y: effort.altitude,
                    type: 'scatter',
                    name: `Effort #${{idx + 1}}`,
                    line: {{ color: effort.color, width: 2 }},
                    mode: 'lines',
                    hoverinfo: 'skip',
                    opacity: 0.7,
                    marker: {{ opacity: 0 }}
                }};
                traces.push(effortTrace);
            }});
            
            const layout = {{
                title: {{
                    text: 'Profilo Altimetrico Completo',
                    font: {{ color: '#fff', size: 14 }}
                }},
                xaxis: {{
                    title: 'Distanza (km)',
                    color: '#9ca3af',
                    gridcolor: 'rgba(255,255,255,0.1)'
                }},
                yaxis: {{
                    title: 'Altitudine (m)',
                    color: '#9ca3af',
                    gridcolor: 'rgba(255,255,255,0.1)'
                }},
                plot_bgcolor: 'rgba(15,23,42,0)',
                paper_bgcolor: 'rgba(15,23,42,.95)',
                font: {{ family: 'Segoe UI', color: '#9ca3af' }},
                margin: {{ l: 50, r: 20, t: 50, b: 40 }},
                hovermode: false,
                showlegend: false
            }};
            
            const config = {{ responsive: true, displayModeBar: false }};
            Plotly.newPlot('elevation-chart', traces, layout, config);
        }}

        function highlightEffortInChart(idx) {{
            // Modifica l'opacità delle tracce: quella selezionata a 1, altre a 0.3
            const update = {{
                opacity: elevationData.efforts.map((_, i) => i === idx ? 1 : 0.3)
            }};
            Plotly.restyle('elevation-chart', update, elevationData.efforts.map((_, i) => i + 1));
        }}

        function resetChartHighlight() {{
            // Torna all'opacità originale di tutte le tracce
            const update = {{
                opacity: elevationData.efforts.map(() => 0.7)
            }};
            Plotly.restyle('elevation-chart', update, elevationData.efforts.map((_, i) => i + 1));
        }}

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

            // Aggiungi marcatori per gli efforts con SVG custom colorati per zona
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
                
                // Crea elemento SVG custom per il marker colorato
                const el = document.createElement('div');
                el.style.width = '30px';
                el.style.height = '30px';
                el.style.borderRadius = '50%';
                el.style.backgroundColor = effort.color;
                el.style.border = '3px solid white';
                el.style.boxShadow = `0 2px 8px rgba(0,0,0,.6), 0 0 0 2px ${{effort.color}}`;
                el.style.cursor = 'pointer';
                el.style.display = 'flex';
                el.style.alignItems = 'center';
                el.style.justifyContent = 'center';
                el.style.fontSize = '14px';
                el.style.fontWeight = 'bold';
                el.style.color = 'white';
                el.innerHTML = (idx + 1);
                
                const marker = new maplibregl.Marker({{ element: el }})
                    .setLngLat([coordStart[0], coordStart[1]])
                    .setPopup(new maplibregl.Popup({{ anchor: 'bottom', offset: [0, -15] }}).setHTML(`
                        <div style="padding: 8px; min-width: 160px;">
                            <b style="color: #60a5fa;">Effort #${{idx + 1}}</b><br>
                            <span style="color: #fbbf24;">Potenza: ${{effort.avg.toFixed(0)}} W</span><br>
                            <span style="color: ${{effort.color}};">●●●●● ${{effort.avg.toFixed(0)}} W</span><br>
                            <span style="font-size: 11px; color: #9ca3af;">Visualizza traccia</span>
                        </div>
                    `))
                    .addTo(map);
                
                // Aggiungi event listener per mostrare/nascondere il segmento
                marker.getPopup().on('open', () => {{
                    removeActiveEffortLayer();
                    activeEffortIdx = idx;
                    const layerId = `effort-${{idx}}`;
                    activeEffortLayer = layerId;
                    
                    const segmentGeoJSON = {{
                        'type': 'Feature',
                        'geometry': {{
                            'type': 'LineString',
                            'coordinates': effort.segment
                        }}
                    }};
                    
                    map.addSource(layerId, {{ 'type': 'geojson', 'data': segmentGeoJSON }});
                    map.addLayer({{
                        'id': layerId,
                        'type': 'line',
                        'source': layerId,
                        'paint': {{
                            'line-color': effort.color,
                            'line-width': 6,
                            'line-opacity': 0.8
                        }}
                    }});
                    
                    // Evidenzia la traccia nel grafico altimetrico
                    highlightEffortInChart(idx);
                    console.log(`Segment ${{idx}} displayed and highlighted`);
                }});
                
                marker.getPopup().on('close', () => {{
                    removeActiveEffortLayer();
                    activeEffortIdx = null;
                    resetChartHighlight();
                }});
            }});
            console.log('Markers added');
            
            // Disegna il grafico altimetrico totale
            drawFullElevationChart();
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
