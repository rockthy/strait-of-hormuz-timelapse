import os
import subprocess
import datetime
import shutil

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

def make_video():
    # Ensure the directory for videos exists
    os.makedirs("videos", exist_ok=True)
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    output_file = f"videos/hormuz_timelapse_{today}.mp4"
    
    # Get all screenshots
    screenshots = sorted([f for f in os.listdir("screenshots") if f.startswith("hormuz_") and f.endswith(".png")])
    
    if not screenshots:
        print("No screenshots found to make a video.")
        return None

    # Create a temporary file list for ffmpeg
    with open("file_list.txt", "w") as f:
        for img in screenshots:
            f.write(f"file 'screenshots/{img}'\n")
            f.write("duration 0.5\n") # 0.5 seconds per frame
        # Add the last image again to prevent ffmpeg from skipping it
        f.write(f"file 'screenshots/{screenshots[-1]}'\n")

    # Run ffmpeg to create the video
    try:
        command = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "file_list.txt",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            output_file
        ]
        subprocess.run(command, check=True)
        
        # Create a copy as latest.mp4
        shutil.copy(output_file, "videos/latest.mp4")
        
        # Update index.html with the new video in the archive
        update_index(today)
        
        print(f"Video created: {output_file}")
        return output_file
    except Exception as e:
        print(f"Error creating video: {e}")
        return None
    finally:
        if os.path.exists("file_list.txt"):
            os.remove("file_list.txt")

if __name__ == "__main__":
    make_video()
