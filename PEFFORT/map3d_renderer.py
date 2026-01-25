"""
renderer_3DMAP.py - Rendering templates for 3D Map visualization

Handles HTML/CSS/JavaScript template generation for the 3D map.
Separated from business logic (core_3DMAP.py) and orchestration (builder_3DMAP.py).
"""

import json


def get_css_styles() -> str:
    """
    Return CSS styling for the 3D map interface.
    
    Returns:
        str: Complete CSS stylesheet
    """
    return """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #fff; }
        #map { position: absolute; top: 0; bottom: 180px; left: 310px; width: calc(100% - 310px); height: calc(100% - 180px); }
        #elevation-chart { position: absolute; bottom: 0; left: 310px; width: calc(100% - 310px); height: 180px; background: rgba(15,23,42,.95); overflow: hidden; }
        #resize-handle { position: absolute; top: -5px; left: 0; right: 0; width: 100%; height: 10px; cursor: ns-resize; background: transparent; z-index: 20; }
        #hover-tooltip { position: fixed; top: 10px; right: 20px; background: rgba(15,23,42,.95); padding: 12px 16px; border-radius: 8px; border: 1px solid rgba(255,255,255,.2); font-size: 12px; color: #fbbf24; z-index: 100; display: none; box-shadow: 0 4px 12px rgba(0,0,0,.5); }
        .info-panel { position: absolute; top: 20px; left: 20px; background: rgba(15,23,42,.95); padding: 20px; border-radius: 10px; border: 1px solid rgba(255,255,255,.2); font-size: 14px; max-width: 280px; z-index: 10; box-shadow: 0 4px 20px rgba(0,0,0,.4); }
        .info-panel h3 { color: #60a5fa; margin-bottom: 12px; font-size: 16px; }
        .info-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,.1); }
        .info-row:last-child { border-bottom: none; }
        .info-label { color: #9ca3af; font-weight: 500; }
        .info-value { color: #fbbf24; font-weight: 600; }
        .controls { position: absolute; bottom: 180px; right: 20px; display: flex; flex-direction: column; gap: 10px; z-index: 10; }
        .control-btn { background: #1e40af; color: white; border: none; padding: 10px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; transition: all .3s ease; box-shadow: 0 2px 8px rgba(0,0,0,.3); }
        .control-btn:hover { background: #1e3a8a; box-shadow: 0 4px 12px rgba(0,0,0,.4); }
        #styleSelect { background: #1e40af; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 13px; box-shadow: 0 2px 8px rgba(0,0,0,.3); }
        #sidebar { position: fixed; left: 0; top: 0; width: 310px; height: 100%; background: rgba(15,23,42,.98); border-right: 1px solid rgba(255,255,255,.2); z-index: 100; overflow-y: auto; padding: 20px; }
        #sidebar-close { position: absolute; top: 15px; right: 15px; background: #1e40af; color: white; border: none; width: 30px; height: 30px; border-radius: 50%; cursor: pointer; font-size: 18px; display: flex; align-items: center; justify-content: center; }
        #sidebar-close:hover { background: #1e3a8a; }
        .sidebar-section { margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,.1); }
        .sidebar-section:last-child { border-bottom: none; }
        .sidebar-title { color: #60a5fa; font-size: 13px; font-weight: 600; margin-bottom: 10px; }
        .sidebar-row { display: flex; justify-content: space-between; padding: 6px 0; font-size: 12px; color: #9ca3af; }
        .sidebar-label { color: #9ca3af; }
        .sidebar-value { color: #fbbf24; font-weight: 600; }
    """


