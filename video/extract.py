import subprocess


command = [
    'ccextractor_win_portable\ccextractorwinfull.exe',
    'test.mp4',
    '-o',
    'test.srt'
]

try:
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print("Subtitle extraction successful.")
except subprocess.CalledProcessError as e:
    print(f"Subtitle extraction failed: {e}")
    print(e.stderr)
