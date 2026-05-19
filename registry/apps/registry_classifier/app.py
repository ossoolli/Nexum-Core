import os
import shutil

def classify_registry_files(source_dir, target_base_dir):
    # logic to classify registry files based on extension or content
    if not os.path.exists(target_base_dir):
        os.makedirs(target_base_dir)
    
    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)
        if os.path.isfile(file_path):
            # Classification logic placeholder
            category = 'others'
            if filename.endswith('.reg'):
                category = 'registry_data'
            
            dest_dir = os.path.join(target_base_dir, category)
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(file_path, os.path.join(dest_dir, filename))
            print(f'Moved {filename} to {category}')

if __name__ == '__main__':
    print('Starting Registry File Classification...')
    classify_registry_files('/tmp/registry_source', '/home/madarmutaz/Mutaz-dev/registry/data/classified')