def get_javascript_code(efforts_data_json: str, elevation_data_json: str, geojson_str: str, 
                        maptiler_key: str, center_lat: float, center_lon: float, zoom: int) -> str:
    """
    Generate the complete JavaScript code for map interaction and visualization.
    
    Args:
        efforts_data_json: JSON string of efforts data
        elevation_data_json: JSON string of elevation profile data
        geojson_str: JSON string of the GeoJSON traccia
        maptiler_key: MapTiler API key
        center_lat: Map center latitude
        center_lon: Map center longitude
        zoom: Initial zoom level
        
    Returns:
        str: Complete JavaScript code block
    """
    return f"""
        const styles = [
            {{ key: 'outdoor', name: 'Outdoor', url: `https://api.maptiler.com/maps/outdoor-v2/style.json?key={maptiler_key}` }},
            {{ key: 'streets', name: 'Streets', url: `https://api.maptiler.com/maps/streets-v2/style.json?key={maptiler_key}` }},
            {{ key: 'topo', name: 'Topo', url: `https://api.maptiler.com/maps/topo-v2/style.json?key={maptiler_key}` }},
            {{ key: 'bright', name: 'Bright', url: `https://api.maptiler.com/maps/bright-v2/style.json?key={maptiler_key}` }},
            {{ key: 'dark', name: 'Dark', url: `https://api.maptiler.com/maps/darkmatter/style.json?key={maptiler_key}` }},
            {{ key: 'winter', name: 'Winter', url: `https://api.maptiler.com/maps/winter/style.json?key={maptiler_key}` }},
            {{ key: 'satellite', name: 'Satellite', url: `https://api.maptiler.com/maps/satellite/style.json?key={maptiler_key}` }},
            {{ key: 'hybrid', name: 'Hybrid', url: `https://api.maptiler.com/maps/hybrid/style.json?key={maptiler_key}` }}
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
        const elevationData = JSON.parse('{elevation_data_json}');
        console.log('Elevation data:', elevationData);
        
        let activeEffortLayer = null;
        let activeEffortIdx = null;
        let currentEfforts = JSON.parse('{efforts_data_json}');

        function openEffortSidebar(idx) {{
            const effort = currentEfforts[idx];
            const sidebar = document.getElementById('sidebar');
            
            let hrHtml = effort.max_hr > 0 ? `
                <div class="sidebar-section">
                    <div class="sidebar-title">❤️ FREQUENZA CARDIACA</div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">Media</span>
                        <span class="sidebar-value">${{effort.avg_hr.toFixed(0)}} bpm</span>
                    </div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">Massima</span>
                        <span class="sidebar-value">${{effort.max_hr.toFixed(0)}} bpm</span>
                    </div>
                </div>
            ` : '';
            
            let vamHtml = effort.avg_grade >= 4.5 ? `
                <div class="sidebar-row">
                    <span class="sidebar-label">Teorico</span>
                    <span class="sidebar-value">${{effort.vam_teorico.toFixed(0)}} m/h</span>
                </div>
            ` : '';
            
            const html = `
                <div class="sidebar-section">
                    <div class="sidebar-title">⚡ POTENZA & RELATIVA & CADENZA & HR - Effort #${{idx + 1}}</div>
                    <div style="color: #60a5fa; font-size: 11px; margin-bottom: 8px; font-weight: 600;">Potenza</div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">Media</span>
                        <span class="sidebar-value">${{effort.avg.toFixed(0)}} W</span>
                    </div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">Best 5s</span>
                        <span class="sidebar-value">${{effort.best_5s}} W</span>
                    </div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">1ª metà</span>
                        <span class="sidebar-value">${{effort.watts_first.toFixed(0)}} W</span>
                    </div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">2ª metà</span>
                        <span class="sidebar-value">${{effort.watts_second.toFixed(0)}} W</span>
                    </div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">Rapporto</span>
                        <span class="sidebar-value">${{effort.watts_ratio.toFixed(2)}}</span>
                    </div>
                    
                    <div style="color: #60a5fa; font-size: 11px; margin-top: 12px; margin-bottom: 8px; font-weight: 600;">Potenza Relativa</div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">Media</span>
                        <span class="sidebar-value">${{effort.w_kg.toFixed(2)}} W/kg</span>
                    </div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">Best 5s</span>
                        <span class="sidebar-value">${{effort.best_5s_watt_kg.toFixed(2)}} W/kg</span>
                    </div>
                    
                    <div style="color: #60a5fa; font-size: 11px; margin-top: 12px; margin-bottom: 8px; font-weight: 600;">Cadenza & HR</div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">🌀 Cadenza</span>
                        <span class="sidebar-value">${{effort.avg_cadence.toFixed(0)}} rpm</span>
                    </div>
                    ${{hrHtml}}
                </div>
                
                <div class="sidebar-section">
                    <div class="sidebar-title">⏱️ TEMPO & DISTANZA & ALTIMETRIA & VAM</div>
                    <div style="color: #60a5fa; font-size: 11px; margin-bottom: 8px; font-weight: 600;">Tempo & Distanza</div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">Durata</span>
                        <span class="sidebar-value">${{effort.duration}}s</span>
                    </div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">Distanza</span>
                        <span class="sidebar-value">${{effort.distance_km.toFixed(2)}} km</span>
                    </div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">Velocità</span>
                        <span class="sidebar-value">${{effort.avg_speed.toFixed(1)}} km/h</span>
                    </div>
                    
                    <div style="color: #60a5fa; font-size: 11px; margin-top: 12px; margin-bottom: 8px; font-weight: 600;">Altimetria</div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">Guadagno</span>
                        <span class="sidebar-value">${{effort.elevation.toFixed(0)}} m</span>
                    </div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">Media</span>
                        <span class="sidebar-value">${{effort.avg_grade.toFixed(1)}}%</span>
                    </div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">Massima</span>
                        <span class="sidebar-value">${{effort.max_grade.toFixed(1)}}%</span>
                    </div>
                    
                    <div style="color: #60a5fa; font-size: 11px; margin-top: 12px; margin-bottom: 8px; font-weight: 600;">VAM</div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">Effettivo</span>
                        <span class="sidebar-value">${{effort.vam.toFixed(0)}} m/h</span>
                    </div>
                    ${{vamHtml}}
                </div>
                
                <div class="sidebar-section">
                    <div class="sidebar-title">🔋 LAVORO & 🔥 DENSITÀ ORARIA</div>
                    <div style="color: #60a5fa; font-size: 11px; margin-bottom: 8px; font-weight: 600;">Lavoro (kJ)</div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">Totale</span>
                        <span class="sidebar-value">${{effort.kj.toFixed(0)}} kJ</span>
                    </div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">Sopra CP</span>
                        <span class="sidebar-value">${{effort.kj_over_cp.toFixed(0)}} kJ</span>
                    </div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">Per kg</span>
                        <span class="sidebar-value">${{effort.kj_kg.toFixed(1)}} kJ/kg</span>
                    </div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">Per kg > CP</span>
                        <span class="sidebar-value">${{effort.kj_kg_over_cp.toFixed(1)}} kJ/kg</span>
                    </div>
                    
                    <div style="color: #60a5fa; font-size: 11px; margin-top: 12px; margin-bottom: 8px; font-weight: 600;">Densità Oraria (kJ/h/kg)</div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">Totale</span>
                        <span class="sidebar-value">${{effort.kj_h_kg.toFixed(1)}} kJ/h/kg</span>
                    </div>
                    <div class="sidebar-row">
                        <span class="sidebar-label">Sopra CP</span>
                        <span class="sidebar-value">${{effort.kj_h_kg_over_cp.toFixed(1)}} kJ/h/kg</span>
                    </div>
                </div>
            `;
            
            document.getElementById('sidebar-content').innerHTML = html;
            
            // Highlights chart e segmento mappa
            highlightEffortInChart(idx);
            removeActiveEffortLayer();
            activeEffortIdx = idx;
            const layerId = `effort-${{idx}}`;
            activeEffortLayer = layerId;
            
            const effort_data = currentEfforts[idx];
            const segmentGeoJSON = {{
                'type': 'Feature',
                'geometry': {{
                    'type': 'LineString',
                    'coordinates': effort_data.segment
                }}
            }};
            
            map.addSource(layerId, {{ 'type': 'geojson', 'data': segmentGeoJSON }});
            map.addLayer({{
                'id': layerId,
                'type': 'line',
                'source': layerId,
                'paint': {{
                    'line-color': effort_data.color,
                    'line-width': 6,
                    'line-opacity': 0.8
                }}
            }});
        }}

        function removeActiveEffortLayer() {{
            if (activeEffortLayer && map.getLayer(activeEffortLayer)) {{
                map.removeLayer(activeEffortLayer);
            }}
            if (activeEffortLayer && map.getSource(activeEffortLayer)) {{
                map.removeSource(activeEffortLayer);
            }}
            activeEffortLayer = null;
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
                hovertemplate: '<b>Distanza:</b> %{{x:.2f}} km<br><b>Altitudine:</b> %{{y:.0f}} m<extra></extra>'
            }};
            
            // Tracce effort sovrapposte
            const traces = [baseTrace];
            elevationData.efforts.forEach((effort, idx) => {{
                const effortTrace = {{
                    x: effort.distance,
                    y: effort.altitude,
                    type: 'scatter',
                    name: `Effort #${{idx + 1}}`,
                    line: {{ color: effort.color, width: 3 }},
                    mode: 'lines',
                    hovertemplate: '<b>Effort #' + (idx + 1) + '</b><br><b>Distanza:</b> %{{x:.2f}} km<br><b>Altitudine:</b> %{{y:.0f}} m<extra></extra>',
                    opacity: 1,
                    marker: {{ opacity: 0 }}
                }};
                traces.push(effortTrace);
            }});
            
            const layout = {{
                title: {{ text: '' }},
                xaxis: {{
                    title: '',
                    color: '#9ca3af',
                    gridcolor: 'rgba(255,255,255,0.1)',
                    showgrid: false
                }},
                yaxis: {{
                    title: '',
                    color: '#9ca3af',
                    gridcolor: 'rgba(255,255,255,0.1)',
                    showgrid: false
                }},
                plot_bgcolor: 'rgba(15,23,42,0)',
                paper_bgcolor: 'rgba(15,23,42,.95)',
                font: {{ family: 'Segoe UI', color: '#9ca3af', size: 11 }},
                margin: {{ l: 30, r: 10, t: 5, b: 20 }},
                hovermode: 'x unified',
                showlegend: false
            }};
            
            const config = {{ responsive: true, displayModeBar: false }};
            Plotly.newPlot('elevation-chart', traces, layout, config);
        }}

        function highlightEffortInChart(idx) {{
            // Modifica l'opacità delle tracce: quella selezionata a 1, altre a 0.2
            const update = {{
                opacity: elevationData.efforts.map((_, i) => i === idx ? 1 : 0.2),
                'line.width': elevationData.efforts.map((_, i) => i === idx ? 4 : 3)
            }};
            Plotly.restyle('elevation-chart', update, elevationData.efforts.map((_, i) => i + 1));
            
            // Aggiungi linee verticali all'inizio e fine dell'effort
            const effort = elevationData.efforts[idx];
            const startDist = effort.distance[0];
            const endDist = effort.distance[effort.distance.length - 1];
            const maxAlt = Math.max(...effort.altitude);
            
            // Crea annotation per info effort
            const infoBox = {{
                x: (startDist + endDist) / 2,
                y: maxAlt * 0.9,
                text: `<b>Effort #${{idx + 1}}</b><br>${{effort.avg.toFixed(0)}} W`,
                showarrow: false,
                bgcolor: effort.color,
                bordercolor: '#fff',
                borderwidth: 1,
                font: {{ color: '#fff', size: 11 }},
                align: 'center'
            }};
            
            Plotly.relayout('elevation-chart', {{
                annotations: [infoBox],
                'shapes[0]': {{
                    type: 'line',
                    x0: startDist,
                    x1: startDist,
                    y0: 0,
                    y1: maxAlt,
                    xref: 'x',
                    yref: 'y',
                    line: {{ color: effort.color, width: 2, dash: 'dash' }}
                }},
                'shapes[1]': {{
                    type: 'line',
                    x0: endDist,
                    x1: endDist,
                    y0: 0,
                    y1: maxAlt,
                    xref: 'x',
                    yref: 'y',
                    line: {{ color: effort.color, width: 2, dash: 'dash' }}
                }}
            }});
        }}

        function resetChartHighlight() {{
            // Torna all'opacità originale di tutte le tracce
            const update = {{
                opacity: elevationData.efforts.map(() => 1),
                'line.width': elevationData.efforts.map(() => 3)
            }};
            Plotly.restyle('elevation-chart', update, elevationData.efforts.map((_, i) => i + 1));
            
            // Rimuovi linee verticali e annotation
            Plotly.relayout('elevation-chart', {{
                annotations: [],
                shapes: []
            }});
        }}

        // Resize handle per l'altimetria
        let isResizing = false;
        const resizeHandle = document.getElementById('resize-handle');
        const elevationChart = document.getElementById('elevation-chart');
        const mapDiv = document.getElementById('map');

        resizeHandle.addEventListener('mousedown', (e) => {{
            isResizing = true;
            e.preventDefault();
        }});

        document.addEventListener('mousemove', (e) => {{
            if (!isResizing) return;
            
            const newHeight = Math.max(100, Math.min(400, window.innerHeight - e.clientY));
            
            elevationChart.style.height = newHeight + 'px';
            mapDiv.style.bottom = newHeight + 'px';
            mapDiv.style.height = 'calc(100% - ' + newHeight + 'px)';
            
            // Ridisegna i grafici
            Plotly.Plots.resize('elevation-chart');
        }});

        document.addEventListener('mouseup', () => {{
            isResizing = false;
        }});

        function addTerrain() {{
            try {{
                if (!map.getSource('terrain-dem')) {{
                    map.addSource('terrain-dem', {{
                        'type': 'raster-dem',
                        'url': `https://api.maptiler.com/tiles/terrain-rgb/tiles.json?key={maptiler_key}`,
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
            const efforts = JSON.parse('{efforts_data_json}');
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
                    .setPopup(new maplibregl.Popup({{ anchor: 'top', offset: [0, 15], maxWidth: 250 }}).setHTML(`
                        <div style="padding: 10px; font-size: 12px; color: #9ca3af; background: rgba(15,23,42,.95);">
                            <b style="color: #60a5fa;">Effort #${{idx + 1}}</b><br>
                            <div style="border-top: 1px solid rgba(255,255,255,.2); margin: 6px 0; padding-top: 6px;">
                                <div><b>⚡ ${{effort.avg.toFixed(0)}} W</b> | 🌀 ${{effort.avg_cadence.toFixed(0)}} rpm</div>
                                <div>⏱️ ${{effort.duration}}s | 🚴‍♂️ ${{effort.avg_speed.toFixed(1)}} km/h</div>
                            </div>
                        </div>
                    `))
                    .addTo(map);
                
                // Click sul marker apre subito la sidebar
                el.addEventListener('click', () => {{
                    openEffortSidebar(idx);
                    marker.getPopup().addTo(map);
                }});
            }});
            console.log('Markers added');
            
            // Disegna il grafico altimetrico totale
            drawFullElevationChart();
        }});

        map.on('error', (e) => {{ console.error('Map error:', e); }});

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
        
        // Event listener per chiudere la sidebar
        document.getElementById('sidebar-close').addEventListener('click', () => {{
            removeActiveEffortLayer();
            activeEffortIdx = null;
            resetChartHighlight();
            document.getElementById('sidebar-content').innerHTML = '';
        }});

        // Initialize style name on first load
        map.on('load', () => {{ updateStyleName(); }});
    """


