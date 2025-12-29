#!/usr/bin/env python3
"""
Auto-Rebuild Watcher - Monitors financial data files and auto-rebuilds dashboard
Watches for changes in Archive/processed/*.json and automatically triggers rebuild
"""

import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import signal

class FileWatcher:
    def __init__(self, watch_path, build_script, debounce_seconds=5):
        self.watch_path = Path(watch_path)
        self.build_script = Path(build_script)
        self.debounce_seconds = debounce_seconds
        self.last_modified = {}
        self.running = True

        # Handle Ctrl+C gracefully
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        print('\n\n⏹️  Stopping watcher...')
        self.running = False
        sys.exit(0)

    def log(self, message):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def check_for_changes(self):
        """Check if any watched files have changed"""
        changed_files = []

        for file in self.watch_path.glob("*.json"):
            try:
                current_mtime = file.stat().st_mtime

                if file.name not in self.last_modified:
                    # First time seeing this file
                    self.last_modified[file.name] = current_mtime
                elif current_mtime > self.last_modified[file.name]:
                    # File has been modified
                    self.last_modified[file.name] = current_mtime
                    changed_files.append(file.name)

            except Exception as e:
                self.log(f"Error checking {file.name}: {str(e)}")

        return changed_files

    def rebuild_dashboard(self):
        """Trigger dashboard rebuild"""
        self.log("🔄 Building dashboard...")

        try:
            result = subprocess.run(
                [sys.executable, str(self.build_script)],
                cwd=str(self.build_script.parent),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                self.log("✓ Dashboard rebuilt successfully")
                return True
            else:
                self.log(f"❌ Build failed:")
                if result.stderr:
                    print(result.stderr)
                return False

        except subprocess.TimeoutExpired:
            self.log("❌ Build timed out (>5 minutes)")
            return False
        except Exception as e:
            self.log(f"❌ Build error: {str(e)}")
            return False

    def run(self, check_interval=2):
        """Main watch loop"""
        self.log("▶️  Auto-rebuild watcher started")
        self.log(f"📁 Watching: {self.watch_path}")
        self.log(f"🔨 Build script: {self.build_script}")
        self.log(f"⏱️  Check interval: {check_interval}s, Debounce: {self.debounce_seconds}s")
        self.log("Press Ctrl+C to stop\n")

        # Initialize file states
        self.log("Scanning initial file states...")
        self.check_for_changes()
        self.log(f"Monitoring {len(self.last_modified)} files\n")

        last_build_time = 0

        while self.running:
            try:
                changed = self.check_for_changes()

                if changed:
                    current_time = time.time()

                    # Debounce: only rebuild if enough time has passed
                    if current_time - last_build_time >= self.debounce_seconds:
                        self.log(f"📝 Detected changes: {', '.join(changed)}")

                        if self.rebuild_dashboard():
                            last_build_time = current_time
                            self.log(f"⏳ Debounce active for {self.debounce_seconds}s\n")
                        else:
                            self.log("Skipping debounce due to build failure\n")
                    else:
                        remaining = self.debounce_seconds - (current_time - last_build_time)
                        self.log(f"⏸️  Changes detected but debouncing ({remaining:.0f}s remaining)")

                time.sleep(check_interval)

            except Exception as e:
                self.log(f"❌ Watcher error: {str(e)}")
                time.sleep(check_interval)

        self.log("👋 Watcher stopped")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Watch financial data files and auto-rebuild dashboard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Use default paths
  %(prog)s --interval 5              # Check every 5 seconds
  %(prog)s --debounce 10             # Wait 10s between rebuilds
        """
    )

    parser.add_argument(
        '--watch',
        default=None,
        help='Path to watch for changes (default: Archive/processed)'
    )

    parser.add_argument(
        '--build',
        default=None,
        help='Path to build script (default: build_all.py)'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=2,
        help='Check interval in seconds (default: 2)'
    )

    parser.add_argument(
        '--debounce',
        type=int,
        default=5,
        help='Debounce time in seconds (default: 5)'
    )

    args = parser.parse_args()

    # Determine paths
    base_path = Path(__file__).parent.parent

    watch_path = args.watch if args.watch else base_path / "Archive" / "processed"
    build_script = args.build if args.build else base_path / "build_all.py"

    # Validate paths
    if not watch_path.exists():
        print(f"❌ Error: Watch path does not exist: {watch_path}")
        sys.exit(1)

    if not build_script.exists():
        print(f"❌ Error: Build script does not exist: {build_script}")
        sys.exit(1)

    # Create and run watcher
    watcher = FileWatcher(watch_path, build_script, args.debounce)
    watcher.run(args.interval)


if __name__ == "__main__":
    main()
