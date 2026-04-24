# Strait of Hormuz Daily Timelapse

Automated system to capture hourly screenshots of ship traffic in the Strait of Hormuz and generate a daily time-lapse video.

## Features

- **Hourly Captures**: Automatically takes a screenshot of the Strait of Hormuz map from VesselFinder every hour.
- **Daily Time-lapse**: Compiles the last 24 hours of screenshots into a sped-up MP4 video.
- **GitHub Pages Hosting**: Automatically hosts the latest video and an archive on GitHub Pages.
- **Email Notifications**: Sends a daily email to the user with a link to the new video.

## Repository Structure

- `capture.py`: Playwright script to navigate to VesselFinder and capture the map.
- `make_video.py`: FFmpeg script to compile screenshots into a video and update the index.
- `send_email.py`: Helper script to send email notifications via Gmail.
- `index.html`: Landing page for GitHub Pages to view the videos.
- `screenshots/`: Directory where hourly captures are stored.
- `videos/`: Directory where daily time-lapse videos are stored.

## Setup Instructions

### 1. Enable GitHub Pages
1. Go to your repository **Settings**.
2. Navigate to **Pages** in the left sidebar.
3. Under **Build and deployment > Source**, select **GitHub Actions**.

### 2. Configure Workflow Permissions
1. Go to **Settings > Actions > General**.
2. Scroll down to **Workflow permissions**.
3. Select **Read and write permissions**.
4. Check **Allow GitHub Actions to create and approve pull requests**.
5. Click **Save**.

### 3. Add Workflow Files
Due to security restrictions, you must manually create the workflow files in the `.github/workflows/` directory:

#### `.github/workflows/hourly_capture.yml`
```yaml
name: Hourly Screenshot Capture
on:
  schedule:
    - cron: '0 * * * *'
  workflow_dispatch:
jobs:
  capture:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      - run: |
          pip install playwright
          playwright install chromium --with-deps
      - run: python capture.py
      - run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add screenshots/
          git commit -m "Add hourly screenshot" || echo "No changes"
          git push
```

#### `.github/workflows/daily_video.yml`
```yaml
name: Daily Video Compilation and Email
on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:
jobs:
  build_and_deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pages: write
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      - run: |
          pip install playwright
          playwright install chromium --with-deps
          sudo apt-get update && sudo apt-get install -y ffmpeg
      - run: python make_video.py
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: 'videos'
      - id: deployment
        uses: actions/deploy-pages@v4
      - name: Send Email
        env:
          RECIPIENT_EMAIL: johnx93@gmail.com
          VIDEO_URL: ${{ steps.deployment.outputs.page_url }}/hormuz_timelapse_$(date +%Y-%m-%d).mp4
        run: python send_email.py $RECIPIENT_EMAIL $VIDEO_URL
```

## Credits
Created by [Manus AI](https://manus.im).
