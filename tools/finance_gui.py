#!/usr/bin/env python3
"""
Mom's Budget Manager - GUI Application
Simple interface with one-click budget report generation
"""

import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import sys
import os
from pathlib import Path
import threading
import webbrowser

# Directories
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.parent

TOOLS_DIR = BASE_DIR / "tools"
REPORT_FILE = BASE_DIR / "financial_report.html"


class ConsoleRedirector:
    """Redirect stdout/stderr to GUI console"""
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()

    def flush(self):
        pass


class BudgetGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mom's Budget Manager")
        self.root.geometry("1000x700")

        # Color scheme
        self.colors = {
            'navy': '#0F1626',
            'leather': '#AB987A',
            'purple': '#667eea',
            'dark_bg': '#1a1a1a',
        }

        self.root.configure(bg=self.colors['dark_bg'])

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        """Create all GUI widgets"""

        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=BOTH, expand=YES, padx=0, pady=0)

        # Header
        header = tk.Frame(main_container, bg=self.colors['navy'], height=120)
        header.pack(fill=X, side=TOP)
        header.pack_propagate(False)

        title_label = tk.Label(
            header,
            text="💰 MOM'S BUDGET MANAGER",
            font=("Helvetica", 28, "bold"),
            bg=self.colors['navy'],
            fg='white',
            anchor=CENTER
        )
        title_label.pack(pady=30)

        # Content area
        content = tk.Frame(main_container, bg=self.colors['dark_bg'])
        content.pack(fill=BOTH, expand=YES, padx=20, pady=20)

        # Instructions
        instructions = tk.Label(
            content,
            text="Drop your Excel budget file in the 'data/inputs' folder,\nthen click the button below to generate your report!",
            font=("Helvetica", 12),
            bg=self.colors['dark_bg'],
            fg=self.colors['leather'],
            justify=CENTER
        )
        instructions.pack(pady=20)

        # Big RUN ALL button
        self.run_btn = ttkb.Button(
            content,
            text="🚀 GENERATE REPORT",
            command=self.run_analysis,
            bootstyle="danger",
            width=30,
            padding=20
        )
        self.run_btn.pack(pady=30)

        # Secondary buttons
        btn_row = tk.Frame(content, bg=self.colors['dark_bg'])
        btn_row.pack(pady=10)

        open_report_btn = ttkb.Button(
            btn_row,
            text="📊 Open Report",
            command=self.open_report,
            bootstyle="warning",
            width=15,
            padding=10
        )
        open_report_btn.pack(side=LEFT, padx=5)

        edit_budget_btn = ttkb.Button(
            btn_row,
            text="💰 Edit Budget",
            command=self.open_budget_editor,
            bootstyle="info",
            width=15,
            padding=10
        )
        edit_budget_btn.pack(side=LEFT, padx=5)

        clear_btn = ttkb.Button(
            btn_row,
            text="🗑️ Clear Console",
            command=self.clear_console,
            bootstyle="secondary",
            width=15,
            padding=10
        )
        clear_btn.pack(side=LEFT, padx=5)

        # Console output section
        console_label = tk.Label(
            content,
            text="CONSOLE OUTPUT",
            font=("Helvetica", 11, "bold"),
            bg=self.colors['dark_bg'],
            fg=self.colors['leather'],
            anchor=W
        )
        console_label.pack(fill=X, pady=(20, 5))

        # Console frame with scrollbar
        console_frame = tk.Frame(content, bg=self.colors['dark_bg'])
        console_frame.pack(fill=BOTH, expand=YES, pady=10)

        scrollbar = ttk.Scrollbar(console_frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.console = tk.Text(
            console_frame,
            bg='#1e1e1e',
            fg='#d4d4d4',
            font=("Consolas", 10),
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            padx=10,
            pady=10
        )
        self.console.pack(fill=BOTH, expand=YES)
        scrollbar.config(command=self.console.yview)

        # Redirect stdout to console
        sys.stdout = ConsoleRedirector(self.console)
        sys.stderr = ConsoleRedirector(self.console)

        # Status bar
        self.status_bar = tk.Label(
            main_container,
            text="Ready - Drop Excel file in data/inputs/ and click Generate Report",
            bg=self.colors['navy'],
            fg=self.colors['leather'],
            font=("Helvetica", 9),
            anchor=W,
            padx=10,
            height=2
        )
        self.status_bar.pack(fill=X, side=BOTTOM)

        # Print welcome message
        self.print_welcome()

    def print_welcome(self):
        """Print welcome message"""
        print("=" * 70)
        print("💰 MOM'S BUDGET MANAGER")
        print("=" * 70)
        print()
        print("Welcome! Here's how to use this program:")
        print()
        print("1. Drop your Excel budget file in: data/inputs/")
        print("2. Click the big 'GENERATE REPORT' button above")
        print("3. Wait for it to finish processing")
        print("4. Click 'Open Report' to view your beautiful budget report!")
        print()
        print("You can also:")
        print("  • Click 'Edit Budget' to modify your budget categories")
        print("  • Click 'Clear Console' to clean up this window")
        print()
        print("That's it! Ready when you are.")
        print()

    def run_analysis(self):
        """Run the full budget analysis"""
        def run():
            try:
                self.update_status("Processing...")
                self.run_btn.config(state='disabled')

                # Import and run finance module
                import finance

                manager = finance.BudgetManager()
                success = manager.run()

                if success:
                    self.update_status("Complete! Click 'Open Report' to view")
                    messagebox.showinfo(
                        "Success!",
                        "Report generated successfully!\n\nClick 'Open Report' to view it."
                    )
                else:
                    self.update_status("Error - Check console for details")

            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()
                self.update_status("Error - Check console")
                messagebox.showerror("Error", f"Failed to generate report:\n{str(e)}")

            finally:
                self.run_btn.config(state='normal')

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def open_report(self):
        """Open generated HTML report"""
        if REPORT_FILE.exists():
            try:
                webbrowser.open(f"file://{REPORT_FILE}")
                print(f"✅ Opening report: {REPORT_FILE}")
                self.update_status("Report opened in browser")
            except Exception as e:
                print(f"❌ Error opening report: {e}")
                messagebox.showerror("Error", f"Failed to open report: {e}")
        else:
            messagebox.showwarning(
                "Report Not Found",
                "Report not found!\n\nClick 'GENERATE REPORT' first to create it."
            )
            print("⚠️ Report not found. Generate report first.")

    def open_budget_editor(self):
        """Open budget editor HTML"""
        budget_editor = BASE_DIR / "budget_editor.html"
        if budget_editor.exists():
            try:
                webbrowser.open(f"file://{budget_editor}")
                print(f"✅ Opening budget editor: {budget_editor}")
                self.update_status("Budget editor opened in browser")
            except Exception as e:
                print(f"❌ Error opening budget editor: {e}")
                messagebox.showerror("Error", f"Failed to open budget editor: {e}")
        else:
            messagebox.showerror("Error", "Budget editor not found!")

    def clear_console(self):
        """Clear console output"""
        self.console.delete(1.0, tk.END)
        self.print_welcome()
        self.update_status("Console cleared")

    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)


def main():
    """Main entry point"""
    root = ttkb.Window(
        title="Mom's Budget Manager",
        themename="darkly",
        size=(1000, 700)
    )

    app = BudgetGUI(root)

    root.mainloop()


if __name__ == "__main__":
    main()
