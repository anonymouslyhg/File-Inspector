import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
from collections import defaultdict

st.set_page_config(page_title="File Inspector", layout="wide")

# Helper: format bytes
def format_bytes(size):
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:3.1f} {x}"
        size /= 1024.0
    return f"{size:.1f} TB"

# File scanner
def scan_folder(path):
    file_data = []
    for root, _, files in os.walk(path):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                size = os.path.getsize(filepath)
                ext = os.path.splitext(file)[1].lower()
                mtime = os.path.getmtime(filepath)
                file_data.append({
                    "Name": file,
                    "Extension": ext,
                    "Size (bytes)": size,
                    "Size (formatted)": format_bytes(size),
                    "Modified": time.strftime('%Y-%m-%d', time.localtime(mtime)),
                    "Path": filepath
                })
            except Exception as e:
                continue
    return pd.DataFrame(file_data)

# Title
st.title("🕵️ File Inspector — Smart Folder Analyzer")

folder = st.text_input("Enter folder path (absolute):", "")

if folder and os.path.isdir(folder):
    with st.spinner("🔍 Scanning folder..."):
        df = scan_folder(folder)

    st.success(f"✅ Found {len(df)} files in total.")

    st.subheader("📂 File Overview")
    st.dataframe(df[['Name', 'Extension', 'Size (formatted)', 'Modified']], use_container_width=True)

    # Charts
    st.subheader("📊 File Type Distribution")
    type_count = df['Extension'].value_counts().head(10)
    fig1, ax1 = plt.subplots()
    type_count.plot(kind='barh', ax=ax1, color="teal")
    ax1.set_xlabel("Count")
    ax1.set_title("Top File Extensions")
    st.pyplot(fig1)

    st.subheader("💾 Size by File Type")
    size_by_type = df.groupby("Extension")["Size (bytes)"].sum().sort_values(ascending=False).head(10)
    fig2, ax2 = plt.subplots()
    size_by_type.plot(kind='bar', ax=ax2, color="salmon")
    ax2.set_ylabel("Total Size (bytes)")
    st.pyplot(fig2)

    # Duplicate detection
    st.subheader("🧬 Duplicate File Detector (by Name + Size)")
    dup_df = df[df.duplicated(subset=["Name", "Size (bytes)"], keep=False)]
    if not dup_df.empty:
        st.warning(f"⚠️ Found {len(dup_df)} duplicate files")
        st.dataframe(dup_df[['Name', 'Size (formatted)', 'Path']])
    else:
        st.success("🎉 No duplicates detected.")

    # Junk file cleaner
    st.subheader("🗑 Junk File Cleaner")
    junk_exts = ['.tmp', '.log', '.bak']
    junk_files = df[df['Extension'].isin(junk_exts)]

    if not junk_files.empty:
        st.info(f"🧹 Found {len(junk_files)} junk files:")
        st.dataframe(junk_files[['Name', 'Extension', 'Path']])
        if st.button("Delete All Junk Files"):
            for path in junk_files['Path']:
                try:
                    os.remove(path)
                except:
                    continue
            st.success("🗑 Junk files deleted.")
    else:
        st.success("✅ No junk files found.")

else:
    st.info("Please enter a valid folder path.")

st.markdown("---")
st.caption("Built with ❤️ using Python and Streamlit")
