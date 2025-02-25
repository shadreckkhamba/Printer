import re
import os
import time
from config import PrinterConfiguration
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

LABEL_PRINTER_FILE_EXTENSION_PATTERN = r"\.(zpl|lbl)$"
DELIMITER = "##########BEGIN FORM##########"

class LabelPrinterHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.config = PrinterConfiguration().read()

    def delete_file(self, file_path):
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"{file_path} has been deleted.")
            except Exception as e:
                print(f"An error occurred while deleting {file_path}: {str(e)}")
        else:
            print(f"{file_path} does not exist.")

    def on_modified(self, event):
        # Check if the file extension matches
        if re.search(LABEL_PRINTER_FILE_EXTENSION_PATTERN, event.src_path):
            try:
                with open(event.src_path, 'r') as file:
                    content = file.read()
            except Exception as e:
                print(f"Error reading {event.src_path}: {str(e)}")
                return

            if DELIMITER in content:
                # Split the content into two parts
                parts = content.split(DELIMITER)
                first_part = parts[0].strip()
                second_part = parts[1].strip()

                # Write the parts into temporary files
                temp_first = event.src_path + ".first"
                temp_second = event.src_path + ".second"
                try:
                    with open(temp_first, 'w') as tf:
                        tf.write(first_part)
                    with open(temp_second, 'w') as ts:
                        ts.write(second_part)
                except Exception as e:
                    print(f"Error writing temporary files: {str(e)}")
                    return

                # Get printer names from config (or use defaults)
                printer1 = self.config.get("DEFAULT", "printer1", fallback="Printer1")
                printer2 = self.config.get("DEFAULT", "printer2", fallback="Printer2")

                # Construct print commands for each part
                command1 = f'lpr -P {printer1} -o raw "{temp_first}"'
                command2 = f'lpr -P {printer2} -o raw "{temp_second}"'

                print("✨️ Printing first part (Card): " + command1)
                os.system(command1)
                print("✨️ Printing second part (Form): " + command2)
                os.system(command2)

                # Clean up the temporary files
                try:
                    os.remove(temp_first)
                    os.remove(temp_second)
                except Exception as e:
                    print(f"Error deleting temporary files: {str(e)}")
            else:
                # If no delimiter, print as a single job
                command = 'lpr -o raw "' + event.src_path + '"'
                print("✨️ Printing Label Printer File: " + command)
                os.system(command)

            # Optionally delete the file after printing
            if self.config.getboolean('DEFAULT', 'delete_files', fallback=False):
                self.delete_file(event.src_path)


if __name__ == '__main__':
    print("✨️ Starting Label Printer Tracker Service")
    printhandler = LabelPrinterHandler()
    folder_config_path = printhandler.config.get('DEFAULT', 'file_directory', fallback='Downloads')
    target_directory = os.path.join(os.path.expanduser("~"), folder_config_path)
    if not os.path.exists(target_directory):
        raise NameError(f"Target directory {target_directory} does not exist!")
    obs = Observer()
    obs.schedule(printhandler, path=target_directory)
    obs.start()
    print(f"👀️ Monitoring directory: {target_directory}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("✅️ Exiting Label Printer Tracker")
    finally:
        obs.stop()
        obs.join()