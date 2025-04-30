cd dist
gci -file | where { $_.Name -match 'main.+.js.map' } | Rename-Item -NewName 'main.js.map'
gci -file | where { $_.Name -match 'main.+.js' } | Rename-Item -NewName 'main.js'
(gc index.html) -replace '/main.+.js', 'main.js' | Out-File -FilePath index.html -Encoding default
cd ..