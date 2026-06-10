param(
    [Parameter(Mandatory=$true)]
    [string]$RemoteUrl
)
if (-not (git rev-parse --is-inside-work-tree 2>$null)) {
    Write-Error "Not inside a git repository"
    exit 1
}
git remote add origin $RemoteUrl
git branch -M main -Force
git push -u origin main
