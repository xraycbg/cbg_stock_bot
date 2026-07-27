import re

with open("app.py", "r") as f:
    content = f.read()

# 1. Add CSS
css_rule = """
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.pro-card-marker) {
        background: linear-gradient(145deg, #111827 0%, #0f172a 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 22px !important;
        padding: 18px 20px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35) !important;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.pro-card-marker) > div {
        gap: 0 !important;
    }
"""
content = content.replace("    .pro-card-header {", css_rule + "\n    .pro-card-header {")

# 2. Refactor the loop
# We will find the start of the del_col1 ... st.columns line
pattern = r"(        del_col1, del_col2, del_col3 = st\.columns\(\[7\.5, 1\.5, 0\.1\]\).*?)(?=    st\.stop\(\)|$)"
match = re.search(pattern, content, flags=re.DOTALL)
if match:
    old_loop_body = match.group(1)
    
    # We need to indent everything by 4 spaces and wrap in `with st.container(border=True):`
    lines = old_loop_body.split('\n')
    new_lines = ["        with st.container(border=True):", "            st.markdown('<div class=\"pro-card-marker\"></div>', unsafe_allow_html=True)"]
    for line in lines:
        if line.strip() == "":
            new_lines.append(line)
        else:
            new_lines.append("    " + line)
            
    # Also we remove the old card_html wrappers
    new_loop_body = '\n'.join(new_lines)
    
    # Clean up the old HTML wrappers
    new_loop_body = new_loop_body.replace('            card_html = f"""<div class="pro-card list-card-touch">', '            card_html = f"""<div style="padding:0;">')
    # Remove the closing tag
    new_loop_body = new_loop_body.replace("            st.markdown('</div>', unsafe_allow_html=True) # pro-card closing tag", "")
    
    content = content[:match.start()] + new_loop_body + content[match.end():]
    
with open("app.py", "w") as f:
    f.write(content)
print("Patch2 applied")
