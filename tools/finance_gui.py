#!/usr/bin/env python3
"""
Family Finance Manager - GUI Application
Modern GUI interface with embedded budget editor and console output
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import json
import sys
import os
from pathlib import Path
import threading
from datetime import datetime

# Directories - Simple hybrid path detection
if getattr(sys, 'frozen', False):
    # Running as executable - use exe location as base
    BASE_DIR = Path(sys.executable).parent
else:
    # Running as script in tools/ - use parent directory as base
    BASE_DIR = Path(__file__).parent.parent

TOOLS_DIR = BASE_DIR / "tools"
CONFIG_FILE = TOOLS_DIR / "config.json"


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


class FinanceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Family Finance Manager")
        self.root.geometry("1200x800")

        # Color scheme
        self.colors = {
            'navy': '#0F1626',
            'leather': '#AB987A',
            'coral': '#FF533D',
            'eggshell': '#F5F5F5',
            'dark_bg': '#1a1a1a',
            'light_text': '#e0e0e0'
        }

        # Configure root background
        self.root.configure(bg=self.colors['dark_bg'])

        # Config storage
        self.config = {}
        self.budget_entries = {}

        # Create UI
        self.create_widgets()

        # Load config
        self.load_config()

    def create_widgets(self):
        """Create all GUI widgets"""

        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=BOTH, expand=YES, padx=0, pady=0)

        # Header
        header = tk.Frame(main_container, bg=self.colors['navy'], height=80)
        header.pack(fill=X, side=TOP)
        header.pack_propagate(False)

        title_label = tk.Label(
            header,
            text="FINANCE MANAGER",
            font=("Helvetica", 24, "normal"),
            bg=self.colors['navy'],
            fg='white',
            anchor=CENTER
        )
        title_label.pack(pady=10)

        subtitle_label = tk.Label(
            header,
            text="FINANCE MANAGER",
            font=("Helvetica", 10, "normal"),
            bg=self.colors['navy'],
            fg=self.colors['leather'],
            anchor=CENTER
        )
        subtitle_label.pack()

        # Create notebook (tabs)
        notebook = ttkb.Notebook(main_container, bootstyle="dark")
        notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Tab 1: Operations
        operations_tab = ttk.Frame(notebook)
        notebook.add(operations_tab, text="Operations")
        self.create_operations_tab(operations_tab)

        # Tab 2: Budget Editor
        budget_tab = ttk.Frame(notebook)
        notebook.add(budget_tab, text="Budget Editor")
        self.create_budget_tab(budget_tab)

        # Status bar at bottom
        self.status_bar = tk.Label(
            main_container,
            text="Ready",
            bg=self.colors['navy'],
            fg=self.colors['leather'],
            font=("Helvetica", 9),
            anchor=W,
            padx=10,
            height=2
        )
        self.status_bar.pack(fill=X, side=BOTTOM)

    def create_operations_tab(self, parent):
        """Create operations tab with command buttons and console"""

        # Top section - Command buttons
        btn_frame = tk.Frame(parent, bg=self.colors['dark_bg'])
        btn_frame.pack(fill=X, padx=20, pady=20)

        # Button style configuration
        btn_style = {
            'width': 15,
            'bootstyle': "dark"
        }

        # Row 1 buttons
        row1 = tk.Frame(btn_frame, bg=self.colors['dark_bg'])
        row1.pack(fill=X, pady=10)

        import_btn = ttkb.Button(
            row1,
            text="IMPORT",
            command=self.run_import,
            **btn_style
        )
        import_btn.pack(side=LEFT, padx=5)

        analyze_btn = ttkb.Button(
            row1,
            text="ANALYZE",
            command=self.run_analyze,
            **btn_style
        )
        analyze_btn.pack(side=LEFT, padx=5)

        report_btn = ttkb.Button(
            row1,
            text="REPORT",
            command=self.run_report,
            **btn_style
        )
        report_btn.pack(side=LEFT, padx=5)

        # Row 2 - Main action button
        row2 = tk.Frame(btn_frame, bg=self.colors['dark_bg'])
        row2.pack(fill=X, pady=10)

        all_btn = ttkb.Button(
            row2,
            text="RUN ALL",
            command=self.run_all,
            bootstyle="danger",
            width=30,
            padding=15
        )
        all_btn.pack(pady=5)

        open_report_btn = ttkb.Button(
            row2,
            text="OPEN REPORT",
            command=self.open_report,
            bootstyle="warning",
            width=30,
            padding=10
        )
        open_report_btn.pack(pady=5)

        # Console output section
        console_label = tk.Label(
            parent,
            text="CONSOLE OUTPUT",
            font=("Helvetica", 11, "bold"),
            bg=self.colors['dark_bg'],
            fg=self.colors['leather'],
            anchor=W
        )
        console_label.pack(fill=X, padx=20)

        # Console frame with scrollbar
        console_frame = tk.Frame(parent, bg=self.colors['dark_bg'])
        console_frame.pack(fill=BOTH, expand=YES, padx=20, pady=(5, 20))

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

        # Clear console button
        clear_btn = ttkb.Button(
            parent,
            text="CLEAR CONSOLE",
            command=self.clear_console,
            bootstyle="secondary",
            width=20
        )
        clear_btn.pack(pady=(0, 10))

    def create_budget_tab(self, parent):
        """Create budget editor tab"""

        # Create canvas with scrollbar
        canvas_frame = tk.Frame(parent, bg=self.colors['dark_bg'])
        canvas_frame.pack(fill=BOTH, expand=YES)

        canvas = tk.Canvas(canvas_frame, bg=self.colors['dark_bg'])
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['dark_bg'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Content in scrollable frame
        content = scrollable_frame

        # Monthly earnings section
        earnings_frame = tk.Frame(content, bg=self.colors['navy'], padx=20, pady=15)
        earnings_frame.pack(fill=X, padx=20, pady=20)

        earnings_label = tk.Label(
            earnings_frame,
            text="MONTHLY EARNINGS",
            font=("Helvetica", 10, "bold"),
            bg=self.colors['navy'],
            fg=self.colors['leather']
        )
        earnings_label.pack(side=LEFT, padx=10)

        self.earnings_var = tk.StringVar(value="0")
        earnings_entry = ttk.Entry(
            earnings_frame,
            textvariable=self.earnings_var,
            font=("Helvetica", 14),
            width=15
        )
        earnings_entry.pack(side=LEFT, padx=10)

        update_summary_btn = ttkb.Button(
            earnings_frame,
            text="UPDATE",
            command=self.update_summary,
            bootstyle="warning",
            width=10
        )
        update_summary_btn.pack(side=LEFT, padx=10)

        # Summary section
        summary_frame = tk.Frame(content, bg=self.colors['dark_bg'])
        summary_frame.pack(fill=X, padx=20, pady=10)

        self.total_budget_var = tk.StringVar(value="$0.00")
        self.left_for_savings_var = tk.StringVar(value="$0.00")

        # Summary cards
        summary_row = tk.Frame(summary_frame, bg=self.colors['dark_bg'])
        summary_row.pack(fill=X)

        for label, var in [
            ("TOTAL BUDGET", self.total_budget_var),
            ("LEFT FOR SAVINGS", self.left_for_savings_var)
        ]:
            card = tk.Frame(summary_row, bg=self.colors['navy'], padx=20, pady=15)
            card.pack(side=LEFT, padx=5, fill=X, expand=YES)

            lbl = tk.Label(
                card,
                text=label,
                font=("Helvetica", 9, "bold"),
                bg=self.colors['navy'],
                fg=self.colors['leather']
            )
            lbl.pack()

            val = tk.Label(
                card,
                textvariable=var,
                font=("Helvetica", 16, "bold"),
                bg=self.colors['navy'],
                fg='white'
            )
            val.pack()

        # Budget categories section
        categories_label = tk.Label(
            content,
            text="BUDGET CATEGORIES",
            font=("Helvetica", 12, "bold"),
            bg=self.colors['dark_bg'],
            fg=self.colors['leather'],
            anchor=W
        )
        categories_label.pack(fill=X, padx=20, pady=(20, 10))

        # Budget grid
        self.budget_frame = tk.Frame(content, bg=self.colors['dark_bg'])
        self.budget_frame.pack(fill=BOTH, expand=YES, padx=20, pady=10)

        # Action buttons
        actions_frame = tk.Frame(content, bg=self.colors['dark_bg'])
        actions_frame.pack(fill=X, padx=20, pady=20)

        load_config_btn = ttkb.Button(
            actions_frame,
            text="LOAD CONFIG",
            command=self.load_config_file,
            bootstyle="warning",
            width=20,
            padding=10
        )
        load_config_btn.pack(side=LEFT, padx=5)

        save_config_btn = ttkb.Button(
            actions_frame,
            text="SAVE CONFIG",
            command=self.save_config_file,
            bootstyle="danger",
            width=20,
            padding=10
        )
        save_config_btn.pack(side=LEFT, padx=5)

    def populate_budget_categories(self):
        """Populate budget category entry fields"""

        # Clear existing entries
        for widget in self.budget_frame.winfo_children():
            widget.destroy()

        self.budget_entries = {}

        if 'budget' not in self.config:
            return

        # Sort categories alphabetically
        categories = sorted(self.config['budget'].items())

        # Create grid of entries (2 columns)
        row = 0
        col = 0

        for category, amount in categories:
            # Category frame
            cat_frame = tk.Frame(
                self.budget_frame,
                bg=self.colors['navy'],
                padx=15,
                pady=10
            )
            cat_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")

            # Category label
            label = tk.Label(
                cat_frame,
                text=category,
                font=("Helvetica", 10),
                bg=self.colors['navy'],
                fg='white',
                anchor=W,
                width=25
            )
            label.pack(side=LEFT, padx=5)

            # Amount entry
            var = tk.StringVar(value=str(amount))
            entry = ttk.Entry(
                cat_frame,
                textvariable=var,
                font=("Helvetica", 11),
                width=12
            )
            entry.pack(side=RIGHT, padx=5)

            self.budget_entries[category] = var

            # Move to next position
            col += 1
            if col > 1:  # 2 columns
                col = 0
                row += 1

        # Configure grid weights
        self.budget_frame.columnconfigure(0, weight=1)
        self.budget_frame.columnconfigure(1, weight=1)

    def load_config(self):
        """Load config from config.json"""
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r') as f:
                    self.config = json.load(f)

                # Update earnings
                if 'income' in self.config and 'monthly_earnings' in self.config['income']:
                    self.earnings_var.set(str(self.config['income']['monthly_earnings']))

                # Populate budget categories
                self.populate_budget_categories()

                # Update summary
                self.update_summary()

                print(f"✅ Config loaded from {CONFIG_FILE}")
            else:
                print(f"⚠️ Config file not found: {CONFIG_FILE}")
        except Exception as e:
            print(f"❌ Error loading config: {e}")

    def load_config_file(self):
        """Load config from file dialog"""
        filename = filedialog.askopenfilename(
            title="Select config.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'r') as f:
                    self.config = json.load(f)

                if 'income' in self.config and 'monthly_earnings' in self.config['income']:
                    self.earnings_var.set(str(self.config['income']['monthly_earnings']))

                self.populate_budget_categories()
                self.update_summary()

                print(f"✅ Config loaded from {filename}")
                messagebox.showinfo("Success", "Config loaded successfully!")
            except Exception as e:
                print(f"❌ Error loading config: {e}")
                messagebox.showerror("Error", f"Failed to load config: {e}")

    def save_config_file(self):
        """Save config to file"""
        try:
            # Update config with current values
            if 'income' not in self.config:
                self.config['income'] = {}

            self.config['income']['monthly_earnings'] = float(self.earnings_var.get())

            if 'budget' not in self.config:
                self.config['budget'] = {}

            for category, var in self.budget_entries.items():
                try:
                    self.config['budget'][category] = float(var.get())
                except ValueError:
                    self.config['budget'][category] = 0.0

            self.config['last_updated'] = datetime.now().strftime('%Y-%m-%d')

            # Save to config.json
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)

            print(f"✅ Config saved to {CONFIG_FILE}")
            messagebox.showinfo("Success", f"Config saved to {CONFIG_FILE}")

        except Exception as e:
            print(f"❌ Error saving config: {e}")
            messagebox.showerror("Error", f"Failed to save config: {e}")

    def update_summary(self):
        """Update budget summary"""
        try:
            total_budget = sum(
                float(var.get()) for var in self.budget_entries.values()
            )

            earnings = float(self.earnings_var.get())
            left_for_savings = earnings - total_budget

            self.total_budget_var.set(f"${total_budget:,.2f}")
            self.left_for_savings_var.set(f"${left_for_savings:,.2f}")

        except Exception as e:
            print(f"⚠️ Error updating summary: {e}")

    def run_command(self, command):
        """Run finance.py command in background thread"""
        def run():
            try:
                self.update_status(f"Running: {command}")
                print(f"\n{'='*70}")
                print(f"Running: python finance.py {command}")
                print(f"{'='*70}\n")

                # Import finance module and run commands directly
                # This avoids subprocess issues with PyInstaller
                import finance

                fm = finance.FinanceManager()

                if command == 'import':
                    fm.load_transactions()
                elif command == 'analyze':
                    fm.load_transactions()
                    fm.analyze_spending()
                elif command == 'report':
                    fm.load_transactions()
                    fm.analyze_spending()
                    fm.generate_report()
                elif command == 'all':
                    print("=" * 70)
                    print("🚀 RUNNING FULL FINANCIAL ANALYSIS")
                    print("=" * 70)
                    fm.load_transactions()
                    fm.analyze_spending()
                    report_file = fm.generate_report()
                    fm.archive_monthly()
                    print("\n" + "=" * 70)
                    print("✅ COMPLETE!")
                    print("=" * 70)
                    print(f"\n📊 Open your report: {report_file}")
                    print(f"💰 Edit budget: budget_editor.html\n")

                print(f"\n✅ Command completed successfully")
                self.update_status("Ready")

            except Exception as e:
                print(f"❌ Error running command: {e}")
                import traceback
                traceback.print_exc()
                self.update_status("Error")

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def run_import(self):
        """Run import command"""
        self.run_command("import")

    def run_analyze(self):
        """Run analyze command"""
        self.run_command("analyze")

    def run_report(self):
        """Run report command"""
        self.run_command("report")

    def run_all(self):
        """Run all command"""
        self.run_command("all")

    def open_report(self):
        """Open generated HTML report"""
        report_path = BASE_DIR / "financial_report.html"

        if report_path.exists():
            try:
                import webbrowser
                webbrowser.open(f"file://{report_path}")
                print(f"✅ Opening report: {report_path}")
            except Exception as e:
                print(f"❌ Error opening report: {e}")
        else:
            messagebox.showwarning(
                "Report Not Found",
                f"Report not found at {report_path}\n\nRun 'REPORT' or 'RUN ALL' first."
            )
            print(f"⚠️ Report not found: {report_path}")

    def clear_console(self):
        """Clear console output"""
        self.console.delete(1.0, tk.END)
        print("Console cleared")

    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)


def main():
    """Main entry point"""
    root = ttkb.Window(
        title="Family Finance Manager",
        themename="darkly",
        size=(1200, 800)
    )

    app = FinanceGUI(root)

    # Print welcome message
    print("="*70)
    print("FAMILY FINANCE MANAGER")
    print("="*70)
    print()
    print("Welcome! Use the buttons above to run financial operations.")
    print()
    print("Commands:")
    print("  IMPORT   - Import transactions from data/transactions.csv")
    print("  ANALYZE  - Analyze spending patterns")
    print("  REPORT   - Generate financial report")
    print("  RUN ALL  - Run everything (import → analyze → report)")
    print()
    print("Use the 'Budget Editor' tab to edit your budget categories.")
    print()

    root.mainloop()


if __name__ == "__main__":
    main()
