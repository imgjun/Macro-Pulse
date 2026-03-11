import os
import tempfile


def create_temp_png_path(prefix):
    with tempfile.NamedTemporaryFile(
        prefix=f"macro_pulse_{prefix}_", suffix=".png", delete=False
    ) as handle:
        return handle.name


def resolve_output_path(output_path, prefix):
    if output_path:
        return output_path
    return create_temp_png_path(prefix)


def cleanup_files(file_paths):
    for file_path in file_paths:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            print(f"Removed temporary file: {file_path}")
