import magic
import os

def recognize_file(file_path):
    """
    يستخدم مكتبة python-magic للتعرف على نوع الملف بناءً على محتوياته (MIME type)
    """
    if not os.path.exists(file_path):
        return "File not found."
    
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)
    return f"Detected File Type: {file_type}"

if __name__ == '__main__':
    # مثال للاستخدام عند إرسال ملف للمسار المحدد
    import sys
    if len(sys.argv) > 1:
        print(recognize_file(sys.argv[1]))