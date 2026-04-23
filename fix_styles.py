import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find('    def apply_global_styles(self):')
end_match = re.search(r'\n    def \w', content[start+50:])
end = start + 50 + end_match.start() + 1

new_method = '''    def apply_global_styles(self):
        import os as _os
        css_path = _os.path.join(_os.path.dirname(__file__), 'style', 'style.css')
        try:
            with open(css_path, 'r', encoding='utf-8') as _f:
                css = _f.read()
            st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
        except Exception as _e:
            print(f'CSS load error: {_e}')

'''

content = content[:start] + new_method + content[end:]

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done - apply_global_styles now loads from style/style.css')
