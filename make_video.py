import os
import subprocess
import datetime
import shutil


def get_all_screenshots(directory="screenshots"):
    screenshots = []
    for filename in sorted(os.listdir(directory)):
        if filename.startswith("hormuz_") and filename.endswith(".png"):
            screenshots.append(filename)
    return screenshots


def get_recent_screenshots(directory="screenshots", hours=24):
    cutoff = datetime.datetime.now() - datetime.timedelta(hours=hours)
    recent_screenshots = []

    for filename in get_all_screenshots(directory):
        try:
            timestamp_str = filename[len("hormuz_"):-len(".png")]
            captured_at = datetime.datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
        except ValueError:
            continue

        if captured_at >= cutoff:
            recent_screenshots.append(filename)

    return recent_screenshots

def update_index(date_str):
    if not os.path.exists("index.html"):
        return
        
    with open("index.html", "r") as f:
        content = f.read()
        
    new_entry = f'<li><a href="videos/hormuz_timelapse_{date_str}.mp4">{date_str}</a></li>'
    if new_entry not in content:
        if "<!-- List of videos will be here -->" in content:
            content = content.replace("<!-- List of videos will be here -->", f"{new_entry}\n            <!-- List of videos will be here -->")
        
        with open("index.html", "w") as f:
            f.write(content)


def validate_video_file(path):
    if not os.path.exists(path):
        raise RuntimeError(f"Expected output video was not created: {path}")
    if os.path.getsize(path) == 0:
        raise RuntimeError(f"Output video is empty: {path}")

def make_video():
    # Ensure the directory for videos exists
    os.makedirs("videos", exist_ok=True)
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    output_file = f"videos/hormuz_timelapse_{today}.mp4"
    
    if not os.path.isdir("screenshots"):
        raise RuntimeError("Screenshots directory does not exist.")

    # Use the last 48 hours so the timelapse still has content on days where
    # some hourly captures failed. 24h is the ideal case; 48h is the fallback.
    screenshots = get_recent_screenshots(hours=48)

    if not screenshots:
        # Fall back to all available screenshots if none exist within 48 hours.
        print("No screenshots from the last 48 hours found. Falling back to all available screenshots.")
        screenshots = get_all_screenshots()

    if not screenshots:
        raise RuntimeError("No screenshots found to make a video.")

    # Create a temporary file list for ffmpeg
    with open("file_list.txt", "w") as f:
        for img in screenshots:
            f.write(f"file 'screenshots/{img}'\n")

    # Run ffmpeg to create the video.
    # -r 1 means 1fps output = 1 second per frame.
    # With 24 hourly frames this gives a ~24 second daily timelapse.
    try:
        command = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "file_list.txt",
            "-r", "1",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            output_file
        ]
        subprocess.run(command, check=True)
        validate_video_file(output_file)
        
        # Create a copy as latest.mp4
        shutil.copy(output_file, "videos/latest.mp4")
        validate_video_file("videos/latest.mp4")
        
        # Update index.html with the new video in the archive
        update_index(today)
        
        print(f"Video created: {output_file}")
        return output_file
    except Exception as e:
        print(f"Error creating video: {e}")
        raise
    finally:
        if os.path.exists("file_list.txt"):
            os.remove("file_list.txt")

if __name__ == "__main__":
    try:
        make_video()
    except Exception:
        raise SystemExit(1)
