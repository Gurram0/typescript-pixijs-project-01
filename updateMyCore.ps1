$installModules = $args[0]
Write-Output "arg: $installModules"

$gameName=Split-Path -Path (Get-Location) -Leaf
Write-Output "Game folder: $gameName"
cd..
cd core-pixi-webpack
Write-Output "CORE FOLDER:"(Split-Path -Path (Get-Location) -Leaf)
if($installModules -eq "true")
{
    Write-Output "***npm run il***"
    npm run il
}
Write-Output "***npm run export***"
npm run export
Write-Output "***scripts finished - back to game folder***"
cd..
cd $gameName
Get-Location