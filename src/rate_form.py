import streamlit as st
import re
import os
from github import Github

# --- Set token as environment variable ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "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")
REPO_NAME = "mariaherliana1/auto-anna-form"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

def push_to_github(file_path, commit_message):
    with open(file_path, "r") as f:
        content = f.read()

    try:
        file = repo.get_contents(file_path)
        repo.update_file(file.path, commit_message, content, file.sha)
    except:
        repo.create_file(file_path, commit_message, content)

# Example usage:
push_to_github("idn_area_codes.py", "Updated area codes via Streamlit app")

# ==== CONSTANTS ====
VALID_CARRIERS = ["Atlasat", "Indosat"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IDN_AREA_CODES = os.path.join(BASE_DIR, "idn_area_codes.py")
INTERNATIONAL_RATES = os.path.join(BASE_DIR, "international_rates.py")

# ---------- INIT ----------
if "step" not in st.session_state:
    st.session_state.step = 1
if "category" not in st.session_state:
    st.session_state.category = None
if "prefix" not in st.session_state:
    st.session_state.prefix = ""
if "name" not in st.session_state:
    st.session_state.name = ""
if "rate" not in st.session_state:
    st.session_state.rate = 0.0
if "carrier" not in st.session_state:
    st.session_state.carrier = VALID_CARRIERS[0]

st.title("📞 Prefix & Rate Updater (Multi-Step Wizard)")

# ========== STEP 1 ==========
if st.session_state.step == 1:
    st.header("Step 1: Select Category")

    st.session_state.category = st.selectbox(
        "Choose a category:",
        ["EMERGENCY_NUMBERS", "INTERNATIONAL_PHONE_PREFIXES", "PHONE_PREFIXES"]
    )

    if st.button("➡ Next"):
        st.session_state.step = 2
        st.rerun()

# ========== STEP 2 ==========
elif st.session_state.step == 2:
    st.header(f"Step 2: Enter Data for {st.session_state.category}")

    st.session_state.prefix = st.text_input("Prefix (e.g., +62, 911)", st.session_state.prefix)
    st.session_state.name = st.text_input("Country or Prefix Name", st.session_state.name)

    if st.session_state.category == "INTERNATIONAL_PHONE_PREFIXES":
        st.session_state.carrier = st.selectbox("Carrier", VALID_CARRIERS, index=VALID_CARRIERS.index(st.session_state.carrier))
        st.session_state.rate = st.number_input(
            "Rate (only for International)", 
            min_value=0.0, step=0.1, format="%.2f",
            value=st.session_state.rate
        )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ Back"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("➡ Next"):
            if not st.session_state.prefix or not st.session_state.name:
                st.error("❌ Please fill in both prefix and name.")
            else:
                st.session_state.step = 3
                st.rerun()

# ========== STEP 3 ==========
elif st.session_state.step == 3:
    st.header("Step 3: Confirm & Update")

    st.subheader("Preview Changes:")
    st.code(f"""
File: {IDN_AREA_CODES}
→ {st.session_state.category}[{st.session_state.prefix}]: "{st.session_state.name}",
    """, language="python")

    if st.session_state.category == "INTERNATIONAL_PHONE_PREFIXES":
        st.code(f"""
File: {INTERNATIONAL_RATES}
→ {st.session_state.carrier}["International - {st.session_state.name}"]: {st.session_state.rate},
        """, language="python")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ Back"):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("✅ Confirm & Update"):
            # ---- Update idn_area_codes.py ----
            with open(IDN_AREA_CODES, "r") as f:
                content = f.read()

            category = st.session_state.category
            prefix = st.session_state.prefix
            name = st.session_state.name

            pattern = rf"({category}\s*=\s*{{)(.*?)(\}})"
            match = re.search(pattern, content, re.DOTALL)

            if match:
                existing_block = match.group(2)
                # Correct format: 961: "LBN",
                entry_pattern = rf"{prefix}\s*:\s*\".*?\""
                new_entry = f"{prefix}: \"{name}\","

                if re.search(entry_pattern, existing_block):
                    existing_block = re.sub(entry_pattern, new_entry, existing_block)
                    st.info(f"🔄 Updated existing {category} entry.")
                else:
                    # Append new entry on its own line before the closing brace
                    existing_block = existing_block.rstrip() + f"\n    {new_entry}\n"
                    st.success(f"➕ Added new {category} entry.")

                new_content = re.sub(pattern, rf"\1{existing_block}\3", content, flags=re.DOTALL)
                with open("idn_area_codes.py", "rb") as f:
                    st.download_button("⬇️ Download Updated idn_area_codes.py", f, file_name="idn_area_codes.py")

            # ---- Update international_rates.py ----
            if category == "INTERNATIONAL_PHONE_PREFIXES":
                carrier = st.session_state.carrier
                rate_name = f"International - {name}"
                rate_value = st.session_state.rate

                with open(INTERNATIONAL_RATES, "r") as f:
                    st.download_button("⬇️ Download Updated international_rates.py", f, file_name="international_rates.py")

                if carrier not in rates_content:
                    insertion_point = re.search(r"INTERNATIONAL_RATES\s*=\s*{", rates_content)
                    if insertion_point:
                        pos = insertion_point.end()
                        rates_content = rates_content[:pos] + f'\n    "{carrier}": {{\n    }},' + rates_content[pos:]
                        st.info(f"➕ Created new carrier block for {carrier}.")

                carrier_pattern = rf'("{carrier}"\s*:\s*{{)(.*?)(\}})'
                match_carrier = re.search(carrier_pattern, rates_content, re.DOTALL)

                if match_carrier:
                    carrier_block = match_carrier.group(2)
                    rate_pattern = rf'"{rate_name}"\s*:\s*[\d.]+'
                    new_rate_line = f'"{rate_name}": {rate_value},'

                    if re.search(rate_pattern, carrier_block):
                        carrier_block = re.sub(rate_pattern, new_rate_line, carrier_block)
                        st.info(f"🔄 Updated rate for {carrier} - {rate_name}.")
                    else:
                        # Append new rate on its own line before the closing brace
                        carrier_block = carrier_block.rstrip() + f"\n        {new_rate_line}\n"
                        st.success(f"➕ Added new rate for {carrier} - {rate_name}.")

                    rates_content = re.sub(carrier_pattern, rf'\1{carrier_block}\3', rates_content, flags=re.DOTALL)

                with open(INTERNATIONAL_RATES, "w") as f:
                    f.write(rates_content)

            st.balloons()
            st.success("✅ All updates applied successfully!")

            if st.button("➕ Add Another"):
                # Reset all wizard-related states
                st.session_state.update({
                    "step": 1,
                    "prefix": "",
                    "country": "",
                    "rate": 0.0,
                    "carrier": "Indosat",
                    "category": "",
                })
                st.rerun()  # ✅ Force Streamlit to restart at Step 1
