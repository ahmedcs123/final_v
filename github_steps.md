# How to Upload Your Project to GitHub

Open your terminal in the project folder (`c:\Users\Ahmed Abo-Essa\OneDrive\Desktop\F`) and run the following commands one by one:

### 1. Initialize Git
```powershell
git init
```

### 2. Add All Files
```powershell
git add .
```

### 3. Commit Your Changes
```powershell
git commit -m "Final version ready for deployment"
```

### 4. Rename Branch to Main
```powershell
git branch -M main
```

### 5. Link Your Repository
```powershell
git remote add origin https://github.com/ahmedcs123/final_v.git
```

### 6. Push to GitHub
```powershell
git push -u origin main
```

---
**Note:** If `git remote add origin` fails because it already exists, run:
```powershell
git remote set-url origin https://github.com/ahmedcs123/final_v.git
```
Then run step 6 again.
