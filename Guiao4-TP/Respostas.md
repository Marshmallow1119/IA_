Variáveis independentes

ST -> utilizador tem sobrecarga de trabalho
UPAL -> utilizador está a usar o PAL

Variáveis dependentes

FER -> frequencia exagerada de utilizacao do rato
PA -> precisa de ajuda
CP -> cara preocupada
CNL -> correino não lido

Topologia de rede
'sc'->ST
'pt'-> UPAL
'cp'->CP
'fr'->FER
'pa'->PA
'cnl'->CNL

    ST
   /|
  / | 
CNL | PA----UPAL
    | /\    /
    |/  \  /
    CA  FER


P(ST)=0.60
P(UPAL)=0.05

P(PA|UPAL)= 0.25
P(PA|~UPAL)= 0.004



P(PA|ST,UPAL)=0.02
P(PA|ST,~UPAL)=0.01
P(PA|~ST,UPAL)=0.011
P(PA|~ST,~UPAL)=0.001

P(CP|ST,PA)= 0.02
P(CP|ST,~PA)= 0.01
P(CP|~ST,PA)= 0.011
P(CP|~ST,~PA)= 0.001

P(FER|PA,UPAL)=0.9
P(FER|PA,~UPAL)=0.1
P(FER|~PA,UPAL)=0.9
P(FER|~PA,~UPAL)=0.01


P(CNL|ST)= 0.9
P(CNL|~ST)= 0.001