import os
import glob
import csv

def process_csv_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    if not lines:
        return
    
    reader = list(csv.reader(lines))
    headers = reader[0]
    rows = reader[1:]
    
    skip_cols = {'Timestamp', 'Address', 'Step_ID', 'Step_Name', 'Status', 'Phase', ''}
    
    time_idx = -1
    phase_idx = -1
    status_idx = -1
    data_col_indices = []
    
    for idx, h in enumerate(headers):
        h_clean = h.strip()
        if h_clean == 'Phase':
            phase_idx = idx
        elif h_clean == 'Status':
            status_idx = idx
        elif h_clean not in skip_cols:
            data_col_indices.append(idx)
            
    if not data_col_indices:
        return
        
    # Group normal values by Phase for each column
    phase_values = {col_idx: {} for col_idx in data_col_indices}
    
    for row in rows:
        if len(row) != len(headers):
            continue
        status = row[status_idx].strip() if status_idx != -1 else 'NORMAL'
        phase = row[phase_idx].strip() if phase_idx != -1 else 'DEFAULT'
        
        if status == 'NORMAL':
            for col_idx in data_col_indices:
                try:
                    val = float(row[col_idx])
                    if phase not in phase_values[col_idx]:
                        phase_values[col_idx][phase] = []
                    phase_values[col_idx][phase].append(val)
                except ValueError:
                    pass
                    
    # Calculate means per phase
    phase_means = {col_idx: {} for col_idx in data_col_indices}
    for col_idx in data_col_indices:
        for phase, vals in phase_values[col_idx].items():
            if vals:
                phase_means[col_idx][phase] = sum(vals) / len(vals)
        # Global fallback
        all_vals = [v for vals in phase_values[col_idx].values() for v in vals]
        if all_vals:
            phase_means[col_idx]['DEFAULT'] = sum(all_vals) / len(all_vals)
            
    # Now adjust rows in place where status == NORMAL and phase != RAMP
    modified_rows = []
    for row in rows:
        if len(row) != len(headers):
            modified_rows.append(row)
            continue
            
        status = row[status_idx].strip() if status_idx != -1 else 'NORMAL'
        phase = row[phase_idx].strip() if phase_idx != -1 else 'DEFAULT'
        
        if status == 'NORMAL' and phase != 'RAMP':
            new_row = list(row)
            for col_idx in data_col_indices:
                try:
                    val = float(row[col_idx])
                    target = phase_means[col_idx].get(phase, phase_means[col_idx].get('DEFAULT', val))
                    margin = abs(target) * 0.025  # 2.5% max variation
                    if margin == 0:
                        margin = 0.01
                    
                    lower = target - margin
                    upper = target + margin
                    
                    if val < lower:
                        val = lower
                    elif val > upper:
                        val = upper
                        
                    new_row[col_idx] = str(val)
                except ValueError:
                    pass
            modified_rows.append(new_row)
        else:
            modified_rows.append(row)
            
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(modified_rows)
    print(f"Processed {os.path.basename(filepath)}")

def main():
    root_dir = r"C:\Users\aicam\Documents\RxM"
    csv_files = glob.glob(os.path.join(root_dir, "**", "*.csv"), recursive=True)
    for filepath in csv_files:
        process_csv_file(filepath)

if __name__ == '__main__':
    main()
