import os

def find_analytics_references(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "analytics" in content:
                        print(f"Found in {filepath}")
                        # Show the specific lines
                        with open(filepath, 'r', encoding='utf-8') as f2:
                            for i, line in enumerate(f2):
                                if "analytics" in line:
                                    print(f"  Line {i+1}: {line.strip()}")

# Thay đổi đường dẫn thư mục template của bạn
find_analytics_references('dashboard/templates') 