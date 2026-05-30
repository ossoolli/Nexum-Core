import os

from core.base_agent import BaseAgent

class SystemCodeEditorAgent(BaseAgent):
    def __init__(self):
        try:
            super().__init__(
                name="system_code_editor",
                goal="Directly modify and update system configuration or source code files based on specified logic or provided code snippets, executing changes in-place rather than generating a script for manual execution. This includes tasks like opening specific files, parsing their content, inserting/replacing code blocks, and saving the modified files.",
                tools=['search_web', 'fetch_webpage'],
                triggers=['every_hour']
            )
            self.log("SystemCodeEditorAgent initialized successfully.")
        except Exception as e:
            self.log(f"Error during SystemCodeEditorAgent initialization: {e}", level="ERROR")

    async def run(self, file_path: str = None, old_content_marker: str = None, new_content: str = None, action_type: str = "replace"):
        try:
            self.log(f"SystemCodeEditorAgent run initiated for file: {file_path}")

            if not file_path:
                self.log("No file_path provided for modification.", level="WARNING")
                return

            if not os.path.exists(file_path):
                self.log(f"File not found: {file_path}", level="ERROR")
                return

            if action_type not in ["replace", "insert_before", "insert_after", "delete"]:
                self.log(f"Invalid action_type: {action_type}. Supported types: replace, insert_before, insert_after, delete.", level="ERROR")
                return

            self.log(f"Attempting to modify file: {file_path} with action: {action_type}")
            await self._modify_file(file_path, old_content_marker, new_content, action_type)
            self.log(f"SystemCodeEditorAgent run completed for file: {file_path}")

        except Exception as e:
            self.log(f"Error during SystemCodeEditorAgent run: {e}", level="ERROR")

    async def _modify_file(self, file_path: str, old_content_marker: str = None, new_content: str = None, action_type: str = "replace"):
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()

            modified_lines = []
            file_modified = False
            for line in lines:
                if old_content_marker and old_content_marker in line:
                    file_modified = True
                    if action_type == "replace":
                        if new_content is not None:
                            modified_lines.append(new_content + '\n')
                            self.log(f"Replaced content at marker: '{old_content_marker}' in {file_path}")
                        else:
                            self.log(f"No new_content provided for replace action at marker: '{old_content_marker}'. Skipping replacement.", level="WARNING")
                    elif action_type == "insert_before":
                        if new_content is not None:
                            modified_lines.append(new_content + '\n')
                            self.log(f"Inserted content before marker: '{old_content_marker}' in {file_path}")
                        modified_lines.append(line)
                    elif action_type == "insert_after":
                        modified_lines.append(line)
                        if new_content is not None:
                            modified_lines.append(new_content + '\n')
                            self.log(f"Inserted content after marker: '{old_content_marker}' in {file_path}")
                    elif action_type == "delete":
                        self.log(f"Deleted line containing marker: '{old_content_marker}' in {file_path}")
                        continue
                    else:
                        modified_lines.append(line)
                else:
                    modified_lines.append(line)

            if not file_modified and old_content_marker:
                self.log(f"Marker '{old_content_marker}' not found in file: {file_path}. No changes applied.", level="WARNING")
                return

            if file_modified:
                backup_path = f"{file_path}.bak"
                with open(backup_path, 'w') as f_bak:
                    f_bak.writelines(lines)
                self.log(f"Original file backed up to: {backup_path}")

                with open(file_path, 'w') as f:
                    f.writelines(modified_lines)
                self.log(f"File {file_path} successfully modified and saved.")
            else:
                self.log(f"No modifications made to {file_path}.", level="INFO")

        except FileNotFoundError:
            self.log(f"File not found: {file_path}", level="ERROR")
        except PermissionError:
            self.log(f"Permission denied to modify file: {file_path}", level="ERROR")
        except Exception as e:
            self.log(f"Error during file modification: {e}", level="ERROR")