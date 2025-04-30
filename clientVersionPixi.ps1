#############Skripta za verzioniranje iger za NC! 
##GAME VERZIJA (ali build verzija) je sestavljena iz:
## GA->kratica brand-a (lahko je tudi LU!)
## 01->naša verzija repota (stari-01, novi-02, še bolj novi-03...)
## št->svn revision number (dobljena avtomatsko iz svn)
## ML->datum v obliki M=07, L=2020 => 072020
##skripta je lahko za lokalni build, kot tudi za server!
##Vhodni parametri: verzija repota, (lokalna) pot do repota, pot do bildanih iger, ime igre ("ime1"), kratice verzije ("LU") - deprecated
##vhodni parametri (12.11.2020): verzija repota, (lokalna) pot do repota, pot do bildanih iger, kratice verzije ("LU")
##OPOMBA2: vsi vhodni argumenti, razen poti, se naj vnesejo kot stringi-med narokovaji=>"lv"

###vhodni argumenti:
$gameName = $args[0] ##ime igre

#GAME REV and COUNT
#$gitPot =  ""
#cd $gitPot
$countNum = git rev-list --count HEAD
$revNum = git rev-parse --short HEAD

# Load JSON file for core tag
$json = Get-Content -Path package.json -Raw | ConvertFrom-Json
$getDependencies= ($json.dependencies)
Write-Output "$getDependencies"
$getCorePixiBuild= (($getDependencies."core-pixi-webpack").split('#v')[-1]).Split(".")
$aa= $getCorePixiBuild[0].PadLeft(2, '0')
$bb= $getCorePixiBuild[1].PadLeft(2, '0')
$cccc= $getCorePixiBuild[2].PadLeft(4, '0')

$coreTag = $aa+$bb+$cccc

#Write-Output "Version: $json"
Write-Output "Version: $coreTag"


#CORE REV and COUNT
# $gitPotCore = "..\core-pixi-webpack\"
# cd $gitPotCore
# $countNumCore = git rev-list --count HEAD
# $revNumCore = git rev-parse --short HEAD

#DATE
$countdate = Get-Date -UFormat "%m%Y" #pridobimo datum v pravi obliki...podatek za VERZIJO
$revDate = Get-Date -UFormat "%Y%m%d" #podatek za REVIZIVO

#blocks
$F = "_"
$prefix = "GA"
$repoVer = "04"

##create version
$version = "$prefix$F$repoVer$F$coreTag$F$countNum$F$countdate" ##končna verzija, ki se mora zapisati...
$revision = "$prefix$revDate$F$coreTag$F$revNum" #formatirana revizija pripravljena za zapis

# $gitPotGame = "..\build\"
# cd $gitPotGame
Write-Output "Mapa:$gameName"
####ŠE ZAPIS VERZIJE V FAJL V MAPO + V VSE STRINGS FAJLE#####
$jePot = Test-Path "prod_bin\assets\version\gameversion.json" #dodamo še zadnji check
if($jePot -eq $false)
{
    Write-Output "Mapa ali datoteka za verzijo NE OBSTAJA! Verzija ne bo zapisana."
    exit 4
}

#tu vemo, da pot in fajl obstajata (vendar je lahko file zapisan narobe):
try {
    $jsonObj = Get-Content "prod_bin\assets\version\gameversion.json" | ConvertFrom-Json
    $jsonObj.GAMEVERSION = $version
}
catch [System.ArgumentException] { #tu vemo, da gre za napačen json zapis...zato naredimo kar svojega!
    #zato ustvarimo kar svoj json object:
    $jsonObj = [PSCustomObject]@{
        GAMEVERSION = $version
    }
}
catch { #za primere, če se zgodi karkoli drugega čudnega
    Write-Output $_
    exit 1 #končamo...
}

#če je vse ok, zapišemo verzijo v desktop in mobile fajl ter generiramo dodaten info file
#ZAPIS V DESKTOP
$jsonStr = ConvertTo-Json $jsonObj
Set-Content -Path "prod_bin\assets\version\gameversion.json" -Value $jsonStr ##tu pa povozimo vsebino version fajla...se v celoti zapiše
New-Item -Path "prod_bin\assets\version" -Name "$version.version" -ItemType "file" -Value $version -Force ##legacy-shranimo version file v mapo (samo za hitrejše odčitavanje verzije)
New-Item -Path "prod_bin\assets\version" -Name "$revision.revision" -ItemType "file" -Value $revision -Force ##legacy-shranimo version file v mapo (samo za hitrejše odčitavanje verzije)

Write-Output "Version: $version"
Write-Output "Revision: $revision"