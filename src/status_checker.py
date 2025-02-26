import os
import time


def check_success_in_last_hour(
        time_to_check: int,
        status_file: str
):
    """Check if application was successful in the last hour"""

    current_time = time.time()

    if not os.path.exists(status_file):
        updated_in_last_hour = False
        os.makedirs(os.path.dirname(status_file), exist_ok=True)
    else:
        with open(status_file, 'r') as f:
            content = f.read().strip()
            last_success = float(content) if content else 0
            updated_in_last_hour = (current_time - last_success) < time_to_check

    with open(status_file, 'w') as f:
        f.write(str(current_time))

    return updated_in_last_hour
