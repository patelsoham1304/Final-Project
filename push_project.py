import subprocess
import sys

def run(cmd):
    print(f"\n>> {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print("[ERR/INFO]:", result.stderr.strip())
    return result.returncode

def main():
    repo_url = "https://github.com/patelsoham1304/Final-Project.git"
    print("=" * 50)
    print("Pushing complete project to GitHub...")
    print(f"Target: {repo_url}")
    print("=" * 50)

    run("git config --global user.name \"patelsoham1304\"")
    run("git config --global user.email \"patelsoham1304@users.noreply.github.com\"")
    
    run("git status --short")
    run("git add .")
    run("git commit -m \"feat: complete education path generator application\"")
    run("git branch -M main")
    run(f"git remote remove origin")
    run(f"git remote add origin {repo_url}")
    print("\nPushing to GitHub (main branch)...")
    code = run("git push -u origin main --force")
    
    if code == 0:
        print("\n" + "=" * 50)
        print("SUCCESS: Project successfully pushed to GitHub!")
        print("Repo: https://github.com/patelsoham1304/Final-Project")
        print("=" * 50)
    else:
        print("\n[!] Push failed or requires GitHub login credentials.")

if __name__ == "__main__":
    main()
