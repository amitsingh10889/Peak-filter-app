# Streamlit app to paste sample and background peaks, and filter based on 5 ppm window

import streamlit as st
import pandas as pd
import io

# === Helper Function ===
def filter_peaks(sample_text, background_text):
    # Parse sample peaks
    sample_lines = sample_text.strip().split('\n')
    sample_data = []
    for line in sample_lines:
        parts = line.strip().split()
        if len(parts) >= 2:
            mz, intensity = map(float, parts[:2])
            sample_data.append((mz, intensity))
    sample_df = pd.DataFrame(sample_data, columns=['m/z', 'Intensity'])

    # Parse background peaks
    background_lines = background_text.strip().split('\n')
    background_mz = []
    for line in background_lines:
        parts = line.strip().split()
        if len(parts) >= 1:
            mz = float(parts[0])
            background_mz.append(mz)

    # 5 ppm filtering
    def is_background(sample_mz, background_list):
        ppm_window = sample_mz * 5 / 1e6
        for bg_mz in background_list:
            if abs(sample_mz - bg_mz) <= ppm_window:
                return True
        return False

    background_list = background_mz
    sample_df['Is_Background'] = sample_df['m/z'].apply(lambda x: is_background(x, background_list))

    filtered_sample_df = sample_df[sample_df['Is_Background'] == False][['m/z', 'Intensity']]

    return filtered_sample_df

# === Streamlit App ===
st.title('Background Subtraction Tool')

st.write("""
Paste your **Background Peaks** and **Sample Peaks** below.
Each line should have **m/z and intensity separated by space**.

Example:
```
500.001 1200
600.002 1100
700.003 900
```
""")

background_text = st.text_area("Paste Background Peaks (m/z and Intensity)", height=200)
sample_text = st.text_area("Paste Sample Peaks (m/z and Intensity)", height=200)

if st.button('Filter Peaks'):
    if background_text and sample_text:
        filtered_df = filter_peaks(sample_text, background_text)
        st.success(f"Filtering complete. {len(filtered_df)} peaks remaining.")

        st.dataframe(filtered_df)

        # Download filtered data
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download Filtered Peaks as CSV",
            data=csv,
            file_name='filtered_peaks.csv',
            mime='text/csv',
        )
    else:
        st.error("Please paste both Background and Sample data!")

