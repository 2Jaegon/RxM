import streamlit as st
import streamlit.components.v1 as components


def render_process_visualization():
    # Corrected Data Topology:
    # 1. Factory Equipments -> AI Node (Red Circle)
    # 2. RAG Vector DB -> AI Node (Red Circle)
    # 3. AI Node -> Factory Equipment (Prescriptive Feedback)
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Pretendard', -apple-system, sans-serif; user-select: none; }
            body {
                background: #0B0D10;
                color: #F1F5F9;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                padding: 0.8rem;
                overflow: hidden;
            }

            /* Toolbar Header */
            .n8n-toolbar {
                width: 100%;
                max-width: 1060px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: rgba(15, 23, 42, 0.9);
                border: 1px solid rgba(52, 211, 153, 0.25);
                padding: 0.5rem 1rem;
                border-radius: 12px;
                margin-bottom: 0.6rem;
                backdrop-filter: blur(12px);
            }

            .toolbar-title {
                font-size: 0.85rem;
                font-weight: 800;
                color: #34D399;
                display: flex;
                align-items: center;
                gap: 0.4rem;
            }

            .toolbar-actions {
                display: flex;
                gap: 0.4rem;
            }

            .tb-btn {
                background: #1E293B;
                border: 1px solid rgba(255, 255, 255, 0.15);
                color: #F8FAFC;
                padding: 0.3rem 0.7rem;
                border-radius: 8px;
                font-size: 0.72rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.15s ease;
                display: flex;
                align-items: center;
                gap: 0.3rem;
            }
            .tb-btn:hover {
                background: #34D399;
                color: #052E16;
                border-color: #34D399;
            }
            .tb-btn.danger {
                border-color: rgba(239, 68, 68, 0.4);
                color: #F87171;
            }
            .tb-btn.danger:hover {
                background: #EF4444;
                color: #FFF;
                border-color: #EF4444;
            }

            /* Factory Canvas Area */
            .factory-canvas {
                position: relative;
                width: 100%;
                max-width: 1060px;
                height: 520px;
                background: radial-gradient(circle at 50% 50%, rgba(16, 185, 129, 0.08) 0%, rgba(11, 13, 16, 0.96) 80%);
                border: 2px solid rgba(52, 211, 153, 0.35);
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 0 40px rgba(16, 185, 129, 0.08);
            }

            .factory-bg-grid {
                position: absolute;
                top: 0; left: 0; width: 100%; height: 100%;
                background-image: radial-gradient(rgba(52, 211, 153, 0.12) 1px, transparent 1px);
                background-size: 20px 20px;
                pointer-events: none;
            }

            .factory-badge {
                position: absolute;
                top: 12px;
                left: 14px;
                background: rgba(16, 185, 129, 0.15);
                border: 1px solid rgba(52, 211, 153, 0.4);
                color: #34D399;
                padding: 0.25rem 0.7rem;
                border-radius: 14px;
                font-size: 0.7rem;
                font-weight: 800;
                letter-spacing: 0.05em;
                z-index: 2;
            }

            /* Compact Central Intelligence Core Hub */
            .central-hub {
                position: absolute;
                top: 50%;
                right: 30px;
                transform: translateY(-50%);
                width: fit-content;
                height: fit-content;
                background: rgba(15, 23, 42, 0.88);
                backdrop-filter: blur(16px);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 16px;
                box-shadow: 0 12px 36px rgba(0, 0, 0, 0.7);
                z-index: 10;
                display: flex;
                flex-direction: column;
                gap: 1.5rem;
                justify-content: space-around;
                align-items: center;
                padding: 1.8rem 1rem 1rem 1rem;
            }

            .hub-label {
                position: absolute;
                top: 8px;
                font-size: 0.55rem;
                font-weight: 800;
                color: #64748B;
                letter-spacing: 0.08em;
            }

            /* Micro RAG Purple Circle Node */
            .node-purple {
                width: 44px;
                height: 44px;
                border-radius: 50%;
                background: radial-gradient(circle at 35% 35%, #C084FC 0%, #7E22CE 70%, #581C87 100%);
                border: 1.5px solid rgba(192, 132, 252, 0.7);
                box-shadow: 0 0 15px rgba(168, 85, 247, 0.4);
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                color: #FFFFFF;
                cursor: pointer;
                transition: transform 0.15s ease;
            }
            .node-purple:hover { transform: scale(1.12); }

            /* Micro AI Red Circle Node */
            .node-red {
                width: 44px;
                height: 44px;
                border-radius: 50%;
                background: radial-gradient(circle at 35% 35%, #F87171 0%, #DC2626 70%, #991B1B 100%);
                border: 1.5px solid rgba(248, 113, 113, 0.7);
                box-shadow: 0 0 15px rgba(239, 68, 68, 0.4);
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                color: #FFFFFF;
                cursor: pointer;
                transition: transform 0.15s ease;
            }
            .node-red:hover { transform: scale(1.12); }

            .micro-icon { font-size: 0.7rem; }
            .micro-title { font-size: 0.62rem; font-weight: 800; margin-top: 1px; }

            /* Compact n8n Equipment Node Card (150px width) */
            .n8n-node {
                position: absolute;
                width: 150px;
                background: rgba(15, 23, 42, 0.92);
                border: 1.5px solid rgba(52, 211, 153, 0.4);
                border-radius: 10px;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
                cursor: move;
                z-index: 12;
                transition: border-color 0.15s ease, box-shadow 0.15s ease;
            }
            .n8n-node:hover {
                border-color: #34D399;
                box-shadow: 0 6px 20px rgba(52, 211, 153, 0.2);
            }
            .n8n-node.selected {
                border-color: #F5D996;
                box-shadow: 0 0 14px rgba(245, 217, 150, 0.5);
            }

            .n8n-node-header {
                background: rgba(30, 41, 59, 0.8);
                padding: 0.35rem 0.5rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 9px 9px 0 0;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            .n8n-node-name {
                font-size: 0.7rem;
                font-weight: 700;
                color: #F8FAFC;
                display: flex;
                align-items: center;
                gap: 0.25rem;
            }
            .node-delete-icon {
                color: #94A3B8;
                font-size: 0.75rem;
                cursor: pointer;
                padding: 0 0.2rem;
                transition: color 0.15s ease;
            }
            .node-delete-icon:hover { color: #F87171; }

            .n8n-node-body {
                padding: 0.4rem 0.5rem;
            }

            /* Micro Parameters & Components Tags */
            .param-tag {
                display: inline-flex;
                align-items: center;
                gap: 0.2rem;
                background: rgba(52, 211, 153, 0.15);
                color: #34D399;
                border: 1px solid rgba(52, 211, 153, 0.3);
                font-size: 0.58rem;
                font-weight: 600;
                padding: 0.1rem 0.35rem;
                border-radius: 4px;
                margin-right: 0.2rem;
                margin-bottom: 0.2rem;
            }
            .part-tag {
                display: inline-flex;
                align-items: center;
                gap: 0.2rem;
                background: rgba(168, 85, 247, 0.15);
                color: #C084FC;
                border: 1px solid rgba(168, 85, 247, 0.3);
                font-size: 0.58rem;
                font-weight: 600;
                padding: 0.1rem 0.35rem;
                border-radius: 4px;
                margin-right: 0.2rem;
                margin-bottom: 0.2rem;
            }
            .tag-del {
                cursor: pointer;
                font-size: 0.55rem;
                opacity: 0.7;
            }
            .tag-del:hover { opacity: 1; color: #F87171; }

            /* Micro Port Sockets (10px x 10px) */
            .port-socket {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: #34D399;
                border: 1.5px solid #0F172A;
                position: absolute;
                top: 50%;
                transform: translateY(-50%);
                cursor: pointer;
                transition: transform 0.15s ease;
                z-index: 15;
            }
            .port-socket:hover {
                transform: translateY(-50%) scale(1.5);
                background: #F5D996;
            }
            .port-in { left: -5px; }
            .port-out { right: -5px; }

            /* Modal Dialog Overlay */
            .modal-overlay {
                position: fixed;
                top: 0; left: 0; width: 100vw; height: 100vh;
                background: rgba(0, 0, 0, 0.75);
                backdrop-filter: blur(8px);
                z-index: 100;
                display: none;
                justify-content: center;
                align-items: center;
            }
            .modal-box {
                background: #0F172A;
                border: 1px solid rgba(52, 211, 153, 0.4);
                border-radius: 14px;
                width: 380px;
                padding: 1.2rem;
                box-shadow: 0 16px 40px rgba(0,0,0,0.8);
            }
            .modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 0.8rem;
            }
            .modal-title { font-size: 0.9rem; font-weight: 800; color: #34D399; }
            .modal-close-btn {
                background: transparent;
                border: none;
                color: #94A3B8;
                font-size: 1rem;
                cursor: pointer;
                padding: 0.2rem;
            }
            .modal-close-btn:hover { color: #FFF; }
            .modal-input {
                width: 100%;
                background: #1E293B;
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 8px;
                color: #FFF;
                padding: 0.45rem 0.6rem;
                font-size: 0.75rem;
                margin-bottom: 0.7rem;
            }
            .modal-actions {
                display: flex;
                gap: 0.6rem;
                margin-top: 0.4rem;
            }
            .modal-btn {
                background: #34D399; color: #052E16; font-weight: 700;
                border: none; padding: 0.45rem 0.9rem; border-radius: 8px; cursor: pointer; flex: 1; font-size: 0.75rem;
                transition: background 0.15s ease;
            }
            .modal-btn:hover { background: #6EE7B7; }
            .modal-btn-cancel {
                background: #334155; color: #E2E8F0; font-weight: 600;
                border: 1px solid rgba(255,255,255,0.1); padding: 0.45rem 0.9rem; border-radius: 8px; cursor: pointer; flex: 1; font-size: 0.75rem;
                transition: background 0.15s ease;
            }
            .modal-btn-cancel:hover { background: #475569; color: #FFF; }

            .current-items-list {
                max-height: 90px;
                overflow-y: auto;
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 8px;
                padding: 0.4rem;
                margin-bottom: 0.7rem;
            }

            canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 4; pointer-events: none; }
        </style>
    </head>
    <body>
        <!-- n8n Toolbar -->
        <div class="n8n-toolbar">
            <div class="toolbar-title">
                ⚡ FACTORY FLOW BUILDER
            </div>
            <div class="toolbar-actions">
                <button class="tb-btn" onclick="openAddNodeModal()">➕ 장비 추가</button>
                <button class="tb-btn" onclick="openEditModal()">⚙️ 파라미터 / 부품 편집</button>
                <button class="tb-btn danger" onclick="deleteSelectedNode()">🗑️ 장비 삭제</button>
                <button class="tb-btn" onclick="resetToDefaults()">🔄 초기화</button>
            </div>
        </div>

        <!-- Factory Canvas Area -->
        <div class="factory-canvas" id="canvas-container">
            <div class="factory-bg-grid"></div>
            <div class="factory-badge">FACTORY AREA</div>

            <!-- Nodes Container -->
            <div id="nodes-container"></div>

            <!-- Compact Central Hub -->
            <div class="central-hub">
                <div class="hub-label">HUB</div>
                
                <!-- Micro RAG Node (Top Knowledge Base) -->
                <div class="node-purple" id="node-rag" title="RAG 지식베이스 DB">
                    <div class="micro-icon">📚</div>
                    <div class="micro-title">RAG</div>
                </div>

                <!-- Micro AI Node (Bottom Intelligence Engine) -->
                <div class="node-red" id="node-ai" title="AI 처방 엔진">
                    <div class="micro-icon">🧠</div>
                    <div class="micro-title">AI</div>
                </div>
            </div>

            <canvas id="flowCanvas"></canvas>
        </div>

        <!-- Add Node Modal -->
        <div class="modal-overlay" id="add-modal" onclick="closeModalOnOverlay(event, 'add-modal')">
            <div class="modal-box">
                <div class="modal-header">
                    <div class="modal-title">➕ 신규 장비 노드 추가</div>
                    <button class="modal-close-btn" onclick="closeModal('add-modal')">✕</button>
                </div>
                <label style="font-size:0.7rem; color:#94A3B8;">장비 이름</label>
                <input class="modal-input" id="node-name-input" placeholder="예: 식각장비_A, Vacuum_Pump_1" value="식각장비_B">
                <label style="font-size:0.7rem; color:#94A3B8;">장비 아이콘</label>
                <select class="modal-input" id="node-icon-input">
                    <option value="🏭">🏭 식각장비</option>
                    <option value="⚡">⚡ RF Matcher</option>
                    <option value="🌀">🌀 Vacuum Pump</option>
                    <option value="🎛️">🎛️ Gas Controller</option>
                </select>
                <div class="modal-actions">
                    <button class="modal-btn-cancel" onclick="closeModal('add-modal')">취소</button>
                    <button class="modal-btn" onclick="confirmAddNode()">생성하기</button>
                </div>
            </div>
        </div>

        <!-- Edit Node Modal -->
        <div class="modal-overlay" id="edit-modal" onclick="closeModalOnOverlay(event, 'edit-modal')">
            <div class="modal-box">
                <div class="modal-header">
                    <div class="modal-title">⚙️ 파라미터 & 부품 편집</div>
                    <button class="modal-close-btn" onclick="closeModal('edit-modal')">✕</button>
                </div>
                <div id="modal-selected-name" style="font-size:0.75rem; color:#34D399; font-weight:700; margin-bottom:0.6rem;"></div>
                
                <label style="font-size:0.7rem; color:#94A3B8;">현재 파라미터 목록 (클릭시 삭제)</label>
                <div class="current-items-list" id="current-params-list"></div>

                <label style="font-size:0.7rem; color:#94A3B8;">추가 파라미터 (예: RF_Power: 1450W)</label>
                <input class="modal-input" id="param-input" placeholder="RF_Power: 1450W">

                <label style="font-size:0.7rem; color:#94A3B8;">현재 하위 부품 목록 (클릭시 삭제)</label>
                <div class="current-items-list" id="current-parts-list"></div>

                <label style="font-size:0.7rem; color:#94A3B8;">추가 하위 부품 (예: Plasma Chamber)</label>
                <input class="modal-input" id="part-input" placeholder="Plasma Chamber">

                <div class="modal-actions">
                    <button class="modal-btn-cancel" onclick="closeModal('edit-modal')">취소</button>
                    <button class="modal-btn" onclick="confirmEditNode()">저장하기</button>
                </div>
            </div>
        </div>

        <script>
            const defaultNodes = [
                {
                    id: 'node-1',
                    name: '식각장비_A',
                    icon: '🏭',
                    x: 35,
                    y: 70,
                    params: ['RF: 1,450W', 'Press: 45mTorr'],
                    parts: ['Chamber']
                },
                {
                    id: 'node-2',
                    name: 'Vacuum_Pump_1',
                    icon: '🌀',
                    x: 35,
                    y: 280,
                    params: ['RPM: 3,600'],
                    parts: ['Turbomolecular']
                },
                {
                    id: 'node-3',
                    name: 'RF_Matcher_A',
                    icon: '⚡',
                    x: 240,
                    y: 170,
                    params: ['Freq: 13.56MHz'],
                    parts: ['Capacitor']
                }
            ];

            const defaultConnections = [
                { from: 'node-1', to: 'node-3' },
                { from: 'node-2', to: 'node-3' }
            ];

            function loadState() {
                try {
                    const savedNodes = localStorage.getItem('rxm_nodes_data');
                    const savedConns = localStorage.getItem('rxm_connections_data');
                    return {
                        nodes: savedNodes ? JSON.parse(savedNodes) : defaultNodes,
                        connections: savedConns ? JSON.parse(savedConns) : defaultConnections
                    };
                } catch(e) {
                    return { nodes: defaultNodes, connections: defaultConnections };
                }
            }

            function saveState() {
                try {
                    localStorage.setItem('rxm_nodes_data', JSON.stringify(nodesData));
                    localStorage.setItem('rxm_connections_data', JSON.stringify(connections));
                } catch(e) {}
            }

            const state = loadState();
            let nodesData = state.nodes;
            let connections = state.connections;

            let selectedNodeId = nodesData.length > 0 ? nodesData[0].id : null;
            let wiringStartNodeId = null;
            let mouseX = 0, mouseY = 0;

            const container = document.getElementById('nodes-container');
            const canvas = document.getElementById('flowCanvas');
            const ctx = canvas.getContext('2d');

            function resizeCanvas() {
                const rect = document.getElementById('canvas-container').getBoundingClientRect();
                canvas.width = rect.width;
                canvas.height = rect.height;
            }
            resizeCanvas();
            window.addEventListener('resize', resizeCanvas);

            document.getElementById('canvas-container').addEventListener('mousemove', (e) => {
                const cRect = document.getElementById('canvas-container').getBoundingClientRect();
                mouseX = e.clientX - cRect.left;
                mouseY = e.clientY - cRect.top;
            });

            function renderNodes() {
                container.innerHTML = '';
                nodesData.forEach(node => {
                    const isSelected = node.id === selectedNodeId;
                    const elem = document.createElement('div');
                    elem.className = `n8n-node ${isSelected ? 'selected' : ''}`;
                    elem.id = node.id;
                    elem.style.left = node.x + 'px';
                    elem.style.top = node.y + 'px';

                    const paramsHTML = node.params.map((p, idx) => `<span class="param-tag">${p} <span class="tag-del" onclick="removeParam('${node.id}', ${idx})">✕</span></span>`).join('');
                    const partsHTML = node.parts.map((pt, idx) => `<span class="part-tag">🔧 ${pt} <span class="tag-del" onclick="removePart('${node.id}', ${idx})">✕</span></span>`).join('');

                    elem.innerHTML = `
                        <div class="port-socket port-in" data-nodeid="${node.id}" data-type="in" title="입력 포트"></div>
                        <div class="n8n-node-header">
                            <div class="n8n-node-name"><span>${node.icon}</span> ${node.name}</div>
                            <span class="node-delete-icon" onclick="deleteNodeById('${node.id}')" title="삭제">✕</span>
                        </div>
                        <div class="n8n-node-body">
                            <div>${paramsHTML}</div>
                            <div>${partsHTML}</div>
                        </div>
                        <div class="port-socket port-out" data-nodeid="${node.id}" data-type="out" title="출력 포트"></div>
                    `;

                    elem.addEventListener('mousedown', (e) => {
                        if (e.target.classList.contains('tag-del') || e.target.classList.contains('node-delete-icon')) return;

                        const portSocket = e.target.closest('.port-socket');
                        if (portSocket) {
                            const pNodeId = portSocket.getAttribute('data-nodeid');
                            const pType = portSocket.getAttribute('data-type');
                            if (pType === 'out') {
                                wiringStartNodeId = pNodeId;
                                
                                function onPortMouseUp(upEvent) {
                                    const targetElem = document.elementFromPoint(upEvent.clientX, upEvent.clientY);
                                    let targetNodeId = null;
                                    
                                    if (targetElem) {
                                        const inPort = targetElem.closest('.port-in');
                                        if (inPort) {
                                            targetNodeId = inPort.getAttribute('data-nodeid');
                                        } else if (targetElem.closest('#node-ai')) {
                                            targetNodeId = 'node-ai';
                                        } else if (targetElem.closest('#node-rag')) {
                                            targetNodeId = 'node-rag';
                                        }
                                    }
                                    
                                    if (targetNodeId && wiringStartNodeId !== targetNodeId) {
                                        if (!connections.some(c => c.from === wiringStartNodeId && c.to === targetNodeId)) {
                                            connections.push({ from: wiringStartNodeId, to: targetNodeId });
                                            saveState();
                                        }
                                    }
                                    wiringStartNodeId = null;
                                    window.removeEventListener('mouseup', onPortMouseUp);
                                }
                                window.addEventListener('mouseup', onPortMouseUp);
                            } else if (pType === 'in' && wiringStartNodeId && wiringStartNodeId !== pNodeId) {
                                if (!connections.some(c => c.from === wiringStartNodeId && c.to === pNodeId)) {
                                    connections.push({ from: wiringStartNodeId, to: pNodeId });
                                    saveState();
                                }
                                wiringStartNodeId = null;
                            }
                            return;
                        }

                        document.querySelectorAll('.n8n-node').forEach(n => n.classList.remove('selected'));
                        elem.classList.add('selected');
                        selectedNodeId = node.id;

                        const cRect = document.getElementById('canvas-container').getBoundingClientRect();
                        const offsetX = e.clientX - (cRect.left + node.x);
                        const offsetY = e.clientY - (cRect.top + node.y);

                        function onMouseMove(moveEvent) {
                            let newX = moveEvent.clientX - cRect.left - offsetX;
                            let newY = moveEvent.clientY - cRect.top - offsetY;

                            node.x = Math.max(10, Math.min(newX, cRect.width - 165));
                            node.y = Math.max(10, Math.min(newY, cRect.height - 90));

                            elem.style.left = node.x + 'px';
                            elem.style.top = node.y + 'px';
                            saveState();
                        }

                        function onMouseUp() {
                            window.removeEventListener('mousemove', onMouseMove);
                            window.removeEventListener('mouseup', onMouseUp);
                        }

                        window.addEventListener('mousemove', onMouseMove);
                        window.addEventListener('mouseup', onMouseUp);
                    });

                    container.appendChild(elem);
                });
            }

            renderNodes();

            function deleteNodeById(id) {
                nodesData = nodesData.filter(n => n.id !== id);
                connections = connections.filter(c => c.from !== id && c.to !== id);
                if (selectedNodeId === id) {
                    selectedNodeId = nodesData.length > 0 ? nodesData[0].id : null;
                }
                saveState();
                renderNodes();
            }

            function deleteSelectedNode() {
                if (selectedNodeId) deleteNodeById(selectedNodeId);
            }

            function removeParam(nodeId, idx) {
                const node = nodesData.find(n => n.id === nodeId);
                if (node && node.params) {
                    node.params.splice(idx, 1);
                    saveState();
                    renderNodes();
                }
            }

            function removePart(nodeId, idx) {
                const node = nodesData.find(n => n.id === nodeId);
                if (node && node.parts) {
                    node.parts.splice(idx, 1);
                    saveState();
                    renderNodes();
                }
            }

            function resetToDefaults() {
                localStorage.removeItem('rxm_nodes_data');
                localStorage.removeItem('rxm_connections_data');
                nodesData = JSON.parse(JSON.stringify(defaultNodes));
                connections = JSON.parse(JSON.stringify(defaultConnections));
                selectedNodeId = 'node-1';
                wiringStartNodeId = null;
                saveState();
                renderNodes();
            }

            function closeModal(modalId) {
                document.getElementById(modalId).style.display = 'none';
            }
            function closeModalOnOverlay(e, modalId) {
                if (e.target.id === modalId) closeModal(modalId);
            }
            window.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    closeModal('add-modal');
                    closeModal('edit-modal');
                    wiringStartNodeId = null;
                }
            });

            function openAddNodeModal() { document.getElementById('add-modal').style.display = 'flex'; }
            function confirmAddNode() {
                const name = document.getElementById('node-name-input').value || 'New Equipment';
                const icon = document.getElementById('node-icon-input').value;
                const newId = 'node-' + Date.now();
                nodesData.push({
                    id: newId,
                    name: name,
                    icon: icon,
                    x: 40 + ((nodesData.length % 5) * 25),
                    y: 80 + ((nodesData.length % 5) * 20),
                    params: ['Status: OK'],
                    parts: ['Standard Part']
                });
                selectedNodeId = newId;
                saveState();
                renderNodes();
                closeModal('add-modal');
            }

            function openEditModal() {
                const node = nodesData.find(n => n.id === selectedNodeId);
                if (!node) {
                    alert('편집할 장비 노드를 먼저 선택해주세요.');
                    return;
                }
                document.getElementById('modal-selected-name').innerText = `선택된 장비: ${node.icon} ${node.name}`;
                
                const pContainer = document.getElementById('current-params-list');
                pContainer.innerHTML = node.params.map((p, idx) => `<span class="param-tag">${p} <span class="tag-del" onclick="removeParamModal('${node.id}', ${idx})">✕</span></span>`).join('') || '<span style="font-size:0.68rem; color:#64748B;">등록된 파라미터 없음</span>';

                const ptContainer = document.getElementById('current-parts-list');
                ptContainer.innerHTML = node.parts.map((pt, idx) => `<span class="part-tag">🔧 ${pt} <span class="tag-del" onclick="removePartModal('${node.id}', ${idx})">✕</span></span>`).join('') || '<span style="font-size:0.68rem; color:#64748B;">등록된 하위 부품 없음</span>';

                document.getElementById('param-input').value = '';
                document.getElementById('part-input').value = '';
                document.getElementById('edit-modal').style.display = 'flex';
            }

            function removeParamModal(nodeId, idx) {
                removeParam(nodeId, idx);
                openEditModal();
            }

            function removePartModal(nodeId, idx) {
                removePart(nodeId, idx);
                openEditModal();
            }

            function confirmEditNode() {
                const node = nodesData.find(n => n.id === selectedNodeId);
                if (node) {
                    const paramVal = document.getElementById('param-input').value;
                    const partVal = document.getElementById('part-input').value;
                    if (paramVal) node.params.push(paramVal);
                    if (partVal) node.parts.push(partVal);
                    saveState();
                }
                renderNodes();
                closeModal('edit-modal');
            }

            // Dynamic Data Particles
            let particles = [];
            function syncParticles() {
                particles = particles.filter(p => connections.some(c => c.from === p.from && c.to === p.to));
                connections.forEach(c => {
                    if (!particles.some(p => p.from === c.from && p.to === c.to)) {
                        let pColor = '#34D399';
                        if (c.to === 'node-ai') pColor = '#F87171';
                        else if (c.to === 'node-rag') pColor = '#A855F7';
                        
                        particles.push({
                            from: c.from,
                            to: c.to,
                            color: pColor,
                            speed: 0.008 + Math.random() * 0.006,
                            t: Math.random()
                        });
                    }
                });
            }

            function drawCables() {
                const cRect = document.getElementById('canvas-container').getBoundingClientRect();

                // 1. Draw Connections (Equipment, AI, RAG)
                connections.forEach(c => {
                    const srcNode = nodesData.find(n => n.id === c.from);
                    if (!srcNode) return;
                    
                    const srcElem = document.getElementById(c.from);
                    let sx = srcNode.x + 150, sy = srcNode.y + 35;
                    let dx, dy;
                    
                    if (srcElem) {
                        const outPort = srcElem.querySelector('.port-out');
                        if (outPort) {
                            const outR = outPort.getBoundingClientRect();
                            sx = outR.left - cRect.left + outR.width / 2;
                            sy = outR.top - cRect.top + outR.height / 2;
                        }
                    }

                    if (c.to === 'node-ai' || c.to === 'node-rag') {
                        const dstElem = document.getElementById(c.to);
                        if (dstElem) {
                            const dstR = dstElem.getBoundingClientRect();
                            dx = dstR.left - cRect.left + dstR.width / 2;
                            dy = dstR.top - cRect.top + dstR.height / 2;
                        }
                    } else {
                        const dstNode = nodesData.find(n => n.id === c.to);
                        if (!dstNode) return;
                        dx = dstNode.x; dy = dstNode.y + 35;
                        const dstElem = document.getElementById(c.to);
                        if (dstElem) {
                            const inPort = dstElem.querySelector('.port-in');
                            if (inPort) {
                                const inR = inPort.getBoundingClientRect();
                                dx = inR.left - cRect.left + inR.width / 2;
                                dy = inR.top - cRect.top + inR.height / 2;
                            }
                        }
                    }

                    if (dx !== undefined && dy !== undefined) {
                        ctx.save();
                        if (c.to === 'node-ai') ctx.strokeStyle = 'rgba(248, 113, 113, 0.7)';
                        else if (c.to === 'node-rag') ctx.strokeStyle = 'rgba(192, 132, 252, 0.7)';
                        else ctx.strokeStyle = 'rgba(52, 211, 153, 0.65)';
                        
                        ctx.lineWidth = 2.5;
                        ctx.setLineDash([5, 5]);
                        ctx.beginPath();
                        ctx.moveTo(sx, sy);
                        const midX = (sx + dx) / 2;
                        ctx.bezierCurveTo(midX, sy, midX, dy, dx, dy);
                        ctx.stroke();
                        ctx.restore();
                    }
                });

                // 2. Rubber-band Guide Cable during wiring
                if (wiringStartNodeId) {
                    const srcElem = document.getElementById(wiringStartNodeId);
                    if (srcElem) {
                        const outPort = srcElem.querySelector('.port-out');
                        if (outPort) {
                            const outR = outPort.getBoundingClientRect();
                            const sx = outR.left - cRect.left + outR.width / 2;
                            const sy = outR.top - cRect.top + outR.height / 2;

                            ctx.save();
                            ctx.strokeStyle = '#F5D996';
                            ctx.lineWidth = 3;
                            ctx.setLineDash([4, 4]);
                            ctx.beginPath();
                            ctx.moveTo(sx, sy);
                            const midX = (sx + mouseX) / 2;
                            ctx.bezierCurveTo(midX, sy, midX, mouseY, mouseX, mouseY);
                            ctx.stroke();
                            ctx.restore();
                        }
                    }
                }

                // 3. RAG Node (Purple) -> AI Node (Red) Knowledge Injection Stream
                const ragElem = document.getElementById('node-rag');
                const aiElem = document.getElementById('node-ai');

                if (ragElem && aiElem) {
                    const ragR = ragElem.getBoundingClientRect();
                    const aiR = aiElem.getBoundingClientRect();

                    const ragX = ragR.left - cRect.left + ragR.width / 2;
                    const ragY = ragR.top - cRect.top + ragR.height;
                    const aiX = aiR.left - cRect.left + aiR.width / 2;
                    const aiY = aiR.top - cRect.top;

                    // Vertical connection between RAG and AI
                    ctx.save();
                    ctx.strokeStyle = 'rgba(192, 132, 252, 0.7)';
                    ctx.lineWidth = 2.5;
                    ctx.setLineDash([4, 4]);
                    ctx.beginPath();
                    ctx.moveTo(ragX, ragY);
                    ctx.lineTo(aiX, aiY);
                    ctx.stroke();
                    ctx.restore();

                    // Removed hardcoded Equipment Network -> AI Node Stream
                }
            }

            function animate() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                drawCables();

                // Dynamic Equipment Particles
                syncParticles();
                particles.forEach(p => {
                    p.t += p.speed;
                    if (p.t > 1) p.t = 0;

                    const srcNode = nodesData.find(n => n.id === p.from);
                    if (!srcNode) return;

                    const srcElem = document.getElementById(p.from);
                    const cRect = document.getElementById('canvas-container').getBoundingClientRect();
                    
                    let sx = srcNode.x + 150, sy = srcNode.y + 35;
                    let dx, dy;

                    if (srcElem) {
                        const outPort = srcElem.querySelector('.port-out');
                        if (outPort) {
                            const outR = outPort.getBoundingClientRect();
                            sx = outR.left - cRect.left + outR.width / 2;
                            sy = outR.top - cRect.top + outR.height / 2;
                        }
                    }

                    if (p.to === 'node-ai' || p.to === 'node-rag') {
                        const dstElem = document.getElementById(p.to);
                        if (dstElem) {
                            const dstR = dstElem.getBoundingClientRect();
                            dx = dstR.left - cRect.left + dstR.width / 2;
                            dy = dstR.top - cRect.top + dstR.height / 2;
                        }
                    } else {
                        const dstNode = nodesData.find(n => n.id === p.to);
                        if (!dstNode) return;
                        dx = dstNode.x; dy = dstNode.y + 35;
                        const dstElem = document.getElementById(p.to);
                        if (dstElem) {
                            const inPort = dstElem.querySelector('.port-in');
                            if (inPort) {
                                const inR = inPort.getBoundingClientRect();
                                dx = inR.left - cRect.left + inR.width / 2;
                                dy = inR.top - cRect.top + inR.height / 2;
                            }
                        }
                    }
                    
                    if (dx === undefined || dy === undefined) return;

                    const t = p.t;
                    const mt = 1 - t;
                    const midX = (sx + dx) / 2;
                    
                    // Cubic Bezier matching the line:
                    // P0 = (sx, sy), P1 = (midX, sy), P2 = (midX, dy), P3 = (dx, dy)
                    const x = (mt*mt*mt)*sx + 3*(mt*mt)*t*midX + 3*mt*(t*t)*midX + (t*t*t)*dx;
                    const y = (mt*mt*mt)*sy + 3*(mt*mt)*t*sy + 3*mt*(t*t)*dy + (t*t*t)*dy;

                    ctx.save();
                    ctx.shadowBlur = 8;
                    ctx.shadowColor = p.color;
                    ctx.fillStyle = p.color;
                    ctx.beginPath();
                    ctx.arc(x, y, 3.5, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.restore();
                });

                requestAnimationFrame(animate);
            }

            animate();
        </script>
    </body>
    </html>
    """

    components.html(html_code, height=580)
