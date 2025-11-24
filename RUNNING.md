# How to Run the Financial Hub Builder

There are multiple ways to run the Financial Hub Builder. Choose the one that works best for you.

---

## 🚀 Recommended: Use the Launcher Scripts

### Windows
```cmd
run_financial_hub.bat
```
Just double-click `run_financial_hub.bat` or run it from command prompt.

### Mac/Linux
```bash
chmod +x run_financial_hub.sh
./run_financial_hub.sh
```

---

## 🐍 Direct Python

### From Repository Root
```bash
python3 financial_docs/build_all.py
```

### From financial_docs Directory
```bash
cd financial_docs
python3 build_all.py
```

---

## 📦 Building an Executable with PyInstaller

### Why Your Current .exe Might Not Work

1. **Silent failures** - No console = no error messages
2. **Working directory issues** - Exe can't find `Archive/` folder
3. **Missing dependencies** - Not all Python files were packaged

### Building It Correctly

1. **Install PyInstaller**
   ```bash
   pip install pyinstaller
   ```

2. **Use the provided spec file**
   ```bash
   pyinstaller build_exe.spec
   ```

   This creates `dist/FinancialHub.exe` with:
   - Console window (so you can see errors)
   - Proper working directory handling
   - All required scripts bundled

3. **Run the executable**
   ```bash
   dist/FinancialHub.exe
   ```

### Debugging Your Current .exe

If your exe still doesn't work, run it from command line to see errors:

```cmd
# Windows Command Prompt
cd path\to\your\exe\directory
your_exe_name.exe

# Keep window open to see errors
your_exe_name.exe & pause
```

---

## 🔧 Troubleshooting

### "No such file or directory: Archive/"

**Problem:** Script can't find the Archive folder.

**Solution:** Run from repository root, not from `dist/` or some other folder.

### "Module not found"

**Problem:** Python can't find the scripts.

**Solution:**
- Use the launcher scripts (`run_financial_hub.bat` or `run_financial_hub.py`)
- Or make sure you're in the repository root when running

### Exe does nothing / closes immediately

**Problem:** The exe is probably set to `console=False` or has errors you can't see.

**Solutions:**
1. Rebuild with `console=True` (already set in `build_exe.spec`)
2. Run from command prompt to see errors
3. Use `run_financial_hub.py` instead - easier to debug

### Permission Errors

**Problem:** Can't write to `Archive/` folders.

**Solution:**
- Run from a directory where you have write permissions
- Don't run from `Program Files` or system directories

---

## 📂 Where Files Are Created

When you run the builder, it creates/updates:

```
financial_docs/
├── financial_hub.html          ← Main output (open this!)
└── Archive/
    ├── reports/                ← Generated markdown reports
    │   ├── TRANSACTION_ANALYSIS_REPORT.md
    │   ├── BUDGET_VS_ACTUAL.md
    │   ├── FINANCIAL_HEALTH_SCORE.md
    │   └── SCENARIO_ANALYSIS.md
    └── processed/              ← Generated JSON data
        └── dashboard_data.json
```

---

## 💡 Best Practice

**For regular use:** Just use the batch/shell scripts!
- Simple
- Easy to debug
- No compilation needed
- Works from any directory

**For distribution:** Build an exe with the proper spec file
- Bundle everything together
- Keep `console=True` for debugging
- Test thoroughly before distributing

---

## 🆘 Still Having Issues?

1. **Check Python version**
   ```bash
   python --version  # Should be 3.8+
   ```

2. **Check you're in the right directory**
   ```bash
   ls financial_docs/build_all.py  # Should exist
   ```

3. **Try the Python wrapper directly**
   ```bash
   python run_financial_hub.py
   ```
   This has extra debugging output to show what's happening.

4. **Run with verbose output**
   ```bash
   python -v financial_docs/build_all.py
   ```

---

**Still stuck?** The launcher scripts will show you exactly what's wrong!
