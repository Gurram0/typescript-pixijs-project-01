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
$ver = $args[0] ##CERT VERZIJA

##create version
$version = "$ver" ##končna verzija, ki se mora zapisati...

####ŠE ZAPIS VERZIJE V FAJL V MAPO + V VSE STRINGS FAJLE#####
$jePot = Test-Path "dist\version\gameversion.json" #dodamo še zadnji check
if($jePot -eq $false)
{
    Write-Output "Mapa ali datoteka za verzijo NE OBSTAJA! Verzija ne bo zapisana."
    exit 4
}

#tu vemo, da pot in fajl obstajata (vendar je lahko file zapisan narobe):
try {
    $jsonObj = Get-Content "dist\version\gameversion.json" | ConvertFrom-Json
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
Set-Content -Path "dist\version\gameversion.json" -Value $jsonStr ##tu pa povozimo vsebino version fajla...se v celoti zapiše
New-Item -Path "dist\version" -Name "$version.certversion" -ItemType "file" -Value $version -Force ##legacy-shranimo version file v mapo (samo za hitrejše odčitavanje verzije)