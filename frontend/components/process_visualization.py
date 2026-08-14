import streamlit as st
import streamlit.components.v1 as components
import time
import os
import json


def render_process_visualization():
    # Load all dataset CSVs into a dict
    base_dir = r"c:\Users\aicam\Documents\RxM"
    dataset_dirs = {
        'case1': 'dataset_case1_normal',
        'case2': 'dataset_case2_global_cascade',
        'case3': 'dataset_case3_selective_cascade',
        'case4': 'dataset_case4_early_spike',
        'case5': 'dataset_case5_late_drift'
    }
    
    preloaded_datasets = {}
    for case_name, folder_name in dataset_dirs.items():
        folder_path = os.path.join(base_dir, folder_name)
        preloaded_datasets[case_name] = {}
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith(".csv"):
                    file_path = os.path.join(folder_path, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            lines = [l.strip() for l in content.split('\n') if l.strip()]
                            if len(lines) > 1:
                                headers = [h.replace('\ufeff', '').strip() for h in lines[0].split(',')]
                                cols = [c.strip() for c in lines[1].split(',')]
                                
                                addr_idx = headers.index('Address') if 'Address' in headers else (headers.index('Step_ID') if 'Step_ID' in headers else -1)
                                name_idx = headers.index('Step_Name') if 'Step_Name' in headers else -1
                                
                                if addr_idx >= 0 and len(cols) > addr_idx:
                                    step_addr = cols[addr_idx]
                                    preloaded_datasets[case_name][step_addr] = content
                                    
                                if name_idx >= 0 and len(cols) > name_idx:
                                    step_name = cols[name_idx]
                                    preloaded_datasets[case_name][step_name] = content
                                    preloaded_datasets[case_name][step_name.replace("_", " ")] = content
                                    
                                file_base = os.path.splitext(filename)[0]
                                preloaded_datasets[case_name][file_base] = content
                                preloaded_datasets[case_name][file_base.replace("_", " ")] = content
                                # Also index by number prefix e.g. "05" or "step_05"
                                parts = file_base.split('_')
                                if parts:
                                    preloaded_datasets[case_name][parts[0]] = content
                                    preloaded_datasets[case_name]["step_" + parts[0]] = content
                    except Exception as e:
                        pass
                        
    # Convert to JSON and safely escape backslashes and single quotes to prevent breaking JS literal
    preloaded_datasets_json = json.dumps(preloaded_datasets).replace('\\', '\\\\').replace("'", "\\'")

    # Corrected Data Topology:
    # 1. Factory Equipments -> AI Node (Red Circle)
    # 2. RAG Vector DB -> AI Node (Red Circle)
    # 3. AI Node -> Factory Equipment (Prescriptive Feedback)
    html_code = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="utf-8">
        <!-- Cache Bust: """ + str(time.time()) + """ -->
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
                height: 100vh;
                width: 100vw;
                padding: 1.2rem;
                overflow: hidden;
            }

            /* Toolbar Header */
            .n8n-toolbar {
                width: 100%;
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
                flex: 1;
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


            /* Compact Central Intelligence Core Hub */
            .central-hub {
                position: absolute;
                top: 150px;
                left: 880px;
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
                width: 34px;
                height: 34px;
                border-radius: 50%;
                background: transparent;
                border: 1.5px solid rgba(192, 132, 252, 0.7);
                box-shadow: 0 0 15px rgba(168, 85, 247, 0.4);
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                color: #C084FC;
                cursor: pointer;
                transition: transform 0.15s ease;
            }
            .node-purple:hover { transform: scale(1.12); }

            /* Micro AI Red Circle Node */
            .node-red {
                width: 34px;
                height: 34px;
                border-radius: 50%;
                background: transparent;
                border: 1.5px solid rgba(248, 113, 113, 0.7);
                box-shadow: 0 0 15px rgba(239, 68, 68, 0.4);
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                color: #F87171;
                cursor: pointer;
                transition: transform 0.15s ease;
            }
            .node-red:hover { transform: scale(1.12); }

            .micro-icon { font-size: 0.65rem; }
            .micro-title { font-size: 0.58rem; font-weight: 800; margin-top: 1px; }

            /* Micro Box Equipment Node Card */
            .n8n-node {
                position: absolute;
                min-width: 65px;
                width: max-content;
                background: rgba(15, 23, 42, 0.92);
                border: 1.5px solid rgba(52, 211, 153, 0.4);
                border-radius: 6px;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
                cursor: move;
                z-index: 12;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 0.4rem 0.4rem 0.3rem 0.4rem;
                transition: border-color 0.15s ease, box-shadow 0.15s ease;
            }
            .n8n-node:hover {
                border-color: #34D399;
                box-shadow: 0 6px 20px rgba(52, 211, 153, 0.2);
                transform: translateY(-2px);
            }
            .n8n-node.selected {
                border-color: #3B82F6;
                box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.4), 0 8px 24px rgba(0, 0, 0, 0.5);
            }
            .n8n-node.anomalous {
                border-color: #EF4444 !important;
                box-shadow: 0 0 25px rgba(239, 68, 68, 0.95), inset 0 0 10px rgba(239, 68, 68, 0.4) !important;
                animation: pulse-red 1.2s infinite ease-in-out;
            }
            @keyframes pulse-red {
                0% {
                    box-shadow: 0 0 15px rgba(239, 68, 68, 0.6), inset 0 0 5px rgba(239, 68, 68, 0.2);
                    border-color: #EF4444;
                }
                50% {
                    box-shadow: 0 0 35px rgba(239, 68, 68, 1), inset 0 0 15px rgba(239, 68, 68, 0.6);
                    border-color: #FF7875;
                }
                100% {
                    box-shadow: 0 0 15px rgba(239, 68, 68, 0.6), inset 0 0 5px rgba(239, 68, 68, 0.2);
                    border-color: #EF4444;
                }
            }

            .node-alarm-badge {
                position: absolute;
                top: -8px;
                right: -8px;
                background: #EF4444;
                color: #FFFFFF;
                font-size: 0.46rem;
                font-weight: 800;
                padding: 1px 4px;
                border-radius: 4px;
                border: 1px solid #FFA39E;
                box-shadow: 0 0 10px rgba(239, 68, 68, 0.9);
                animation: badge-blink 0.8s infinite alternate ease-in-out;
                z-index: 20;
                pointer-events: none;
            }
            @keyframes badge-blink {
                0% { opacity: 0.75; transform: scale(0.92); }
                100% { opacity: 1; transform: scale(1.08); }
            }

            .fail-unresolved-badge {
                font-size: 0.62rem;
                font-weight: 700;
                padding: 2px 7px;
                border-radius: 4px;
                background: rgba(239, 68, 68, 0.2);
                color: #F87171;
                border: 1px solid rgba(239, 68, 68, 0.4);
            }
            .fail-unresolved-badge.all-clear {
                background: rgba(52, 211, 153, 0.15);
                color: #34D399;
                border-color: rgba(52, 211, 153, 0.3);
            }
            .btn-resolve-all {
                background: rgba(52, 211, 153, 0.15);
                border: 1px solid rgba(52, 211, 153, 0.4);
                color: #34D399;
                font-size: 0.62rem;
                font-weight: 700;
                padding: 3px 8px;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.15s ease;
            }
            .btn-resolve-all:hover {
                background: #34D399;
                color: #052E16;
                box-shadow: 0 0 10px rgba(52, 211, 153, 0.4);
            }
            .btn-resolve-action {
                background: #1E293B;
                border: 1px solid #34D399;
                color: #34D399;
                font-size: 0.6rem;
                font-weight: 700;
                padding: 3px 7px;
                border-radius: 4px;
                cursor: pointer;
                transition: all 0.15s ease;
            }
            .btn-resolve-action:hover {
                background: #34D399;
                color: #052E16;
                box-shadow: 0 0 8px rgba(52, 211, 153, 0.5);
            }
            .badge-resolved {
                display: inline-flex;
                align-items: center;
                gap: 2px;
                font-size: 0.58rem;
                font-weight: 600;
                color: #34D399;
                background: rgba(52, 211, 153, 0.1);
                border: 1px solid rgba(52, 211, 153, 0.25);
                padding: 2px 6px;
                border-radius: 4px;
            }

            .micro-lot-badge {
                font-size: 0.44rem;
                color: #38BDF8;
                background: rgba(56, 189, 248, 0.12);
                border: 1px solid rgba(56, 189, 248, 0.3);
                padding: 1px 3px;
                border-radius: 3px;
                max-width: 100%;
                white-space: nowrap;
                text-align: center;
                margin-top: 2px;
                font-family: monospace;
            }
            .micro-lot-badge.lot-fail {
                color: #EF4444;
                background: rgba(239, 68, 68, 0.25);
                border-color: #EF4444;
                font-weight: 800;
                animation: badge-blink 0.8s infinite alternate ease-in-out;
            }

            .lot-trace-link {
                color: #38BDF8;
                cursor: pointer;
                text-decoration: underline;
                transition: color 0.15s ease;
            }
            .lot-trace-link:hover {
                color: #7DD3FC;
                text-shadow: 0 0 8px rgba(56, 189, 248, 0.6);
            }

            /* Lot Traceability Timeline Styles */
            .lot-trace-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
                gap: 10px;
                max-height: 480px;
                overflow-y: auto;
                padding: 10px;
                background: rgba(15, 23, 42, 0.5);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
            .lot-step-card {
                background: #1E293B;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px 10px;
                display: flex;
                flex-direction: column;
                gap: 4px;
                transition: transform 0.15s ease, border-color 0.15s ease;
            }
            .lot-step-card:hover {
                transform: translateY(-2px);
                border-color: #38BDF8;
            }
            .lot-step-card.status-ok {
                border-left: 3px solid #34D399;
            }
            .lot-step-card.status-origin {
                border-left: 4px solid #EF4444;
                background: rgba(239, 68, 68, 0.1);
                box-shadow: 0 0 12px rgba(239, 68, 68, 0.25);
            }
            .lot-step-card.status-cascade {
                border-left: 4px solid #F59E0B;
                background: rgba(245, 158, 11, 0.08);
            }
            .lot-step-num {
                font-size: 0.62rem;
                font-weight: 800;
                color: #94A3B8;
            }
            .lot-step-title {
                font-size: 0.75rem;
                font-weight: 700;
                color: #F8FAFC;
            }
            .lot-step-badge {
                font-size: 0.58rem;
                font-weight: 700;
                padding: 1px 5px;
                border-radius: 4px;
                width: fit-content;
            }
            .lot-step-badge.badge-ok {
                background: rgba(52, 211, 153, 0.15);
                color: #34D399;
                border: 1px solid rgba(52, 211, 153, 0.3);
            }
            .lot-step-badge.badge-origin {
                background: #EF4444;
                color: #FFFFFF;
                border: 1px solid #FFA39E;
            }
            .lot-step-badge.badge-cascade {
                background: rgba(245, 158, 11, 0.2);
                color: #FBBF24;
                border: 1px solid rgba(245, 158, 11, 0.4);
            }
            .lot-step-desc {
                font-size: 0.62rem;
                color: #94A3B8;
                line-height: 1.3;
            }

            .micro-box-icon {
                font-size: 0.9rem;
                margin-bottom: 2px;
            }
            .micro-box-name {
                font-size: 0.55rem;
                font-weight: 700;
                color: #F8FAFC;
                text-align: center;
                white-space: nowrap;
                line-height: 1.2;
                margin-bottom: 3px;
                width: 100%;
            }
            .micro-tag {
                font-size: 0.45rem;
                color: #34D399;
                background: rgba(52, 211, 153, 0.15);
                border: 1px solid rgba(52, 211, 153, 0.3);
                padding: 1px 4px;
                border-radius: 3px;
                max-width: 100%;
                white-space: nowrap;
                text-align: center;
            }
            .node-delete-icon {
                color: #94A3B8;
                font-size: 0.65rem;
                cursor: pointer;
                transition: color 0.15s ease;
            }
            .node-delete-icon:hover { color: #F87171; }

            /* Micro Parameters & Components Tags */
            .param-tag {
                display: inline-flex;
                align-items: center;
                gap: 0.15rem;
                background: rgba(52, 211, 153, 0.15);
                color: #34D399;
                border: 1px solid rgba(52, 211, 153, 0.3);
                font-size: 0.48rem;
                font-weight: 600;
                padding: 0.1rem 0.2rem;
                border-radius: 3px;
                margin-right: 0.15rem;
                margin-bottom: 0.15rem;
            }
            .part-tag {
                display: inline-flex;
                align-items: center;
                gap: 0.15rem;
                background: rgba(168, 85, 247, 0.15);
                color: #C084FC;
                border: 1px solid rgba(168, 85, 247, 0.3);
                font-size: 0.48rem;
                font-weight: 600;
                padding: 0.1rem 0.2rem;
                border-radius: 3px;
                margin-right: 0.15rem;
                margin-bottom: 0.15rem;
            }
            .tag-del {
                cursor: pointer;
                font-size: 0.55rem;
                opacity: 0.7;
            }
            .tag-del:hover { opacity: 1; color: #F87171; }

            /* Micro Port Sockets */
            .port-socket {
                width: 14px;
                height: 14px;
                border-radius: 50%;
                background: #34D399;
                border: 2px solid #0F172A;
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                cursor: crosshair;
                transition: transform 0.15s ease, opacity 0.15s ease, background 0.15s ease;
                z-index: 15;
                opacity: 0;
            }
            .n8n-node:hover .port-socket {
                opacity: 0.3;
            }
            .port-socket:hover {
                transform: translate(-50%, -50%) scale(1.4);
                background: #F5D996;
                opacity: 1 !important;
            }

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
            
            .conn-search-item {
                padding: 0.4rem 0.6rem;
                border-bottom: 1px solid rgba(255,255,255,0.05);
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 0.7rem;
                color: #E2E8F0;
            }
            .conn-search-item:last-child { border-bottom: none; }
            .conn-search-item:hover { background: rgba(255,255,255,0.05); }
            .conn-search-actions { display: flex; gap: 4px; }
            .conn-search-action {
                font-size: 0.55rem; padding: 0.2rem 0.4rem; border-radius: 4px; cursor: pointer;
                border: 1px solid rgba(255,255,255,0.2); background: transparent; color: #94A3B8; transition: all 0.15s;
            }
            .conn-search-action:hover { background: #34D399; color: #0F172A; border-color: #34D399; }
            .conn-search-action.out:hover { background: #A855F7; color: #FFF; border-color: #A855F7; }

            .tab-container {
                display: flex;
                gap: 10px;
                margin-bottom: 1rem;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                padding-bottom: 0.5rem;
            }
            .tab-btn {
                background: none;
                border: none;
                color: #94A3B8;
                font-size: 0.75rem;
                cursor: pointer;
                padding: 0.4rem 0.8rem;
                border-radius: 4px;
                transition: all 0.2s;
            }
            .tab-btn:hover {
                background: rgba(255,255,255,0.05);
            }
            .tab-btn.active {
                color: #34D399;
                background: rgba(52, 211, 153, 0.1);
                font-weight: 700;
            }
            .tab-content {
                display: none;
            }
            .tab-content.active {
                display: block;
            }

            .marquee-box {
                position: absolute;
                border: 1px dashed #34D399;
                background: rgba(52, 211, 153, 0.15);
                pointer-events: none;
                z-index: 50;
                display: none;
            }

            canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 4; pointer-events: none; }

            /* Toast Notification */
            .toast {
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(16, 185, 129, 0.95);
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 0.8rem;
                font-weight: 600;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                opacity: 0;
                pointer-events: none;
                transition: opacity 0.3s ease, transform 0.3s ease;
                z-index: 1000;
            }
            .toast.show {
                opacity: 1;
                transform: translateX(-50%) translateY(-10px);
            }
        </style>
    </head>
    <body>
        <!-- n8n Toolbar -->
        <div class="n8n-toolbar">
            <div class="toolbar-title" id="breadcrumb-nav">
                FACTORY FLOW BUILDER <span style="margin: 0 8px; color:#64748B;">|</span> Main Map
            </div>
            
            <!-- Test Scenario Selector -->
            <div style="display:flex; align-items:center; gap: 10px; margin-left: 20px; flex-grow: 1;">
                <label style="font-size:0.75rem; color:#94A3B8;">테스트 시나리오:</label>
                <select id="test-case-selector" class="modal-input" onchange="applyTestCase(this.value)" style="width: 250px; padding: 0.2rem 0.4rem; background: rgba(15, 23, 42, 0.8); margin: 0; font-size: 0.72rem;">
                    <option value="">적용 안함 (수동 업로드)</option>
                    <option value="case1">Case 1: 정상 공정 (Baseline Normal)</option>
                    <option value="case2">Case 2: 전역 연쇄 불량 (Global Cascade - 중기)</option>
                    <option value="case3">Case 3: 선택적 연쇄 불량 (Selective Cascade - 후기)</option>
                    <option value="case4">Case 4: 초기 돌발 불량 (Early Transient Defect - 초기)</option>
                    <option value="case5">Case 5: 후기 점진 열화 불량 (Late Progressive Drift - 후기)</option>
                </select>
            </div>

            <div class="toolbar-actions">
                <button class="tb-btn" onclick="openLotTraceModal()" style="border-color: #38BDF8; color: #38BDF8; margin-right: 4px;">Lot 공정 추적</button>
                <button class="tb-btn" id="btn-save" onclick="manualSave()" style="margin-right: 4px;">위치 저장</button>
                <button class="tb-btn" id="btn-add-node" onclick="openAddNodeModal()">장비/공장 추가</button>
            </div>
        </div>

        <!-- Factory Canvas Area -->
        <div class="factory-canvas" id="canvas-container">
            <div class="factory-bg-grid"></div>


            <!-- Zoom Wrapper for DOM Elements -->
            <div id="zoom-wrapper" style="transform-origin: 0 0; width: 100%; height: 100%; position: absolute; top: 0; left: 0; pointer-events: none; z-index: 10;">
                <!-- Nodes Container (Restore pointer events) -->
                <div id="nodes-container" style="pointer-events: auto;"></div>

                <!-- Compact Central Hub -->
                <div class="central-hub" id="central-hub" style="pointer-events: auto; cursor: move;">
                    <div class="hub-label">HUB</div>
                    
                    <!-- Micro RAG Node (Top Knowledge Base) -->
                    <div class="node-purple" id="node-rag" title="RAG 지식베이스 DB">
                        <div class="micro-title">RAG</div>
                    </div>

                    <!-- Micro AI Node (Bottom Intelligence Engine) -->
                    <div class="node-red" id="node-ai" title="AI 처방 엔진">
                        <div class="micro-title">AI</div>
                    </div>
                </div>
            </div>

            <canvas id="flowCanvas"></canvas>
        </div>

        <!-- Add Node Modal -->
        <div class="modal-overlay" id="add-modal" onclick="closeModalOnOverlay(event, 'add-modal')">
            <div class="modal-box">
                <div class="modal-header">
                    <div class="modal-title" id="add-modal-title">➕ 신규 장비 노드 추가</div>
                    <button class="modal-close-btn" onclick="closeModal('add-modal')">✕</button>
                </div>
                <label style="font-size:0.7rem; color:#94A3B8;" id="add-modal-name-label">장비 이름</label>
                <input class="modal-input" id="node-name-input" placeholder="이름을 입력하세요">
                
                <div id="add-modal-extra-fields">
                    <label style="font-size:0.7rem; color:#94A3B8;">8대 공정 (Tag)</label>
                    <select class="modal-input" id="node-tag-input" style="cursor: pointer;">
                        <option value="Fab">Fab (공장)</option>
                        <option value="Etch">Etch</option>
                        <option value="Litho">Litho</option>
                        <option value="CVD">CVD</option>
                        <option value="PVD">PVD</option>
                        <option value="CMP">CMP</option>
                        <option value="Implant">Implant</option>
                        <option value="Wet Process">Wet Process</option>
                        <option value="Wet Etch">Wet Etch</option>
                        <option value="RTP">RTP</option>
                        <option value="Epitaxy">Epitaxy</option>
                        <option value="ECP">ECP</option>
                        <option value="Material">Material</option>
                        <option value="BEOL">BEOL</option>
                        <option value="Passivation">Passivation</option>
                        <option value="Test">Test</option>
                    </select>
                    <label style="font-size:0.7rem; color:#94A3B8;">세부 공정 (Process)</label>
                    <input class="modal-input" id="node-process-input" placeholder="예: ICP, PVD">
                    <label style="font-size:0.7rem; color:#94A3B8;">초기 파라미터 (쉼표로 구분)</label>
                    <input class="modal-input" id="node-add-param-input" placeholder="예: Temperature, Pressure">
                    <label style="font-size:0.7rem; color:#94A3B8;">초기 하위 부품 (쉼표로 구분)</label>
                    <input class="modal-input" id="node-add-part-input" placeholder="예: Sensor A, Valve B">
                </div>

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
                    <div class="modal-title" id="modal-selected-name" style="color:#34D399; font-weight:700; max-width: 90%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"></div>
                    <button class="modal-close-btn" onclick="closeModal('edit-modal')">✕</button>
                </div>
                <div style="display: flex; gap: 20px; width: 100%; flex: 1; overflow: hidden;" id="edit-modal-flex">
                    
                    <!-- Left Column (Sensor Data) -->
                    <div id="edit-modal-left" style="flex: 1.5; display: flex; flex-direction: column; min-width: 450px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                            <label style="font-size:0.75rem; color:#34D399; display: block; font-weight: bold;"> 실시간 센서 데이터 (CSV)</label>
                            <div id="modal-current-lot-badge" style="font-size: 0.68rem; color: #38BDF8; background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.3); padding: 2px 8px; border-radius: 4px; font-weight: 600;">
                                현재 가공 Lot: 대기 중
                            </div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 10px; background: rgba(15, 23, 42, 0.6); padding: 4px 8px; border: 1px solid rgba(52, 211, 153, 0.3); border-radius: 4px; margin-bottom: 4px;">
                            <button type="button" onclick="document.getElementById('sensor-csv-upload').click()" style="padding: 4px 8px; font-size: 0.7rem; background: rgba(52, 211, 153, 0.15); border: 1px solid #34D399; color: #34D399; border-radius: 4px; cursor: pointer; white-space: nowrap;">파일 선택</button>
                            <span id="sensor-csv-filename" style="font-size: 0.75rem; color: #94A3B8; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 280px;">선택된 파일 없음</span>
                        </div>
                        <input type="file" id="sensor-csv-upload" accept=".csv" class="modal-input" style="display: none;">
                        <div style="display: flex; gap: 15px; flex: 1.5; min-height: 250px; margin-top: 10px; width: 100%;">
                            <div id="sensor-chart-container" style="flex: 1.5; min-height: 200px; background: rgba(0,0,0,0.2); border-radius: 6px; padding: 10px; position: relative;">
                                <canvas id="sensorChart"></canvas>
                            </div>
                            <div id="sensor-table-container" style="flex: 1; min-height: 200px; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(52, 211, 153, 0.3); border-radius: 6px; padding: 10px; overflow-y: auto;">
                                <div style="font-size: 0.75rem; color: #34D399; font-weight: bold; margin-bottom: 8px;">실시간 수치 (Real-time)</div>
                                <table style="width: 100%; color: #E2E8F0; font-size: 0.65rem; border-collapse: collapse;">
                                    <thead>
                                        <tr style="border-bottom: 1px solid rgba(52, 211, 153, 0.3); text-align: left;">
                                            <th style="padding: 4px; padding-bottom: 8px; text-align: left; width: 30px;">
                                                <input type="checkbox" id="sensor-check-all" checked onchange="toggleAllSensorDatasets(this.checked)" style="cursor: pointer;">
                                            </th>
                                            <th style="padding: 4px; padding-bottom: 8px; text-align: left;">항목</th>
                                            <th style="padding: 4px; padding-bottom: 8px; text-align: left;">Target</th>
                                            <th style="padding: 4px; padding-bottom: 8px; text-align: left;">Current</th>
                                            <th style="padding: 4px; padding-bottom: 8px; text-align: left;">Min</th>
                                            <th style="padding: 4px; padding-bottom: 8px; text-align: left;">Max</th>
                                            <th style="padding: 4px; padding-bottom: 8px; text-align: left;">단위</th>
                                        </tr>
                                    </thead>
                                    <tbody id="sensor-data-table-body">
                                        <tr><td colspan="6" style="padding: 8px; text-align: center; color: #94A3B8;">대기 중...</td></tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div id="sensor-fail-log-container" style="flex: 1; min-height: 150px; margin-top: 15px; width: 100%; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 6px; padding: 10px; overflow-y: auto;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <div style="font-size: 0.75rem; color: #EF4444; font-weight: bold; display: flex; align-items: center; gap: 4px;">
                                        Fail Log
                                    </div>
                                    <span id="fail-unresolved-count-badge" class="fail-unresolved-badge all-clear">정상 (0건)</span>
                                </div>
                                <button type="button" class="btn-resolve-all" id="btn-resolve-all-fails" onclick="resolveAllFailLogsForCurrentNode()">
                                    전체 조치 완료
                                </button>
                            </div>
                            <table style="width: 100%; color: #E2E8F0; font-size: 0.65rem; border-collapse: collapse;">
                                <thead>
                                    <tr style="border-bottom: 1px solid rgba(239, 68, 68, 0.4); text-align: left;">
                                        <th style="padding: 4px; padding-bottom: 8px; width: 110px;">Date-Time</th>
                                        <th style="padding: 4px; padding-bottom: 8px; width: 130px; color: #38BDF8;">Lot ID</th>
                                        <th style="padding: 4px; padding-bottom: 8px; width: 170px;">Failed Param (Value / Range)</th>
                                        <th style="padding: 4px; padding-bottom: 8px;">All Recorded Data</th>
                                        <th style="padding: 4px; padding-bottom: 8px; width: 95px; text-align: center;">조치 상태</th>
                                    </tr>
                                </thead>
                                <tbody id="sensor-fail-log-body">
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Right Column (Tabs & Info) -->
                    <div id="edit-modal-right" style="flex: 1; display: flex; flex-direction: column; min-width: 320px;">
                        <div class="tab-container" id="edit-tab-container">
                            <button class="tab-btn active" id="tab-btn-info" onclick="switchEditTab('info')">기본 정보</button>
                            <button class="tab-btn" id="tab-btn-params" onclick="switchEditTab('params')">파라미터</button>
                            <button class="tab-btn" id="tab-btn-parts" onclick="switchEditTab('parts')">하위 부품</button>
                        </div>

                        <div id="fab-edit-content" style="display: none; padding-top: 0.5rem; padding-bottom: 0.5rem;">
                            <label style="font-size:0.7rem; color:#94A3B8;">내부 장비 목록</label>
                            <div class="current-items-list" id="fab-internal-nodes-list" style="min-height: 80px; max-height: 200px; margin-bottom: 10px;"></div>
                        </div>

                        <div class="tab-content active" id="tab-content-info" style="flex: 1;">
                            <label style="font-size:0.7rem; color:#94A3B8;">8대 공정 (Tag)</label>
                            <select class="modal-input" id="edit-tag-input" style="cursor: pointer;">
                                <option value="Fab">Fab (공장)</option>
                                <option value="Etch">Etch</option>
                                <option value="Litho">Litho</option>
                                <option value="CVD">CVD</option>
                                <option value="PVD">PVD</option>
                                <option value="CMP">CMP</option>
                                <option value="Implant">Implant</option>
                                <option value="Wet Process">Wet Process</option>
                                <option value="Wet Etch">Wet Etch</option>
                                <option value="RTP">RTP</option>
                                <option value="Epitaxy">Epitaxy</option>
                                <option value="ECP">ECP</option>
                                <option value="Material">Material</option>
                                <option value="BEOL">BEOL</option>
                                <option value="Passivation">Passivation</option>
                                <option value="Test">Test</option>
                            </select>
                            <label style="font-size:0.7rem; color:#94A3B8;">Address (주소)</label>
                            <input class="modal-input" id="edit-address-input" placeholder="예: 01, 15 (자동으로 step_가 붙습니다)">
                            <label style="font-size:0.7rem; color:#94A3B8;">세부 공정 (Process)</label>
                            <input class="modal-input" id="edit-process-input" placeholder="예: ICP, PVD">

                            <div style="display: flex; gap: 10px; margin-top: 0.2rem;">
                                <div style="flex: 1;">
                                    <label style="font-size:0.65rem; color:#94A3B8;">이전 공정 (Previous)</label>
                                    <div class="current-items-list" id="current-incoming-list" style="min-height: 50px; max-height: 80px; padding: 0.3rem;"></div>
                                </div>
                                <div style="flex: 1;">
                                    <label style="font-size:0.65rem; color:#94A3B8;">이후 공정 (Next)</label>
                                    <div class="current-items-list" id="current-outgoing-list" style="min-height: 50px; max-height: 80px; padding: 0.3rem;"></div>
                                </div>
                            </div>

                            <label style="font-size:0.65rem; color:#94A3B8; margin-top: 0.2rem; display: block;">연결 장비 검색 추가</label>
                            <div style="position: relative; margin-bottom: 0.5rem;">
                                <input class="modal-input" id="conn-search-input" placeholder="연결할 장비 이름 검색..." autocomplete="off" style="margin-bottom: 0;">
                                <div id="conn-search-results" style="position: absolute; top: calc(100% + 2px); left: 0; width: 100%; background: #1E293B; border: 1px solid rgba(52, 211, 153, 0.4); border-radius: 6px; z-index: 50; max-height: 150px; overflow-y: auto; display: none; box-shadow: 0 4px 12px rgba(0,0,0,0.5);"></div>
                            </div>
                        </div>

                        <div class="tab-content" id="tab-content-params" style="flex: 1;">
                            <label style="font-size:0.7rem; color:#94A3B8;">현재 파라미터 목록 (클릭시 삭제)</label>
                            <div class="current-items-list" id="current-params-list" style="max-height: 150px;"></div>
                            <label style="font-size:0.7rem; color:#94A3B8;">추가 파라미터</label>
                            <input class="modal-input" id="param-input" placeholder="파라미터 입력">
                        </div>

                        <div class="tab-content" id="tab-content-parts" style="flex: 1;">
                            <label style="font-size:0.7rem; color:#94A3B8;">현재 하위 부품 목록 (클릭시 삭제)</label>
                            <div class="current-items-list" id="current-parts-list" style="max-height: 150px;"></div>
                            <label style="font-size:0.7rem; color:#94A3B8;">추가 하위 부품</label>
                            <input class="modal-input" id="part-input" placeholder="하위 부품 입력">
                        </div>

                        <div class="modal-actions" style="margin-top: auto; padding-top: 20px;">
                            <button class="modal-btn-cancel" onclick="closeModal('edit-modal')">취소</button>
                            <button class="modal-btn-cancel" style="color: #F87171; border-color: rgba(248, 113, 113, 0.4);" onclick="deleteNodeFromModal()">삭제</button>
                            <button class="modal-btn" onclick="confirmEditNode()">저장하기</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Confirm Modal -->
        <div class="modal-overlay" id="confirm-modal" onclick="closeModalOnOverlay(event, 'confirm-modal')">
            <div class="modal-box" style="width: 300px;">
                <div class="modal-header">
                    <div class="modal-title">확인</div>
                    <button class="modal-close-btn" onclick="closeModal('confirm-modal')">✕</button>
                </div>
                <div id="confirm-modal-message" style="font-size:0.75rem; color:#E2E8F0; margin-bottom:1.5rem; margin-top:0.5rem; text-align:center;">정말로 삭제하시겠습니까?</div>
                <div class="modal-actions">
                    <button class="modal-btn-cancel" onclick="closeModal('confirm-modal')">취소</button>
                    <button class="modal-btn" style="background:#F87171; color:#450A0A;" onclick="executeConfirmAction()">확인</button>
                </div>
            </div>
        </div>

        <!-- Lot Traceability Modal -->
        <div class="modal-overlay" id="lot-trace-modal" onclick="closeModalOnOverlay(event, 'lot-trace-modal')">
            <div class="modal-box" style="width: 85vw; max-width: 1050px; height: 85vh; display: flex; flex-direction: column;">
                <div class="modal-header" style="border-bottom: 1px solid rgba(56, 189, 248, 0.3); padding-bottom: 8px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div class="modal-title" style="color: #38BDF8; font-size: 0.95rem;">Lot 공정 이력 및 결함 추적기 (Lot Traceability Tracker)</div>
                        <select id="lot-trace-selector" class="modal-input" onchange="renderLotTraceTimeline(this.value)" style="width: 220px; margin: 0; padding: 0.25rem 0.5rem; font-size: 0.75rem; border-color: #38BDF8; color: #38BDF8; font-weight: bold;">
                            <option value="LOT-20260812-B02">LOT-20260812-B02 (이상 발생 Lot)</option>
                            <option value="LOT-20260812-A01">LOT-20260812-A01 (정상 가공 Lot)</option>
                            <option value="LOT-20260812-C03">LOT-20260812-C03 (후기 가공 Lot)</option>
                        </select>
                    </div>
                    <button class="modal-close-btn" onclick="closeModal('
                    -trace-modal')">✕</button>
                </div>
                
                <!-- Lot Summary Banner -->
                <div id="lot-trace-summary-banner" style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 8px; padding: 8px 12px; margin-bottom: 10px; font-size: 0.72rem; color: #E2E8F0; display: flex; justify-content: space-between; align-items: center;">
                    <div id="lot-summary-info">로딩 중...</div>
                    <div id="lot-summary-status-badge"></div>
                </div>

                <!-- 35-step Journey Grid -->
                <div style="flex: 1; overflow-y: auto; padding-right: 4px;">
                    <div class="lot-trace-grid" id="lot-trace-steps-container">
                    </div>
                </div>
                
                <div class="modal-actions" style="margin-top: 10px; padding-top: 6px; border-top: 1px solid rgba(255,255,255,0.08);">
                    <button class="modal-btn-cancel" onclick="closeModal('lot-trace-modal')">닫기</button>
                </div>
            </div>
        </div>

        <script>
            const preloadedDatasets = JSON.parse('""" + preloaded_datasets_json + """');
            const cmosSteps = [
                { name: "베어 웨이퍼 준비", tag: "Material", process: "Wafer Prep" },
                { name: "세정", tag: "Wet Process", process: "Cleaning" },
                { name: "Pad 증착", tag: "CVD", process: "Deposition" },
                { name: "STI 포토", tag: "Litho", process: "Photo" },
                { name: "STI 식각", tag: "Etch", process: "Etching" },
                { name: "STI 갭필", tag: "CVD", process: "Gap Fill" },
                { name: "STI 평탄화", tag: "CMP", process: "Planarization" },
                { name: "세정", tag: "Wet Process", process: "Cleaning" },
                { name: "N/P-Well 주입", tag: "Implant", process: "Implantation" },
                { name: "활성화 열처리", tag: "RTP", process: "Thermal" },
                { name: "더미게이트 증착", tag: "CVD", process: "Deposition" },
                { name: "더미게이트 식각", tag: "Etch", process: "Etching" },
                { name: "LDD 이온주입", tag: "Implant", process: "Implantation" },
                { name: "스페이서 식각", tag: "Etch", process: "Etching" },
                { name: "S/D 에피택시", tag: "Epitaxy", process: "Deposition" },
                { name: "고농도 S/D 주입", tag: "Implant", process: "Implantation" },
                { name: "ILD0 증착", tag: "CVD", process: "Deposition" },
                { name: "ILD0 평탄화", tag: "CMP", process: "Planarization" },
                { name: "더미 폴리 제거", tag: "Wet Etch", process: "Etching" },
                { name: "금속 게이트 증착", tag: "CVD", process: "ALD" },
                { name: "금속 평탄화", tag: "CMP", process: "Planarization" },
                { name: "컨택홀 포토", tag: "Litho", process: "Litho" },
                { name: "컨택홀 식각", tag: "Etch", process: "Etching" },
                { name: "살리사이드 열처리", tag: "RTP", process: "Thermal" },
                { name: "컨택 갭필", tag: "CMP", process: "CVD/CMP" },
                { name: "1층 금속 절연막", tag: "CVD", process: "Deposition" },
                { name: "다마신 포토", tag: "Litho", process: "Damascene Litho" },
                { name: "다마신 식각", tag: "Etch", process: "Damascene Etch" },
                { name: "Cu Barrier/Seed", tag: "PVD", process: "Deposition" },
                { name: "구리 전해도금", tag: "ECP", process: "Deposition" },
                { name: "구리 평탄화", tag: "CMP", process: "Planarization" },
                { name: "상위 배선층 반복", tag: "BEOL", process: "Loop" },
                { name: "보호막 증착", tag: "CVD", process: "Passivation" },
                { name: "패드 오픈 식각", tag: "Etch", process: "Etching" },
                { name: "칩 테스트", tag: "Test", process: "EDS" }
            ];

            const defaultFabNodes = cmosSteps.map((step, index) => {
                const cols = 7;
                const row = Math.floor(index / cols);
                const col = row % 2 === 0 ? (index % cols) : (cols - 1 - (index % cols));
                
                let params = [];
                let parts = [];
                const t = step.tag;
                
                if (t.includes('Wet Process') || t.includes('Wet Etch')) {
                    params = ["농도 (HF, SC-1/2 등)", "배스 온도", "DI 비저항", "Spin RPM", "공정 시간"];
                    parts = ["케미컬 필터", "O-ring", "PTFE 배관/밸브", "석영 배스", "스핀 척"];
                } else if (t.includes('RTP') || t.includes('Furnace')) {
                    params = ["Zone 온도 프로파일", "공정 가스 유량", "챔버 압력", "공정 시간"];
                    parts = ["쿼츠 튜브", "열전대(TC)", "히터 엘리먼트", "할로겐 램프", "SiC 보트"];
                } else if (t.includes('Litho')) {
                    params = ["노광량 (Dose)", "Focus Offset", "오버레이 오차", "감광액 두께/RPM", "Bake 온도"];
                    parts = ["광원 램프", "PR 디스펜스 노즐", "화학 필터", "WEE 램프"];
                } else if (t.includes('Etch') || t.includes('Damascene')) {
                    params = ["Source/Bias Power", "가스 혼합 비율", "챔버 진공 압력", "ESC 표면 온도", "후면 He 압력"];
                    parts = ["포커스 링", "샤워헤드", "챔버 내벽 라이너", "정전척(ESC)", "TMP 부품"];
                } else if (t.includes('CVD') || t.includes('ALD')) {
                    params = ["서셉터 온도", "챔버 압력", "전구체 유량/시간", "Purge 가스 유량", "RF 파워"];
                    parts = ["샤워헤드", "서셉터", "전구체 기화기", "포어라인 트랩", "슬릿 밸브 O-링"];
                } else if (t.includes('PVD')) {
                    params = ["DC 파워", "Ar 가스 유량", "챔버 고진공도", "자석 회전 속도"];
                    parts = ["Target (금속)", "Shield", "마그네트론 어셈블리"];
                } else if (t.includes('Implant')) {
                    params = ["도즈량 (Dose)", "가속 에너지 (keV)", "Beam Current", "Tilt/Twist 각도"];
                    parts = ["이온 소스 필라멘트", "고전압 애자", "패러데이 컵", "질량 분석기 슬릿"];
                } else if (t.includes('CMP')) {
                    params = ["헤드 다운포스", "플래튼/헤드 RPM", "슬러리 유량/온도", "세정 브러시 압력"];
                    parts = ["연마 패드", "다이아몬드 디스크", "리테이닝 링", "PVA 브러시"];
                } else if (t.includes('ECP')) {
                    params = ["전류 밀도", "배스 온도", "유기 첨가제 농도", "도금 시간"];
                    parts = ["애노드(구리판)", "도금액 미세 필터", "립 실"];
                } else {
                    params = ["Status: Normal", "Process Time: Auto"];
                    parts = ["Standard Unit"];
                }

                let initX = 40 + col * 115;
                let initY = 30 + row * 95;
                let nodeW = 65, nodeH = 50;
                let gridSize = 40, dotOffset = 20;
                let targetCx = initX + nodeW / 2;
                let targetCy = initY + nodeH / 2;
                let snappedCx = Math.round((targetCx - dotOffset) / gridSize) * gridSize + dotOffset;
                let snappedCy = Math.round((targetCy - dotOffset) / gridSize) * gridSize + dotOffset;

                return {
                    id: 'node-cmos-' + index,
                    address: 'step_' + String(index + 1).padStart(2, '0'),
                    name: step.name,
                    icon: step.icon,
                    tag: step.tag,
                    process: step.process,
                    x: snappedCx - nodeW / 2,
                    y: snappedCy - nodeH / 2,
                    params: params,
                    parts: parts
                };
            });

            const defaultFabConnections = [];
            for (let i = 0; i < defaultFabNodes.length - 1; i++) {
                defaultFabConnections.push({ from: defaultFabNodes[i].id, to: defaultFabNodes[i+1].id });
            }
            // Connect the last node to AI node
            defaultFabConnections.push({ from: defaultFabNodes[defaultFabNodes.length - 1].id, to: 'node-ai' });

            const defaultViews = {
                'main': {
                    nodes: [{
                        id: 'fab-cmos',
                        name: 'CMOS 공정 팹',
                        icon: '🏭',
                        x: Math.round(((window.innerWidth / 2 - 100) + 65/2 - 20) / 40) * 40 + 20 - 65/2,
                        y: Math.round(((window.innerHeight / 2 - 50) + 50/2 - 20) / 40) * 40 + 20 - 50/2,
                        params: ['Fab'],
                        parts: []
                    }],
                    connections: [{ from: 'fab-cmos', to: 'node-ai' }]
                },
                'fab-cmos': {
                    nodes: defaultFabNodes,
                    connections: defaultFabConnections
                }
            };

            let viewsData = JSON.parse(localStorage.getItem('rxm_views_data_v3')) || JSON.parse(JSON.stringify(defaultViews));
            
            // Backward compatibility migration: Move params[0] to tag if tag is not defined.
            Object.values(viewsData).forEach(view => {
                if (view.nodes) {
                    view.nodes.forEach(node => {
                        if (!node.tag && node.params && node.params.length > 0) {
                            if (node.params[0] === 'Fab') {
                                node.tag = 'Fab';
                                node.params.shift();
                            } else if (node.params[0] !== 'Status: OK') {
                                node.tag = node.params[0];
                                node.params.shift();
                            }
                        }
                        // Migrate address if missing
                        if (!node.address && node.id && node.id.startsWith('node-cmos-')) {
                            const idxStr = node.id.replace('node-cmos-', '');
                            const idx = parseInt(idxStr, 10);
                            if (!isNaN(idx)) {
                                node.address = 'step_' + String(idx + 1).padStart(2, '0');
                            }
                        }
                    });
                }
            });
            
            let currentViewId = 'main';

            function saveState() {
                try {
                    viewsData[currentViewId].nodes = nodesData;
                    viewsData[currentViewId].connections = connections;
                    localStorage.setItem('rxm_views_data_v3', JSON.stringify(viewsData));
                } catch(e) {}
            }

            let nodesData = viewsData[currentViewId].nodes;
            let connections = viewsData[currentViewId].connections;

            function navigateView(viewId) {
                saveState();
                currentViewId = viewId;
                if (!viewsData[viewId]) {
                    viewsData[viewId] = { nodes: [], connections: [] };
                }
                nodesData = viewsData[currentViewId].nodes;
                connections = viewsData[currentViewId].connections;
                selectedNodeId = null;
                
                zoom = 1; panX = 0; panY = 0;
                updateTransform();
                updateBreadcrumb();
                renderNodes();
            }

            function updateBreadcrumb() {
                const nav = document.getElementById('breadcrumb-nav');
                const btnAdd = document.getElementById('btn-add-node');
                if (!nav) return;
                if (currentViewId === 'main') {
                    nav.innerHTML = `FACTORY FLOW BUILDER <span style="margin: 0 8px; color:#64748B;">|</span> Main Map`;
                    if (btnAdd) btnAdd.innerText = '신규 공장 추가';
                } else {
                    const fabNode = viewsData['main'].nodes.find(n => n.id === currentViewId) || {name: currentViewId};
                    nav.innerHTML = `FACTORY FLOW BUILDER <span style="margin: 0 8px; color:#64748B;">|</span> <span style="cursor:pointer; color:#94A3B8; text-decoration:underline;" onclick="navigateView('main')">Main Map</span> <span style="margin: 0 8px; color:#64748B;">&gt;</span> <span style="color:#F8FAFC;">${fabNode.name}</span>`;
                    if (btnAdd) btnAdd.innerText = '신규 장비 추가';
                }
            }
            updateBreadcrumb();

            let selectedNodeId = nodesData.length > 0 ? nodesData[0].id : null;
            let selectedNodeIds = new Set();
            if (selectedNodeId) selectedNodeIds.add(selectedNodeId);
            
            let wiringStartNodeId = null;
            let mouseX = 0, mouseY = 0;
            let rawMouseX = -1000, rawMouseY = -1000;
            
            // Pan and Zoom states
            let zoom = 1;
            let panX = 0, panY = 0;
            let isPanning = false;
            let panStartX = 0, panStartY = 0;

            // Marquee states
            let isMarquee = false;
            let marqueeStartX = 0;
            let marqueeStartY = 0;
            const marqueeEl = document.createElement('div');
            marqueeEl.className = 'marquee-box';

            const container = document.getElementById('nodes-container');
            const canvas = document.getElementById('flowCanvas');
            const ctx = canvas.getContext('2d');
            
            document.getElementById('zoom-wrapper').appendChild(marqueeEl);

            function resizeCanvas() {
                const rect = document.getElementById('canvas-container').getBoundingClientRect();
                canvas.width = rect.width;
                canvas.height = rect.height;
            }
            resizeCanvas();
            window.addEventListener('resize', resizeCanvas);

            function updateTransform() {
                const zoomWrapper = document.getElementById('zoom-wrapper');
                if (zoomWrapper) {
                    zoomWrapper.style.transform = `translate(${panX}px, ${panY}px) scale(${zoom})`;
                }
                const bgGrid = document.querySelector('.factory-bg-grid');
                if (bgGrid) {
                    bgGrid.style.backgroundPosition = `${panX}px ${panY}px`;
                    bgGrid.style.backgroundSize = `${40 * zoom}px ${40 * zoom}px`;
                }
            }

            document.getElementById('canvas-container').addEventListener('contextmenu', e => {
                if (e.target.id === 'canvas-container' || e.target.id === 'flowCanvas' || e.target.classList.contains('factory-bg-grid')) {
                    e.preventDefault();
                    
                    const cRect = document.getElementById('canvas-container').getBoundingClientRect();
                    const clickX = e.clientX - cRect.left;
                    const clickY = e.clientY - cRect.top;
                    
                    let clickedConnection = -1;
                    
                    ctx.save();
                    ctx.translate(panX, panY);
                    ctx.scale(zoom, zoom);
                    ctx.lineWidth = 15; // thick stroke for easier clicking
                    
                    for (let i = connections.length - 1; i >= 0; i--) {
                        const c = connections[i];
                        const srcNode = nodesData.find(n => n.id === c.from);
                        if (!srcNode) continue;
                        const srcElem = document.getElementById(c.from);
                        let sx = srcNode.x + 75, sy = srcNode.y + 30;
                        let dx, dy;
                        if (srcElem) {
                            const outPort = srcElem.querySelector('.port-socket');
                            const wc = getWorldCoords(outPort);
                            if (wc) { sx = wc.x; sy = wc.y; }
                        }
                        if (c.to === 'node-ai' || c.to === 'node-rag') {
                            const dstElem = document.getElementById(c.to);
                            const wc = getWorldCoords(dstElem);
                            if (wc) { dx = wc.x; dy = wc.y; }
                        } else {
                            const dstNode = nodesData.find(n => n.id === c.to);
                            if (!dstNode) continue;
                            dx = dstNode.x; dy = dstNode.y + 35;
                            const dstElem = document.getElementById(c.to);
                            if (dstElem) {
                                const inPort = dstElem.querySelector('.port-socket');
                                const wc = getWorldCoords(inPort);
                                if (wc) { dx = wc.x; dy = wc.y; }
                            }
                        }
                        
                        if (dx !== undefined && dy !== undefined) {
                            ctx.beginPath();
                            ctx.moveTo(sx, sy);
                            const midX = (sx + dx) / 2;
                            ctx.bezierCurveTo(midX, sy, midX, dy, dx, dy);
                            if (ctx.isPointInStroke(clickX, clickY)) {
                                clickedConnection = i;
                                break;
                            }
                        }
                    }
                    ctx.restore();
                    
                    if (clickedConnection !== -1) {
                        showConfirmModal('선택하신 연결선을 삭제하시겠습니까?', () => {
                            connections.splice(clickedConnection, 1);
                            saveState();
                            renderNodes();
                        });
                    }
                }
            });

            document.getElementById('canvas-container').addEventListener('mousedown', (e) => {
                if (e.target.id === 'canvas-container' || e.target.id === 'flowCanvas' || e.target.classList.contains('factory-bg-grid')) {
                    const cRect = document.getElementById('canvas-container').getBoundingClientRect();
                    
                    if (e.button === 0 && !e.ctrlKey && !e.metaKey) { // Left click
                        isMarquee = true;
                        marqueeStartX = ((e.clientX - cRect.left) - panX) / zoom;
                        marqueeStartY = ((e.clientY - cRect.top) - panY) / zoom;
                        marqueeEl.style.display = 'block';
                        marqueeEl.style.left = marqueeStartX + 'px';
                        marqueeEl.style.top = marqueeStartY + 'px';
                        marqueeEl.style.width = '0px';
                        marqueeEl.style.height = '0px';
                        
                        if (!e.shiftKey) {
                            selectedNodeIds.clear();
                            document.querySelectorAll('.n8n-node').forEach(n => n.classList.remove('selected'));
                        }
                    } else { // Right/Middle click
                        isPanning = true;
                        panStartX = (e.clientX - cRect.left) - panX;
                        panStartY = (e.clientY - cRect.top) - panY;
                    }
                }
            });

            window.addEventListener('mouseup', () => {
                isPanning = false;
                if (isMarquee) {
                    isMarquee = false;
                    marqueeEl.style.display = 'none';
                    if (selectedNodeIds.size === 1) {
                        selectedNodeId = Array.from(selectedNodeIds)[0];
                    } else if (selectedNodeIds.size === 0) {
                        selectedNodeId = null;
                    }
                }
            });

            document.getElementById('canvas-container').addEventListener('wheel', (e) => {
                e.preventDefault();
                const zoomIntensity = 0.1;
                const delta = e.deltaY < 0 ? 1 : -1;
                const newZoom = Math.min(Math.max(0.2, zoom + delta * zoomIntensity), 3);
                
                const cRect = document.getElementById('canvas-container').getBoundingClientRect();
                const rx = e.clientX - cRect.left;
                const ry = e.clientY - cRect.top;
                
                panX = rx - (rx - panX) * (newZoom / zoom);
                panY = ry - (ry - panY) * (newZoom / zoom);
                zoom = newZoom;
                
                updateTransform();
            }, { passive: false });

            document.getElementById('canvas-container').addEventListener('mousemove', (e) => {
                const cRect = document.getElementById('canvas-container').getBoundingClientRect();
                const rx = e.clientX - cRect.left;
                const ry = e.clientY - cRect.top;
                
                if (isPanning) {
                    panX = rx - panStartX;
                    panY = ry - panStartY;
                    updateTransform();
                } else if (isMarquee) {
                    const currentX = (rx - panX) / zoom;
                    const currentY = (ry - panY) / zoom;
                    
                    const left = Math.min(marqueeStartX, currentX);
                    const top = Math.min(marqueeStartY, currentY);
                    const width = Math.abs(currentX - marqueeStartX);
                    const height = Math.abs(currentY - marqueeStartY);
                    
                    marqueeEl.style.left = left + 'px';
                    marqueeEl.style.top = top + 'px';
                    marqueeEl.style.width = width + 'px';
                    marqueeEl.style.height = height + 'px';
                    
                    if (!e.shiftKey) selectedNodeIds.clear();
                    nodesData.forEach(n => {
                        if (n.x + 80 > left && n.x < left + width && n.y + 50 > top && n.y < top + height) {
                            selectedNodeIds.add(n.id);
                        }
                    });
                    
                    document.querySelectorAll('.n8n-node').forEach(el => {
                        if (selectedNodeIds.has(el.id)) el.classList.add('selected');
                        else el.classList.remove('selected');
                    });
                }
                
                mouseX = (rx - panX) / zoom;
                mouseY = (ry - panY) / zoom;
                rawMouseX = rx;
                rawMouseY = ry;
            });

            function renderNodes() {
                container.innerHTML = '';
                
                const centralHub = document.getElementById('central-hub');
                if (centralHub) {
                    if (viewsData[currentViewId].hubPos) {
                        centralHub.style.left = viewsData[currentViewId].hubPos.x + 'px';
                        centralHub.style.top = viewsData[currentViewId].hubPos.y + 'px';
                    } else {
                        centralHub.style.left = '880px';
                        centralHub.style.top = '150px';
                    }
                }

                nodesData.forEach(node => {
                    const isSelected = selectedNodeIds.has(node.id);
                    const elem = document.createElement('div');
                    elem.className = `n8n-node ${isSelected ? 'selected' : ''} ${node.isAnomalous ? 'anomalous' : ''}`;
                    elem.id = node.id;
                    elem.style.left = node.x + 'px';
                    elem.style.top = node.y + 'px';

                    const tagHTML = node.tag ? `<div class="micro-tag" style="background:rgba(52,211,153,0.15); color:#34D399; margin-bottom:2px;">${node.tag}</div>` : '';
                    const processHTML = node.process ? `<div class="micro-tag" style="background:rgba(168,85,247,0.15); color:#A855F7; margin-bottom:2px;">${node.process}</div>` : '';
                    const alarmBadgeHTML = node.isAnomalous ? `<div class="node-alarm-badge" title="이상 감지 발생! 더블클릭하여 조치">FAIL</div>` : '';

                    let lotBadgeHTML = '';
                    if (node.currentLotId) {
                        const lotShort = node.currentLotId.replace('LOT-20260812-', '');
                        lotBadgeHTML = `<div class=\"micro-lot-badge ${node.isAnomalous ? 'lot-fail' : ''}\" title=\"현재 가공 Lot: ${node.currentLotId}\"> ${lotShort}</div>`;
                    }

                    elem.innerHTML = `
                        ${alarmBadgeHTML}
                        <div class="micro-box-name">${node.name}</div>
                        ${tagHTML}
                        ${processHTML}
                        ${lotBadgeHTML}
                        <div class="port-socket" data-nodeid="${node.id}" title="연결 포인트"></div>
                    `;

                    elem.addEventListener('dblclick', (e) => {
                        if (node.tag === 'Fab' || (node.params && node.params.includes('Fab'))) {
                            navigateView(node.id);
                        } else {
                            selectedNodeId = node.id;
                            window.editModalMode = 'chart';
                            openEditModal();
                        }
                    });

                    elem.addEventListener('contextmenu', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        selectedNodeId = node.id;
                        window.editModalMode = 'edit';
                        openEditModal();
                    });

                    elem.addEventListener('mousedown', (e) => {
                        if (e.target.classList.contains('tag-del') || e.target.classList.contains('node-delete-icon')) return;

                        const portSocket = e.target.closest('.port-socket');
                        if (portSocket) {
                            const pNodeId = portSocket.getAttribute('data-nodeid');
                            wiringStartNodeId = pNodeId;
                            
                            function onPortMouseUp(upEvent) {
                                const targetElem = document.elementFromPoint(upEvent.clientX, upEvent.clientY);
                                let targetNodeId = null;
                                
                                if (targetElem) {
                                    const inPort = targetElem.closest('.port-socket');
                                    if (inPort) {
                                        targetNodeId = inPort.getAttribute('data-nodeid');
                                    } else if (targetElem.closest('#node-ai')) {
                                        targetNodeId = 'node-ai';
                                    } else if (targetElem.closest('#node-rag')) {
                                        targetNodeId = 'node-rag';
                                    }
                                }
                                
                                if (targetNodeId && wiringStartNodeId !== targetNodeId) {
                                    if (!connections.some(c => (c.from === wiringStartNodeId && c.to === targetNodeId) || (c.from === targetNodeId && c.to === wiringStartNodeId))) {
                                        connections.push({ from: wiringStartNodeId, to: targetNodeId });
                                        saveState();
                                    }
                                }
                                wiringStartNodeId = null;
                                window.removeEventListener('mouseup', onPortMouseUp);
                            }
                            window.addEventListener('mouseup', onPortMouseUp);
                            return;
                        }

                        if (!selectedNodeIds.has(node.id)) {
                            if (!e.shiftKey) {
                                selectedNodeIds.clear();
                            }
                            selectedNodeIds.add(node.id);
                            selectedNodeId = node.id;
                            
                            document.querySelectorAll('.n8n-node').forEach(el => {
                                if (selectedNodeIds.has(el.id)) el.classList.add('selected');
                                else el.classList.remove('selected');
                            });
                        }

                        const cRect = document.getElementById('canvas-container').getBoundingClientRect();
                        const startMouseWorldX = ((e.clientX - cRect.left) - panX) / zoom;
                        const startMouseWorldY = ((e.clientY - cRect.top) - panY) / zoom;
                        
                        const startPositions = new Map();
                        selectedNodeIds.forEach(id => {
                            const n = nodesData.find(nd => nd.id === id);
                            if (n) startPositions.set(id, {x: n.x, y: n.y});
                        });

                        function onMouseMove(moveEvent) {
                            const curWorldX = ((moveEvent.clientX - cRect.left) - panX) / zoom;
                            const curWorldY = ((moveEvent.clientY - cRect.top) - panY) / zoom;
                            const dx = curWorldX - startMouseWorldX;
                            const dy = curWorldY - startMouseWorldY;

                            selectedNodeIds.forEach(id => {
                                const n = nodesData.find(nd => nd.id === id);
                                const startPos = startPositions.get(id);
                                if (n && startPos) {
                                    const el = document.getElementById(id);
                                    let nodeW = 65;
                                    let nodeH = 50;
                                    if (el) {
                                        nodeW = el.offsetWidth || 65;
                                        nodeH = el.offsetHeight || 50;
                                    }
                                    
                                    const gridSize = 40;
                                    const dotOffset = gridSize / 2; // Dots are at center of 40x40 cells
                                    
                                    let targetX = startPos.x + dx;
                                    let targetY = startPos.y + dy;
                                    let targetCx = targetX + nodeW / 2;
                                    let targetCy = targetY + nodeH / 2;
                                    
                                    let snappedCx = Math.round((targetCx - dotOffset) / gridSize) * gridSize + dotOffset;
                                    let snappedCy = Math.round((targetCy - dotOffset) / gridSize) * gridSize + dotOffset;
                                    
                                    n.x = snappedCx - nodeW / 2;
                                    n.y = snappedCy - nodeH / 2;
                                    
                                    if (el) {
                                        el.style.left = n.x + 'px';
                                        el.style.top = n.y + 'px';
                                    }
                                }
                            });
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

            function performNodeDeletion(id) {
                nodesData = nodesData.filter(n => n.id !== id);
                connections = connections.filter(c => c.from !== id && c.to !== id);
                if (selectedNodeId === id) {
                    selectedNodeId = nodesData.length > 0 ? nodesData[0].id : null;
                }
                saveState();
                renderNodes();
            }

            function deleteNodeById(id) {
                const nodeToDelete = nodesData.find(n => n.id === id);
                if (nodeToDelete && nodeToDelete.params && nodeToDelete.params.includes('Fab')) {
                    if (viewsData[id] && viewsData[id].nodes && viewsData[id].nodes.length > 0) {
                        showConfirmModal('이 공장(Fab) 내부에는 장비가 배치되어 있습니다. 정말로 공장과 내부 장비를 모두 삭제하시겠습니까?', () => {
                            delete viewsData[id];
                            performNodeDeletion(id);
                        });
                        return;
                    }
                    delete viewsData[id];
                }
                performNodeDeletion(id);
            }

            function deleteNodeFromModal() {
                if (selectedNodeId) {
                    deleteNodeById(selectedNodeId);
                    closeModal('edit-modal');
                }
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

            function closeModal(modalId) {
                if (modalId === 'edit-modal' && typeof clearChartState === 'function') {
                    clearChartState();
                }
                document.getElementById(modalId).style.display = 'none';
            }
            function closeModalOnOverlay(e, modalId) {
                if (e.target.id === modalId) closeModal(modalId);
            }
            
            let confirmActionCallback = null;
            function showConfirmModal(message, callback) {
                document.getElementById('confirm-modal-message').innerText = message;
                confirmActionCallback = callback;
                document.getElementById('confirm-modal').style.display = 'flex';
            }
            function executeConfirmAction() {
                if (confirmActionCallback) confirmActionCallback();
                closeModal('confirm-modal');
            }
            function manualSave() {
                saveState();
                showToast('위치와 연결이 성공적으로 저장되었습니다!');
            }

            function showToast(message) {
                const toast = document.getElementById('toast-message');
                if (toast) {
                    toast.innerText = message;
                    toast.classList.add('show');
                    if (window._toastTimeout) clearTimeout(window._toastTimeout);
                    window._toastTimeout = setTimeout(() => {
                        toast.classList.remove('show');
                    }, 2800);
                }
            }

            function renderFailLogTable(node) {
                const logBody = document.getElementById('sensor-fail-log-body');
                const countBadge = document.getElementById('fail-unresolved-count-badge');
                const modalLotBadge = document.getElementById('modal-current-lot-badge');
                if (modalLotBadge) {
                    const curLot = node.currentLotId || '대기 중';
                    modalLotBadge.innerText = `현재 가공 Lot: ${curLot}`;
                }
                if (!logBody) return;

                if (!node || !node.failLogs || node.failLogs.length === 0) {
                    logBody.innerHTML = `
                        <tr>
                            <td colspan="5" style="padding: 14px; text-align: center; color: #94A3B8; font-size: 0.7rem;">
                                기록된 Fail 내역이 없습니다 (정상 작동 중)
                            </td>
                        </tr>
                    `;
                    if (countBadge) {
                        countBadge.className = 'fail-unresolved-badge all-clear';
                        countBadge.innerText = '정상 (0건)';
                    }
                    return;
                }

                const unresolvedLogs = node.failLogs.filter(l => l.status === 'UNRESOLVED');
                if (countBadge) {
                    if (unresolvedLogs.length > 0) {
                        countBadge.className = 'fail-unresolved-badge';
                        countBadge.innerText = `미조치 ${unresolvedLogs.length}건`;
                    } else {
                        countBadge.className = 'fail-unresolved-badge all-clear';
                        countBadge.innerText = '모든 조치 완료';
                    }
                }

                let rowsHtml = '';
                node.failLogs.forEach(log => {
                    const isResolved = log.status === 'RESOLVED';
                    const targetLotId = log.lotId || 'LOT-20260812-B02';
                    const lotDisplay = log.lotDisplay || (log.lotId ? `${log.lotId}` : 'LOT-20260812-B02');
                    rowsHtml += `
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.06); background: ${isResolved ? 'rgba(52, 211, 153, 0.04)' : 'rgba(239, 68, 68, 0.08)'};">
                            <td style="padding: 6px 4px; white-space: nowrap; font-size: 0.65rem; color: ${isResolved ? '#94A3B8' : '#F1F5F9'};">
                                ${log.timestamp}
                            </td>
                            <td style="padding: 6px 4px; white-space: nowrap; font-size: 0.65rem; color: #38BDF8; font-weight: 600;">
                                <span class="lot-trace-link" onclick="openLotTraceModal('${targetLotId}')" title="클릭하여 ${targetLotId}의 35개 전 공정 이력 추적">
                                ${lotDisplay}
                                </span>
                            </td>
                            <td style="padding: 6px 4px; color: ${isResolved ? '#94A3B8' : '#EF4444'}; font-weight: bold; font-size: 0.65rem;">
                                ${log.failedParam}
                            </td>
                            <td style="padding: 6px 4px; font-size: 0.6rem; color: #94A3B8; word-break: break-all;">
                                ${log.allData}
                            </td>
                            <td style="padding: 6px 4px; text-align: center; white-space: nowrap;">
                                ${isResolved
                                    ? `<span class="badge-resolved" title="조치 완료 시각: ${log.resolvedAt || '-'}">✅ 조치 완료</span>`
                                    : `<button type="button" class="btn-resolve-action" onclick="resolveSingleFailLog('${node.id}', '${log.id}')">🛠️ 조치 완료</button>`
                                }
                            </td>
                        </tr>
                    `;
                });
                logBody.innerHTML = rowsHtml;
            }

            window.openLotTraceModal = function(selectedLotId) {
                const modal = document.getElementById('lot-trace-modal');
                if (!modal) return;
                modal.style.display = 'flex';
                
                const selector = document.getElementById('lot-trace-selector');
                if (selector && selectedLotId) {
                    selector.value = selectedLotId;
                }
                const currentVal = selector ? selector.value : (selectedLotId || 'LOT-20260812-B02');
                renderLotTraceTimeline(currentVal);
            };

            window.renderLotTraceTimeline = function(lotId) {
                const container = document.getElementById('lot-trace-steps-container');
                const infoBanner = document.getElementById('lot-summary-info');
                const statusBadge = document.getElementById('lot-summary-status-badge');
                if (!container) return;

                const nodes = (viewsData['fab-cmos'] && viewsData['fab-cmos'].nodes) ? viewsData['fab-cmos'].nodes : [];
                
                let defectCount = 0;
                let originStepName = '';
                let cascadeCount = 0;

                let stepsHtml = '';
                nodes.forEach((node, idx) => {
                    const stepNumStr = node.address ? node.address.replace('step_', '') : (idx + 1 < 10 ? '0' + (idx + 1) : '' + (idx + 1));
                    
                    let stepStatus = 'NORMAL';
                    let defectDetail = '';
                    
                    // Check if node has preloaded CSV or parsed fail logs for this lot
                    if (node._parsedStatusData && node._parsedFailDetails && node._parsedRowMeta) {
                        for (let i = 0; i < node._parsedRowMeta.length; i++) {
                            const meta = node._parsedRowMeta[i];
                            if (meta.lotId === lotId) {
                                if (node._parsedStatusData[i]) {
                                    const detail = node._parsedFailDetails[i];
                                    if (node.id === 'step-05' || node.name.includes('STI 식각') || node.name.includes('컨택홀 포토') || node.id === 'step-22' || node.id === 'step-29') {
                                        if (stepStatus !== 'DEFECT_ORIGIN') {
                                            stepStatus = 'DEFECT_ORIGIN';
                                            originStepName = node.name;
                                            defectDetail = detail ? detail.failedParam : '파라미터 규격 이탈';
                                        }
                                    } else {
                                        if (stepStatus === 'NORMAL') {
                                            stepStatus = 'CASCADE_DEFECT';
                                            defectDetail = detail ? detail.failedParam : '선행 공정 결함 연쇄 전파';
                                        }
                                    }
                                }
                            }
                        }
                    } else if (node.failLogs) {
                        const matchingLogs = node.failLogs.filter(l => l.lotId === lotId || !l.lotId);
                        if (matchingLogs.length > 0) {
                            if (node.id === 'step-05' || node.name.includes('STI 식각') || node.name.includes('컨택홀 포토') || node.id === 'step-22' || node.id === 'step-29') {
                                stepStatus = 'DEFECT_ORIGIN';
                                originStepName = node.name;
                            } else {
                                stepStatus = 'CASCADE_DEFECT';
                            }
                            defectDetail = matchingLogs[0].failedParam;
                        }
                    }

                    if (stepStatus === 'DEFECT_ORIGIN') defectCount++;
                    if (stepStatus === 'CASCADE_DEFECT') cascadeCount++;

                    let cardClass = 'status-ok';
                    let badgeHtml = '<span class="lot-step-badge badge-ok"> 정상 가공 완료</span>';
                    let descHtml = '<div class="lot-step-desc">모든 공정 파라미터 규격(Spec) 내 정상 가공</div>';

                    if (stepStatus === 'DEFECT_ORIGIN') {
                        cardClass = 'status-origin';
                        badgeHtml = '<span class="lot-step-badge badge-origin"> 불량 발생 원점 (ORIGIN)</span>';
                        descHtml = `<div class="lot-step-desc" style="color: #FCA5A5; font-weight: bold;">[이상 원인] ${defectDetail || '챔버 파워/압력 급변'}</div>`;
                    } else if (stepStatus === 'CASCADE_DEFECT') {
                        cardClass = 'status-cascade';
                        badgeHtml = '<span class="lot-step-badge badge-cascade"> 연쇄 불량 전파 (CASCADE)</span>';
                        descHtml = `<div class="lot-step-desc" style="color: #FCD34D;">[연쇄 영향] ${defectDetail || '선행 불량으로 인한 품질 편차 전파'}</div>`;
                    }

                    stepsHtml += `
                        <div class="lot-step-card ${cardClass}" onclick="openNodeFromTrace('${node.id}')" style="cursor: pointer;" title="클릭하여 [${node.name}] 장비 상세 데이터 확인">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span class="lot-step-num">Step ${stepNumStr}</span>
                                ${badgeHtml}
                            </div>
                            <div class="lot-step-title">${node.name}</div>
                            <div style="font-size: 0.58rem; color: #64748B;">공정: ${node.process || node.tag || 'Standard'}</div>
                            ${descHtml}
                        </div>
                    `;
                });

                container.innerHTML = stepsHtml;

                if (infoBanner && statusBadge) {
                    infoBanner.innerHTML = `
                        <div>
                            <div> 추적 대상 Lot: <strong style="color:#38BDF8; font-size:0.8rem;">${lotId}</strong> | 웨이퍼 수량: <strong>25매</strong></div>
                            <div style="font-size:0.65rem; color:#94A3B8; margin-top:2px;">OHT 이송 경로: Step 01 (웨이퍼 준비) ➔ Step 35 (칩 테스트)</div>
                        </div>
                    `;
                    if (defectCount > 0) {
                        statusBadge.innerHTML = `
                            <div style="background: rgba(239, 68, 68, 0.2); border: 1px solid #EF4444; color: #FCA5A5; padding: 4px 8px; border-radius: 6px; font-weight: bold; text-align: right;">
                                 [${originStepName}] 결함 발생 ➔ 후속 ${cascadeCount}개 공정 연쇄 영향
                            </div>
                        `;
                    } else {
                        statusBadge.innerHTML = `
                            <div style="background: rgba(52, 211, 153, 0.15); border: 1px solid #34D399; color: #34D399; padding: 4px 8px; border-radius: 6px; font-weight: bold; text-align: right;">
                                 전 공정 정상 가공 완료 (Zero Defect)
                            </div>
                        `;
                    }
                }
            };

            window.openNodeFromTrace = function(nodeId) {
                closeModal('lot-trace-modal');
                selectedNodeId = nodeId;
                window.editModalMode = 'chart';
                openEditModal();
            };

            window.resolveSingleFailLog = function(nodeId, logId) {
                let targetNode = null;
                Object.values(viewsData).forEach(view => {
                    if (view.nodes) {
                        const found = view.nodes.find(n => n.id === nodeId);
                        if (found) targetNode = found;
                    }
                });
                if (!targetNode || !targetNode.failLogs) return;

                const logItem = targetNode.failLogs.find(l => l.id === logId);
                if (logItem) {
                    logItem.status = 'RESOLVED';
                    logItem.resolvedAt = new Date().toLocaleTimeString();
                }

                const stillUnresolved = targetNode.failLogs.some(l => l.status === 'UNRESOLVED');
                if (!stillUnresolved) {
                    targetNode.isAnomalous = false;
                    targetNode.hasActiveAlarm = false;
                    showToast(` [${targetNode.name}] 모든 결함 조치 완료 - 모듈 경고등(빨간색 테두리)이 해제되었습니다.`);
                } else {
                    showToast(` [${targetNode.name}] 해당 결함 항목이 조치 완료되었습니다.`);
                }

                renderFailLogTable(targetNode);
                renderNodes();
                saveState();
            };

            window.resolveAllFailLogsForCurrentNode = function() {
                let targetNode = null;
                Object.values(viewsData).forEach(view => {
                    if (view.nodes) {
                        const found = view.nodes.find(n => n.id === selectedNodeId);
                        if (found) targetNode = found;
                    }
                });
                if (!targetNode || !targetNode.failLogs || targetNode.failLogs.length === 0) {
                    showToast('조치할 결함 로그가 없습니다.');
                    return;
                }

                targetNode.failLogs.forEach(l => {
                    l.status = 'RESOLVED';
                    l.resolvedAt = new Date().toLocaleTimeString();
                });
                targetNode.isAnomalous = false;
                targetNode.hasActiveAlarm = false;

                renderFailLogTable(targetNode);
                renderNodes();
                saveState();
                showToast(` [${targetNode.name}] 전체 결함 로그 조치 완료 - 모듈 경고등(빨간색 테두리)이 꺼졌습니다.`);
            };

            window.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    closeModal('add-modal');
                    closeModal('edit-modal');
                    wiringStartNodeId = null;
                }
                if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
                    e.preventDefault();
                    manualSave();
                }
                if ((e.key === '`' || e.code === 'Backquote') && currentViewId !== 'main') {
                    e.preventDefault();
                    navigateView('main');
                }
            });

            function openAddNodeModal() {
                const title = document.getElementById('add-modal-title');
                const tagInput = document.getElementById('node-tag-input');
                const nameLabel = document.getElementById('add-modal-name-label');
                const extraFields = document.getElementById('add-modal-extra-fields');
                
                document.getElementById('node-name-input').value = '';
                
                if (currentViewId === 'main') {
                    if (title) title.innerText = '➕ 신규 공장 추가';
                    if (nameLabel) nameLabel.innerText = '공장 이름';
                    if (extraFields) extraFields.style.display = 'none';
                    if (tagInput) { tagInput.value = 'Fab'; tagInput.disabled = true; }
                } else {
                    if (title) title.innerText = '➕ 신규 장비 추가';
                    if (nameLabel) nameLabel.innerText = '장비 이름';
                    if (extraFields) extraFields.style.display = 'block';
                    if (tagInput) { tagInput.value = 'Etch'; tagInput.disabled = false; }
                }
                document.getElementById('node-process-input').value = '';
                document.getElementById('node-add-param-input').value = '';
                document.getElementById('node-add-part-input').value = '';
                document.getElementById('add-modal').style.display = 'flex';
            }
            function confirmAddNode() {
                const name = document.getElementById('node-name-input').value || '새 장비';
                const isFab = currentViewId === 'main';
                const tagStr = isFab ? 'Fab' : (document.getElementById('node-tag-input').value || '');
                const procStr = document.getElementById('node-process-input').value || '';
                const icon = '';
                
                const newId = (isFab ? 'fab-' : 'node-') + Date.now();
                // Calculate center of current screen in world coordinates
                const cRect = document.getElementById('canvas-container').getBoundingClientRect();
                const centerX = ((cRect.width / 2) - panX) / zoom - 75;
                const centerY = ((cRect.height / 2) - panY) / zoom - 30;

                const gridSize = 40;
                const dotOffset = gridSize / 2;
                let nodeW = 65;
                let nodeH = 50;

                let targetX = centerX + ((nodesData.length % 5) * 15);
                let targetY = centerY + ((nodesData.length % 5) * 15);
                
                let targetCx = targetX + nodeW / 2;
                let targetCy = targetY + nodeH / 2;
                
                let snappedCx = Math.round((targetCx - dotOffset) / gridSize) * gridSize + dotOffset;
                let snappedCy = Math.round((targetCy - dotOffset) / gridSize) * gridSize + dotOffset;
                
                let newX = snappedCx - nodeW / 2;
                let newY = snappedCy - nodeH / 2;
                
                let paramStr = document.getElementById('node-add-param-input').value.trim();
                let partStr = document.getElementById('node-add-part-input').value.trim();
                
                let initialParams = isFab ? ['Fab'] : [];
                if (paramStr) {
                    initialParams.push(...paramStr.split(',').map(s => s.trim()).filter(s => s));
                } else if (!isFab) {
                    initialParams.push('Status: OK');
                }

                let initialParts = isFab ? [] : [];
                if (partStr) {
                    initialParts.push(...partStr.split(',').map(s => s.trim()).filter(s => s));
                } else if (!isFab) {
                    initialParts.push('Standard Part');
                }

                nodesData.push({
                    id: newId,
                    name: name,
                    icon: icon,
                    tag: tagStr,
                    process: procStr,
                    x: newX,
                    y: newY,
                    params: initialParams,
                    parts: initialParts
                });
                selectedNodeId = newId;
                saveState();
                renderNodes();
                closeModal('add-modal');
            }

            function switchEditTab(tabName) {
                document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(tc => {
                    tc.classList.remove('active');
                    tc.style.display = '';
                });
                const tBtn = document.getElementById(`tab-btn-${tabName}`);
                if (tBtn) tBtn.classList.add('active');
                const tContent = document.getElementById(`tab-content-${tabName}`);
                if (tContent) tContent.classList.add('active');
            }

            function openEditModal() {
                const node = nodesData.find(n => n.id === selectedNodeId);
                if (!node) {
                    alert('편집할 장비 노드를 먼저 선택해주세요.');
                    return;
                }
                const titleEl = document.getElementById('modal-selected-name');
                titleEl.innerHTML = `
                    <span id="edit-node-name-text" style="cursor: pointer;" title="더블클릭하여 이름 수정">${node.name}</span>
                    <input id="edit-node-name-input" type="text" style="display:none; font-size:0.9rem; font-weight:700; color:#34D399; padding:0; margin:0; width:150px; background:transparent; border:none; border-bottom:1px solid #34D399; outline:none;" value="${node.name}">
                `;

                const textSpan = document.getElementById('edit-node-name-text');
                const nameInput = document.getElementById('edit-node-name-input');
                
                textSpan.addEventListener('dblclick', () => {
                    textSpan.style.display = 'none';
                    nameInput.style.display = 'inline-block';
                    nameInput.focus();
                });
                
                nameInput.addEventListener('blur', () => {
                    if (nameInput.value.trim() !== '') {
                        textSpan.innerText = nameInput.value;
                    }
                    nameInput.style.display = 'none';
                    textSpan.style.display = 'inline-block';
                });
                
                nameInput.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') nameInput.blur();
                });
                
                const tagInput = document.getElementById('edit-tag-input');
                const tabContainer = document.getElementById('edit-tab-container');
                const fabContent = document.getElementById('fab-edit-content');
                
                const modalBox = document.querySelector('#edit-modal .modal-box');
                const leftCol = document.getElementById('edit-modal-left');
                const rightCol = document.getElementById('edit-modal-right');
                
                if (currentViewId === 'main') {
                    tagInput.value = 'Fab';
                    tagInput.disabled = true;
                    if (tabContainer) tabContainer.style.display = 'none';
                    if (fabContent) fabContent.style.display = 'block';
                    
                    // Shrink modal for Fab view (hide sensor column)
                    if (modalBox) modalBox.style.width = '400px';
                    if (leftCol) leftCol.style.display = 'none';
                    if (rightCol) rightCol.style.width = '100%';

                    document.querySelectorAll('#edit-modal .tab-content').forEach(tc => {
                        tc.classList.remove('active');
                        tc.style.display = 'none';
                    });
                    
                    const internalNodes = viewsData[node.id] && viewsData[node.id].nodes ? viewsData[node.id].nodes : [];
                    const fabList = document.getElementById('fab-internal-nodes-list');
                    if (fabList) {
                        fabList.innerHTML = internalNodes.length > 0 
                            ? internalNodes.map(n => `<div style="font-size: 0.75rem; color: #E2E8F0; padding: 6px; border-bottom: 1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;"><span>${n.name}</span><span style="color:#94A3B8; font-size:0.65rem;">${n.tag || ''}</span></div>`).join('')
                            : '<div style="font-size:0.7rem; color:#94A3B8; padding: 10px; text-align:center;">내부에 장비가 없습니다.</div>';
                    }
                } else {
                    tagInput.value = node.tag || 'Etch';
                    tagInput.disabled = false;
                    if (tabContainer) tabContainer.style.display = 'flex';
                    if (fabContent) fabContent.style.display = 'none';
                    
                    // Adjust modal layout based on editModalMode
                    if (modalBox) {
                        if (window.editModalMode === 'chart') {
                            modalBox.style.width = '95vw';
                        } else if (window.editModalMode === 'edit') {
                            modalBox.style.width = '95vw';
                        } else {
                            modalBox.style.width = '95vw';
                        }
                        modalBox.style.height = '95vh';
                        modalBox.style.display = 'flex';
                        modalBox.style.flexDirection = 'column';
                        modalBox.style.overflow = 'hidden';
                    }
                    
                    if (window.editModalMode === 'chart') {
                        if (leftCol) leftCol.style.display = 'flex';
                        if (rightCol) rightCol.style.display = 'none';
                    } else if (window.editModalMode === 'edit') {
                        if (leftCol) leftCol.style.display = 'none';
                        if (rightCol) {
                            rightCol.style.display = 'flex';
                            rightCol.style.width = '100%';
                        }
                    } else {
                        if (leftCol) leftCol.style.display = 'flex';
                        if (rightCol) {
                            rightCol.style.display = 'flex';
                            rightCol.style.width = 'auto';
                        }
                    }


                    document.querySelectorAll('#edit-modal .tab-content').forEach(tc => tc.style.display = '');
                    switchEditTab('info');
                    
                    const uploadInput = document.getElementById('sensor-csv-upload');
                    const uploadFilename = document.getElementById('sensor-csv-filename');
                    let badgeContainer = document.getElementById('test-case-active-badge');
                    
                    if (uploadFilename) {
                        if (node.testCsvData && node.testCsvName) {
                            uploadFilename.innerText = node.testCsvName;
                            uploadFilename.style.color = '#34D399';
                        } else if (node.manualCsvData && node.manualCsvName) {
                            uploadFilename.innerText = node.manualCsvName;
                            uploadFilename.style.color = '#34D399';
                        } else {
                            uploadFilename.innerText = '선택된 파일 없음';
                            uploadFilename.style.color = '#94A3B8';
                        }
                    }
                    if (uploadInput) {
                        uploadInput.value = '';
                        try {
                            if (node.testCsvData && node.testCsvName) {
                                const file = new File([node.testCsvData], node.testCsvName, { type: 'text/csv' });
                                const dt = new DataTransfer();
                                dt.items.add(file);
                                uploadInput.files = dt.files;
                            } else if (node.manualCsvData && node.manualCsvName) {
                                const file = new File([node.manualCsvData], node.manualCsvName, { type: 'text/csv' });
                                const dt = new DataTransfer();
                                dt.items.add(file);
                                uploadInput.files = dt.files;
                            }
                        } catch(e) {}
                    }
                    if (badgeContainer) badgeContainer.style.display = 'none';
                    
                    if (node.testCsvData) {
                        setTimeout(() => startChartWithCSV(node.testCsvData), 100);
                    } else {
                        if (node.manualCsvData) {
                            setTimeout(() => startChartWithCSV(node.manualCsvData), 100);
                        }
                    }
                }
                
                let displayAddr = node.address || '';
                if (displayAddr.startsWith('step_')) displayAddr = displayAddr.replace('step_', '');
                document.getElementById('edit-address-input').value = displayAddr;
                
                document.getElementById('edit-process-input').value = node.process || '';
                
                const incList = document.getElementById('current-incoming-list');
                const outList = document.getElementById('current-outgoing-list');
                
                const incConns = connections.filter(c => c.to === node.id);
                const outConns = connections.filter(c => c.from === node.id);
                
                incList.innerHTML = incConns.map(c => {
                    const fromNode = nodesData.find(n => n.id === c.from) || {name: c.from};
                    return `<div class="conn-search-item"><span>${fromNode.name}</span><span class="tag-del" style="font-size:0.65rem;" onclick="removeConnModal('${c.from}', '${c.to}')">✕</span></div>`;
                }).join('') || '<div style="font-size:0.6rem; color:#64748B; text-align:center; padding-top:0.2rem;">이전 공정 없음</div>';
                
                outList.innerHTML = outConns.map(c => {
                    const toNode = nodesData.find(n => n.id === c.to) || {name: c.to};
                    return `<div class="conn-search-item"><span>${toNode.name}</span><span class="tag-del" style="font-size:0.65rem;" onclick="removeConnModal('${c.from}', '${c.to}')">✕</span></div>`;
                }).join('') || '<div style="font-size:0.6rem; color:#64748B; text-align:center; padding-top:0.2rem;">이후 공정 없음</div>';
                
                document.getElementById('conn-search-input').value = '';
                document.getElementById('conn-search-results').style.display = 'none';
                
                const pContainer = document.getElementById('current-params-list');
                pContainer.innerHTML = node.params.map((p, idx) => `<span class="param-tag">${p} <span class="tag-del" onclick="removeParamModal('${node.id}', ${idx})">✕</span></span>`).join('') || '<span style="font-size:0.68rem; color:#64748B;">등록된 파라미터 없음</span>';

                const ptContainer = document.getElementById('current-parts-list');
                ptContainer.innerHTML = node.parts.map((pt, idx) => `<span class="part-tag">${pt} <span class="tag-del" onclick="removePartModal('${node.id}', ${idx})">✕</span></span>`).join('') || '<span style="font-size:0.68rem; color:#64748B;">등록된 하위 부품 없음</span>';

                document.getElementById('param-input').value = '';
                document.getElementById('part-input').value = '';
                renderFailLogTable(node);
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

            function removeConnModal(fromId, toId) {
                connections = connections.filter(c => !(c.from === fromId && c.to === toId));
                saveState();
                renderNodes();
                openEditModal();
            }

            function addConnModal(fromId, toId) {
                if (!connections.some(c => (c.from === fromId && c.to === toId))) {
                    connections.push({ from: fromId, to: toId });
                    saveState();
                    renderNodes();
                }
                openEditModal();
                document.getElementById('conn-search-input').value = '';
                document.getElementById('conn-search-results').style.display = 'none';
            }

            document.getElementById('conn-search-input').addEventListener('input', function(e) {
                const val = e.target.value.toLowerCase().trim();
                const resDiv = document.getElementById('conn-search-results');
                if (!val) {
                    resDiv.style.display = 'none';
                    return;
                }
                
                const matches = nodesData.filter(n => n.id !== selectedNodeId && n.name.toLowerCase().includes(val));
                if (matches.length === 0) {
                    resDiv.innerHTML = '<div style="padding:0.5rem; font-size:0.65rem; color:#64748B; text-align:center;">결과 없음</div>';
                } else {
                    resDiv.innerHTML = matches.map(m => `
                        <div class="conn-search-item">
                            <span>${m.name}</span>
                            <div class="conn-search-actions">
                                <button class="conn-search-action" onclick="addConnModal('${m.id}', '${selectedNodeId}')">이전 공정 추가</button>
                                <button class="conn-search-action out" onclick="addConnModal('${selectedNodeId}', '${m.id}')">이후 공정 추가</button>
                            </div>
                        </div>
                    `).join('');
                }
                resDiv.style.display = 'block';
            });

            function confirmEditNode() {
                const node = nodesData.find(n => n.id === selectedNodeId);
                if (node) {
                    const nameInput = document.getElementById('edit-node-name-input');
                    if (nameInput && nameInput.value.trim() !== '') {
                        node.name = nameInput.value;
                    }
                    node.tag = currentViewId === 'main' ? 'Fab' : document.getElementById('edit-tag-input').value;
                    
                    let addrVal = document.getElementById('edit-address-input').value.trim();
                    if (addrVal && !addrVal.startsWith('step_')) {
                        addrVal = 'step_' + addrVal;
                    }
                    node.address = addrVal;
                    
                    node.process = document.getElementById('edit-process-input').value;
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
            function getWorldCoords(elem) {
                if (!elem) return null;
                const r = elem.getBoundingClientRect();
                const cRect = document.getElementById('canvas-container').getBoundingClientRect();
                return {
                    x: ((r.left - cRect.left + r.width / 2) - panX) / zoom,
                    y: ((r.top - cRect.top + r.height / 2) - panY) / zoom
                };
            }

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
                            speed: 0.002 + Math.random() * 0.0015,
                            t: Math.random()
                        });
                    }
                });
            }

            function drawCables() {
                // 1. Draw Connections (Equipment, AI, RAG)
                connections.forEach(c => {
                    const srcNode = nodesData.find(n => n.id === c.from);
                    if (!srcNode) return;
                    
                    const srcElem = document.getElementById(c.from);
                    let sx = srcNode.x + 75, sy = srcNode.y + 30;
                    let dx, dy;
                    
                    if (srcElem) {
                        const outPort = srcElem.querySelector('.port-socket');
                        const wc = getWorldCoords(outPort);
                        if (wc) { sx = wc.x; sy = wc.y; }
                    }

                    if (c.to === 'node-ai' || c.to === 'node-rag') {
                        const dstElem = document.getElementById(c.to);
                        const wc = getWorldCoords(dstElem);
                        if (wc) { dx = wc.x; dy = wc.y; }
                    } else {
                        const dstNode = nodesData.find(n => n.id === c.to);
                        if (!dstNode) return;
                        dx = dstNode.x; dy = dstNode.y + 35;
                        const dstElem = document.getElementById(c.to);
                        if (dstElem) {
                            const inPort = dstElem.querySelector('.port-socket');
                            const wc = getWorldCoords(inPort);
                            if (wc) { dx = wc.x; dy = wc.y; }
                        }
                    }

                    if (dx !== undefined && dy !== undefined) {
                        ctx.save();
                        ctx.beginPath();
                        ctx.moveTo(sx, sy);
                        const midX = (sx + dx) / 2;
                        ctx.bezierCurveTo(midX, sy, midX, dy, dx, dy);
                        
                        ctx.save();
                        ctx.lineWidth = 15;
                        const isHovered = ctx.isPointInStroke(rawMouseX, rawMouseY);
                        ctx.restore();

                        if (isHovered) {
                            ctx.strokeStyle = '#FDE047';
                            ctx.lineWidth = 4;
                            ctx.shadowBlur = 12;
                            ctx.shadowColor = '#FDE047';
                            ctx.setLineDash([]);
                        } else {
                            if (c.to === 'node-ai') ctx.strokeStyle = 'rgba(248, 113, 113, 0.7)';
                            else if (c.to === 'node-rag') ctx.strokeStyle = 'rgba(192, 132, 252, 0.7)';
                            else ctx.strokeStyle = 'rgba(52, 211, 153, 0.65)';
                            ctx.lineWidth = 2.5;
                            ctx.setLineDash([5, 5]);
                        }
                        
                        ctx.stroke();
                        ctx.restore();
                    }
                });

                // 2. Rubber-band Guide Cable during wiring
                if (wiringStartNodeId) {
                    const srcElem = document.getElementById(wiringStartNodeId);
                    if (srcElem) {
                        const outPort = srcElem.querySelector('.port-socket');
                        const wc = getWorldCoords(outPort);
                        if (wc) {
                            ctx.save();
                            ctx.strokeStyle = 'rgba(245, 217, 150, 0.8)';
                            ctx.lineWidth = 2.5;
                            ctx.setLineDash([4, 4]);
                            ctx.beginPath();
                            ctx.moveTo(wc.x, wc.y);
                            const midX = (wc.x + mouseX) / 2;
                            ctx.bezierCurveTo(midX, wc.y, midX, mouseY, mouseX, mouseY);
                            ctx.stroke();
                            ctx.restore();
                        }
                    }
                }

                // 3. Central Hub internal connections
                const ragElem = document.getElementById('node-rag');
                const aiElem = document.getElementById('node-ai');
                if (ragElem && aiElem) {
                    const ragR = ragElem.getBoundingClientRect();
                    const aiR = aiElem.getBoundingClientRect();
                    const cRect = document.getElementById('canvas-container').getBoundingClientRect();

                    const ragX = ((ragR.left - cRect.left + ragR.width / 2) - panX) / zoom;
                    const ragY = ((ragR.top - cRect.top + ragR.height) - panY) / zoom;
                    const aiX = ((aiR.left - cRect.left + aiR.width / 2) - panX) / zoom;
                    const aiY = ((aiR.top - cRect.top) - panY) / zoom;

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
                
                // Apply Pan and Zoom to Canvas context
                ctx.save();
                ctx.translate(panX, panY);
                ctx.scale(zoom, zoom);

                drawCables();

                // Dynamic Equipment Particles
                syncParticles();
                particles.forEach(p => {
                    p.t += p.speed;
                    if (p.t > 1) p.t = 0;

                    const srcNode = nodesData.find(n => n.id === p.from);
                    if (!srcNode) return;

                    const srcElem = document.getElementById(p.from);
                    let sx = srcNode.x + 75, sy = srcNode.y + 30;
                    let dx, dy;

                    if (srcElem) {
                        const outPort = srcElem.querySelector('.port-socket');
                        const wc = getWorldCoords(outPort);
                        if (wc) { sx = wc.x; sy = wc.y; }
                    }

                    if (p.to === 'node-ai' || p.to === 'node-rag') {
                        const dstElem = document.getElementById(p.to);
                        const wc = getWorldCoords(dstElem);
                        if (wc) { dx = wc.x; dy = wc.y; }
                    } else {
                        const dstNode = nodesData.find(n => n.id === p.to);
                        if (!dstNode) return;
                        dx = dstNode.x; dy = dstNode.y + 35;
                        const dstElem = document.getElementById(p.to);
                        if (dstElem) {
                            const inPort = dstElem.querySelector('.port-socket');
                            const wc = getWorldCoords(inPort);
                            if (wc) { dx = wc.x; dy = wc.y; }
                        }
                    }
                    
                    if (dx === undefined || dy === undefined) return;

                    const t = p.t;
                    const mt = 1 - t;
                    const midX = (sx + dx) / 2;
                    
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

                // Restore Canvas context
                ctx.restore();

                requestAnimationFrame(animate);
            }

            animate();
            
            // Hub Draggable Logic
            const centralHub = document.getElementById('central-hub');
            if (centralHub) {
                centralHub.addEventListener('mousedown', (e) => {
                    const cRect = document.getElementById('canvas-container').getBoundingClientRect();
                    const startMouseWorldX = ((e.clientX - cRect.left) - panX) / zoom;
                    const startMouseWorldY = ((e.clientY - cRect.top) - panY) / zoom;
                    
                    if (!viewsData[currentViewId].hubPos) {
                        viewsData[currentViewId].hubPos = {
                            x: parseFloat(centralHub.style.left) || 880,
                            y: parseFloat(centralHub.style.top) || 150
                        };
                    }
                    const startHubX = viewsData[currentViewId].hubPos.x;
                    const startHubY = viewsData[currentViewId].hubPos.y;
                    
                    function onMouseMove(moveEvent) {
                        const curWorldX = ((moveEvent.clientX - cRect.left) - panX) / zoom;
                        const curWorldY = ((moveEvent.clientY - cRect.top) - panY) / zoom;
                        const dx = curWorldX - startMouseWorldX;
                        const dy = curWorldY - startMouseWorldY;
                        
                        const targetX = startHubX + dx;
                        const targetY = startHubY + dy;
                        
                        const hubW = centralHub.offsetWidth || 100;
                        const hubH = centralHub.offsetHeight || 150;
                        
                        const gridSize = 40;
                        const dotOffset = gridSize / 2;
                        
                        const targetCx = targetX + hubW / 2;
                        const targetCy = targetY + hubH / 2;
                        
                        const snappedCx = Math.round((targetCx - dotOffset) / gridSize) * gridSize + dotOffset;
                        const snappedCy = Math.round((targetCy - dotOffset) / gridSize) * gridSize + dotOffset;
                        
                        viewsData[currentViewId].hubPos.x = snappedCx - hubW / 2;
                        viewsData[currentViewId].hubPos.y = snappedCy - hubH / 2;
                        
                        centralHub.style.left = viewsData[currentViewId].hubPos.x + 'px';
                        centralHub.style.top = viewsData[currentViewId].hubPos.y + 'px';
                    }
                    
                    function onMouseUp() {
                        window.removeEventListener('mousemove', onMouseMove);
                        window.removeEventListener('mouseup', onMouseUp);
                        saveState();
                    }
                    
                    window.addEventListener('mousemove', onMouseMove);
                    window.addEventListener('mouseup', onMouseUp);
                });
            }

            // Chart Streaming Logic
            let sensorChart = null;
            let streamInterval = null;
            
            function clearChartState() {
                if (streamInterval) clearInterval(streamInterval);
                if (sensorChart) {
                    sensorChart.destroy();
                    sensorChart = null;
                }
                const uploadInput = document.getElementById('sensor-csv-upload');
                if (uploadInput) uploadInput.value = '';
            }

            function applyTestCase(caseName) {
                if (viewsData['fab-cmos'] && viewsData['fab-cmos'].nodes) {
                    viewsData['fab-cmos'].nodes.forEach(node => {
                        if (caseName && preloadedDatasets[caseName]) {
                            let csvData = null;
                            let matchedName = null;
                            if (node.address && preloadedDatasets[caseName][node.address]) {
                                csvData = preloadedDatasets[caseName][node.address];
                                matchedName = node.address + '.csv';
                            } else if (node.stepId && preloadedDatasets[caseName]['step_' + node.stepId]) {
                                csvData = preloadedDatasets[caseName]['step_' + node.stepId];
                                matchedName = 'step_' + node.stepId + '.csv';
                            } else if (preloadedDatasets[caseName][node.name]) {
                                csvData = preloadedDatasets[caseName][node.name];
                                matchedName = node.name + '.csv';
                            } else if (preloadedDatasets[caseName][node.name.replace(/ /g, '_')]) {
                                csvData = preloadedDatasets[caseName][node.name.replace(/ /g, '_')];
                                matchedName = node.name.replace(/ /g, '_') + '.csv';
                            }
                            
                            if (csvData) {
                                node.testCsvData = csvData;
                                node.testCsvName = matchedName;
                                const lines = csvData.trim().split('\\n');
                                if (lines.length > 1) {
                                    const headers = lines[0].split(',');
                                    const skipCols = ['Timestamp', '\ufeffTimestamp', 'Address', 'Step_ID', 'Step_Name', 'Status', 'Phase', 'Lot_ID', 'Wafer_ID', ''];
                                    const numCols = [];
                                    headers.forEach((h, i) => {
                                        if (!skipCols.includes(h.trim())) numCols.push(i);
                                    });
                                    
                                    const statusIdx = headers.findIndex(h => h.trim() === 'Status');
                                    const timeIdx = headers.findIndex(h => h.trim() === 'Timestamp');
                                    const lotIdx = headers.findIndex(h => h.trim() === 'Lot_ID');
                                    const waferIdx = headers.findIndex(h => h.trim() === 'Wafer_ID');
                                    const phaseIdx = headers.findIndex(h => h.trim() === 'Phase');
                                    
                                    // Parse numeric rows
                                    const dataRows = [];
                                    const rawRows = [];
                                    for (let i = 1; i < lines.length; i++) {
                                        const row = lines[i].split(',');
                                        if (row.length === headers.length) {
                                            const r = {};
                                            numCols.forEach(idx => { r[idx] = parseFloat(row[idx].trim()); });
                                            dataRows.push(r);
                                            rawRows.push(row);
                                        }
                                    }
                                    
                                    const statuses = [];
                                    const failDetails = [];
                                    const rowMeta = [];
                                    
                                    dataRows.forEach((rowObj, ri) => {
                                        let anomalous = false;
                                        let failMsgs = [];
                                        const fullRow = rawRows[ri];
                                        const timestamp = timeIdx >= 0 ? fullRow[timeIdx] : `Point_${ri}`;
                                        const phase = phaseIdx >= 0 ? fullRow[phaseIdx].trim() : 'DEFAULT';
                                        const rawLotId = lotIdx >= 0 ? fullRow[lotIdx].trim() : '';
                                        const isRowIdle = (phase === 'IDLE' || !rawLotId || rawLotId === '' || rawLotId === 'null' || rawLotId === 'NaN');
                                        const lotId = isRowIdle ? '' : rawLotId;
                                        const waferId = isRowIdle ? '' : (waferIdx >= 0 ? fullRow[waferIdx].trim() : '');
                                        const lotDisplay = lotId;
                                        
                                        rowMeta.push({
                                            lotId: lotId,
                                            waferId: waferId,
                                            lotDisplay: lotDisplay,
                                            phase: phase
                                        });

                                        // 1) Status column check (ground truth)
                                        if (statusIdx >= 0) {
                                            const sVal = fullRow[statusIdx].trim().toUpperCase();
                                            if (sVal && sVal !== 'NORMAL' && sVal !== 'STATUS' && sVal !== 'OK' && sVal !== 'IDLE' && sVal !== '') {
                                                anomalous = true;
                                                failMsgs.push(fullRow[statusIdx].trim());
                                            }
                                        } else {
                                            // Fallback: only if no Status column is present in CSV
                                            if (phase !== 'RAMP' && phase !== 'IDLE') {
                                                for (const colIdx of numCols) {
                                                    const window = [];
                                                    for (let w = Math.max(0, ri - 2); w <= ri; w++) {
                                                        const v = dataRows[w][colIdx];
                                                        if (!isNaN(v)) window.push(v);
                                                    }
                                                    if (window.length < 2) continue;
                                                    const avg = window.reduce((a, b) => a + b, 0) / window.length;
                                                    const std = Math.sqrt(window.reduce((a, b) => a + (b - avg) ** 2, 0) / window.length);
                                                    const current = dataRows[ri][colIdx];
                                                    if (!isNaN(current) && std > 0 && Math.abs(current - avg) > 4 * std) {
                                                        anomalous = true;
                                                        const hName = headers[colIdx].trim();
                                                        failMsgs.push(`${hName} (${current.toFixed(2)})`);
                                                        break;
                                                    }
                                                }
                                            }
                                        }
                                        
                                        statuses.push(anomalous);
                                        if (anomalous) {
                                            const allDataStr = numCols.map(c => `${headers[c].trim()}: ${rowObj[c] !== undefined && !isNaN(rowObj[c]) ? rowObj[c].toFixed(2) : '-'}`).join(', ');
                                            failDetails.push({
                                                rowIdx: ri,
                                                timestamp: timestamp,
                                                lotId: lotId,
                                                waferId: waferId,
                                                lotDisplay: lotDisplay,
                                                failedParam: failMsgs.join(', '),
                                                allData: allDataStr
                                            });
                                        } else {
                                            failDetails.push(null);
                                        }
                                    });
                                    
                                    node._parsedStatusData = statuses;
                                    node._parsedFailDetails = failDetails;
                                    node._parsedRowMeta = rowMeta;
                                    node.currentLotId = (rowMeta.length > 0 && rowMeta[0].lotId) ? rowMeta[0].lotId : null;
                                    node.currentWaferId = (rowMeta.length > 0 && rowMeta[0].waferId) ? rowMeta[0].waferId : null;
                                    node.failLogs = [];
                                    node.isAnomalous = false;
                                    node.hasActiveAlarm = false;
                                }
                            } else {
                                node.testCsvData = null;
                                node.testCsvName = null;
                                node._parsedStatusData = null;
                                node._parsedFailDetails = null;
                                node._parsedRowMeta = null;
                                node.currentLotId = null;
                                node.currentWaferId = null;
                                node.failLogs = [];
                                node.isAnomalous = false;
                                node.hasActiveAlarm = false;
                            }
                        } else {
                            node.testCsvData = null;
                            node.testCsvName = null;
                            node._parsedStatusData = null;
                            node._parsedFailDetails = null;
                            node._parsedRowMeta = null;
                            node.currentLotId = null;
                            node.currentWaferId = null;
                            node.failLogs = [];
                            node.isAnomalous = false;
                            node.hasActiveAlarm = false;
                        }
                    });
                    saveState();
                    renderNodes();
                }
            }


            // Lightweight DOM patch - updates node state WITHOUT full re-render
            // Avoids destroying/recreating DOM elements (which breaks event listeners)
            function patchNodes() {
                nodesData.forEach(node => {
                    const elem = document.getElementById(node.id);
                    if (!elem) return;

                    // Update anomalous CSS class
                    if (node.isAnomalous) {
                        elem.classList.add('anomalous');
                    } else {
                        elem.classList.remove('anomalous');
                    }

                    // Update alarm badge (FAIL indicator)
                    let alarmBadge = elem.querySelector('.node-alarm-badge');
                    if (node.isAnomalous) {
                        if (!alarmBadge) {
                            alarmBadge = document.createElement('div');
                            alarmBadge.className = 'node-alarm-badge';
                            alarmBadge.title = '이상 감지 발생! 더블클릭하여 조치';
                            alarmBadge.textContent = 'FAIL';
                            elem.insertBefore(alarmBadge, elem.firstChild);
                        }
                    } else {
                        if (alarmBadge) alarmBadge.remove();
                    }

                    // Update lot badge text/class
                    let lotBadge = elem.querySelector('.micro-lot-badge');
                    if (node.currentLotId) {
                        const lotShort = node.currentLotId.replace('LOT-20260812-', '');
                        const lotClass = 'micro-lot-badge' + (node.isAnomalous ? ' lot-fail' : '');
                        if (!lotBadge) {
                            lotBadge = document.createElement('div');
                            lotBadge.className = lotClass;
                            // Insert before port-socket
                            const port = elem.querySelector('.port-socket');
                            if (port) elem.insertBefore(lotBadge, port);
                            else elem.appendChild(lotBadge);
                        } else {
                            lotBadge.className = lotClass;
                        }
                        lotBadge.title = '현재 가공 Lot: ' + node.currentLotId;
                        lotBadge.textContent = '▶ ' + lotShort;
                    } else {
                        if (lotBadge) lotBadge.remove();
                    }
                });
            }

            // Global Anomaly Tracking Interval
            if (window.globalAnomalyInterval) clearInterval(window.globalAnomalyInterval);
            window.globalAnomalyInterval = setInterval(() => {
                if (!window.simulationStartTime || !viewsData[currentViewId] || !viewsData[currentViewId].nodes) return;
                
                const msPerPoint = 100;
                const elapsedMs = Date.now() - window.simulationStartTime;
                
                let anyChanged = false;
                viewsData[currentViewId].nodes.forEach(node => {
                    const statuses = node._parsedStatusData;
                    const failDetails = node._parsedFailDetails;
                    const rowMeta = node._parsedRowMeta;
                    if (statuses && statuses.length > 0) {
                        const currentRow = Math.floor(elapsedMs / msPerPoint) % statuses.length;
                        
                        if (rowMeta && rowMeta[currentRow]) {
                            const meta = rowMeta[currentRow];
                            const effLotId = (meta.lotId && meta.lotId !== '') ? meta.lotId : null;
                            const effWaferId = (meta.waferId && meta.waferId !== '') ? meta.waferId : null;
                            if (node.currentLotId !== effLotId || node.currentWaferId !== effWaferId) {
                                node.currentLotId = effLotId;
                                node.currentWaferId = effWaferId;
                                anyChanged = true;
                            }
                        }

                        const isRowAnomalous = statuses[currentRow] === true;
                        if (isRowAnomalous && failDetails && failDetails[currentRow]) {
                            const detail = failDetails[currentRow];
                            node.failLogs = node.failLogs || [];
                            const exists = node.failLogs.some(l => l.rowIdx === currentRow || l.timestamp === detail.timestamp);
                            if (!exists) {
                                node.failLogs.unshift({
                                    id: 'fail_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7),
                                    rowIdx: currentRow,
                                    timestamp: detail.timestamp,
                                    lotId: detail.lotId,
                                    waferId: detail.waferId,
                                    lotDisplay: detail.lotDisplay,
                                    failedParam: detail.failedParam,
                                    allData: detail.allData,
                                    status: 'UNRESOLVED',
                                    createdAt: new Date().toLocaleTimeString()
                                });
                                if (!node.hasActiveAlarm || !node.isAnomalous) {
                                    node.hasActiveAlarm = true;
                                    node.isAnomalous = true;
                                    anyChanged = true;
                                }
                            }
                        }
                        
                        // Node stays anomalous/glowing red as long as there is at least one UNRESOLVED fail log!
                        const hasUnresolved = (node.failLogs || []).some(l => l.status === 'UNRESOLVED');
                        if (node.isAnomalous !== hasUnresolved) {
                            node.isAnomalous = hasUnresolved;
                            node.hasActiveAlarm = hasUnresolved;
                            anyChanged = true;
                        }
                    } else if (node.isAnomalous) {
                        node.isAnomalous = false;
                        node.hasActiveAlarm = false;
                        anyChanged = true;
                    }
                });
                
                // Propagate to main Fab node if any internal node is anomalous
                if (viewsData['fab-cmos'] && viewsData['fab-cmos'].nodes) {
                    const hasFabAnomalous = viewsData['fab-cmos'].nodes.some(n => n.isAnomalous);
                    const fabNode = viewsData['main']?.nodes?.find(n => n.id === 'fab-cmos');
                    if (fabNode && fabNode.isAnomalous !== hasFabAnomalous) {
                        fabNode.isAnomalous = hasFabAnomalous;
                        if (currentViewId === 'main') anyChanged = true;
                    }
                }
                
                if (anyChanged) {
                    patchNodes();
                    const modal = document.getElementById('edit-modal');
                    if (modal && modal.style.display !== 'none' && selectedNodeId) {
                        const cur = (viewsData[currentViewId]?.nodes || []).find(n => n.id === selectedNodeId);
                        if (cur) renderFailLogTable(cur);
                    }
                }
            }, 100);

            function startChartWithCSV(text) {
                const lines = text.trim().split('\\n');
                if (lines.length < 2) return;
                
                const headers = lines[0].split(',');
                
                // Identify data columns (ignore Timestamp, Step_ID, Step_Name, Status, Phase, Address, Lot_ID, Wafer_ID)
                const skipCols = ['Timestamp', '\ufeffTimestamp', 'Address', 'Step_ID', 'Step_Name', 'Status', 'Phase', 'Lot_ID', 'Wafer_ID', ''];
                const dataColIndices = [];
                const datasets = [];
                
                const colors = ['#34D399', '#A855F7', '#FBBF24', '#60A5FA', '#F472B6', '#EF4444', '#F97316'];
                
                headers.forEach((h, idx) => {
                    const colName = h.trim();
                    if (!skipCols.includes(colName)) {
                        dataColIndices.push(idx);
                        datasets.push({
                            label: colName,
                            data: [],
                            borderColor: colors[(dataColIndices.length - 1) % colors.length],
                            backgroundColor: 'transparent',
                            borderWidth: 2,
                            pointRadius: [],
                            pointBackgroundColor: [],
                            pointHoverRadius: 5,
                            tension: 0.3,
                            spanGaps: false
                        });
                    }
                });
                
                const timeIndex = headers.findIndex(h => h.trim() === 'Timestamp');
                const lotIndex = headers.findIndex(h => h.trim() === 'Lot_ID');
                const waferIndex = headers.findIndex(h => h.trim() === 'Wafer_ID');
                const phaseIndex = headers.findIndex(h => h.trim() === 'Phase');
                const statusIndex = headers.findIndex(h => h.trim().replace(/^\ufeff/, '') === 'Status');
                const phaseShort = {'RAMP': 'R', 'IDLE': 'I', 'ACTIVE': 'A'};
                
                // Prepare data array
                const fullData = [];
                for(let i=1; i<lines.length; i++) {
                    const row = lines[i].split(',');
                    if (row.length === headers.length) {
                        fullData.push(row);
                    }
                }
                
                clearChartState();
                
                window.lastFailTimestamp = null;
                const modalNode = (viewsData[currentViewId]?.nodes || []).find(n => n.id === selectedNodeId);
                if (modalNode) {
                    renderFailLogTable(modalNode);
                }
                
                window.currentStats = {};
                const valuesByPhase = {};
                dataColIndices.forEach(colIdx => valuesByPhase[colIdx] = {});
                
                for(let i=0; i<fullData.length; i++) {
                    const row = fullData[i];
                    const phase = phaseIndex >= 0 ? row[phaseIndex].trim() : 'DEFAULT';
                    
                    dataColIndices.forEach(colIdx => {
                        let v = parseFloat(row[colIdx]);
                        if (!isNaN(v)) {
                            if (!valuesByPhase[colIdx][phase]) valuesByPhase[colIdx][phase] = [];
                            valuesByPhase[colIdx][phase].push(v);
                        }
                    });
                }
                
                dataColIndices.forEach((colIdx) => {
                    const colNameRaw = headers[colIdx].trim();
                    const parts = colNameRaw.split('_');
                    let unit = parts.length > 1 ? parts.pop() : '-';
                    let name = parts.join('_');
                    
                    let phaseStats = {};
                    for (const [phase, vals] of Object.entries(valuesByPhase[colIdx])) {
                        let mean = vals.reduce((a,b) => a+b, 0) / (vals.length || 1);
                        let variance = vals.reduce((a,b) => a + (b - mean)**2, 0) / (vals.length || 1);
                        let std = Math.sqrt(variance);
                        let spread = Math.max(3 * std, Math.abs(mean) * 0.15, 0.5);
                        
                        phaseStats[phase] = {
                            target: mean,
                            min: mean - spread,
                            max: mean + spread
                        };
                    }
                    
                    let allVals = [];
                    Object.values(valuesByPhase[colIdx]).forEach(arr => allVals.push(...arr));
                    let globalMean = allVals.reduce((a,b) => a+b, 0) / (allVals.length || 1);
                    let globalVariance = allVals.reduce((a,b) => a + (b - globalMean)**2, 0) / (allVals.length || 1);
                    let globalStd = Math.sqrt(globalVariance);
                    let globalSpread = Math.max(3 * globalStd, Math.abs(globalMean) * 0.15, 0.5);
                    
                    phaseStats['DEFAULT'] = {
                        target: globalMean,
                        min: globalMean - globalSpread,
                        max: globalMean + globalSpread
                    };
                    
                    window.currentStats[colIdx] = {
                        name: name,
                        unit: unit,
                        phaseStats: phaseStats
                    };
                });
                
                window.toggleSensorDataset = function(dsIdx, isChecked) {
                    if (sensorChart && sensorChart.data.datasets[dsIdx]) {
                        sensorChart.data.datasets[dsIdx].hidden = !isChecked;
                        sensorChart.update();
                        
                        const allChecked = sensorChart.data.datasets.every(ds => !ds.hidden);
                        const checkAll = document.getElementById('sensor-check-all');
                        if (checkAll) checkAll.checked = allChecked;
                    }
                };
                
                window.toggleAllSensorDatasets = function(isChecked) {
                    if (sensorChart) {
                        sensorChart.data.datasets.forEach((ds) => {
                            ds.hidden = !isChecked;
                        });
                        sensorChart.update();
                        
                        document.querySelectorAll('input[id^="sensor-check-"]').forEach(cb => {
                            if (cb.id !== 'sensor-check-all') {
                                cb.checked = isChecked;
                            }
                        });
                    }
                };

                const tbodyInit = document.getElementById('sensor-data-table-body');
                if (tbodyInit) {
                    let htmlRowsInit = '';
                    dataColIndices.forEach((colIdx, dsIdx) => {
                        const statConfig = window.currentStats[colIdx];
                        const stat = statConfig.phaseStats['DEFAULT'];
                        htmlRowsInit += `
                            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);" id="sensor-row-${colIdx}">
                                <td style="padding: 6px 4px; text-align: left;">
                                    <input type="checkbox" id="sensor-check-${colIdx}" checked onchange="toggleSensorDataset(${dsIdx}, this.checked)" style="margin-right: 5px; cursor: pointer;">
                                </td>
                                <td style="padding: 6px 4px; word-break: break-all; text-align: left;">${statConfig.name}</td>
                                <td id="sensor-target-${colIdx}" style="padding: 6px 4px; text-align: left; color: #94A3B8;">${stat.target.toFixed(2)}</td>
                                <td id="sensor-val-${colIdx}" style="padding: 6px 4px; text-align: left; color: #34D399; font-weight: bold;">-</td>
                                <td id="sensor-min-${colIdx}" style="padding: 6px 4px; text-align: left; color: #94A3B8;">${stat.min.toFixed(2)}</td>
                                <td id="sensor-max-${colIdx}" style="padding: 6px 4px; text-align: left; color: #94A3B8;">${stat.max.toFixed(2)}</td>
                                <td style="padding: 6px 4px; text-align: left; color: #64748B;">${statConfig.unit}</td>
                            </tr>
                        `;
                    });
                    tbodyInit.innerHTML = htmlRowsInit;
                }
                
                const ctx = document.getElementById('sensorChart').getContext('2d');
                sensorChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: datasets
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: false,
                        spanGaps: false,
                        layout: {
                            padding: { bottom: 4 }
                        },
                        plugins: {
                            legend: {
                                labels: { color: '#E2E8F0', font: { size: 10 } }
                            },
                            tooltip: {
                                mode: 'index',
                                intersect: false,
                                backgroundColor: 'rgba(15,23,42,0.9)',
                                titleColor: '#34D399',
                                bodyColor: '#F8FAFC'
                            }
                        },
                        scales: {
                            x: {
                                ticks: {
                                    maxTicksLimit: 8,
                                    color: '#94A3B8',
                                    font: { size: 10 },
                                    callback: function(val) {
                                        const lbl = this.getLabelForValue(val);
                                        // Show only timestamp, phase shown as dot via plugin
                                        return Array.isArray(lbl) ? lbl[0] : lbl;
                                    }
                                },
                                grid: { color: 'rgba(255,255,255,0.05)' }
                            },
                            y: {
                                ticks: { color: '#94A3B8' },
                                grid: { color: 'rgba(255,255,255,0.05)' }
                            }
                        }
                    },
                    plugins: []

                });


                
                function updateRealTimeTable(currentRowData, timestamp, currentPhase) {
                    let hasFail = false;
                    let failMessages = [];
                    let allDataStr = [];
                    
                    const rawLotId = lotIndex >= 0 ? currentRowData[lotIndex].trim() : '';
                    const isStandby = (currentPhase === 'IDLE' || !rawLotId || rawLotId === '' || rawLotId === 'null' || rawLotId === 'NaN');
                    const lotId = isStandby ? '' : rawLotId;
                    const waferId = isStandby ? '' : (waferIndex >= 0 ? currentRowData[waferIndex].trim() : '');
                    const lotDisplay = lotId;
                    
                    // Check Status column if present in CSV
                    let isRowExplicitFail = false;
                    let explicitStatusVal = '';
                    if (!isStandby && statusIndex >= 0 && currentRowData[statusIndex]) {
                        explicitStatusVal = currentRowData[statusIndex].trim();
                        const sUpper = explicitStatusVal.toUpperCase();
                        if (sUpper && sUpper !== 'NORMAL' && sUpper !== 'STATUS' && sUpper !== 'OK' && sUpper !== 'IDLE' && sUpper !== '') {
                            isRowExplicitFail = true;
                        }
                    }
                    
                    dataColIndices.forEach((colIdx) => {
                        const val = parseFloat(currentRowData[colIdx]);
                        const statConfig = window.currentStats[colIdx];
                        const stat = statConfig.phaseStats[currentPhase] || statConfig.phaseStats['DEFAULT'];
                        
                        const targetCell = document.getElementById(`sensor-target-${colIdx}`);
                        const minCell = document.getElementById(`sensor-min-${colIdx}`);
                        const maxCell = document.getElementById(`sensor-max-${colIdx}`);
                        const valCell = document.getElementById(`sensor-val-${colIdx}`);
                        
                        if (isStandby) {
                            if (targetCell) targetCell.textContent = '-';
                            if (minCell) minCell.textContent = '-';
                            if (maxCell) maxCell.textContent = '-';
                            if (valCell) valCell.textContent = '- (대기중)';
                            allDataStr.push(`${statConfig.name}: 대기중`);
                        } else {
                            if (targetCell) targetCell.textContent = stat.target.toFixed(2);
                            if (minCell) minCell.textContent = stat.min.toFixed(2);
                            if (maxCell) maxCell.textContent = stat.max.toFixed(2);
                            if (valCell) valCell.textContent = !isNaN(val) ? val.toFixed(2) : '-';
                            
                            allDataStr.push(`${statConfig.name}: ${!isNaN(val) ? val.toFixed(2) : '-'}`);
                            if (!isNaN(val) && (val < stat.min || val > stat.max) && currentPhase !== 'RAMP' && currentPhase !== 'IDLE') {
                                failMessages.push(`${statConfig.name} (${val.toFixed(2)} / ${stat.min.toFixed(2)}~${stat.max.toFixed(2)})`);
                            }
                        }
                    });
                    
                    if (statusIndex >= 0) {
                        hasFail = isRowExplicitFail;
                        if (isRowExplicitFail && failMessages.length === 0) {
                            failMessages.push(explicitStatusVal);
                        }
                    } else {
                        hasFail = !isStandby && failMessages.length > 0;
                    }
                    
                    const node = (viewsData[currentViewId]?.nodes || []).find(n => n.id === selectedNodeId);
                    if (node) {
                        node.currentLotId = lotId ? lotId : null;
                        node.currentWaferId = waferId ? waferId : null;
                        if (hasFail) {
                            node.failLogs = node.failLogs || [];
                            if (window.lastFailTimestamp !== timestamp) {
                                window.lastFailTimestamp = timestamp;
                                const exists = node.failLogs.some(l => l.timestamp === timestamp);
                                if (!exists) {
                                    node.failLogs.unshift({
                                        id: 'fail_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7),
                                        timestamp: timestamp,
                                        lotId: lotId,
                                        waferId: waferId,
                                        lotDisplay: lotDisplay,
                                        failedParam: failMessages.join('<br>'),
                                        allData: allDataStr.join(', '),
                                        status: 'UNRESOLVED',
                                        createdAt: new Date().toLocaleTimeString()
                                    });
                                    let stateChanged = false;
                                    if (!node.isAnomalous || !node.hasActiveAlarm) {
                                        node.isAnomalous = true;
                                        node.hasActiveAlarm = true;
                                        stateChanged = true;
                                    }
                                    if (stateChanged) renderNodes();
                                    node.failLogsUpdated = true;
                                }
                            }
                        }
                        if (node.failLogsUpdated) {
                            renderFailLogTable(node);
                            node.failLogsUpdated = false;
                        }
                    }
                }

                // Continuous Streaming Simulation
                if (!window.simulationStartTime) window.simulationStartTime = Date.now();
                const msPerPoint = 100;
                const maxPoints = 30;
                
                let lastRenderedRow = -1;
                
                function pushChartPoint(r) {
                    const row = fullData[r];
                    const timestamp = timeIndex >= 0 ? (row[timeIndex].includes(' ') ? row[timeIndex].split(' ')[1] : row[timeIndex]) : r.toString();
                    const phaseRaw = phaseIndex >= 0 ? row[phaseIndex].trim() : 'DEFAULT';
                    const phase = phaseShort[phaseRaw] || phaseRaw;
                    const rawLotId = lotIndex >= 0 ? row[lotIndex].trim() : '';
                    const isStandby = (phaseRaw === 'IDLE' || !rawLotId || rawLotId === '' || rawLotId === 'null' || rawLotId === 'NaN');
                    
                    sensorChart.data.labels.push(phase ? [timestamp, phase] : timestamp);
                    if (sensorChart.data.labels.length > maxPoints) {
                        sensorChart.data.labels.shift();
                    }
                    
                    // Check if explicit fail
                    let isFailRow = false;
                    if (!isStandby && statusIndex >= 0 && row[statusIndex]) {
                        const sUpper = row[statusIndex].trim().toUpperCase();
                        if (sUpper && sUpper !== 'NORMAL' && sUpper !== 'STATUS' && sUpper !== 'OK' && sUpper !== 'IDLE' && sUpper !== '') {
                            isFailRow = true;
                        }
                    }
                    
                    dataColIndices.forEach((colIdx, dsIdx) => {
                        const ds = sensorChart.data.datasets[dsIdx];
                        if (isStandby) {
                            ds.data.push(null);
                            ds.pointBackgroundColor.push('transparent');
                            ds.pointRadius.push(0);
                        } else {
                            const rawVal = parseFloat(row[colIdx]);
                            const val = !isNaN(rawVal) ? rawVal : null;
                            ds.data.push(val);
                            ds.pointBackgroundColor.push(isFailRow ? '#EF4444' : 'transparent');
                            ds.pointRadius.push(isFailRow ? 5 : 2);
                        }
                        
                        if (ds.data.length > maxPoints) {
                            ds.data.shift();
                            ds.pointBackgroundColor.shift();
                            ds.pointRadius.shift();
                        }
                    });
                }

                streamInterval = setInterval(() => {
                    if (fullData.length === 0) return;
                    
                    const elapsedMs = Date.now() - window.simulationStartTime;
                    const currentRow = Math.floor(elapsedMs / msPerPoint) % fullData.length;
                    
                    if (currentRow !== lastRenderedRow) {
                        if (lastRenderedRow === -1) {
                            const fillCount = Math.min(maxPoints, fullData.length);
                            for (let i = fillCount - 1; i >= 0; i--) {
                                let r = (currentRow - i + fullData.length) % fullData.length;
                                pushChartPoint(r);
                            }
                            lastRenderedRow = currentRow;
                            sensorChart.update('none');
                        } else {
                            let pointsToAdd = (currentRow - lastRenderedRow + fullData.length) % fullData.length;
                            if (pointsToAdd > maxPoints) pointsToAdd = maxPoints;
                            
                            if (pointsToAdd > 0) {
                                for (let step = 1; step <= pointsToAdd; step++) {
                                    let r = (lastRenderedRow + step) % fullData.length;
                                    pushChartPoint(r);
                                }
                                lastRenderedRow = currentRow;
                                sensorChart.update('none');
                            }
                        }

                        // Update real-time table
                        const tstamp = timeIndex >= 0 ? fullData[currentRow][timeIndex] : currentRow.toString();
                        const rPhase = phaseIndex >= 0 ? fullData[currentRow][phaseIndex].trim() : 'DEFAULT';
                        updateRealTimeTable(fullData[currentRow], tstamp, rPhase);
                    }
                }, 50); // Fast poll to stay in perfect global sync
            }

            const csvInput = document.getElementById('sensor-csv-upload');
            if (csvInput) {
                csvInput.addEventListener('change', function(e) {
                    const file = e.target.files[0];
                    if (!file) return;
                    
                    const reader = new FileReader();
                    reader.onload = function(evt) {
                        const csvText = evt.target.result;
                        const node = nodesData.find(n => n.id === selectedNodeId);
                        if (node) {
                            node.manualCsvData = csvText;
                            node.manualCsvName = file.name;
                            const uploadFilename = document.getElementById('sensor-csv-filename');
                            if (uploadFilename) {
                                uploadFilename.innerText = file.name;
                                uploadFilename.style.color = '#34D399';
                            }
                            saveState();
                        }
                        startChartWithCSV(csvText);
                    };
                    reader.readAsText(file);
                });
            }

        </script>
        <div class="toast" id="toast-message">위치와 연결이 성공적으로 저장되었습니다!</div>
    </body>
    </html>
    """

    components.html(html_code, height=580)