def generate_3d_map_html(efforts_data_json: str, elevation_data_json: str, geojson_str: str,
                         maptiler_key: str, center_lat: float, center_lon: float, zoom: int,
                         distance_km: float) -> str:
    """
    Generate the complete HTML document for the 3D map visualization.
    
    Args:
        efforts_data_json: JSON string of efforts data
        elevation_data_json: JSON string of elevation profile data
        geojson_str: JSON string of the GeoJSON traccia
        maptiler_key: MapTiler API key
        center_lat: Map center latitude
        center_lon: Map center longitude
        zoom: Initial zoom level
        distance_km: Total track distance in km
        
    Returns:
        str: Complete HTML document
    """
    css_styles = get_css_styles()
    javascript_code = get_javascript_code(efforts_data_json, elevation_data_json, geojson_str, 
                                         maptiler_key, center_lat, center_lon, zoom)
    
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
        {css_styles}
    </style>
</head>
<body>
    <div id='hover-tooltip'></div>
    <div id='map'></div>
    <div id='elevation-chart'>
        <div id='resize-handle'></div>
    </div>
    
    <div id='sidebar'>
        <button id='sidebar-close'>✕</button>
        <div id='sidebar-content'></div>
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
        {javascript_code}
    </script>
</body>
</html>"""
    
    return html
